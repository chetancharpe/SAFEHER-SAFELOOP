from datetime import datetime
import json
from .risk import risk_model


BASE_PATH = [[28.6139, 77.2090], [28.6185, 77.2150], [28.6221, 77.2220], [28.6280, 77.2300]]


def route_candidates(destination: str, lat: float, lng: float, demo: bool = False) -> list[dict]:
    hour = datetime.now().hour
    day = datetime.now().weekday()
    if demo or destination.lower().replace(" ", "") in {"collegehome", "college->home", "home"}:
        raw = [
            ("FASTEST ROUTE", "fastest", 2.4, 18, 0.36, 0.42, 0.60, 0.55, 0.52),
            ("SAFELOOP ROUTE", "safeloop", 2.7, 21, 0.88, 0.78, 0.22, 0.16, 0.18),
            ("BALANCED ROUTE", "balanced", 2.6, 20, 0.68, 0.65, 0.38, 0.28, 0.34),
        ]
    else:
        seed = sum(ord(c) for c in destination.lower()) % 13
        raw = [
            ("FASTEST ROUTE", "fastest", 2.1 + seed / 20, 15 + seed % 6, 0.42, 0.50, 0.52, 0.44, 0.48),
            ("SAFELOOP ROUTE", "safeloop", 2.4 + seed / 18, 18 + seed % 7, 0.82, 0.72, 0.24, 0.18, 0.22),
            ("BALANCED ROUTE", "balanced", 2.3 + seed / 19, 17 + seed % 7, 0.65, 0.64, 0.34, 0.30, 0.30),
        ]

    candidates = []
    for index, (label, mode, distance, duration, lighting, crowd, incident, weather, road) in enumerate(raw):
        prediction = risk_model.predict({
            "hour": hour,
            "day_of_week": day,
            "lighting_factor": lighting,
            "crowd_density": crowd,
            "historical_incident_density": incident,
            "weather_factor": weather,
            "road_environment_factor": road,
        })
        if demo:
            demo_scores = {"fastest": 72, "safeloop": 29, "balanced": 44}
            score = demo_scores[mode]
            prediction.update({"risk_score": score, "risk_level": "HIGH" if score == 72 else "LOW" if score == 29 else "MODERATE", "safety_score": 100 - score})
        path = [[lat, lng]] + [[p[0] + index * 0.001, p[1] - index * 0.001] for p in BASE_PATH[1:]]
        candidates.append({
            "label": label,
            "mode": mode,
            "distance_km": round(distance, 1),
            "duration_min": duration,
            "risk_score": prediction["risk_score"],
            "risk_level": prediction["risk_level"],
            "safety_score": prediction["safety_score"],
            "lighting_factor": lighting,
            "crowd_factor": crowd,
            "time_factor": 1 - incident,
            "environment_factor": 1 - road,
            "path": path,
            "path_json": json.dumps(path),
            "data_label": prediction["label"],
        })
    safest = min(candidates, key=lambda item: item["risk_score"])
    fastest = min(candidates, key=lambda item: item["duration_min"])
    for item in candidates:
        item["recommended"] = item["mode"] == safest["mode"]
        item["explanation"] = (
            f"SAFELOOP recommends this route because its estimated environmental risk is lower, "
            f"although it takes {max(0, item['duration_min'] - fastest['duration_min'])} minutes longer."
            if item["recommended"]
            else "This route is shown for comparison using demo environmental data."
        )
    return candidates
