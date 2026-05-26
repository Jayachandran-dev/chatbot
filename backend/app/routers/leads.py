"""Leads & conversations (admin)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import current_user
from ..models import Lead, Conversation, User, Site
from ..schemas import LeadOut, ConversationOut

router = APIRouter(prefix="/api/sites/{site_id}", tags=["leads"])


@router.get("/leads", response_model=List[LeadOut])
def list_leads(site_id: str, db: Session = Depends(get_db),
               _: User = Depends(current_user)):
    return db.query(Lead).filter(Lead.site_id == site_id) \
        .order_by(Lead.created_at.desc()).all()


@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(site_id: str, db: Session = Depends(get_db),
                       _: User = Depends(current_user)):
    return db.query(Conversation).filter(Conversation.site_id == site_id) \
        .order_by(Conversation.started_at.desc()).limit(200).all()


@router.get("/leads/{lead_id}/conversations", response_model=List[ConversationOut])
def lead_conversations(site_id: str, lead_id: str,
                       db: Session = Depends(get_db),
                       _: User = Depends(current_user)):
    return db.query(Conversation).filter(
        Conversation.site_id == site_id,
        Conversation.lead_id == lead_id,
    ).order_by(Conversation.started_at.desc()).all()
