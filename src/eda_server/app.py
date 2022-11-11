import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from eda_server.api import router as api_router
from eda_server.config import Settings, load_settings
from eda_server.db.dependency import get_db_session_factory
from eda_server.db.metameta.asyncmeta import AMetaMeta
from eda_server.db.provider import DatabaseProvider

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:9000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
]

root_router = APIRouter()


_settings = load_settings()
_provider = DatabaseProvider(_settings.database_url)
_eda_meta = AMetaMeta()
_eda_meta.register_engine(
    _provider.engine,
    _provider.session_factory,
    engine_name=_settings.db_name,
)


def get_settings() -> Settings:
    return _settings


def get_provider() -> DatabaseProvider:
    return _provider


def get_metameta() -> AMetaMeta:
    return _eda_meta


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


def setup_routes(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(api_router)


def setup_database_handlers(app: FastAPI) -> None:
    settings = app.state.settings
    provider = get_provider()
    app.add_event_handler("shutdown", provider.close)
    app.dependency_overrides[
        get_db_session_factory
    ] = lambda: provider.session_factory


def configure_logging(app):
    settings = app.state.settings
    log_level = settings.log_level.upper()
    # The nested loggers will inherit parent logger log level.
    logging.getLogger("eda_server").setLevel(log_level)


# TODO(cutwater): Use dependency overrides.
# TODO(cutwater): Implement customizable ApplicationBuilder for testing.
def create_app() -> FastAPI:
    """Initialize FastAPI application."""
    app = FastAPI(
        title="Ansible Events API",
        description="API for Event Driven Automation",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.state.settings = get_settings()

    configure_logging(app)
    setup_cors(app)
    setup_routes(app)

    setup_database_handlers(app)

    return app
