from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "user"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    emergency_phrase: str | None = None
    microphone_enabled: bool | None = None


class RouteCompareIn(BaseModel):
    origin: str = "Current Location"
    destination: str
    latitude: float = 28.6139
    longitude: float = 77.2090
    mode: str = "balanced"
    demo: bool = False


class SafetyScoreIn(BaseModel):
    hour: int
    day_of_week: int
    lighting_factor: float
    crowd_density: float
    historical_incident_density: float
    weather_factor: float
    road_environment_factor: float


class JourneyCreateIn(BaseModel):
    destination: str
    selected_mode: str = "safeloop"
    route: dict


class JourneyCompleteIn(BaseModel):
    status: str = "completed"


class SOSCreateIn(BaseModel):
    latitude: float = 28.6139
    longitude: float = 77.2090
    trigger_type: str = "manual"
    journey_id: int | None = None
    severity: str = "high"


class ContactIn(BaseModel):
    name: str
    relationship: str
    phone: str = ""
    email: EmailStr | None = None
    notification_enabled: bool = True


class FeedbackIn(BaseModel):
    journey_id: int | None = None
    rating: int = Field(ge=1, le=5)
    route_useful: bool
    score_made_sense: bool
    would_use_again: bool
    comments: str = ""


class EmergencyOut(BaseModel):
    id: int
    status: str
    trigger_type: str
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True
