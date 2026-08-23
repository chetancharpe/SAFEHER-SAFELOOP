from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Feedback, Journey, SafetyScore
from ..schemas.api import FeedbackIn, JourneyCompleteIn, JourneyCreateIn
from ..utils.security import current_user


router = APIRouter(prefix="/api", tags=["journeys"])


@router.post("/journeys")
def create_journey(payload: JourneyCreateIn, user=Depends(current_user), db: Session = Depends(get_db)):
    route = payload.route
    journey = Journey(
        user_id=user.id,
        destination=payload.destination,
        selected_mode=payload.selected_mode,
        distance_km=route.get("distance_km", 0),
        duration_min=route.get("duration_min", 0),
        safety_score=route.get("safety_score", 0),
        risk_score=route.get("risk_score", 0),
        risk_level=route.get("risk_level", "LOW"),
        status="active",
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)
    return {"id": journey.id, "status": journey.status, "journey": serialize_journey(journey)}


@router.get("/journeys")
def list_journeys(user=Depends(current_user), db: Session = Depends(get_db)):
    journeys = db.query(Journey).filter(Journey.user_id == user.id).order_by(Journey.started_at.desc()).all()
    return [serialize_journey(journey) for journey in journeys]


@router.post("/journeys/{journey_id}/complete")
def complete_journey(journey_id: int, payload: JourneyCompleteIn, user=Depends(current_user), db: Session = Depends(get_db)):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    journey.status = payload.status
    journey.completed_at = datetime.utcnow()
    score = SafetyScore(
        journey_id=journey.id,
        user_id=user.id,
        score=journey.safety_score,
        risk_level=journey.risk_level,
        lighting="Good" if journey.risk_score <= 40 else "Moderate",
        crowd="Moderate",
        time="Moderate",
        environment="Good" if journey.risk_score <= 40 else "Variable",
    )
    db.add(score)
    db.commit()
    db.refresh(journey)
    return {
        "message": "JOURNEY COMPLETE",
        "report": {
            "distance_km": journey.distance_km,
            "duration_min": journey.duration_min,
            "safety_score": journey.safety_score,
            "estimated_risk": journey.risk_level,
            "risk_factors": {
                "Lighting": score.lighting,
                "Crowd": score.crowd,
                "Time": score.time,
                "Environment": score.environment,
            },
        },
    }


@router.post("/feedback")
def create_feedback(payload: FeedbackIn, user=Depends(current_user), db: Session = Depends(get_db)):
    feedback = Feedback(user_id=user.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    return {"message": "Thank you for the feedback.", "feedback_id": feedback.id}


def serialize_journey(journey: Journey) -> dict:
    return {
        "id": journey.id,
        "destination": journey.destination,
        "selected_mode": journey.selected_mode,
        "status": journey.status,
        "distance_km": journey.distance_km,
        "duration_min": journey.duration_min,
        "safety_score": journey.safety_score,
        "risk_score": journey.risk_score,
        "risk_level": journey.risk_level,
        "started_at": journey.started_at.isoformat(),
        "completed_at": journey.completed_at.isoformat() if journey.completed_at else None,
    }
