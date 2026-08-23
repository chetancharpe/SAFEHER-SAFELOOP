from pathlib import Path
import joblib
import numpy as np


FEATURES = [
    "hour",
    "day_of_week",
    "lighting_factor",
    "crowd_density",
    "historical_incident_density",
    "weather_factor",
    "road_environment_factor",
]


def risk_level(score: int) -> str:
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MODERATE"
    if score <= 80:
        return "HIGH"
    return "CRITICAL"


def safety_score(risk_score_value: int) -> int:
    return max(0, min(100, 100 - risk_score_value))


class RiskModel:
    def __init__(self) -> None:
        self.model = None
        model_path = Path(__file__).resolve().parents[3] / "ml" / "models" / "risk_model.joblib"
        if model_path.exists():
            self.model = joblib.load(model_path)

    def predict(self, payload: dict) -> dict:
        values = [float(payload[key]) for key in FEATURES]
        if self.model:
            score = int(np.clip(self.model.predict([values])[0], 0, 100))
            source = "ml_model"
        else:
            hour = values[0]
            night = 30 if hour >= 21 or hour <= 5 else 8 if hour >= 18 else 0
            score = int(np.clip(
                night
                + (1 - values[2]) * 24
                + (1 - values[3]) * 18
                + values[4] * 20
                + values[5] * 8
                + values[6] * 18,
                0,
                100,
            ))
            source = "deterministic_demo_environmental_fallback"
        return {
            "risk_score": score,
            "risk_level": risk_level(score),
            "safety_score": safety_score(score),
            "model_source": source,
            "label": "Demo environmental data" if source != "ml_model" else "ML environmental risk model",
        }


risk_model = RiskModel()
