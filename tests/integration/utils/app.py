from fastapi import FastAPI

from eda_server.app import setup_cors, setup_routes
from eda_server.db.dependency import get_db_session_factory


def create_test_app(settings, session):
    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_routes(app)

    app.dependency_overrides[get_db_session_factory] = lambda: lambda: session

    return app
