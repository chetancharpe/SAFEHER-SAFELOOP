import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models import Notification, TrustedContact, User, EmergencyEvent

logger = logging.getLogger("safeloop.notifications")


def notify_trusted_contacts(db: Session, user_id: int, emergency_event_id: int) -> list[Notification]:
    settings = get_settings()
    user = db.query(User).filter(User.id == user_id).first()
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == emergency_event_id).first()
    
    user_name = user.name if user else "A user"
    lat = event.latitude if event else 28.6139
    lng = event.longitude if event else 77.2090
    
    # Format a professional emergency message with a map link
    map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=16/{lat}/{lng}"
    alert_msg = f"EMERGENCY ALERT: {user_name} has triggered an SOS. Possible emergency. Coordinates: {lat}, {lng}. View live map: {map_link}"
    
    contacts = db.query(TrustedContact).filter(
        TrustedContact.user_id == user_id,
        TrustedContact.notification_enabled.is_(True),
    ).all()
    
    notifications = []
    
    for contact in contacts:
        status = "demo_sent"
        channel = "demo"
        message = alert_msg
        
        # 1. Attempt Twilio SMS if configured and contact has a phone number
        if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number and contact.phone:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
                auth = (settings.twilio_account_sid, settings.twilio_auth_token)
                data = {
                    "From": settings.twilio_from_number,
                    "To": contact.phone,
                    "Body": alert_msg
                }
                with httpx.Client(timeout=5.0) as client:
                    resp = client.post(url, auth=auth, data=data)
                    if resp.status_code in {200, 201}:
                        status = "sent"
                        channel = "sms"
                        logger.info(f"SMS alert sent to {contact.phone} ({contact.name})")
                    else:
                        status = "failed"
                        channel = "sms"
                        logger.error(f"Twilio API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                status = "failed"
                channel = "sms"
                logger.error(f"Failed to send Twilio SMS to {contact.phone}: {e}")
                
        # 2. Attempt SMTP Email if configured and contact has an email address
        elif settings.smtp_server and settings.smtp_from_email and contact.email:
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.smtp_from_email
                msg['To'] = contact.email
                msg['Subject'] = f"SAFELOOP Emergency Alert: {user_name}"
                
                # HTML structured email for readability
                html_body = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="background-color: #ff5f6d; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                      <h2 style="margin: 0;">SAFELOOP EMERGENCY ALERT</h2>
                    </div>
                    <div style="padding: 20px; border: 1px solid #ddd; border-radius: 0 0 8px 8px; border-top: none;">
                      <p>Dear {contact.name},</p>
                      <p><strong>{user_name}</strong> has triggered an emergency SOS from their SAFELOOP app.</p>
                      <p style="background-color: #fff3f3; padding: 15px; border-left: 5px solid #ff5f6d; border-radius: 4px;">
                        <strong>Status:</strong> Possible Emergency<br/>
                        <strong>Coordinates:</strong> {lat}, {lng}<br/>
                        <strong>Trigger Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                      </p>
                      <p>
                        <a href="{map_link}" style="display: inline-block; padding: 12px 24px; background-color: #ff5f6d; color: white; text-decoration: none; border-radius: 25px; font-weight: bold;">
                          View Live Map Location
                        </a>
                      </p>
                      <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        This notification was automatically sent by the SAFELOOP Personal Safety Platform on behalf of the user.
                      </p>
                    </div>
                  </body>
                </html>
                """
                msg.attach(MIMEText(html_body, 'html'))
                
                with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                    if settings.smtp_username and settings.smtp_password:
                        server.starttls()
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.sendmail(settings.smtp_from_email, contact.email, msg.as_string())
                    
                status = "sent"
                channel = "email"
                logger.info(f"Email alert sent to {contact.email} ({contact.name})")
            except Exception as e:
                status = "failed"
                channel = "email"
                logger.error(f"Failed to send email to {contact.email}: {e}")
        
        # Write record to database
        notification = Notification(
            user_id=user_id,
            emergency_event_id=emergency_event_id,
            recipient=contact.name,
            channel=channel,
            message=message,
            status=status,
        )
        db.add(notification)
        notifications.append(notification)
        
    db.commit()
    return notifications
