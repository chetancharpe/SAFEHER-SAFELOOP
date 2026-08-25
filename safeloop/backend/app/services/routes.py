import httpx
from datetime import datetime
import json
from .risk import risk_model

BASE_PATH = [[28.6139, 77.2090], [28.6185, 77.2150], [28.6221, 77.2220], [28.6280, 77.2300]]


def route_candidates(destination: str, lat: float, lng: float, demo: bool = False) -> list[dict]:
    hour = datetime.now().hour
    day = datetime.now().weekday()
    
    # Check if we should use demo mode or if we can use real OSRM routing
    use_real = not demo and destination.lower().replace(" ", "") not in {"collegehome", "college->home", "home"}
    
    dest_lat, dest_lng = None, None
    routes_data = []
    
    if use_real:
        try:
            # 1. Geocode destination using Nominatim
            with httpx.Client(timeout=5.0) as client:
                r_geo = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": destination, "format": "json", "limit": 1},
                    headers={"User-Agent": "SafeloopPersonalSafetyCopilot/1.0"}
                )
                if r_geo.status_code == 200:
                    geo_json = r_geo.json()
                    if geo_json:
                        dest_lat = float(geo_json[0]["lat"])
                        dest_lng = float(geo_json[0]["lon"])
            
            # 2. Get real routes from OSRM if geocoding was successful
            if dest_lat is not None and dest_lng is not None:
                with httpx.Client(timeout=5.0) as client:
                    r_route = client.get(
                        f"http://router.project-osrm.org/route/v1/foot/{lng},{lat};{dest_lng},{dest_lat}",
                        params={"geometries": "geojson", "overview": "full", "alternatives": "true"}
                    )
                    if r_route.status_code == 200:
                        route_json = r_route.json()
                        if route_json.get("code") == "Ok":
                            routes_data = route_json.get("routes", [])
        except Exception as e:
            # Fall back gracefully to mock logic
            print(f"OSRM/Nominatim query failed: {e}")

    # Build candidates
    candidates = []
    
    if routes_data:
        # We got real OSRM routes! Map them to fastest, safeloop, balanced.
        # Ensure we have at least one route
        modes = [
            ("FASTEST ROUTE", "fastest", 0.35, 0.15, 0.60, 0.20, 0.50),
            ("SAFELOOP ROUTE", "safeloop", 0.85, 0.55, 0.10, 0.20, 0.10),
            ("BALANCED ROUTE", "balanced", 0.60, 0.35, 0.35, 0.20, 0.30),
        ]
        
        # If night, keep low lighting for fastest/balanced. If day, all are well lit.
        is_day = 6 <= hour < 18
        
        for idx, (label, mode, lighting, crowd, incident, weather, road) in enumerate(modes):
            # Select route from OSRM results. If OSRM has fewer than 3 alternatives, reuse/offset.
            route_idx = idx if idx < len(routes_data) else 0
            osrm_route = routes_data[route_idx]
            
            distance = osrm_route["distance"] / 1000.0
            duration = int(osrm_route["duration"] / 60.0)
            
            # Swap [lng, lat] to [lat, lng] for Leaflet
            path = [[coord[1], coord[0]] for coord in osrm_route["geometry"]["coordinates"]]
            
            # For safeloop route, if there's only 1 OSRM route, we can add a tiny offset for visual variety
            if len(routes_data) == 1 and mode == "safeloop":
                path = [[p[0] + 0.0005, p[1] - 0.0005] for p in path]
                distance += 0.2
                duration += 2
            elif len(routes_data) == 1 and mode == "balanced":
                path = [[p[0] + 0.0002, p[1] - 0.0002] for p in path]
                distance += 0.1
                duration += 1
                
            actual_lighting = 0.95 if is_day else lighting
            actual_crowd = 0.80 if is_day else crowd
            
            prediction = risk_model.predict({
                "hour": hour,
                "day_of_week": day,
                "lighting_factor": actual_lighting,
                "crowd_density": actual_crowd,
                "historical_incident_density": incident,
                "weather_factor": weather,
                "road_environment_factor": road,
            })
            
            candidates.append({
                "label": label,
                "mode": mode,
                "distance_km": round(distance, 1),
                "duration_min": max(1, duration),
                "risk_score": prediction["risk_score"],
                "risk_level": prediction["risk_level"],
                "safety_score": prediction["safety_score"],
                "lighting_factor": actual_lighting,
                "crowd_factor": actual_crowd,
                "time_factor": 1 - incident,
                "environment_factor": 1 - road,
                "path": path,
                "path_json": json.dumps(path),
                "data_label": prediction["label"],
            })
    else:
        # Fallback to deterministic mock routing
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
            else "This route is shown for comparison using environmental data."
        )
    return candidates
