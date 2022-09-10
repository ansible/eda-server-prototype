from .session import create_engine, create_session_factory


class DatabaseProvider:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.session_factory = create_session_factory(self.engine)

    async def close(self) -> None:
        await self.engine.dispose()
