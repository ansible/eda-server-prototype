import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine
from .. import dicta
from ..meta import MetaMeta, MetaEngine, MetaSchema
from typing import Any, Callable, Hashable, List, Optional


class AMetaMeta(MetaMeta):
    def __init__(self):
        super().__init__()
        self.engines = self._items
        self.list_engines = self.list_item_keys
        self.child_class = AMetaEngine

    def register_engine(
        self,
        engine: AsyncEngine,
        *,
        engine_name: Optional[str] = None
    ):
        _engine = self.child_class(engine, meta=self, engine_name=engine_name)
        self.engines[_engine.name] = _engine


class AMetaEngine(AMetaMetaBase):
    def __init__(
        self,
        engine: AsyncEngine,
        *,
        meta: MetaMetaBase,
        engine_name: Optional[str] = None
    ):
        super().__init__()
        self.schemata = self._items
        self.list_schemata = self.list_item_keys
        self.resolve_engine_name(engine_name)
        self.ns_excl_pref_regexs = {"expr_1": "^pg_", "expr_2": "^information_schema"}
        self._meta = meta
        self._engine = engine
        self.child_class = AMetaSchema

    @property
    def metameta(self):
        return self._meta

    @propert
    def engine(self):
        return self._engine

    def resolve_engine_name(self, engine_name: str):
        if not engine_name:
            try:
                self.name = engine.raw_connection().connection.get_dsn_parameters()["dbname"]
            except (KeyError, AttributeError) as e:
                raise e.__class__(
                    "Cannot detect engine name from connection. Specify engine name in arguments."
                )
        else:
            self.name = engine_name

    def register_schema(self, schema_name):
        schema = self.child_class(schema_name, self)
        self.schemata[schema_name] = schema

    def _build_discover_engine_query(self):
        if (exclusions_params := getattr(self, "ns_excl_pref_regexs", {})):
            exclusions = (
                " and ".join((f"schema_name !~ :{k}" for k in exclusions_params))
            )
        else:
            exclusions = ""

        sql = f"""
select schema_name
  from information_schema.schemata
 where {exclusions}
;
"""
        return (sql, exclusions_params)

    async def _get_engine_schemata(self):
        query, params = self._build_discover_engine_query()
        schemata = None
        async with self.engine.connect() as conn:
            cur = await conn.execute(query, params)
            schemata = [rec["schema_name"] for rec in cur]

        return schemata

    async def discover_engine(self):
        schemata = await self._get_engine_schemata()
        for schema in schemata:
            self.register_schema(schema)
            await self.schemata[schema].discover_tables()

    def find_table_schemata(self, table_name) -> List["MetaSchema"]:
        return sorted((s for s in self.schemata.items() if table_name in s.tables), key=lambda sch: sch._name)

    def get_table(self, table_name) -> sa.Table:
        for schema in sorted(self.schemata):
            if table_name in self.schemata[schema]:
                return self.schemata[schema][table_name]


class AMetaSchema(AMetaMetaBase):
    def __init__(self, schema_name: str, engine: MetaMetaBase):
        super().__init__()
        self.tables = self._items
        self.list_tables = self.list_item_keys
        self._engine = engine
        self.name = schema_name
        self.sa_metadata = sa.MetaData(schema=self.name)

    @property
    def metaengine(self):
        return self._engine

    @property
    def engine(self):
        return self.metaengine.engine

    def _get_reflection(self, conn):
        self.sa_metadata.reflect(bind=conn)

    async def _reflect_objects(self) -> None:
        async with self.engine.connect() as conn:
            await conn.run_sync(self._get_reflection)

    def _reindex_tables(self) -> None:
        _metadata = self.sa_metadata
        _tables = self.tables
        prefix = f"{self.name}."
        lprefix = len(prefix)
        for tab in _metadata.tables:
            if tab.startswith(prefix):
                mstab = tab[lprefix:]
            else:
                mstab = tab
            _tables[mstab] = _metadata.tables[tab]

    async def discover_tables(self) -> None:
        await self._reflect_objects()
        self._reindex_tables()

    def get_table(self, table_name: str) -> sa.Table:
        return self.tables[table_name]

    def add_table(self, table_name: str, table: sa.Table) -> None:
        self.tables[table_name] = table

    def rm_table(self, table_name: str) -> None:
        del self.tables[table_name]


__all__ = (
    "AMetaMetaBase",
    "AMetaMeta",
    "AMetaEngine",
    "AMetaSchema"
)
