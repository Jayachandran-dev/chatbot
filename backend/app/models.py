"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from .db import Base


def uid() -> str:
    return uuid.uuid4().hex


DEFAULT_CONFIG = {
    "welcomeMessage": "Hi! Welcome to our website. How can I help you today?",
    "leadFormTitle": "Before we start, please share your details:",
    "primaryColor": "#4F46E5",
    "secondaryColor": "#ffffff",
    "position": "bottom-right",
    "botName": "Assistant",
    "botAvatar": "",
    "showContact": False,
    "contactEmail": "",
    "contactPhone": "",
    "requireLead": True,
    "fields": {"name": True, "email": True, "phone": True},
    "fallbackMessage": "I'm not sure about that. Our team will get back to you shortly.",
}


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uid)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Site(Base):
    __tablename__ = "sites"
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False, index=True)
    config = Column(JSON, default=lambda: dict(DEFAULT_CONFIG))
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="site", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="site", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="site", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=uid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False, index=True)
    source_type = Column(String, nullable=False)  # 'file' | 'url'
    source = Column(String, nullable=False)       # filename or URL
    title = Column(String, default="")
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="documents")


class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(String, primary_key=True, default=uid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="faqs")


class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=uid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False, index=True)
    name = Column(String, default="")
    email = Column(String, default="")
    phone = Column(String, default="")
    page_url = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=uid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False, index=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation",
                            cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=uid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' | 'bot'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
