from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from ansible_events_ui.api import router as api_router
from ansible_events_ui.config import load_settings
from ansible_events_ui.db.dependency import get_db_session_factory
from ansible_events_ui.db.provider import DatabaseProvider

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
    return RedirectResponse("/eda/")


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


def setup_ui(app: FastAPI) -> None:
    static_path = "ui/dist"
    ui_app = FastAPI()

    @ui_app.exception_handler(404)
    def not_found(request, exc):
        return FileResponse(f"{static_path}/index.html")

    ui_app.mount(
        "/", StaticFiles(directory=static_path, html=True), name="eda"
    )

    app.mount("/eda", app=ui_app)


def setup_routes(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(api_router)


def setup_database(app: FastAPI) -> None:
    settings = app.state.settings
    provider = DatabaseProvider(settings.database_url)
    app.add_event_handler("shutdown", provider.close)
    app.dependency_overrides[
        get_db_session_factory
    ] = lambda: provider.session_factory


# TODO(cutwater): Use dependency overrides.
# TODO(cutwater): Implement customizable ApplicationBuilder for testing.
def create_app() -> FastAPI:
    """Initialize FastAPI application."""
    settings = load_settings()

    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_ui(app)
    setup_routes(app)

    setup_database(app)

    return app
