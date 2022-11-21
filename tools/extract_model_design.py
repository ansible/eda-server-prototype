#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extracts model design from the database schema into a YAML file."""


import sqlalchemy as sa
import yaml
from sa_metameta import meta


def get_foreign_key_table(field):
    for fk in field.foreign_keys:
        return str(fk.column.table.name)
    return None


def get_foreign_key_field(field):
    for fk in field.foreign_keys:
        return str(fk.column.name)
    return None


engine = sa.create_engine(
    "postgresql://postgres:secret@localhost:5432/eda_server"
)

mm = meta.MetaMeta()
# This will use the database name from the URL as the attribute name
mm.register_engine(engine)
# This will probe all schemata in eda_server and for each schema,
# the tables will be reflected.
mm.eda_server.discover()


models = []
data = {"models": models}

for _, table in mm.eda_server.public.items():
    fields = [
        {
            "name": str(x.name),
            "pk": x.primary_key,
            "type": str(x.type),
            "ref": get_foreign_key_table(x),
            "ref_field": get_foreign_key_field(x),
        }
        for x in list(table.columns)
    ]
    model = {"name": str(table.name), "fields": fields}
    models.append(model)

print(yaml.dump(data))  # noqa: T201
