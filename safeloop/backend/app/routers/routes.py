from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import RouteOption
from ..schemas.api import RouteCompareIn, SafetyScoreIn
from ..services.risk import risk_model
from ..services.routes import route_candidates
from ..utils.security import current_user


router = APIRouter(prefix="/api", tags=["routes"])


@router.post("/routes/compare")
def compare_routes(payload: RouteCompareIn, user=Depends(current_user), db: Session = Depends(get_db)):
    routes = route_candidates(payload.destination, payload.latitude, payload.longitude, payload.demo)
    for route in routes:
        db.add(RouteOption(
            label=route["label"],
            mode=route["mode"],
            distance_km=route["distance_km"],
            duration_min=route["duration_min"],
            risk_score=route["risk_score"],
            risk_level=route["risk_level"],
            lighting_factor=route["lighting_factor"],
            crowd_factor=route["crowd_factor"],
            time_factor=route["time_factor"],
            environment_factor=route["environment_factor"],
            path_json=route["path_json"],
            explanation=route["explanation"],
        ))
    db.commit()
    return {
        "origin": payload.origin,
        "destination": payload.destination,
        "data_notice": "Demo environmental data. Scores estimate environmental risk and do not guarantee safety.",
        "routes": routes,
    }


@router.post("/safety-score")
def safety_score(payload: SafetyScoreIn, user=Depends(current_user)):
    return risk_model.predict(payload.model_dump())
