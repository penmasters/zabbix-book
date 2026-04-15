---
description: |
    Monitor databases with Zabbix ODBC checks. Run SQL queries across MySQL, PostgreSQL
    and more to track performance and availability metrics.
tags: [advanced]
---

# Database Monitoring via ODBC

*Reaching past the operating system layer to observe what actually matters:
the data.*

---

Most monitoring conversations start at the wrong layer. CPU load, memory pressure,
disk I/O — these are the signals that infrastructure teams reach for first, and
rightly so. But consider what they miss. A perfectly healthy database host can
be processing a catastrophic workload: a runaway query holding row-level locks
across thousands of transactions, a replication slot that has grown to consume
40 GB of WAL because a consumer went silent, an order queue where the pending count
has been climbing for six hours while the fulfilment process silently stalled.

None of those failures are visible to an agent watching the OS. They live inside
the database, and to see them, you have to speak the database's own language: SQL.

ODBC — Open Database Connectivity — is the mechanism Zabbix uses to do exactly
that. It enables agentless SQL execution against any database that exposes a compliant
driver, from on-premise MySQL clusters to managed cloud PostgreSQL services to SQL
Server environments deep inside enterprise Windows estates. Used with discipline,
it provides a tier of observability that no other Zabbix check type can match.
Used carelessly, it becomes one of the fastest ways to destabilise a production
database.

This chapter covers the complete ODBC stack — architecture, driver selection,
configuration, item design, discovery patterns, and the operational disciplines
that separate sustainable monitoring from the kind that generates incident tickets
at 3 AM.

---

## The ODBC Execution Stack

Before configuring a single item, it is worth understanding precisely what happens
when Zabbix executes a database monitor check. The path from Zabbix item to query
result is not direct — it passes through two intermediary layers, and each of those
layers has its own configuration surface, failure modes, and performance characteristics.

``` mermaid
flowchart TD
    A[Zabbix Server / Proxy] -->|"item type: Database monitor"| B
    B["ODBC Poller Process\n(blocking — poller unavailable while query runs)"] -->|"ODBC API call"| C
    C["unixODBC Driver Manager\n(/etc/odbcinst.ini, /etc/odbc.ini)"] -->|"resolves DSN → loads driver"| D
    D["Database-Specific ODBC Driver\n(.so shared library)"] -->|"native wire protocol"| E
    E[Target Database]
```

The first layer is unixODBC, the driver manager. It is responsible for maintaining
the registry of installed drivers and translating the symbolic DSN name in your
Zabbix item into a concrete connection. It reads two configuration files:
`/etc/odbcinst.ini` for driver definitions and `/etc/odbc.ini` for named connection
aliases. Without both files populated correctly, nothing downstream can function.

The second layer is the database-specific ODBC driver — a shared library that understands
the wire protocol of the target database. This driver is loaded dynamically by
unixODBC at query time. Its quality matters enormously: driver bugs, TLS implementation
gaps, and timeout handling differences are the most common sources of mysterious
ODBC failures in production. The driver, not unixODBC, is what ultimately speaks
to your database.

???+ note
    ODBC checks are blocking operations. An ODBC poller process remains fully occupied
for the duration of the query — it cannot service other items. A slow query does
not just delay its own item; it reduces the effective throughput of the entire
ODBC poller pool. This is why query performance discipline and correct poller sizing
are inseparable concerns.

This blocking nature has a direct consequence for how you should think about ODBC
at scale. Each concurrent database monitor item in flight consumes one poller slot.
If you have five pollers and six queries executing simultaneously, even briefly,
one item queues. If queries are slow, that queue grows. If queries are pathological
, the entire ODBC poller pool saturates and items go unsupported. Architecture
first; configuration second.

---

## Driver Selection and Installation

ODBC defines a standard interface. The substance behind that interface, the actual
quality, reliability, TLS support, and authentication capability of your monitoring
setup, is entirely determined by the driver you install. Driver selection is not a
minor configuration detail; it is a foundational architectural decision.

