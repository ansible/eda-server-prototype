#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
extract_model_design.py - Extracts model design from the database schema into a YAML file.
"""


import sqlalchemy as sa
from sa_metameta import meta
import yaml
from pprint import pprint


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
# This will probe all schemata in eda_server and for each schema, the tables will be reflected.
mm.eda_server.discover()

# now we can see what tables have been found by using list()
# print(list(mm.eda_server.public))

models = []
data = {"models": models}

for table_name in list(mm.eda_server.public):
    table = mm.eda_server.public[table_name]
    fields = [
        {"name": str(x.name), "pk": x.primary_key, "type": str(x.type), "ref": get_foreign_key_table(x), "ref_field": get_foreign_key_field(x)}
        for x in list(table.columns)
    ]
    #constraints =[
    #    {"name": str(x.name), "table": str(x.table), "type": type(x).__name__, "columns": [{"name": str(y.name)} for y in x.columns]}
    #    for x in list(table.constraints)
    #]
    #pprint(table.foreign_key_constraints)
    #model = {"name": str(table.name), "fields": fields, "constraints": constraints}
    model = {"name": str(table.name), "fields": fields}
    models.append(model)

print(yaml.dump(data))
