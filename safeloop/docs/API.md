# API

Base URL: `http://127.0.0.1:8000`

Auth:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/profile`
- `PUT /api/profile`

Routes and scoring:

- `POST /api/routes/compare`
- `POST /api/safety-score`

Journeys:

- `POST /api/journeys`
- `GET /api/journeys`
- `POST /api/journeys/{id}/complete`

SOS:

- `POST /api/sos`
- `POST /api/sos/{id}/cancel`
- `POST /api/sos/{id}/resolve`

Responders:

- `GET /api/responders/nearby`
- `GET /api/responders/emergencies`
- `POST /api/responders/{event_id}/accept`

Insights and analytics:

- `GET /api/insights`
- `POST /api/feedback`
- `GET /api/analytics`
- `GET /api/health`

Privacy:

- `POST /api/privacy/delete-data`
- `DELETE /api/privacy/delete-account`