Three driver families cover the majority of production Zabbix ODBC deployments.

### MySQL and MariaDB

MariaDB Connector/ODBC is the recommended driver for both `MySQL` and `MariaDB`
workloads, and extends cleanly to cloud-managed MySQL-compatible services including
`Amazon RDS` and `Azure Database` for MySQL. It is actively maintained, widely
packaged, and behaves consistently across distributions.

Older MySQL ODBC packages (`libmyodbc5` and earlier) are still encountered in
legacy environments but should be migrated away from where possible. Version drift
between old MySQL ODBC drivers and modern MySQL 8.x servers can produce authentication
failures, particularly with the `caching_sha2_password` default authentication plugin
introduced in MySQL 8.0.

There is one non-obvious constraint that catches many administrators off-guard:
the ODBC driver you install must be compatible with the connector library that
Zabbix itself was compiled against. Mixing MySQL and MariaDB across these two
layers triggers an upstream bug that causes crashes or silent query failures
(ZBX-7665). The rule is straightforward in principle but easy to violate in practice:

| Zabbix compiled against | Use this ODBC driver |
|---|---|
| PostgreSQL, SQLite, or Oracle connector | MariaDB **or** MySQL ODBC driver |
| MariaDB connector | MariaDB ODBC driver only |
| MySQL connector | MySQL ODBC driver only |

When in doubt, check how your Zabbix binary was compiled — `zabbix_server -V` will
show the linked libraries — and match the ODBC driver to the connector on that
same side of the MySQL/MariaDB divide. Using the same connector as the driver is
also best avoided where possible due to the same upstream issue. This is one of
the few ODBC configuration requirements with no safe workaround other than compliance.

