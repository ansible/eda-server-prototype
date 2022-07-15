import uvicorn

from .config import settings


def main():
    uvicorn.run(
        "ansible_events_ui.app:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
