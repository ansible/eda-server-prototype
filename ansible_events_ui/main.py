import uvicorn


def main():
    uvicorn.run(
        "ansible_events_ui.app:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