[https://support.zabbix.com/browse/ZBX-7665](https://support.zabbix.com/browse/ZBX-7665)


### PostgreSQL

The `psqlodbc` driver is stable, mature, and widely deployed in enterprise PostgreSQL
environments. It supports SSL connections and SCRAM-SHA-256 authentication,
which is the default in PostgreSQL 14 and later.

When monitoring PostgreSQL with SCRAM authentication, verify that your installed
`psqlodbc` version explicitly supports it, older builds do not. Attempting a SCRAM
handshake with an incompatible driver produces an authentication error that is
easy to misdiagnose as a permissions problem.

### Microsoft SQL Server

Microsoft's official `msodbcsql18` driver is the correct choice for SQL Server
monitoring. It supports TLS encryption (often mandatory in enterprise SQL Server
configurations), Kerberos and Active Directory authentication, and Azure SQL Database.
Installation requires Microsoft's official repository and EULA acceptance.

FreeTDS (`tdsodbc`) is a fully open-source TDS protocol implementation available
without any external repository. It works reliably for simple monitoring queries
against on-premise SQL Server instances. However, its TLS implementation lags
behind the official driver, Azure SQL compatibility is inconsistent, and authentication
options are limited. Use it in constrained environments where Microsoft's repository
is unavailable, but test thoroughly before production deployment.

FreeTDS also has a query-level requirement that is not documented prominently and
produces a confusing error when missing. Every SQL query executed through the FreeTDS
driver must be prefixed with `SET NOCOUNT ON`:

```sql
SET NOCOUNT ON
SELECT COUNT(*) FROM orders WHERE status = 'pending'
```

Without this prefix, the driver returns an empty result set and the Zabbix item
goes unsupported with the error "SQL query returned empty result", even when the
query itself is syntactically correct and would return data through any other
client. This is a known driver behaviour (ZBX-19917), not a Zabbix bug. Once the
prefix is in place, FreeTDS behaves predictably for straightforward monitoring
queries.

One additional SQL Server limitation worth knowing regardless of driver choice:
XML data queried from Microsoft SQL Server may be truncated in various ways on
Linux and UNIX systems. If your monitoring queries return XML columns, common in
some SQL Server system views — verify that the full value is being returned rather
than silently cut off at a driver or OS boundary.

???+ note

    ODBC drivers exist for Oracle, IBM Db2, SAP HANA, and many others. Driver quality,
    maintenance cadence, and compatibility with modern authentication standards vary
    significantly outside the three families above. Oracle deserves special mention:
    multiple versions of Oracle Instant Client for Linux have been observed to cause
    Zabbix server crashes when used for ODBC monitoring (ZBX-18402, ZBX-20803). If
    you are monitoring Oracle via ODBC, test driver versions carefully in a non-production
    environment before any production deployment, and treat an upgrade to a new
    Instant Client version as a change that requires re-validation. Before deploying
    any less common driver in production, treat it as an unknown quantity: test
    under realistic load, validate timeout behaviour, and confirm UTF-8 encoding
    handling. Your monitoring reliability is only as good as the driver underneath
    it.

### Built-in Templates

Zabbix ships with ready-made ODBC templates for the most common database platforms.
These are a reasonable starting point — they implement the master item pattern
correctly and include sensible default triggers — but treat them as a baseline
to adapt rather than a finished solution. Production environments invariably have
database configurations, naming conventions, and business metrics that require
customisation beyond what a generic template can provide.

The available templates are: **MariaDB by ODBC**, **MySQL by ODBC**, **MSSQL by
ODBC**, **Oracle by ODBC**, **Percona by ODBC**, and **PostgreSQL by ODBC**. Each
includes a README accessible from the template detail view in the Zabbix frontend,
listing the full set of macros, items, and triggers.

### Driver Packages by Platform

| Database | RHEL / Rocky / Alma | Ubuntu / Debian | SUSE | Vendor Repo? |
|---|---|---|---|---|
| MySQL / MariaDB | `mariadb-connector-odbc` | `mariadb-connector-odbc` | `mariadb-connector-odbc` | No |
| PostgreSQL | `psqlodbc` | `odbc-postgresql` | `psqlODBC` | No |
| SQL Server | `msodbcsql18` | `msodbcsql18` | `msodbcsql18` | Yes |
| SQL Server (OSS) | `freetds`, `freetds-odbc` | `freetds-bin`, `tdsodbc` | `libtdsodbc0` | No |

### Installation

ODBC components must be installed on the Zabbix Server or Proxy that will perform
the checks, not on the monitored database host. The package set is the same regardless
of which database you intend to monitor: the unixODBC driver manager first, then
the database-specific driver on top.

**Rocky Linux 9 / RHEL / Alma**

```bash
sudo dnf install unixODBC unixODBC-devel
sudo dnf install mariadb-connector-odbc    # for MySQL or MariaDB targets
sudo dnf install postgresql-odbc           # for PostgreSQL targets
```

**Ubuntu 24.04 / Debian**

```bash
sudo apt update
sudo apt install unixodbc unixodbc-dev
sudo apt install odbc-mariadb              # for MySQL or MariaDB targets
sudo apt install odbc-postgresql           # for PostgreSQL targets
```

**SUSE**

```bash
sudo zypper install unixODBC-devel
sudo zypper install mariadb-connector-odbc # for MySQL or MariaDB targets
sudo zypper install psqlODBC               # for PostgreSQL targets
```

After installation, confirm that the driver manager can see the installed drivers:

```bash
odbcinst -q -d
```

If a driver you just installed does not appear in the output, the package did not
register it correctly in `/etc/odbcinst.ini` and you will need to add the entry
manually before any DSN referencing that driver will function.

### Configuration Files

Two files define the ODBC configuration on the Zabbix server or proxy host. They
must both be correct for any check to function.

**`/etc/odbcinst.ini` — Driver Registry**

Registers installed drivers under symbolic names. The `Driver` path must point
to an installed `.so` file on the local filesystem.

```ini
[MariaDB]
Description = MariaDB ODBC Driver
Driver      = /usr/lib64/libmaodbc.so

[PostgreSQL]
Description = PostgreSQL ODBC Driver
Driver      = /usr/lib64/psqlodbc.so
```

Verify the registry reflects installed drivers:

```bash
odbcinst -q -d
```

**`/etc/odbc.ini` — Connection Aliases (DSNs)**

Defines named connections that Zabbix items reference by their section header.
Each entry maps a symbolic name to driver, host, port, and database configuration.

```ini
[InventoryDB]
Description = Production Inventory Database
Driver      = MariaDB
Server      = 192.168.1.50
Port        = 3306
Database    = shop_db
User        = zabbix_mon
Password    = strong_password
```

The DSN file contains database credentials. Restrict its permissions immediately
after creation, a world-readable `odbc.ini` on a multi-user host is a straightforward
credential exposure:

```bash
chmod 600 /etc/odbc.ini
```

### Validating the Stack Before Touching Zabbix

Every ODBC troubleshooting session that begins inside Zabbix should have started
here instead. Test the DSN directly with `isql` before configuring any items:

```bash
isql -v InventoryDB
```

A successful connection returns a `Connected!` prompt. If it fails, the problem
is in the ODBC stack — driver registration, credentials, network access, TLS
configuration — and it will fail identically inside Zabbix. Resolve it at this
layer first. The combination of `isql` verification and a correctly sized poller
pool eliminates the vast majority of ODBC support issues before they ever reach
a Zabbix item.

---

## Item Design: Two Keys, Different Philosophies

Zabbix exposes two item keys for ODBC-based database monitoring. They are not
interchangeable variations of the same idea — they represent different philosophies
about how monitoring data should be collected.

### `db.odbc.select` — The Scalar Path

`db.odbc.select` executes a SQL query and returns exactly one value: the first
column of the first row of the result set. Nothing else is preserved.

```text
db.odbc.select[<description>,<dsn>,<connection string>]
```

This simplicity is its strength. There is no JSON preprocessing, no dependent
item chain, no extraction logic to maintain. Write a query that produces a single
number, point it at a DSN, and the value flows directly into item history.

`db.odbc.select` belongs in your design when the question you are asking has
exactly one answer: how many pending orders exist right now? What is the replication
lag in seconds? How many active sessions are connected to this instance? For these
use cases, adding the machinery of `db.odbc.get` would be engineering overhead
with no benefit.

One important operational note: even though you may write a query that intentionally
returns one row, multi-row queries will still only surface the first column of
the first row to Zabbix. Write your SQL to be explicit about what you want, not
reliant on this truncation behaviour.

### `db.odbc.get` — The Scalable Path

`db.odbc.get` executes a SQL query and returns the entire result set as a JSON array.

```text
db.odbc.get[<description>,<dsn>,<connection string>]
```

A query returning multiple rows and columns produces something like:

```json
[
  {"status": "pending",   "total": "15", "oldest_age_minutes": "47"},
  {"status": "processing","total": "8",  "oldest_age_minutes": "12"},
  {"status": "failed",    "total": "3",  "oldest_age_minutes": "183"}
]
```

This single query execution, hitting the database once, can feed an unlimited
number of dependent items through JSONPath preprocessing. As the replication of
database queries as item counts grows, the database load does not.

The canonical design pattern is the **master item**: one `db.odbc.get` item collects
the full result set on a defined interval; dependent items each extract one metric
using JSONPath and may apply additional preprocessing steps like type conversion.
Ten metrics, one query. A hundred metrics, one query. This is not a marginal
optimisation, in environments monitoring dozens of databases, it is the difference
between sustainable load and an ODBC poller pool in permanent saturation.

!!! note

    Database drivers commonly return numeric columns as strings in ODBC result
    sets. Always include a **Change Type** preprocessing step converting to Numeric
    (unsigned) or Numeric (float) on dependent items that will feed triggers or
    graphs. Type inconsistency is the most common cause of trigger misfires on
    freshly built database monitor templates.

#### A Worked Example

Consider a production order management database. Rather than running separate
queries for pending count, processing count, average queue age, and oldest item
age, a single query captures the relevant state in one round-trip:

```sql
SELECT
    status,
    COUNT(*) AS total,
    AVG(TIMESTAMPDIFF(MINUTE, created_at, NOW())) AS avg_age_minutes,
    MAX(TIMESTAMPDIFF(MINUTE, created_at, NOW())) AS oldest_age_minutes
FROM orders
WHERE status IN ('pending', 'processing', 'failed')
GROUP BY status;
```

The master item runs this query every 60 seconds. From it, dependent items extract
pending count, processing count, failed count, and average and maximum queue age
per status — all without touching the database again. A trigger fires when the
oldest failed item exceeds a threshold. Another fires when the pending count exceeds
a threshold relative to its moving average. Zero additional database load beyond
the single master query.

### Choosing Between the Two

| Criterion | `db.odbc.select` | `db.odbc.get` |
|---|---|---|
| Number of metrics per query | One | Unlimited |
| JSON preprocessing required | No | Yes |
| Suitable for dependent items | No | Primary use case |
| Suitable for LLD | No | Yes |
| Database call per metric | One | Fractional (shared) |
| Template complexity | Low | Medium |
| Recommended for new templates | Narrow use cases | Default choice |

In practice: use `db.odbc.select` when the metric genuinely stands alone, the
query is trivially simple, and the item will never need to feed discovery or dependent
logic. In every other case, design around `db.odbc.get` with a master item pattern
from the start. Retrofitting a scalar template into a scalable one after the fact
is substantially more work than getting the architecture right at the outset.

---

## Low-Level Discovery with ODBC

One of the most powerful ODBC patterns available in Zabbix is using it to drive
Low-Level Discovery — automatically generating monitoring items for database objects
whose existence cannot be known at template design time. Tables, schemas, replication
slots, partitions, named queues: anything the database can enumerate, Zabbix can
discover and monitor.

### Native Discovery: `db.odbc.discovery`

The `db.odbc.discovery` key is purpose-built for LLD. It executes a SQL query and
formats the results as a discovery array. The query must alias column names to
match LLD macro format exactly:

```sql
SELECT
    table_name AS "{#TABLE}",
    table_rows AS "{#APPROX_ROWS}"
FROM information_schema.tables
WHERE table_schema = 'shop_db'
  AND table_type   = 'BASE TABLE';
```

This produces one discovered entity per table, with macros available for use in
item prototype keys and names. The common mistake is omitting the quoted LLD macro
format on the alias — the curly brace and hash syntax must be present and quoted,
or Zabbix will not recognise the column as a macro.

### Scalable Discovery via `db.odbc.get`

For larger environments, the master item pattern extends naturally to discovery.
A single `db.odbc.get` item collects the full dataset; a dependent discovery rule
extracts the LLD array using JSONPath; item prototypes are defined as further
dependent items on the master. One query execution per interval drives the entire
discovery and metric collection pipeline.

The performance contrast becomes significant at scale. Native `db.odbc.discovery`
executes its own query for each discovery rule. If you have five discovery rules
covering different aspects of a database — tables, indexes, replication slots,
partitions, connection pools — that is five separate query executions per discovery
interval. The master item pattern reduces that to one, with all five discovery
rules fed from the same result set.

The architectural decision between the two approaches follows a simple heuristic:
if the discovery dataset is small and the discovery interval is measured in hours,
native `db.odbc.discovery` is perfectly adequate and easier to implement. If the
environment is large, the discovery interval is more frequent, or you need to
correlate data from the same query across multiple discovery rules, use the master
item pattern.

!!! note

    Discovery should detect structure, what objects exist, not operational state.
    Keep discovery queries lightweight and prefer metadata sources like `information_schema`
    over scanning operational tables. Run discovery at intervals appropriate to
    how often the underlying structure actually changes: hourly or daily is typical.
    Minute-level discovery intervals for database object discovery are almost
    always unnecessary.

---

## Operational Discipline

ODBC monitoring is unusual among Zabbix check types in that its failure modes are
asymmetric. A misconfigured agent check fails silently or generates a support
event in Zabbix. A misconfigured or carelessly written ODBC check can generate
a noticeable workload on the monitored database — a workload that may compound
under high-frequency polling, grow worse during periods of database stress, and
produce cascading effects across both the monitoring and production stack.

The disciplines below are not optional refinements for mature deployments. They are the baseline for any production ODBC configuration.

### Query Design

Every monitoring query must be lighter than the production workload it observes. This is a firm principle, not a guideline. Queries that use indexed columns, return aggregate results, and touch only the rows they need are acceptable. Queries that scan large tables, perform unindexed joins, or replicate the logic of reporting tools are not.

Before deploying any monitoring query, run `EXPLAIN` or `EXPLAIN ANALYZE` against it and inspect the execution plan. A full table scan on a table with millions of rows, executed every 30 seconds, is not monitoring — it is a scheduled load injection. If the query plan is not acceptable in production context, redesign the query or choose a different monitoring approach.

The temptation to embed business logic in monitoring SQL is common and should be resisted. Monitoring observes systems; it does not replicate application behaviour. A query that reproduces the calculation your order processing service performs to determine fulfilment priority is fragile, hard to maintain, and likely to become incorrect the moment the application logic changes.

### Poller Sizing

The `StartODBCPollers` parameter in `zabbix_server.conf` or `zabbix_proxy.conf` controls the number of concurrent ODBC poller processes.

```
StartODBCPollers=5
```

Too few pollers and items queue, then go unsupported. Too many and you risk overwhelming the database with concurrent connections, particularly if the monitored database enforces connection limits. The correct approach is to start conservatively — 3 to 5 pollers for small deployments — and monitor the ODBC poller busy percentage in Zabbix's own internal metrics. Scale up only when utilisation consistently exceeds 70 to 80 percent. Never increase pollers as a substitute for fixing slow queries; doing so shifts the queuing problem to the database layer, where it becomes invisible in Zabbix metrics.

### Timeouts

Unhandled query timeouts are the most reliable path to a fully saturated poller pool. A query that hangs indefinitely ties up a poller slot until the database eventually errors or the connection is forcibly closed. In a pool of five pollers, three hanging queries means 60 percent of your ODBC capacity is unavailable.

Zabbix 7.0 introduced per-item timeout configuration for database monitor items, accepting values from 1 second to 10 minutes. Use this to set timeouts appropriate to each query's expected duration. A simple aggregate query should have a 5-second timeout. A more complex cross-table query might justify 30 seconds. Nothing in a monitoring context should run for minutes.

### Isolation via Proxy

In any environment with more than a handful of ODBC items, database monitoring should run through a Zabbix Proxy rather than directly from the server. This provides two critical properties: isolation and locality.

Isolation means that a misbehaving ODBC configuration — slow queries, driver crashes, database connectivity loss — affects only the proxy, not the central Zabbix server. The server continues operating normally; the proxy's ODBC items simply go unsupported until the issue is resolved. Without isolation, the same failure degrades the entire server's poller pool.

Locality means the proxy runs on a host with direct network access to the monitored databases, with ODBC drivers installed for that specific database environment, and without routing monitoring traffic through wide-area network paths.

### Credentials and Security

The monitoring database account must be read-only. Not "mostly read-only with a few exceptions" — strictly SELECT only, on the specific databases and schemas it needs to monitor, with no ability to modify data or schema. Create a dedicated account per monitored application:

```sql
CREATE USER 'zabbix_mon'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON shop_db.* TO 'zabbix_mon'@'%';
```

Store credentials in Zabbix macros rather than hardcoded in DSN files where possible. For environments with a secrets management platform, Zabbix's vault integration allows credentials to be fetched at runtime rather than stored in configuration files at all.

Connection strings embedded directly in item keys are visible in the Zabbix frontend to any user with access to the host configuration. This is acceptable in development but not in production. Use DSN-level credentials or macros.

### Connection Pooling

unixODBC supports connection pooling from version 2.0.0 onwards. Enabling it reduces the overhead of repeated connection establishment — the TCP handshake, TLS negotiation, and authentication round-trip that precedes every query in a non-pooled configuration. In high-frequency monitoring environments, this overhead accumulates.

```ini
# In /etc/odbcinst.ini
[ODBC]
Pooling = Yes
```

Pooling is particularly valuable in environments where database connection setup is expensive — SSL mutual authentication, Kerberos, or databases with slow authentication backends. Verify that your specific driver supports pooling correctly before enabling it in production, as driver-level pooling bugs can produce stale connection state or query result corruption.

### Character Encoding

ODBC monitoring is surprisingly sensitive to encoding inconsistencies. The database, the operating system locale, and the ODBC driver must all agree on UTF-8. When they do not, two failure modes emerge: visually corrupted string data in item values, and JSON parse failures in `db.odbc.get` results.

The second mode is more operationally dangerous because it produces item errors rather than incorrect data. A `db.odbc.get` item that returns garbled encoding in a string column will silently break every dependent item and discovery rule that depends on it. Verify encoding consistency during initial deployment, before any dependent item logic is built on top of the master item.

---

## Anti-Patterns and How They Manifest

ODBC anti-patterns tend to be invisible until they are not. The symptoms often appear distant from the root cause — an unrelated monitoring item goes unsupported, database response times spike during a specific window, Zabbix queue depth grows. Knowing the common failure patterns in advance makes them faster to diagnose.

**Monitoring queries written as reports.** A query written for a business report is designed to be complete and correct, not fast. It likely scans multiple large tables, performs several joins, aggregates millions of rows, and computes derived fields. Running it once a month in a reporting tool is fine. Running it every 60 seconds as a Zabbix check against a production database is not. The symptom is a gradual increase in database CPU and I/O during monitoring windows, often dismissed as coincidental load until someone traces it.

**High-frequency polling of expensive metrics.** Not all metrics need to be collected at the same frequency. Replication lag — where a drift of even a few seconds may be significant — warrants a short polling interval. The number of tables in a schema — which changes only when a deployment runs — does not. Applying a 30-second polling interval uniformly across all ODBC items wastes both poller capacity and database resources. Assign intervals based on the operational sensitivity of each metric.

**Using privileged accounts.** Monitoring with a DBA or application account that has write privileges introduces unnecessary risk. A credential leak, an injection vulnerability in a poorly constructed monitoring query, or a simple configuration mistake could result in data modification. The monitoring account must be read-only. There are no legitimate exceptions to this in production.

**Scaling pollers to mask slow queries.** When ODBC items go unsupported due to poller saturation, the instinct is to increase `StartODBCPollers`. If the saturation is caused by a growing item count or a genuine burst in monitoring demand, more pollers is the right answer. If it is caused by slow queries, more pollers shifts the problem: instead of queued items in Zabbix, you get queued connections at the database layer, which may then cause application connection pool exhaustion. Fix the query first. Scale pollers second.

**Ignoring driver-specific known issues.** Each driver family carries its own list of quirks that are not discoverable through normal testing. The MySQL/MariaDB connector mismatch (ZBX-7665), the FreeTDS `SET NOCOUNT ON` requirement (ZBX-19917), Oracle Instant Client crashes on Linux (ZBX-18402, ZBX-20803), and MSSQL XML truncation on UNIX systems are all production-grade failure modes that are entirely invisible during basic connectivity testing. Reviewing the known issues for your specific driver before deployment is not optional reading — it is the step that prevents a category of failures that no amount of query tuning or poller sizing will fix.

**Skipping DSN validation.** Configuring a Zabbix item against an untested DSN and then using Zabbix's error output to debug ODBC connectivity is slower and less informative than using `isql` directly. Zabbix normalises ODBC errors through its own logging layer; `isql` surfaces the raw driver error. Always validate the full stack with `isql` before creating Zabbix items.

---

## Choosing the Right Database Monitoring Approach

ODBC is not the only way to monitor databases in Zabbix, and it is not always the right one. The choice between ODBC, agent-based monitoring, and application-layer HTTP checks depends on what you are measuring, where the database lives, and what operational overhead you are prepared to maintain.

| Criterion | ODBC | Zabbix Agent 2 Plugin |
|---|---|---|
| Agent required on DB host | No | Yes |
| Custom SQL queries | Yes — full flexibility | Limited or none |
| Cloud-managed databases | Yes | Often not possible |
| Infrastructure health metrics | Good | Excellent |
| Business KPI monitoring | Excellent | Not designed for it |
| Risk of slow queries | High (by design) | Low |
| Setup and maintenance cost | Medium to high | Low |

The strategic division in mature environments is clear: Agent 2 plugins handle core database health and OS-level metrics where an agent can be installed; ODBC handles everything that requires direct SQL execution — custom business metrics, application-level state, replication details, and anything residing in tables rather than system views. Neither replaces the other. Together, they provide the full observability stack.

---

## Summary

ODBC occupies a unique position in the Zabbix monitoring toolkit: it is the only mechanism that gives you direct access to the data layer, the place where the most operationally significant state actually lives. Order queues, replication lag, session counts, failed transaction rates, business KPIs — none of these are visible without SQL.

The technical complexity of ODBC is moderate. Installing drivers, configuring DSNs, and writing `db.odbc.select` items is straightforward work. The harder discipline is operational: choosing queries that are genuinely lightweight, sizing the poller pool appropriately, isolating database monitoring through proxies, validating the full stack before configuring items, and resisting the temptation to embed business logic or reporting queries in monitoring checks.

The `db.odbc.get` master item pattern — one query feeding multiple dependent items and discovery rules — is the foundation of any scalable ODBC deployment. Build around it from the start, and ODBC becomes one of the most powerful sources of observability in your Zabbix environment. Treat it as an afterthought, and it becomes one of the most reliable sources of production incidents.

The difference is not in the technology. The difference is in the discipline of the person who configures it.

---

## Questions

- Why does Zabbix rely on unixODBC instead of communicating directly with databases, and what are the operational implications of that indirection?
- A `db.odbc.get` master item runs a query that returns 12 columns across 8 rows. How many dependent items can theoretically be fed from it, and what preprocessing steps would you apply to extract a numeric value from one of those columns?
- You have 5 ODBC pollers and notice that ODBC poller busy percentage is consistently at 95%. Before increasing `StartODBCPollers`, what investigation steps should you take first?
- An ODBC item returns `[08001] Network connectivity issue`. Walk through the diagnostic sequence you would follow, starting from the most foundational layer.
- You are designing a template to monitor a PostgreSQL database that has a variable number of schemas, each with a variable number of tables. Describe the discovery architecture you would use and explain why.
- Why is it dangerous to use the same monitoring approach — polling interval, query complexity, and account privileges — across both development and production environments?
- Your Zabbix server is compiled against the MariaDB connector. A colleague installs the MySQL ODBC driver and configures several database monitor items. What specific failure modes should you anticipate, and how would you resolve the configuration correctly?
- A FreeTDS-based MSSQL monitor item returns "SQL query returned empty result" despite the query executing correctly in a SQL client. What is the cause and what is the fix?

## Useful URLs

- https://www.zabbix.com/documentation/7.4/en/manual/config/items/itemtypes/odbc_checks
- https://blog.zabbix.com/database-odbc-monitoring-with-zabbix/8076/
- https://www.zabbix.com/forum/zabbix-help/413055-installation-and-configuration-of-mssql-by-odbc-docker
