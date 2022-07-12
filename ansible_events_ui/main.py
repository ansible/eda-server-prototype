import uvicorn
from .conf import env


def main():
    uvicorn.run(
        "ansible_events_ui.app:app",
        host=env.str("HTTP_ADDR", default="0.0.0.0"),
        port=env.int("HTTP_PORT", default=8080),
        log_level=env.str("LOG_LEVEL", default="info"),
    )
