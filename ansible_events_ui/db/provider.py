from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseProvider:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def close(self) -> None:
        await self.engine.dispose()
