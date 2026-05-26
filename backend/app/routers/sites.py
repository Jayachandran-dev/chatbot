"""Site management (admin)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import current_user
from ..models import Site, User, DEFAULT_CONFIG
from ..schemas import SiteCreate, SiteOut, ConfigUpdate

router = APIRouter(prefix="/api/sites", tags=["sites"])


def _normalize_domain(d: str) -> str:
    d = (d or "").strip().lower()
    for p in ("http://", "https://"):
        if d.startswith(p):
            d = d[len(p):]
    return d.rstrip("/")


@router.get("", response_model=List[SiteOut])
def list_sites(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.query(Site).order_by(Site.created_at.desc()).all()


@router.post("", response_model=SiteOut)
def create_site(payload: SiteCreate, db: Session = Depends(get_db),
                _: User = Depends(current_user)):
    site = Site(name=payload.name, domain=_normalize_domain(payload.domain),
                config=dict(DEFAULT_CONFIG))
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteOut)
def get_site(site_id: str, db: Session = Depends(get_db),
             _: User = Depends(current_user)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    return site


@router.put("/{site_id}/config", response_model=SiteOut)
def update_config(site_id: str, payload: ConfigUpdate,
                  db: Session = Depends(get_db),
                  _: User = Depends(current_user)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    merged = dict(DEFAULT_CONFIG)
    merged.update(site.config or {})
    merged.update(payload.config or {})
    site.config = merged
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}")
def delete_site(site_id: str, db: Session = Depends(get_db),
                _: User = Depends(current_user)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    db.delete(site)
    db.commit()
    return {"ok": True}
