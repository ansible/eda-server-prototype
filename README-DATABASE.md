# Database guideline

## General rules

_**Note (Ben)**: These are lessons that I have learned over a decade of writing Django and other
Python web applications dealing with large amounts of data. They might be
unusual and controversial, so that's why I am wrote them down here. They are
not rules that we must follow in this project. They are a guide for if and
when we need to scale to large amounts of data or have fast database
operations._

1. Think in sets and do bulk operations. A single entry is a set of one. The
   cost of a single insert or update is similar to the cost of a bulk insert or
   update since most of the cost of database writes are updating indicies.

2. Know what SQL statement that you want to send to the database first. Use
   tools to generate that SQL second. Think about the number and the complexity
   of queries you're writing. Avoid making queries in for loops. Instead combine
   those queries into one or two queries and process the data in a batch.

3. Create a diagram of the schema in Lucid charts, Miro, or Omnigraffle
   something similar. Database schemas that look organized in a diagram are
   easier to understand when writing queries for them.

4. Get the data into the database as fast as possible without processing it.
   Don't leave the user waiting for processing before responding that you
   recevied the data. Receive and write the data quickly and then process
   it later. Make separate tables for incoming data and processed data.
   Don't add indicies to incoming data tables. Provide and API or event
   that lets them know that the data has been processed.

5. Process the data in the database. The database manipulates data many times
   faster and scales better than Python applications. Create and temporary
   tables if needed and drop them when you are done with the operations.
   That said, getting SQL to do the manipulation that you want can be quite
   tricky. Exporting batches of data to tools like Pandas can be useful
   and scale horiztonally in background tasks.

6. Create reporting tables or databases. If you need to generate reports,
   create another set of paritioned tables for those reports and ONLY do read,
   bulk inserts, and drop table partition operations on them. Don't report out of
   the relational tables since it will be way too slow.

7. Write correct queries first and optimize them second if needed. Some queries
   will be slow due to the structure of the relational data. This can be fixed
   by reorganizing the data into reporting tables. Optimizing can take much longer
   than writing the slow correct query and you'll need the slow query anyway to know
   that your optimized query is correct. Besides it is fun to get 10x and 100x speed-ups.

## Writing migrations

### Always check your migrations manually

Some migration tools like (Django ORM and Alembic) provide migration generation capabilities.
It can be handy when creating initial migration for a large number of database tables or doing
simple updates to schema (e.g. adding new tables or columns).
However, the migration auto-generation mechanism is not all-powerful and cannot detect
more complicated changes or generates incorrect code for them.

Therefore, you MUST always check and edit your migrations manually.

For example alembic will detect:

* Table addition or removal
* Table column addition

But cannot detect:

* Table or column rename
* Stored procedures and triggers
* Changes in Enum values list.

**References:**

1. [What does Autogenerate Detect (and what does it not detect?)](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)

### Name database objects

Name your database objects explicitly. Use a consistent and predictable naming schema for your
database objects (including but not limited to tables, indexes, constraints, custom types).
This makes database schema maintenance and further development easier.

If you omit naming your database objects, the database will generate names for them implicitly,
following its own internal naming schema.

Alembic can help you to name your objects, so that you don't have to name them explicitly in your
models. Alembic uses naming schema provided by the SQLAlchemy Metadata object. Default naming schema
includes only rule for naming database indexes, so it's imperative to define a custom naming schema
before creating any migrations.

Example:

```python
import sqlalchemy as sa

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # Unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check
    "fk": "fk_%(table_name)s_%(column_0_N_name)s",  # Foreign key
    "pk": "pk_%(table_name)s",  # Primary key
}
metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
```

However, the naming convention doesn't cover all database objects. For example Enum type
in PostgreSQL is implemented via custom types. Custom type name is generated automatically, so it's
recommended to specify name explicitly:

```python
import enum
from sqlalchemy import Table, Column, Enum, MetaData

class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3

t = Table(
    'data', MetaData(),
    Column('value', Enum(MyEnum, name="table_myenum"))
)
```

**References:**

1. [Alembic: The Importance of Naming Constraints](https://alembic.sqlalchemy.org/en/latest/naming.html)
2. [SQLAlchemy: Configuring Constraint Naming Conventions](https://docs.sqlalchemy.org/en/14/core/constraints.html#constraint-naming-conventions)

### Keep migrations isolated from the outside world

Migrations must not depend on environment they run in or configuration parameters used
at the execution time.

Migrations must not import any code that may change, including any functions, classes or constants
from the project or any 3rd party projects.

When migrations are applied the database tracks only the identifier of the migration tree head or
list of applied migrations. It's hardly possible to track the environment state used at the time
each migration was applied (e.g. configuration parameters, arguments passed to the migration script,
versions of 3rd party dependencies) and the environment may change. It leads to migrations failures
or unexpected side effects that are hard to debug.

### Use migrations for updating schema and existing data

Migrations can be also used for seeding the database, but only if the data introduced in the
migrations doesn't depend on the environment and get updated rarely and via migrations. List of
timezones is a good example of such constant data that may be stored in the database.

Be extremely careful with the data that is seeded via migrations, but may be updated by the business
logic. In the subsequent migrations expect the data may have changed since the migration it was
inserted in. Do not rely on auto-increment or randomly generated identifiers. Do not expect the data
is present in the database.

For seeding the database with the data that relies on environment or configuration, use standalone
scripts or tools. For example if you need to create an initial user records use scripts, management
commands or tools like Ansible.

### Keep migrations backwards compatible

In production environments where services upgraded without downtime or multiple versions of a
service co-exist at the same time (i.e. A\B testing and Blue\Green deployments), applying a database
migration must not break existing services.

Avoid changes that can break previous version of code (such as column and table rename and deletion)
and provide an upgrade path if such change is required.
