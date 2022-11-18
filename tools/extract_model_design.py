#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
extract_model_design.py - Extracts model design from the database schema into a YAML file.
"""


import sqlalchemy as sa
from sa_metameta import meta
import yaml

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
        {"name": str(x.name), "pk": x.primary_key, "type": str(x.type)}
        for x in list(table.columns)
    ]
    model = {"name": str(table.name), "fields": fields}
    models.append(model)

print(yaml.dump(data))
