from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EmergencyEvent
from ..schemas.api import SOSCreateIn
from ..services.notifications import notify_trusted_contacts
from ..services.responders import rank_responders
from ..utils.security import current_user
from ..websocket.manager import manager


router = APIRouter(prefix="/api", tags=["sos"])


@router.post("/sos")
async def create_sos(payload: SOSCreateIn, user=Depends(current_user), db: Session = Depends(get_db)):
    event = EmergencyEvent(
        user_id=user.id,
        journey_id=payload.journey_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        trigger_type=payload.trigger_type,
        severity=payload.severity,
        status="active",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    notifications = notify_trusted_contacts(db, user.id, event.id)
    responders = rank_responders(db, payload.latitude, payload.longitude, 3)
    await manager.broadcast("sos_created", {"event_id": event.id, "status": event.status, "latitude": event.latitude, "longitude": event.longitude})
    await manager.broadcast("responder_notified", {"event_id": event.id, "responders": responders})
    return {
        "event": {"id": event.id, "status": event.status, "trigger_type": event.trigger_type},
        "location_shared": True,
        "trusted_contacts_notified": len(notifications),
        "nearby_responders": responders,
        "notice": "DEMO NOTIFICATION messages are simulated unless a real provider is configured.",
    }


@router.post("/sos/{event_id}/cancel")
async def cancel_sos(event_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id, EmergencyEvent.user_id == user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="SOS event not found")
    event.status = "cancelled"
    db.commit()
    await manager.broadcast("sos_resolved", {"event_id": event.id, "status": "cancelled"})
    return {"message": "SOS cancelled", "status": event.status}


@router.post("/sos/{event_id}/resolve")
async def resolve_sos(event_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="SOS event not found")
    if user.role == "user" and event.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot resolve this event")
    event.status = "resolved"
    db.commit()
    await manager.broadcast("sos_resolved", {"event_id": event.id, "status": "resolved"})
    return {"message": "SOS resolved", "status": event.status}
