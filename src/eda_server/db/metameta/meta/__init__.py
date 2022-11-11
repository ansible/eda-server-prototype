import sqlalchemy as sa
from typing import Any, Hashable, List, Optional
from .. import dicta, MetaMetaBase


class MetaMeta(MetaMetaBase):
    def __init__(self):
        super().__init__()
        self.engines = self._items
        self.list_engines = self.list_item_keys
        self.child_class = MetaEngine

    def register_engine(self, engine: sa.engine.Engine, *, engine_name: Optional[str] = None):
        _engine = self.child_class(engine, meta=self, engine_name=engine_name)
        self.engines[_engine.name] = _engine


class MetaEngine(MetaMetaBase):
    def __init__(
        self,
        engine: sa.engine.Engine,
        session_factory: Callable,
        *,
        meta: MetaMetaBase,
        engine_name: Optional[str] = None
    ):
        super().__init__()
        self.schemata = self._items
        self.list_schemata = self.list_item_keys
        self.resolve_engine_name(engine_name)
        self.ns_excl_pref_regexs = ["^pg_", "^information_schema"]
        self._meta = meta
        self._engine = engine
        self.session_factory = session_factory
        self.child_class = MetaSchema

    def resolve_engine_name(self, engine_name: str):
        if not engine_name:
            try:
                self.name = engine.raw_connection().connection.get_dsn_parameters()["dbname"]
            except (KeyError, AttributeError) as e:
                raise e.__class__("Cannot detect engine name from connection. Specify engine name in arguments.")
        else:
            self.name = engine_name

    def register_schema(self, schema_name):
        schema = self.child_class(schema_name, self)
        self.schemata[schema_name] = schema

    def get_engine(self):
        return self._engine

    def _build_discover_engine_query(self):
        if (exclusions_params := tuple(getattr(self, "ns_excl_pref_regexs", ()))):
            exclusions = "and schema_name !~ %s " * len(exclusions_params)
        else:
            exclusions = ""

        sql = f"""
select schema_name
  from information_schema.schemata
 where 1 = 1
    {exclusions}
;
"""
        return (sql, exclusions_params)

    def _get_engine_schemata(self):
        query, params = self._build_discover_engine_query()
        schemata = None
        db = self.session_factory()
        try:
            cur = db.execute(query, params)
            schemata = [rec["schema_name"] for rec in cur]
        finally:
            db.rollback()

        return schemata

    def discover_engine(self):
        schemata = self._get_engine_schemata()
        for schema in schemata:
            self.register_schema(schema)
            self.schemata[schema].discover_tables()

    def find_table_schemata(self, table_name) -> List["MetaSchema"]:
        return sorted((s for s in self.schemata.items() if table_name in s.tables), key=lambda sch: sch._name)

    def get_table(self, table_name) -> sa.Table:
        for schema in sorted(self.schemata):
            if table_name in self.schemata[schema]:
                return self.schemata[schema][table_name]


class MetaSchema(MetaMetaBase):
    def __init__(self, schema_name: str, engine: MetaMetaBase):
        super().__init__()
        self.tables = self._items
        self.list_tables = self.list_item_keys
        self._engine = engine
        self.name = schema_name
        self.sa_metadata = sa.MetaData(schema=self.name)

    def _reflect_objects(self):
        self.sa_metadata.reflect(bind=self._engine._engine)

    def get_engine(self):
        return self._engine._engine

    def _reindex_tables(self):
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

    def discover_tables(self):
        self._reflect_objects()
        self._reindex_tables()

    def get_table(self, table_name: str) -> sa.Table:
        return self.tables[table_name]

    def add_table(self, table_name: str, table: sa.Table):
        self.tables[table_name] = table

    def rm_table(self, table_name: str):
        del self.tables[table_name]


__all__ = (
    "dicta",
    "MetaMetaBase",
    "MetaMeta",
    "MetaEngine",
    "MetaSchema"
)
