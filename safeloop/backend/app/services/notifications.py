from sqlalchemy.orm import Session
from ..models import Notification, TrustedContact


def notify_trusted_contacts(db: Session, user_id: int, emergency_event_id: int) -> list[Notification]:
    contacts = db.query(TrustedContact).filter(
        TrustedContact.user_id == user_id,
        TrustedContact.notification_enabled.is_(True),
    ).all()
    notifications = []
    for contact in contacts:
        notification = Notification(
            user_id=user_id,
            emergency_event_id=emergency_event_id,
            recipient=contact.name,
            channel="demo",
            message="DEMO NOTIFICATION: possible emergency. Location has been shared for hackathon demo.",
            status="demo_sent",
        )
        db.add(notification)
        notifications.append(notification)
    db.commit()
    return notifications
