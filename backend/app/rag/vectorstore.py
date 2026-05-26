"""Chroma vector store, scoped per site."""
from typing import List, Dict, Any
import chromadb

from ..config import settings
from . import embeddings

_client = None


def client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    return _client


def _collection(site_id: str):
    return client().get_or_create_collection(
        name=f"site_{site_id}",
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(site_id: str, doc_id: str, chunks: List[str], meta: Dict[str, Any]):
    if not chunks:
        return
    col = _collection(site_id)
    vecs = embeddings.embed(chunks)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [{**meta, "doc_id": doc_id, "chunk": i} for i in range(len(chunks))]
    col.add(ids=ids, embeddings=vecs, documents=chunks, metadatas=metadatas)


def delete_doc(site_id: str, doc_id: str):
    col = _collection(site_id)
    try:
        col.delete(where={"doc_id": doc_id})
    except Exception:
        pass


def query(site_id: str, text: str, top_k: int = 4) -> List[Dict[str, Any]]:
    col = _collection(site_id)
    if col.count() == 0:
        return []
    vec = embeddings.embed([text])[0]
    res = col.query(query_embeddings=[vec], n_results=top_k)
    out = []
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    for d, m, dist in zip(docs, metas, dists):
        out.append({"text": d, "meta": m or {}, "score": 1.0 - float(dist)})
    return out
