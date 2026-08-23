from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import EmergencyEvent, Feedback, Journey


def user_insights(db: Session, user_id: int) -> dict:
    journeys = db.query(Journey).filter(Journey.user_id == user_id).all()
    completed = [j for j in journeys if j.status == "completed"]
    avg_score = int(sum(j.safety_score for j in completed) / len(completed)) if completed else 0
    high_risk = len([j for j in journeys if j.risk_score >= 61])
    sos_count = db.query(EmergencyEvent).filter(EmergencyEvent.user_id == user_id).count()
    insight = "Complete a SAFELOOP journey to unlock personalized safety intelligence."
    if completed:
        evening = [j.safety_score for j in completed if j.started_at.hour >= 18]
        daytime = [j.safety_score for j in completed if j.started_at.hour < 18]
        if evening and daytime and sum(evening) / len(evening) < sum(daytime) / len(daytime):
            insight = "Your evening journeys have had a lower average safety score than your daytime journeys."
        else:
            insight = "Your completed journeys show mostly lower estimated environmental risk."
    return {
        "average_safety_score": avg_score,
        "journeys_completed": len(completed),
        "high_risk_segments": high_risk,
        "sos_events": sos_count,
        "insights": [insight],
    }


def analytics(db: Session) -> dict:
    total_feedback = db.query(func.avg(Feedback.rating)).scalar() or 0
    return {
        "total_users": 0,
        "journeys": db.query(Journey).count(),
        "completed_journeys": db.query(Journey).filter(Journey.status == "completed").count(),
        "route_recommendations": db.query(Journey).count(),
        "sos_events": db.query(EmergencyEvent).count(),
        "resolved_sos": db.query(EmergencyEvent).filter(EmergencyEvent.status == "resolved").count(),
        "feedback_rating": round(float(total_feedback), 2),
    }
