"""Local LLM (llama.cpp) with extractive fallback.

If `llama-cpp-python` is installed and the model file is available (auto-downloaded
once on first run), we generate a grounded answer. Otherwise we return a clean
extractive answer built from the top retrieved chunks.

No external API is ever called.
"""
from __future__ import annotations
import os
import threading
from pathlib import Path
from typing import List, Optional

from ..config import settings

_llm = None
_llm_lock = threading.Lock()
_llm_unavailable_reason: Optional[str] = None


def _model_path() -> Path:
    return Path(settings.MODELS_DIR) / settings.LLM_MODEL_FILE


def _download_model() -> bool:
    """Download the GGUF model if missing. Returns True on success."""
    path = _model_path()
    if path.exists() and path.stat().st_size > 1_000_000:
        return True
    try:
        import httpx
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".part")
        with httpx.stream("GET", settings.LLM_MODEL_URL, follow_redirects=True, timeout=None) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=1 << 20):
                    f.write(chunk)
        tmp.rename(path)
        return True
    except Exception as e:
        global _llm_unavailable_reason
        _llm_unavailable_reason = f"model download failed: {e}"
        return False


def get_llm():
    """Lazy-load the llama.cpp model. Returns None if unavailable."""
    global _llm, _llm_unavailable_reason
    if _llm is not None:
        return _llm
    if not settings.LLM_ENABLED:
        return None
    with _llm_lock:
        if _llm is not None:
            return _llm
        try:
            from llama_cpp import Llama  # type: ignore
        except Exception as e:
            _llm_unavailable_reason = f"llama-cpp-python not installed: {e}"
            return None
        if not _download_model():
            return None
        try:
            _llm = Llama(
                model_path=str(_model_path()),
                n_ctx=settings.LLM_CTX,
                n_threads=max(1, (os.cpu_count() or 2) - 1),
                verbose=False,
            )
        except Exception as e:
            _llm_unavailable_reason = f"llama load failed: {e}"
            _llm = None
    return _llm


SYSTEM_PROMPT = (
    "You are {bot_name}, a helpful website assistant for {site_name}. "
    "Answer the user's question using ONLY the provided CONTEXT. "
    "Be concise, friendly and professional. "
    "If the answer is not in the context, say you don't have that information "
    "and offer to connect them with the team. Never invent facts, prices, or contact details."
)


def _build_prompt(bot_name: str, site_name: str, context: str, history: List[dict], user_msg: str) -> str:
    sys = SYSTEM_PROMPT.format(bot_name=bot_name, site_name=site_name)
    parts = [f"<|im_start|>system\n{sys}\n\nCONTEXT:\n{context}\n<|im_end|>"]
    for m in history[-6:]:
        role = "user" if m.get("role") == "user" else "assistant"
        parts.append(f"<|im_start|>{role}\n{m.get('content','')}\n<|im_end|>")
    parts.append(f"<|im_start|>user\n{user_msg}\n<|im_end|>")
    parts.append("<|im_start|>assistant\n")
    return "\n".join(parts)


def _extractive_answer(context_chunks: List[str], user_msg: str, fallback: str) -> str:
    """Fallback when no LLM available: return the best chunk, lightly framed.
    
    Prefers knowledge base chunks over page snippets (which start with [Current page:]).
    """
    if not context_chunks:
        return fallback
    
    # Find the first chunk that is NOT a page snippet
    best = None
    for chunk in context_chunks:
        if not chunk.strip().startswith("[Current page:"):
            best = chunk.strip()
            break
    
    # Fallback to first chunk if all are page snippets
    if best is None:
        best = context_chunks[0].strip()
    
    # Trim to ~3 sentences for readability
    import re
    sents = re.split(r"(?<=[.!?])\s+", best)
    snippet = " ".join(sents[:3]).strip()
    return snippet or fallback


def generate(
    bot_name: str,
    site_name: str,
    context_chunks: List[str],
    history: List[dict],
    user_msg: str,
    fallback: str,
) -> str:
    context = "\n---\n".join(context_chunks) if context_chunks else "(no context found)"
    llm = get_llm()
    if llm is None:
        return _extractive_answer(context_chunks, user_msg, fallback)
    prompt = _build_prompt(bot_name, site_name, context, history, user_msg)
    try:
        out = llm(
            prompt,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=0.2,
            top_p=0.9,
            stop=["<|im_end|>", "<|im_start|>"],
        )
        text = out["choices"][0]["text"].strip()
        return text or _extractive_answer(context_chunks, user_msg, fallback)
    except Exception:
        return _extractive_answer(context_chunks, user_msg, fallback)


def status() -> dict:
    return {
        "enabled": settings.LLM_ENABLED,
        "loaded": _llm is not None,
        "model_file": str(_model_path()),
        "model_present": _model_path().exists(),
        "reason": _llm_unavailable_reason,
    }
