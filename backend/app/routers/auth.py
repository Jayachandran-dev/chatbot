"""Auth router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import verify_password, create_token, current_user
from ..models import User
from ..schemas import Token, LoginIn

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return Token(access_token=create_token(user.username))


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username, "is_admin": user.is_admin}
