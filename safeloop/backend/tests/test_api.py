from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from seed import main as seed_main


client = TestClient(app)


def token(email="demo@example.com", password="Password123!"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(email="demo@example.com"):
    return {"Authorization": f"Bearer {token(email=email)}"}


def setup_module():
    init_db()
    seed_main()


def test_register_and_login():
    response = client.post("/api/auth/register", json={"name": "Test User", "email": "testuser@example.com", "password": "Password123!"})
    assert response.status_code in {200, 409}
    login = client.post("/api/auth/login", json={"email": "demo@example.com", "password": "Password123!"})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_route_calculation_and_risk_scoring():
    response = client.post("/api/routes/compare", headers=auth_headers(), json={"destination": "Home", "demo": True})
    assert response.status_code == 200
    routes = response.json()["routes"]
    assert len(routes) >= 2
    assert routes[0]["risk_score"] == 72
    assert any(route["recommended"] for route in routes)


def test_journey_creation_and_completion_and_feedback():
    routes = client.post("/api/routes/compare", headers=auth_headers(), json={"destination": "Home", "demo": True}).json()["routes"]
    selected = next(route for route in routes if route["mode"] == "safeloop")
    created = client.post("/api/journeys", headers=auth_headers(), json={"destination": "Home", "selected_mode": "safeloop", "route": selected})
    assert created.status_code == 200
    journey_id = created.json()["id"]
    complete = client.post(f"/api/journeys/{journey_id}/complete", headers=auth_headers(), json={"status": "completed"})
    assert complete.status_code == 200
    feedback = client.post("/api/feedback", headers=auth_headers(), json={"journey_id": journey_id, "rating": 5, "route_useful": True, "score_made_sense": True, "would_use_again": True})
    assert feedback.status_code == 200


def test_sos_create_cancel_accept_resolve_and_responder_ranking():
    created = client.post("/api/sos", headers=auth_headers(), json={"trigger_type": "manual", "latitude": 28.6139, "longitude": 77.2090})
    assert created.status_code == 200
    body = created.json()
    assert body["trusted_contacts_notified"] >= 2
    assert len(body["nearby_responders"]) == 3
    event_id = body["event"]["id"]
    accept = client.post(f"/api/responders/{event_id}/accept", headers=auth_headers("responder@example.com"))
    assert accept.status_code == 200
    resolve = client.post(f"/api/sos/{event_id}/resolve", headers=auth_headers("responder@example.com"))
    assert resolve.status_code == 200
    cancelled = client.post("/api/sos", headers=auth_headers(), json={"trigger_type": "manual"})
    cancel_id = cancelled.json()["event"]["id"]
    cancel = client.post(f"/api/sos/{cancel_id}/cancel", headers=auth_headers())
    assert cancel.status_code == 200


def test_insights():
    response = client.get("/api/insights", headers=auth_headers())
    assert response.status_code == 200
    assert "average_safety_score" in response.json()
