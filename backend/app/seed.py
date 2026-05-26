"""Seed default admin and a Zenfuture demo site."""
from sqlalchemy.orm import Session

from .db import SessionLocal, Base, engine
from .models import User, Site, FAQ, DEFAULT_CONFIG
from .auth import hash_password
from .config import settings
from .rag import ingest


ZENFUTURE_ABOUT = (
    "Zenfuture Technologies is a software services company that builds custom web "
    "applications, mobile apps, AI-powered tools, and enterprise integrations. "
    "Our services include web development (Vue.js, React, Angular), backend engineering "
    "(Python, Node.js, .NET), mobile development (Flutter, React Native), cloud "
    "deployments (AWS, Azure, GCP) and AI/ML consulting. We work with startups and "
    "enterprises across India and globally. Reach us at hello@zenfuture.tech or "
    "+91-00000-00000. Our office is located in Chennai, Tamil Nadu, India. "
    "Business hours are Monday to Friday, 9:30 AM to 6:30 PM IST."
)


def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # admin
        if not db.query(User).filter(User.username == settings.ADMIN_USER).first():
            db.add(User(username=settings.ADMIN_USER,
                        password_hash=hash_password(settings.ADMIN_PASSWORD)))
            db.commit()

        # demo site
        demo = db.query(Site).filter(Site.domain == "zenfuture.tech").first()
        if not demo:
            cfg = dict(DEFAULT_CONFIG)
            cfg["botName"] = "ZenBot"
            cfg["welcomeMessage"] = "Hi! Welcome to Zenfuture Technologies. How can I help you today?"
            cfg["contactEmail"] = "hello@zenfuture.tech"
            cfg["showContact"] = True
            demo = Site(name="Zenfuture Technologies",
                        domain="zenfuture.tech", config=cfg)
            db.add(demo)
            db.commit()
            db.refresh(demo)

            # seed some knowledge
            ingest.ingest_text(db, demo.id, "file", "about.txt",
                               "About Zenfuture", ZENFUTURE_ABOUT)

            faqs = [
                ("What services do you offer?",
                 "We offer web & mobile app development, AI/ML consulting, "
                 "cloud deployments and enterprise integrations."),
                ("How can I contact you?",
                 "You can email us at hello@zenfuture.tech or call +91-00000-00000."),
                ("Where are you located?",
                 "Our office is in Chennai, Tamil Nadu, India."),
            ]
            for q, a in faqs:
                faq = FAQ(site_id=demo.id, question=q, answer=a)
                db.add(faq); db.commit(); db.refresh(faq)
                ingest.reindex_faq(db, demo.id, faq)
    finally:
        db.close()
