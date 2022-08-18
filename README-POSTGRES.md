# Database Configuration for Ansible Events

## Base Configuration

Please use [this link](https://www.postgresql.org/docs/current/runtime-config.html) to access the current PostgreSQL configuration documentation.

The base configuration file for PostgreSQL is a copy of `postgresql.conf` taken from a postgres:13 image container. From this base certain parameters were adjusted for a better development base configuration.

The project's PostgreSQL config file can be found at this path: `tools/docker/postgres/postgresql.conf`.

The config file format uses the following format:

* Comments begin with a hash (`#`) character and will end at the end of the current line.
* Parameter names are lowercase and begin at the left.
* Assigning a parameter value uses a keywork = value syntax. (Example for `max_connections`): `max_connections = 100`
    * The equals sign (`=`) should be surrounded by single spaces.
    * Numeric values are bare. (See above example.)
    * Boolean value are bare and have a value of either `on` or `off`
    * String values are enclosed in single-quote characters. Ex: `shared_preload_libraries = 'pg_stat_statements'`
* Parameters may either be commented-out (start the line with a '#' character) or lines may be deleted.

### Changes

#### Config File Includes

* [Includes Documentation](https://www.postgresql.org/docs/14/config-setting.html#CONFIG-INCLUDES)

The following changes were made to the the includes parameters:

| Parameter | Changed Value | Original Value | Description |
| --------- | ------------- | -------------- | ----------- |
| include_dir | **'/etc/postgresql/conf.d'** | '...' | This value sets an include directory to add more configuration options. The directory specified will be scanned for more configuration options in files matching the glob `*.conf`. The initial value `'...'` is simply for illustration purposes as the configuration parameter is initially commented out. This setting is used to match the mount point for extension configuration files. |

## Custom Configuration

All custom configuration files are mounted into the `postgres` container at `/etc/postgresql/conf.d`. Custom config files exist in the repository at `tools/docker/postgres/conf.d` The config files in that directory are named for the configuration block that is customized.

#### SSL

`tools/docker/postgres/conf.d/pg_ssl.conf`

* [SSL Documentation](https://www.postgresql.org/docs/current/runtime-config-connection.html#RUNTIME-CONFIG-CONNECTION-SSL)

The following changes were made to enable SSL connections.

| Parameter | Changed Value | Original Value | Description |
| --------- | ------------- | -------------- | ----------- |
| ssl       | **on**        | off            | Activate (on) or deactivate (off) use of SSL connections. Enabling SSL connections does not exclude non-SSL connections. If you want to **only** use SSL connections, you may want to [try this](https://dba.stackexchange.com/questions/8580/force-postgresql-clients-to-use-ssl). |
| ssl_cert_file | `/etc/ssl/certs/ssl-cert-snakeoil.pem` | server.crt | Name of the file containing the SSL server certificate. The file used here was provided in the [postgres](https://hub.docker.com/_/postgres) image from Docker Bub. If this configuration is to be used in a production environment. This file should be changed to a proper production SSL certificate file. |
| ssl_key_file | `/etc/ssl/private/ssl-cert-snakeoil.key` | server.key | Name of the file containing the SSL server private key. The file used here was provided in the [postgres](https://hub.docker.com/_/postgres) image from Docker Bub. If this configuration is to be used in a production environment. This file should be changed to a proper production SSL certificate file. |

#### Logging

`tools/docker/postgres/conf.d/pg_logging.conf`

* [Logging Documentation](https://www.postgresql.org/docs/current/runtime-config-logging.html)

The following changes were made to the the logging parameters:

| Parameter | Changed Value | Original Value | Description |
| --------- | ------------- | -------------- | ----------- |
| log_min_duration_statement | **1000** | -1 | -1 disables; 0 logs all statements; >0 logs statements executing longer than the specified value (in milliseconds). This is set to log any statement that runs longer than 2 seconds. |
| log_line_prefix | **'%m:%b:[%p]: '** | '%m [%p] ' | %m = timestamp w/milliseconds; %b = backend type; %p = process ID; See the logging documentation link for a full explanation of all available options. The inclusion of %b here allows for differentiation between connections, autovacuum processes, replication (if enabled) or other backend process types are logged. |
| log_statement | **'mod'** | none | Statement type to log: 'mod' = INSERT,UPDATE,DELETE; 'ddl' = CREATE,DROP,ALTER; 'all' = all; 'none' = none; The `'mod'` value was chosen to log modification statements so only the poorly performing select statements are logged via `log_min_duration_statement` setting. |

#### Statistics

`tools/docker/postgres/conf.d/pg_statistics.conf`

* [Statistics Documentation](https://www.postgresql.org/docs/current/runtime-config-statistics.html)

The following changes were made to the the statistics parameters:

| Parameter | Changed Value | Original Value | Description |
| --------- | ------------- | -------------- | ----------- |
| track_functions | **'pl'** | none | Enables tracking of function call counts and time used. Specify pl to track only procedural-language functions, all to also track SQL and C language functions. The default is none, which disables function statistics tracking. Only superusers can change this setting. Setting the value to `'pl'` is meant to focus on any user-defined functions as this project is not writing any PostgreSQL extension code. |
| track_activity_query_size | **2048** | 1024 | Specifies the amount of memory reserved to store the text of the currently executing command for each active session, for the pg_stat_activity.query field. If this value is specified without units, it is taken as bytes. The default value is 1024 bytes. This parameter can only be set at server start. This value was chosen to provide enough of a buffer to capture a potentially large query such as one that may contain multiple CTEs. |

### pg_stat_statements Extension

`tools/docker/postgres/conf.d/pg_stat_statements.conf`

* [pg_stat_statements Extension Documentation](https://www.postgresql.org/docs/current/pgstatstatements.html)

The `pg_stat_statements` extension will capture statistics about the queries that are run. This includes timing information, It will also show the read/write ratios of regular tables (shared_blocks) and temporary tables (local_blocks). The data in this table is cumulative for the database, user, and query. Queries are stored in a parameterized fashion to determine uniqueness.

This module can track statements for any database on the cluster that has the extension enabled.

The following configuration variables have been changed from the default:

| Parameter | Changed Value | Original Value | Description |
| --------- | ------------- | -------------- | ----------- |
| pg_stat_statements.max | **2000** | 5000 | This is the maximum number of statements tracked by the module. This number was lowered because, currently, there is only one database on the cluster and is a good enough buffer of the top queries to track for a project of this design and a data model of this complexity. |
| pg_stat_statements.save | **off** | on | Controls whether or not to save statement statistics across server shutdowns. At this time, there does not appear to be a need for this. |
| pg_stat_statements.track_utility | **off** | on | Whether or not to track statements other than SELECT, INSERT, UPDATE, DELETE. At time time, there does not appear to be a need for this. |

## General Configuration Notes

### Vacuum and Autovacuum

* [Vacuum Documentation](https://www.postgresql.org/docs/14/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-VACUUM-COST)
* [Autovacuum Documentation](https://www.postgresql.org/docs/14/runtime-config-autovacuum.html)

It is a general rule of thumb that autovacuum runs are more efficient when they run more frequently with less to do as their job can be expensive.

Configuring vacuum involves a number of parameters for a default level of efficient servicde. This has to do with checking table size change thresholds and number of modification statements. These values can change for a database that has a large amount of data, ingests large amounts of data, modifies or deletes a large amount of data. Vacuuming configuration defaults may suffice if the data selection are precise (ie: selection of a small set of granular records) versus (re)aggregation and summarization of large numbers of records.

Tuning these parameters will be based on the use case for the database.

### Dynamic Table Adjustments

* [Alter Table Documentation](https://www.postgresql.org/docs/14/sql-altertable.html)
* [Table Storage Parameters Documentation](https://www.postgresql.org/docs/14/sql-createtable.html#SQL-CREATETABLE-STORAGE-PARAMETERS)
* [pg_stat_all_tables Documentation](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ALL-TABLES-VIEW)
* [pg_stat_all_indexes Documentation](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STATIO-ALL-INDEXES-VIEW)

If desired, code can be implemented in an application to monitor and dynamically tune database tables, especially regarding changing autovacuum parameters from the settings in the configuration file. This is done via `ALTER TABLE` statements. When monitoring a table, the `pg_stat_all_tables` view provides a wealth of information about the estimated number of tuples, seq scans (sequential block reads of the stored table data), index hits and other valuable information. These values can be acted upon based on the desired configuration on a per-table basis as table sizes grow.

Index performance can also be checked by checking the hit rate using the `pg_stat_all_indexes` view along with `pg_stat_all_tables` view data.
