from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic_environmental_risk.csv"
MODEL_PATH = ROOT / "models" / "risk_model.joblib"
FEATURES = [
    "hour",
    "day_of_week",
    "lighting_factor",
    "crowd_density",
    "historical_incident_density",
    "weather_factor",
    "road_environment_factor",
]


def generate_synthetic_dataset() -> pd.DataFrame:
    rows = []
    for hour in range(24):
        for day in range(7):
            for lighting in [0.25, 0.5, 0.75, 0.9]:
                for crowd in [0.2, 0.45, 0.7, 0.9]:
                    incident = ((hour * 3 + day * 5) % 10) / 10
                    weather = ((hour + day) % 4) / 10
                    road = ((hour * 2 + day) % 5) / 10
                    night = 30 if hour >= 21 or hour <= 5 else 8 if hour >= 18 else 0
                    risk = np.clip(night + (1 - lighting) * 24 + (1 - crowd) * 18 + incident * 20 + weather * 8 + road * 18, 0, 100)
                    rows.append([hour, day, lighting, crowd, incident, weather, road, risk])
    return pd.DataFrame(rows, columns=FEATURES + ["risk_score"])


def main() -> None:
    ROOT.joinpath("data").mkdir(parents=True, exist_ok=True)
    ROOT.joinpath("models").mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists():
        data = pd.read_csv(DATA_PATH)
    else:
        data = generate_synthetic_dataset()
        data.to_csv(DATA_PATH, index=False)
        print(f"Generated clearly labeled synthetic dataset: {DATA_PATH}")
    x_train, x_test, y_train, y_test = train_test_split(data[FEATURES], data["risk_score"], test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=120, random_state=42, min_samples_leaf=2)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    print({"mae": round(mean_absolute_error(y_test, predictions), 3), "r2": round(r2_score(y_test, predictions), 3)})
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
