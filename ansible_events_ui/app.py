from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from ansible_events_ui.api import router as api_router
from ansible_events_ui.config import load_settings
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


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_staticfiles(app: FastAPI) -> None:
    app.mount("/eda", StaticFiles(directory="ui/dist", html=True), name="eda")


def setup_routes(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(api_router)


def setup_database(app: FastAPI) -> None:
    app.state.db_engine = db_engine = engine_from_settings(app.state.settings)
    app.state.db_sessionmaker = create_sessionmaker(db_engine)
    app.add_event_handler("shutdown", db_engine.dispose)


# TODO(cutwater): Use dependency overrides.
# TODO(cutwater): Implement customizable ApplicationBuilder for testing.
def create_app() -> FastAPI:
    """Initialize FastAPI application."""
    settings = load_settings()

    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_staticfiles(app)
    setup_routes(app)

    setup_database(app)

    return app
