from app.database import SessionLocal, init_db
from app.models import Feedback, Journey, Responder, TrustedContact, User
from app.utils.security import hash_password


def upsert_user(db, name: str, email: str, role: str = "user") -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(name=name, email=email, role=role, hashed_password=hash_password("Password123!"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        demo = upsert_user(db, "Demo Student", "demo@example.com")
        upsert_user(db, "Nisha", "nisha@example.com")
        upsert_user(db, "Ava", "ava@example.com")
        responder_user = upsert_user(db, "Responder One", "responder@example.com", "responder")
        upsert_user(db, "Admin", "admin@example.com", "admin")

        if db.query(TrustedContact).filter(TrustedContact.user_id == demo.id).count() == 0:
            db.add_all([
                TrustedContact(user_id=demo.id, name="Mom", relationship="Parent", phone="+10000000001", email="mom@example.com"),
                TrustedContact(user_id=demo.id, name="Friend", relationship="Friend", phone="+10000000002", email="friend@example.com"),
                TrustedContact(user_id=demo.id, name="Brother", relationship="Sibling", phone="+10000000003", email="brother@example.com", notification_enabled=False),
            ])

        if db.query(Responder).count() < 10:
            responders = [
                ("Campus Gate Security", "campus_security", 28.6165, 77.2120, True, True, 12),
                ("North Hostel Guard", "security_guard", 28.6200, 77.2190, True, True, 8),
                ("Verified Volunteer A", "verified_volunteer", 28.6250, 77.2250, True, True, 5),
                ("Library Security", "campus_security", 28.6180, 77.2100, True, True, 17),
                ("Metro Gate Guard", "security_guard", 28.6300, 77.2340, True, False, 3),
                ("Volunteer B", "verified_volunteer", 28.6100, 77.2040, True, True, 2),
                ("Volunteer C", "verified_volunteer", 28.6350, 77.2380, True, True, 4),
                ("Unverified Helper", "verified_volunteer", 28.6120, 77.2070, False, True, 1),
                ("East Campus Desk", "campus_security", 28.6220, 77.2180, True, True, 9),
                ("Residence Security", "security_guard", 28.6260, 77.2260, True, True, 11),
            ]
            for index, item in enumerate(responders):
                db.add(Responder(
                    user_id=responder_user.id if index == 0 else None,
                    name=item[0],
                    type=item[1],
                    latitude=item[2],
                    longitude=item[3],
                    verified=item[4],
                    available=item[5],
                    response_count=item[6],
                ))

        if db.query(Journey).count() < 20:
            for i in range(20):
                score = 86 if i % 3 else 58
                db.add(Journey(
                    user_id=demo.id,
                    destination="Home" if i % 2 else "Library",
                    selected_mode="safeloop",
                    status="completed",
                    distance_km=2.5 + (i % 5) * 0.2,
                    duration_min=18 + i % 9,
                    safety_score=score,
                    risk_score=100 - score,
                    risk_level="LOW" if score >= 70 else "MODERATE",
                ))

        if db.query(Feedback).count() == 0:
            for rating in [5, 4, 5, 4, 5]:
                db.add(Feedback(user_id=demo.id, rating=rating, route_useful=True, score_made_sense=True, would_use_again=True, comments="Demo feedback"))
        db.commit()
        print("Seeded SAFELOOP demo data. Demo data is synthetic and for hackathon use.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
