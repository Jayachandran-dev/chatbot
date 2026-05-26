"""Pydantic schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str
    password: str


# --- Sites ---
class SiteCreate(BaseModel):
    name: str
    domain: str


class SiteOut(BaseModel):
    id: str
    name: str
    domain: str
    config: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    config: Dict[str, Any]


# --- Knowledge ---
class FAQIn(BaseModel):
    question: str
    answer: str


class FAQOut(FAQIn):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UrlIngest(BaseModel):
    url: str
    crawl: bool = False
    max_pages: int = 10


class DocumentOut(BaseModel):
    id: str
    source_type: str
    source: str
    title: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Leads / Chat ---
class LeadIn(BaseModel):
    site_id: str
    name: str = ""
    email: str = ""
    phone: str = ""
    page_url: str = ""


class LeadOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    page_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatIn(BaseModel):
    site_id: str
    conversation_id: Optional[str] = None
    lead_id: Optional[str] = None
    message: str
    page_url: Optional[str] = ""
    page_title: Optional[str] = ""
    page_text: Optional[str] = ""   # visible text of current page (limited)


class ChatOut(BaseModel):
    conversation_id: str
    reply: str
    sources: List[str] = []


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    started_at: datetime
    messages: List[MessageOut]

    class Config:
        from_attributes = True


# --- Widget bootstrap ---
class WidgetConfig(BaseModel):
    site_id: str
    name: str
    config: Dict[str, Any]
