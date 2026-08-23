from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TrustedContact, User
from ..schemas.api import LoginIn, ProfileUpdate, RegisterIn, Token
from ..utils.security import create_access_token, current_user, hash_password, verify_password


router = APIRouter(prefix="/api", tags=["auth"])


def public_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "emergency_phrase": user.emergency_phrase,
        "microphone_enabled": user.microphone_enabled,
    }


@router.post("/auth/register", response_model=Token)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.role not in {"user", "responder", "admin"}:
        raise HTTPException(status_code=400, detail="Unsupported role")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(name=payload.name, email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    if user.role == "user":
        db.add_all([
            TrustedContact(user_id=user.id, name="Mom", relationship="Parent", phone="+10000000001", email="mom@example.com"),
            TrustedContact(user_id=user.id, name="Friend", relationship="Friend", phone="+10000000002", email="friend@example.com"),
        ])
        db.commit()
    return Token(access_token=create_access_token(user.email, user.role), user=public_user(user))


@router.post("/auth/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return Token(access_token=create_access_token(user.email, user.role), user=public_user(user))


@router.get("/profile")
def profile(user: User = Depends(current_user)):
    return public_user(user)


@router.put("/profile")
def update_profile(payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for field in ["name", "emergency_phrase", "microphone_enabled"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return public_user(user)


@router.post("/privacy/delete-data")
def delete_my_data(user: User = Depends(current_user), db: Session = Depends(get_db)):
    from ..models import EmergencyEvent, Feedback, Journey, Notification, SafetyScore, TrustedContact

    for model in [Notification, Feedback, SafetyScore, EmergencyEvent, Journey, TrustedContact]:
        db.query(model).filter(model.user_id == user.id).delete(synchronize_session=False)
    db.commit()
    return {"message": "Your SAFELOOP journey, SOS, contact, feedback, and notification data has been deleted."}


@router.delete("/privacy/delete-account")
def delete_account(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()
    return {"message": "Your SAFELOOP account has been deleted."}
