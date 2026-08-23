# SAFEHER (SAFELOOP)

Tagline: **Predict. Protect. Respond.**

SAFELOOP is a hackathon MVP for college students and young adults travelling alone. It estimates environmental route risk, supports Safe Journey mode with browser-supported voice SOS, coordinates demo emergency notifications, prioritizes verified responders, and generates personal safety intelligence from completed journeys.

SAFELOOP uses the required product language: **estimated environmental risk**, **possible emergency**, **lower-risk route**, and **verified responder**. It does not claim crime prediction or guaranteed safety.

## Technologies

- Frontend: React, TypeScript, Vite, Tailwind CSS, Leaflet, OpenStreetMap, WebSocket.
- Backend: Python, FastAPI, SQLAlchemy, SQLite, JWT, passlib password hashing.
- AI: scikit-learn, pandas, numpy, RandomForestRegressor.
- Deployment targets: Vercel for frontend, Render for backend.

## Environment Variables

Copy `.env.example` to `.env` at project root and `frontend/.env.example` to `frontend/.env`.

Backend:

```bash
SAFELOOP_ENV=development
DATABASE_URL=sqlite:///./safeloop.db
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEMO_MODE=true
REAL_NOTIFICATION_PROVIDER=
```

Frontend:

```bash
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws
```

## Local Setup

```bash
cd safeloop/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd safeloop/frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Database Setup

SQLite tables initialize on backend startup. Seed demo data with:

```bash
cd safeloop/backend
python seed.py
```

The database layer uses SQLAlchemy and can move to PostgreSQL by changing `DATABASE_URL`.

## ML Training

```bash
cd safeloop
python ml/training/train_model.py
```

If no real data exists, the script generates a clearly labeled synthetic environmental dataset and saves `ml/models/risk_model.joblib`.

## Tests

```bash
cd safeloop/backend
pytest
```

```bash
cd safeloop/frontend
npm test
```

## Demo Credentials

- Student: `demo@example.com` / `Password123!`
- Responder: `responder@example.com` / `Password123!`
- Admin: `admin@example.com` / `Password123!`

Run `python backend/seed.py` first.

## 3-Minute Judge Demo Script

1. Open `/demo`.
2. Click **Login as demo user**.
3. Click **Compare routes** for College → Home.
4. Show FASTEST: 18 min, Risk 72; SAFELOOP: 21 min, Risk 29.
5. Select SAFELOOP route and click **Start Safe Journey**.
6. Click **DEMO VOICE TRIGGER**.
7. Let the 5-second countdown reach zero.
8. Show SOS active: location shared, 2 trusted contacts notified, 3 responders found.
9. Click **Open responder dashboard and accept**.
10. Show responder en route, ETA 3 min.
11. Click **Resolve SOS**.
12. Show Journey Safety Report and then insights dashboard.

## Deployment

Backend on Render:

- Build command: `pip install -r backend/requirements.txt`
- Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `DATABASE_URL`, `JWT_SECRET`, and CORS origins.

Frontend on Vercel:

- Root: `frontend`
- Build: `npm run build`
- Output: `dist`
- Set `VITE_API_URL` and `VITE_WS_URL`.

## Known Limitations

- Route geometry uses deterministic demo candidate paths over OpenStreetMap tiles.
- Browser speech recognition depends on platform support and page activity.
- Notifications are simulated as **DEMO NOTIFICATION** unless a real provider is configured.
- Risk scoring estimates environmental risk; it is not crime prediction and does not guarantee safety.

## Future Roadmap

- Real routing provider integration.
- Real notification provider integration.
- PostgreSQL migrations with Alembic.
- Expanded data governance and export tools.
- More robust responder onboarding and verification workflow.
