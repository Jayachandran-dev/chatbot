"""Knowledge base: documents, URLs, FAQs."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import current_user
from ..models import Document, FAQ, Site, User
from ..schemas import DocumentOut, UrlIngest, FAQIn, FAQOut
from ..rag import ingest, vectorstore

router = APIRouter(prefix="/api/sites/{site_id}", tags=["knowledge"])


def _get_site(db: Session, site_id: str) -> Site:
    s = db.query(Site).filter(Site.id == site_id).first()
    if not s:
        raise HTTPException(404, "Site not found")
    return s


@router.get("/documents", response_model=List[DocumentOut])
def list_docs(site_id: str, db: Session = Depends(get_db),
              _: User = Depends(current_user)):
    _get_site(db, site_id)
    return db.query(Document).filter(Document.site_id == site_id) \
        .order_by(Document.created_at.desc()).all()


@router.post("/documents/upload", response_model=DocumentOut)
async def upload_doc(site_id: str, file: UploadFile = File(...),
                     db: Session = Depends(get_db),
                     _: User = Depends(current_user)):
    _get_site(db, site_id)
    data = await file.read()
    doc = ingest.ingest_file(db, site_id, file.filename, data)
    return doc


@router.post("/documents/url", response_model=List[DocumentOut])
def ingest_url(site_id: str, payload: UrlIngest,
               db: Session = Depends(get_db),
               _: User = Depends(current_user)):
    _get_site(db, site_id)
    docs = ingest.ingest_url(db, site_id, payload.url,
                             payload.crawl, payload.max_pages)
    return docs


@router.delete("/documents/{doc_id}")
def delete_doc(site_id: str, doc_id: str,
               db: Session = Depends(get_db),
               _: User = Depends(current_user)):
    doc = db.query(Document).filter(Document.id == doc_id,
                                    Document.site_id == site_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    vectorstore.delete_doc(site_id, doc_id)
    db.delete(doc)
    db.commit()
    return {"ok": True}


@router.get("/faqs", response_model=List[FAQOut])
def list_faqs(site_id: str, db: Session = Depends(get_db),
              _: User = Depends(current_user)):
    _get_site(db, site_id)
    return db.query(FAQ).filter(FAQ.site_id == site_id) \
        .order_by(FAQ.created_at.desc()).all()


@router.post("/faqs", response_model=FAQOut)
def create_faq(site_id: str, payload: FAQIn,
               db: Session = Depends(get_db),
               _: User = Depends(current_user)):
    _get_site(db, site_id)
    faq = FAQ(site_id=site_id, question=payload.question, answer=payload.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    ingest.reindex_faq(db, site_id, faq)
    return faq


@router.delete("/faqs/{faq_id}")
def delete_faq(site_id: str, faq_id: str,
               db: Session = Depends(get_db),
               _: User = Depends(current_user)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id, FAQ.site_id == site_id).first()
    if not faq:
        raise HTTPException(404, "FAQ not found")
    vectorstore.delete_doc(site_id, f"faq_{faq.id}")
    db.delete(faq)
    db.commit()
    return {"ok": True}
