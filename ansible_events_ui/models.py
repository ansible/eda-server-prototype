
import sqlalchemy


metadata = sqlalchemy.MetaData()


rulesets = sqlalchemy.Table(
    "ruleset",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rules", sqlalchemy.String),
)



inventories = sqlalchemy.Table(
    "inventory",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("inventory", sqlalchemy.String),
)



extravars = sqlalchemy.Table(
    "extravar",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("extravars", sqlalchemy.String),
)




activations = sqlalchemy.Table(
    "activation",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulesetbook_id", sqlalchemy.Integer),
    sqlalchemy.Column("inventory_id", sqlalchemy.String),
    sqlalchemy.Column("extravars_id", sqlalchemy.String),
)


