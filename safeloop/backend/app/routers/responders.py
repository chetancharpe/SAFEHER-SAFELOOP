from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EmergencyEvent, Responder
from ..services.responders import rank_responders, distance_km
from ..utils.security import current_user, require_role
from ..websocket.manager import manager


router = APIRouter(prefix="/api", tags=["responders"])


@router.get("/responders/nearby")
def nearby(latitude: float = 28.6139, longitude: float = 77.2090, user=Depends(current_user), db: Session = Depends(get_db)):
    return {"responders": rank_responders(db, latitude, longitude, 5), "label": "Smart responder prioritization"}


@router.get("/responders/emergencies")
def active_emergencies(user=Depends(require_role("responder", "admin")), db: Session = Depends(get_db)):
    events = db.query(EmergencyEvent).filter(EmergencyEvent.status.in_(["active", "accepted"])).order_by(EmergencyEvent.created_at.desc()).all()
    responder = db.query(Responder).filter(Responder.user_id == user.id).first()
    resp_lat = responder.latitude if responder else 28.6139
    resp_lng = responder.longitude if responder else 77.2090
    
    results = []
    for event in events:
        dist = distance_km(resp_lat, resp_lng, event.latitude, event.longitude)
        dist_m = int(dist * 1000)
        eta = max(2, int(dist * 4) + 2)
        results.append({
            "id": event.id,
            "user": "Anonymous Student",
            "latitude": event.latitude,
            "longitude": event.longitude,
            "status": event.status,
            "distance_m": dist_m,
            "eta_min": eta,
        })
    return results


@router.post("/responders/{event_id}/accept")
async def accept(event_id: int, user=Depends(require_role("responder", "admin")), db: Session = Depends(get_db)):
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="SOS event not found")
    responder = db.query(Responder).filter(Responder.user_id == user.id).first() or db.query(Responder).filter(Responder.verified.is_(True)).first()
    if not responder:
        raise HTTPException(status_code=404, detail="No verified responder profile found")
    event.status = "accepted"
    event.responder_id = responder.id
    responder.response_count += 1
    db.commit()
    
    dist = distance_km(responder.latitude, responder.longitude, event.latitude, event.longitude)
    dist_m = int(dist * 1000)
    eta = max(2, int(dist * 4) + 2)
    
    payload = {"event_id": event.id, "status": event.status, "responder": responder.name, "distance_m": dist_m, "eta_min": eta}
    await manager.broadcast("sos_accepted", payload)
    return payload
