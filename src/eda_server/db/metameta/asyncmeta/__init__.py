from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List, Optional
from ..meta import MetaMeta, MetaEngine, MetaSchema


class AMetaMeta(MetaMeta):
    """
    AMetaMeta is a class for tracking meta engines.

    The meta engines that this class tracks will be a AMetaEngine type.
    The AMetaEngine class is designed to work with SQLAlchemy's AsyncEngine
    engine class.
    """
    @property
    def child_class(self) -> AMetaEngine:
        return AMetaEngine


class AMetaEngine(MetaEngine):
    """
    AMetaEngine is a class for tracking meta schemata.

    The meta schema classes that this class tracks will be a AMetaSchema type.
    The AMetaSchema class is designed to work with SQLAlchemy's AsyncEngine
    engine class.
    """
    @property
    def child_class(self) -> AMetaSchema:
        return AMetaSchema

    async def _get_engine_schemata(self) -> List[str]:
        """
        Build and execute a schema listing query.

        This internal method will build a schema listing query and execute
        the query using asyncio.
        """
        query, params = self._build_discover_engine_query()
        schemata = None
        async with self.engine.connect() as conn:
            cur = await conn.execute(sa.text(query), params)
            schemata = [rec["schema_name"] for rec in cur]

        return schemata

    async def discover(self) -> None:
        """
        Probe a engine for any user schemata.

        Each schema will be registered and tables will be discovered.
        """
        schemata = await self._get_engine_schemata()
        for schema in schemata:
            self.register_schema(schema)
            await self.schemata[schema].discover()


class AMetaSchema(MetaSchema):
    """
    AMetaSchema is a class for tracking tables within a schema.

    This class uses the sqlalchemy.MetaData.reflect method to probe a database
    get the table information and then dynamically build SQLAlchemy table
    objects.
    """
    def _get_reflection(self, conn):
        """
        Internal method to execute the MetaData.reflect()

        This method is necessary to successfully use SQLAlchemy instropection
        code with AsyncEngine.
        """
        self.metadata.reflect(bind=conn)

    async def _reflect_objects(self) -> None:
        """
        Internal method to execute instrospection of an engine.

        This method will establish a connection to the database and
        then use the connection objects run_sync() method so successfully
        execute the MetaData.reflect() method.
        """
        async with self.engine.connect() as conn:
            await conn.run_sync(self._get_reflection)

    async def discover(self) -> None:
        """
        Discover tables within a schema.

        After initial discovery, the tables may have schema prefixes.
        These table names will be re-indexed to ensure that the schema name
        has been remove from the table name key.
        """
        await self._reflect_objects()
        self._reindex_tables()


__all__ = (
    "AMetaMetaBase",
    "AMetaMeta",
    "AMetaEngine",
    "AMetaSchema"
)
