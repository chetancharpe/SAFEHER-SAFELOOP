from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import init_db
from .routers import auth, insights, journeys, responders, routes, sos
from .utils.security import RateLimiter
from .websocket.manager import manager


settings = get_settings()
app = FastAPI(
    title="SAFELOOP API",
    description="AI-powered personal safety MVP using estimated environmental risk.",
    version="0.1.0",
    dependencies=[Depends(RateLimiter())],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(routes.router)
app.include_router(journeys.router)
app.include_router(sos.router)
app.include_router(responders.router)
app.include_router(insights.router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SAFELOOP", "demo_mode": settings.demo_mode}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("event") == "location_updated":
                await manager.broadcast("location_updated", data.get("payload", {}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
