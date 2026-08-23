# Architecture

SAFELOOP is split into `frontend`, `backend`, `ml`, and `docs`.

The frontend is a React/Vite mobile-first app. It provides the landing page, student journey flow, route comparison UI, Safe Journey page, countdown SOS overlay, emergency screen, responder dashboard, privacy controls, insights dashboard, and `/demo`.

The backend is a FastAPI service with JWT authentication, SQLAlchemy models, SQLite persistence, route comparison, risk scoring, journey lifecycle, SOS lifecycle, trusted-contact demo notifications, smart responder prioritization, analytics, and WebSocket broadcasts.

The ML layer trains a `RandomForestRegressor` for estimated environmental risk. In normal runtime, the backend loads `ml/models/risk_model.joblib` when present. If absent, it uses deterministic demo environmental fallback logic and labels the data as demo environmental data.

WebSocket events:

- `sos_created`
- `responder_notified`
- `sos_accepted`
- `location_updated`
- `sos_resolved`
