"""Text chunking utilities."""
from typing import List
import re


def clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", t or "").strip()
    return t


def chunk_text(text: str, size: int = 700, overlap: int = 100) -> List[str]:
    text = clean_text(text)
    if not text:
        return []
    # split on sentence-ish boundaries, then re-pack to ~size chars
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: List[str] = []
    buf = ""
    for s in sentences:
        if len(buf) + len(s) + 1 <= size:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                chunks.append(buf)
            # start new buffer, with overlap from previous tail
            tail = buf[-overlap:] if overlap and buf else ""
            buf = (tail + " " + s).strip()
            # if a single sentence is huge, hard-split
            while len(buf) > size:
                chunks.append(buf[:size])
                buf = buf[size - overlap:]
    if buf:
        chunks.append(buf)
    return chunks
