from typing import Optional

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from ansible_events_ui.app import router as api_router
from ansible_events_ui.config import Settings, load_settings
from ansible_events_ui.db.session import (
    create_sessionmaker,
    engine_from_settings,
)

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:9000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
]

root_router = APIRouter()


@root_router.get("/")
async def root():
    return RedirectResponse("/eda")


@root_router.get("/ping")
def ping():
    return {"ping": "pong!"}


# TODO(cutwater): Use dependency overrides
def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Initialize FastAPI application."""
    if settings is None:
        settings = load_settings()

    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup static files
    app.mount("/eda", StaticFiles(directory="ui/dist", html=True), name="eda")

    # Setup routes
    app.include_router(root_router)
    app.include_router(api_router)

    # Setup database
    app.state.db_engine = db_engine = engine_from_settings(settings)
    app.state.db_sessionmaker = create_sessionmaker(db_engine)
    app.add_event_handler("shutdown", db_engine.dispose)

    return app
