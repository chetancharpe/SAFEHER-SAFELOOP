from app.services.risk import risk_model


def predict_environmental_risk(features: dict) -> dict:
    return risk_model.predict(features)
