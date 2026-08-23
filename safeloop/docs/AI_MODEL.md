# AI Model

SAFELOOP estimates environmental route risk. It does not predict crime and does not guarantee safety.

Model:

- `RandomForestRegressor`
- Features: `hour`, `day_of_week`, `lighting_factor`, `crowd_density`, `historical_incident_density`, `weather_factor`, `road_environment_factor`
- Target: `risk_score` from 0 to 100

Risk interpretation:

- 0-30: LOW
- 31-60: MODERATE
- 61-80: HIGH
- 81-100: CRITICAL

Training:

```bash
python ml/training/train_model.py
```

If no real dataset is present, the script generates `ml/data/synthetic_environmental_risk.csv`. This is clearly labeled synthetic data and must not be presented as real crime statistics.
