"""High-level ingestion orchestration."""
from sqlalchemy.orm import Session

from ..models import Document, FAQ
from ..config import settings
from . import chunker, vectorstore, crawler


def ingest_text(db: Session, site_id: str, source_type: str, source: str,
                title: str, text: str) -> Document:
    chunks = chunker.chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    doc = Document(site_id=site_id, source_type=source_type, source=source,
                   title=title or source, chunk_count=len(chunks))
    db.add(doc)
    db.flush()
    vectorstore.add_chunks(site_id, doc.id, chunks,
                           meta={"source": source, "title": title or source,
                                 "source_type": source_type})
    db.commit()
    db.refresh(doc)
    return doc


def ingest_file(db: Session, site_id: str, filename: str, data: bytes) -> Document:
    text = crawler.extract_file(filename, data)
    return ingest_text(db, site_id, "file", filename, filename, text)


def ingest_url(db: Session, site_id: str, url: str, crawl: bool, max_pages: int):
    docs = []
    if crawl:
        pages = crawler.crawl(url, max_pages=max_pages)
        for u, title, text in pages:
            docs.append(ingest_text(db, site_id, "url", u, title, text))
    else:
        title, text = crawler.fetch_url(url)
        docs.append(ingest_text(db, site_id, "url", url, title, text))
    return docs


def reindex_faq(db: Session, site_id: str, faq: FAQ):
    text = f"Q: {faq.question}\nA: {faq.answer}"
    # store as a tiny document referenced by faq id
    vectorstore.delete_doc(site_id, f"faq_{faq.id}")
    vectorstore.add_chunks(site_id, f"faq_{faq.id}", [text],
                           meta={"source": "FAQ", "title": faq.question[:80],
                                 "source_type": "faq"})
