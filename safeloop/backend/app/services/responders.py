from math import asin, cos, radians, sin, sqrt
from sqlalchemy.orm import Session
from ..models import Responder


def distance_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    radius = 6371
    dlat = radians(b_lat - a_lat)
    dlng = radians(b_lng - a_lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
    return 2 * radius * asin(sqrt(h))


def rank_responders(db: Session, latitude: float, longitude: float, limit: int = 3) -> list[dict]:
    responders = db.query(Responder).filter(Responder.verified.is_(True), Responder.available.is_(True)).all()
    ranked = []
    for responder in responders:
        dist = distance_km(latitude, longitude, responder.latitude, responder.longitude)
        distance_score = max(0, 100 - dist * 30)
        availability_score = 100
        response_score = min(100, responder.response_count * 10)
        score = distance_score * 0.5 + availability_score * 0.3 + response_score * 0.2
        ranked.append({
            "id": responder.id,
            "name": responder.name,
            "type": responder.type,
            "latitude": responder.latitude,
            "longitude": responder.longitude,
            "verified": responder.verified,
            "available": responder.available,
            "response_count": responder.response_count,
            "distance_m": int(dist * 1000),
            "eta_min": max(2, int(dist * 4) + 2),
            "responder_score": round(score, 2),
        })
    return sorted(ranked, key=lambda item: item["responder_score"], reverse=True)[:limit]
