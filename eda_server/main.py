import uvicorn

from .config import load_settings


def main():
    settings = load_settings()
    uvicorn.run(
        "eda_server.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
