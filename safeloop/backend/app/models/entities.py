from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="user")
    emergency_phrase: Mapped[str] = mapped_column(String(80), default="Code Red")
    microphone_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contacts = relationship("TrustedContact", cascade="all, delete-orphan")
    journeys = relationship("Journey", cascade="all, delete-orphan")


class TrustedContact(Base):
    __tablename__ = "trusted_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    relationship: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Responder(Base):
    __tablename__ = "responders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(60))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    response_count: Mapped[int] = mapped_column(Integer, default=0)


class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    origin_label: Mapped[str] = mapped_column(String(255), default="Current Location")
    destination: Mapped[str] = mapped_column(String(255))
    selected_mode: Mapped[str] = mapped_column(String(40), default="safeloop")
    status: Mapped[str] = mapped_column(String(40), default="active")
    distance_km: Mapped[float] = mapped_column(Float, default=0)
    duration_min: Mapped[int] = mapped_column(Integer, default=0)
    safety_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(40), default="LOW")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    routes = relationship("RouteOption", cascade="all, delete-orphan")


class RouteOption(Base):
    __tablename__ = "route_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journey_id: Mapped[int | None] = mapped_column(ForeignKey("journeys.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(80))
    mode: Mapped[str] = mapped_column(String(40))
    distance_km: Mapped[float] = mapped_column(Float)
    duration_min: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    lighting_factor: Mapped[float] = mapped_column(Float)
    crowd_factor: Mapped[float] = mapped_column(Float)
    time_factor: Mapped[float] = mapped_column(Float)
    environment_factor: Mapped[float] = mapped_column(Float)
    path_json: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text, default="")


class SafetyScore(Base):
    __tablename__ = "safety_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journey_id: Mapped[int | None] = mapped_column(ForeignKey("journeys.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    lighting: Mapped[str] = mapped_column(String(60))
    crowd: Mapped[str] = mapped_column(String(60))
    time: Mapped[str] = mapped_column(String(60))
    environment: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    responder_id: Mapped[int | None] = mapped_column(ForeignKey("responders.id"), nullable=True)
    journey_id: Mapped[int | None] = mapped_column(ForeignKey("journeys.id"), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    trigger_type: Mapped[str] = mapped_column(String(40))
    severity: Mapped[str] = mapped_column(String(40), default="high")
    status: Mapped[str] = mapped_column(String(40), default="active")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    emergency_event_id: Mapped[int | None] = mapped_column(ForeignKey("emergency_events.id"), nullable=True)
    recipient: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="demo_sent")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    journey_id: Mapped[int | None] = mapped_column(ForeignKey("journeys.id"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)
    route_useful: Mapped[bool] = mapped_column(Boolean)
    score_made_sense: Mapped[bool] = mapped_column(Boolean)
    would_use_again: Mapped[bool] = mapped_column(Boolean)
    comments: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
