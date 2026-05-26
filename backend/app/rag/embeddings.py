"""Embeddings via sentence-transformers (fully local)."""
from typing import List
import threading

from ..config import settings

_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(settings.EMBED_MODEL)
    return _model


def embed(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = get_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vecs.tolist()
