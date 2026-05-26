"""Public chat + widget bootstrap (no auth)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Site, Lead, Conversation, Message
from ..schemas import ChatIn, ChatOut, LeadIn, LeadOut, WidgetConfig
from ..config import settings
from ..rag import vectorstore, llm, chunker

router = APIRouter(prefix="/api/widget", tags=["widget"])


@router.get("/config/{site_id}", response_model=WidgetConfig)
def widget_config(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    return WidgetConfig(site_id=site.id, name=site.name, config=site.config or {})


@router.post("/lead", response_model=LeadOut)
def create_lead(payload: LeadIn, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == payload.site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    lead = Lead(site_id=payload.site_id, name=payload.name, email=payload.email,
                phone=payload.phone, page_url=payload.page_url)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == payload.site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    cfg = site.config or {}

    # 1. Ensure conversation
    conv = None
    if payload.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == payload.conversation_id,
            Conversation.site_id == site.id,
        ).first()
    if conv is None:
        conv = Conversation(site_id=site.id, lead_id=payload.lead_id)
        db.add(conv)
        db.flush()

    # 2. Persist user message
    user_msg = Message(conversation_id=conv.id, role="user", content=payload.message)
    db.add(user_msg)
    db.flush()

    # 3. Retrieve context from vector store
    retrieved = vectorstore.query(site.id, payload.message, top_k=settings.TOP_K)
    context_chunks: List[str] = [r["text"] for r in retrieved]
    sources = list({r["meta"].get("source", "") for r in retrieved if r["meta"].get("source")})

    # 4. Also include current-page snippet (page-aware grounding)
    if payload.page_text:
        page_excerpt = chunker.clean_text(payload.page_text)[:1500]
        if page_excerpt:
            context_chunks.insert(
                0,
                f"[Current page: {payload.page_title or payload.page_url}]\n{page_excerpt}",
            )

    # 5. Build history
    history = [
        {"role": m.role, "content": m.content}
        for m in conv.messages
        if m.id != user_msg.id
    ]

    # 6. Generate
    reply = llm.generate(
        bot_name=cfg.get("botName", "Assistant"),
        site_name=site.name,
        context_chunks=context_chunks,
        history=history,
        user_msg=payload.message,
        fallback=cfg.get("fallbackMessage", "I'll have our team get back to you."),
    )

    bot_msg = Message(conversation_id=conv.id, role="bot", content=reply)
    db.add(bot_msg)
    db.commit()

    return ChatOut(conversation_id=conv.id, reply=reply, sources=sources)


@router.get("/health")
def health():
    return {"ok": True, "llm": llm.status()}
