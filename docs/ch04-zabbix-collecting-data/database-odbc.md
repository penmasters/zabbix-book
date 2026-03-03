---
description: |
    Monitor databases with Zabbix ODBC checks. Run SQL queries across MySQL, PostgreSQL
    and more to track performance and availability metrics.
tags: [advanced]
---

# Database Monitoring via ODBC

Monitoring operating systems and applications provides important signals, but the
most valuable insights often reside inside the database itself. Order queues, replication
status, session counts, transaction failures, and business KPIs all live at the
data layer.

ODBC (Open Database Connectivity) allows Zabbix to query databases directly without
installing an agent on the database server. In Zabbix 8.0, ODBC remains a powerful
and flexible mechanism for agentless database monitoring, built on top of the
`unixODBC` driver manager.

Used correctly, ODBC enables deep visibility into both infrastructure and business
metrics. Used carelessly, it can introduce performance risk and operational instability.
This chapter explains how to deploy ODBC properly and operate it safely in production
environments.

---

## Architecture Overview

Zabbix does not communicate with databases directly. It relies on the ODBC stack.

``` mermaid
flowchart TD
    subgraph Zabbix Layer
        A[Zabbix Server / Proxy]
        B[ODBC Poller Process]
    end

    subgraph ODBC Layer
        C[unixODBC Driver Manager]
        D[Database-Specific ODBC Driver]
    end

    subgraph Database Layer
        E[Target Database]
    end

    A -->|Executes db.odbc.* item| B
    B -->|ODBC API Call| C
    C -->|Loads Driver| D
    D -->|SQL Execution| E
```

### Execution Flow

1. A Zabbix item of type **Database monitor** executes:
   * `db.odbc.select[]` (single scalar value)
   * `db.odbc.get[]` (JSON result set)
2. An ODBC poller process handles the request.
3. unixODBC resolves the configured DSN (Data Source Name).
4. The database driver executes the SQL query.
5. Results are returned to Zabbix.

ODBC checks are blocking operations. While a query executes, the poller remains occupied.

---

## ODBC Configuration Files

ODBC relies on two configuration layers.

### `/etc/odbcinst.ini` — Driver Definitions

Defines available ODBC drivers.

Example:

``` ini
[MariaDB]
Description = MariaDB ODBC Driver
Driver      = /usr/lib64/libmaodbc.so

[MySQL]
Description = MySQL ODBC Driver
Driver      = /usr/lib64/libmyodbc5.so
```

Verify installed drivers:

``` bash
odbcinst -q -d
```

If the driver is not listed here, the DSN will not function.

---

### `/etc/odbc.ini` — DSN Definitions

Defines connection aliases.

``` ini
[InventoryDB]
Description = Production Inventory Database
Driver      = MariaDB
Server      = 192.168.1.50
Port        = 3306
Database    = shop_db
User        = zabbix_mon
Password    = strong_password
```

The `Driver` name must match the definition in `/etc/odbcinst.ini`.

Restrict file permissions:

``` bash
chmod 600 /etc/odbc.ini
```

---

## Installing ODBC Components

ODBC and correct drivers must be installed on the Zabbix Server or Proxy performing the check.

### Rocky Linux 9

``` bash
sudo dnf install unixODBC unixODBC-devel
sudo dnf install mariadb-connector-odbc or mysql−connector−odbc postgresql-odbc
```

### Ubuntu 24.04

```bash
sudo apt update
sudo apt install unixodbc unixodbc-dev odbc-mariadb odbc-postgresql
```
###  SUSE

``` bash
zypper in unixODBC-devel mariadb-connector-odbc psqlODBC
Verify drivers:
```

```bash
odbcinst -q -d
```

---

## Commonly Used ODBC Drivers

ODBC is only a standard interface. The actual database communication is handled by a database-specific driver. The reliability, performance, authentication support, and TLS capabilities of your monitoring setup depend heavily on this driver.

In Linux-based Zabbix environments, three drivers are most commonly deployed and operationally proven:

* MySQL / MariaDB
* PostgreSQL
* Microsoft SQL Server

While ODBC drivers exist for many other databases, these three represent the majority of real-world Zabbix database monitoring deployments.

---

### MySQL / MariaDB

The most widely used driver in open-source environments.

Typical package names:

* `mariadb-connector-odbc` (RHEL / Rocky / Alma)
* `libmaodbc` or distribution-provided MariaDB ODBC packages

This driver supports:

* MySQL
* MariaDB
* Cloud-managed MySQL-compatible services (e.g., Amazon RDS, Azure Database for MySQL)

MariaDB Connector/ODBC is generally preferred over older MySQL ODBC drivers due to active maintenance and compatibility improvements.

---

### PostgreSQL

PostgreSQL ODBC is stable and widely used in enterprise environments.

Typical package names:

* `odbc-postgresql` (Debian / Ubuntu)
* `psqlodbc` (RHEL-based systems)

Common use cases include:

* ERP systems
* Financial systems
* High-availability PostgreSQL clusters
* Managed PostgreSQL cloud services

When monitoring PostgreSQL, ensure:

* SSL parameters are correctly defined in the DSN if required
* SCRAM authentication is supported by the installed driver version
* Certificate validation is enforced in secure environments

---

### Microsoft SQL Server (MSSQL)

Microsoft provides an official ODBC driver for SQL Server.

Typical package name:

* `msodbcsql18`

Installation usually requires enabling Microsoft’s official repository and accepting the license agreement.

Example (RHEL/Rocky-based systems):

```bash
sudo dnf install msodbcsql18
```

This driver is required for:

* On-premise Microsoft SQL Server
* SQL Server on Linux
* Azure SQL Database

Operational considerations:

* TLS encryption is often mandatory
* Kerberos or Active Directory authentication may require additional configuration
* EULA acceptance is required during installation


### FreeTDS ODBC Driver (tdsodbc) — Community Option

FreeTDS is an open-source implementation of the TDS (Tabular Data Stream) protocol used by SQL Server.

Typical package names:

* freetds
* freetds-odbc
* tdsodbc

Advantages:
* Fully open source
* Available directly from most Linux distributions
* No external vendor repository required

Limitations:
* May lag behind in TLS or encryption support
* Authentication features are more limited
* Azure SQL compatibility can be inconsistent
* Behavior may vary between versions

FreeTDS can work reliably for simple monitoring queries, but it requires careful testing before production use.

---

## ODBC Driver Packages by Operating System

The following table summarizes commonly used driver packages per platform.

| Database        | Rocky / RHEL / Alma      | Ubuntu / Debian                               |  Suse                  | Vendor Repository Required |
| --------------- | ------------------------ | --------------------------------------------- | ---------------------- | -------------------        |
| MySQL / MariaDB | `mariadb-connector-odbc` | `mariadb-connector-odbc` or distro equivalent | mariadb-connector-odbc | No                         |
| PostgreSQL      | `psqlodbc`               | `odbc-postgresql`                             | psqlODBC               | No                         |
| MSSQL           | `msodbcsql18`            | `msodbcsql18`                                 | msodbcsql18            | Yes (Microsoft repo)       |
| MSSQL           | freetds  freetds-odbc    | freetds-bin tdsodbc                           | libtdsodbc0            |                            |


---

## Driver Selection Considerations

When choosing an ODBC driver:

1. Prefer vendor-maintained drivers when available.
2. Verify compatibility with your database version.
3. Confirm support for:
   * TLS/SSL
   * Modern authentication methods
   * UTF-8 encoding
4. Test performance under realistic load before production rollout.

Not all ODBC drivers behave identically. Differences may exist in:

* Timeout handling
* Connection reuse behavior
* Encoding management
* Error reporting
* Pooling support

In production environments, the ODBC driver should be treated as a critical infrastructure
component.

???+ note:

    There are many ODBC drivers available for additional databases such as Oracle,
    Db2, SAP HANA, and others. However, driver quality, maintenance cadence, and
    production stability vary significantly. Before relying on less common drivers
    in a monitoring environment, perform controlled testing and validate behavior
    under load. Monitoring reliability depends as much on the driver as on Zabbix
    itself.

---

### Testing the DSN

Always validate connectivity before configuring Zabbix.

```bash
isql -v InventoryDB
```

If successful:

```
Connected!
```

If not, resolve driver registration, authentication, or network issues first. This saves you from the problems in Zabbix.

---

## Enabling ODBC Pollers

ODBC items require dedicated poller processes.

In `zabbix_server.conf` or `zabbix_proxy.conf`:

```
StartODBCPollers=5
```

Restart Zabbix after modification.

If this parameter is missing, ODBC items remain unsupported.

---

## Creating ODBC Items in Zabbix 8.0

Zabbix provides two database monitor item keys for ODBC-based monitoring:

* `db.odbc.select[]`
* `db.odbc.get[]`

Both keys execute SQL queries via ODBC, but they differ significantly in how results are returned and how they should be used.

---

### `db.odbc.select[]`

Syntax:

```text
db.odbc.select[<unique short description>,<dsn>,<connection string>]
```

Behavior:

* Executes the defined SQL query.
* Returns **a single value**.
* Specifically, it returns:

  * The first column
  * Of the first row
  * Of the query result set

This makes it ideal for queries that produce one scalar result.

### Example

SQL query:

```sql
SELECT COUNT(*) FROM orders WHERE status = 'pending';
```

If the result is:

```
42
```

The item stores:

```
42
```

---

#### When to Use `db.odbc.select`

Recommended for:

* Simple health checks
* Aggregate counts
* Boolean-style checks
* Replication lag values
* Single KPI metrics

It item is particularly suitable when:

* The query is complex
* The result is intentionally singular
* No further JSON processing is required

Because it returns only one value, it is straightforward and lightweight.

---

## `db.odbc.get[]`

Syntax:

```text
db.odbc.get[<unique short description>,<dsn>,<connection string>]
```

Behavior:

* Executes the SQL query.
* Returns the entire result set as a **JSON array**.

Example result:

```json
[
  {"status":"pending","total":"15"},
  {"status":"shipped","total":"120"}
]
```

Unlike `select`, this key preserves all returned rows and columns.

---

#### When to Use `db.odbc.get`

Recommended for:

* Collecting multiple metrics in one query
* Feeding dependent items
* Low-Level Discovery
* Master item designs
* Reducing database load through query consolidation

`db.odbc.get` is the preferred modern approach in Zabbix 8.0 for scalable database monitoring.

---

### Example Using `db.odbc.get`

Type: `Database monitor`
Key: `db.odbc.get[get_stats,InventoryDB]`


SQL Query:

```sql
SELECT status, COUNT(*) AS total
FROM orders
GROUP BY status;
```

Returned JSON:

```json
[
  {"status": "pending", "total": "15"},
  {"status": "shipped", "total": "120"}
]
```

Preprocessing:

1. JSONPath:

   ```
   $.[?(@.status == 'pending')].total.first()
   ```
2. Change type → Numeric (unsigned)

Database drivers often return numbers as strings; type conversion prevents trigger inconsistencies.

---

## Understanding the Parameters

Both keys share the same parameter structure:

1. **Unique short description**

   * An internal identifier.
   * Must be unique per item.
   * Does not affect execution logic.

2. **DSN**

   * The Data Source Name defined in `/etc/odbc.ini`.
   * Points to the database connection configuration.

3. **Connection string (optional)**

   * Allows overriding or extending DSN parameters.
   * Can include credentials or additional driver settings.
   * Useful when DSN-level credentials are not defined.

Example with connection string:

```text
db.odbc.select[check_users,InventoryDB,UID=zabbix_mon;PWD=secret]
```

In production environments, credentials should preferably be handled via macros or secure storage rather than hardcoded strings.

---

# Strategic Comparison

| Feature                          | `db.odbc.select`     | `db.odbc.get`                |
| -------------------------------- | -------------------- | ---------------------------- |
| Returns                          | Single scalar value  | Full result set (JSON array) |
| Suitable for                     | One metric per query | Multiple metrics per query   |
| JSON preprocessing required      | No                   | Yes                          |
| Ideal for dependent items        | No                   | Yes                          |
| Recommended for modern templates | Limited use          | Yes                          |

---

## Design Guidance

Use `db.odbc.select` when:

* You need one value.
* Simplicity is preferred.
* No discovery or dependent logic is required.

Use `db.odbc.get` when:

* You want scalability.
* You want to reduce database query count.
* You are building reusable templates.
* You are implementing LLD.
* You want to follow modern Zabbix design patterns.

In most structured deployments, `db.odbc.get` should be the default choice.

---

## Low-Level Discovery with ODBC

ODBC combined with `db.odbc.get` enables scalable Low-Level Discovery.

Example:

```sql
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'shop_db';
```

Configuration strategy:

* Master item → `db.odbc.get`
* Dependent discovery rule
* JSONPath extracts `{#TABLE}`
* Item prototypes monitor row count per table

This approach reduces database load and improves template scalability.


## Native ODBC Low-Level Discovery (`db.odbc.discovery`)

In addition to `db.odbc.select[]` and `db.odbc.get[]`, Zabbix provides a dedicated key for discovery:

```
db.odbc.discovery[]
```

This key is designed specifically for Low-Level Discovery (LLD) and returns data in the format required by Zabbix discovery rules.

While `db.odbc.get[]` can be combined with dependent items to implement scalable discovery patterns, `db.odbc.discovery[]` offers a simpler and more direct approach for structured environments.

---

### How It Works

The key format:

```
db.odbc.discovery[unique_name,DSN]
```

The SQL query must return columns that correspond to LLD macro names.

Example:

```sql
SELECT table_name AS "{#TABLE}"
FROM information_schema.tables
WHERE table_schema = 'shop_db';
```

This generates discovery data like:

```json
[
  {"{#TABLE}":"orders"},
  {"{#TABLE}":"customers"},
  {"{#TABLE}":"products"}
]
```

Each row becomes one discovered entity.

---

### When to Use `db.odbc.discovery`

Use native discovery when:

* The discovery query is lightweight.
* The returned dataset is small.
* You do not need additional processing logic.
* You prefer simplicity over maximum optimization.

It is particularly suitable for:

* Discovering database tables
* Discovering schemas
* Discovering replication slots
* Discovering logical entities with stable structure

---

### When to Prefer `db.odbc.get` + Dependent LLD

In larger environments, the preferred scalable approach is:

1. Master item → `db.odbc.get`
2. Dependent discovery rule
3. Dependent item prototypes

This approach reduces database load because:

* The SQL query executes only once.
* Multiple items reuse the same dataset.
* Poller usage is minimized.

If you use `db.odbc.discovery[]`, each discovery rule executes its own SQL query.

In small deployments, this difference is negligible.
In large-scale systems, it becomes significant.

---

## Performance Considerations for Discovery

Discovery rules execute periodically.

If a discovery query:

* Scans large metadata tables
* Executes heavy joins
* Runs too frequently

it can introduce unnecessary load.

Best practices:

* Run discovery at longer intervals (e.g., 1h or 24h)
* Keep discovery queries simple
* Avoid scanning large operational tables
* Prefer metadata sources like `information_schema`

Discovery should detect structure changes, not operational metrics.

---

## Common Mistake with `db.odbc.discovery`

A frequent error is returning columns without properly formatted LLD macros.

Incorrect:

```sql
SELECT table_name FROM information_schema.tables;
```

Correct:

```sql
SELECT table_name AS "{#TABLE}"
FROM information_schema.tables;
```

The alias must match the macro format exactly.

---

## Strategic Guidance

For production template design:

* Use `db.odbc.discovery[]` for structural discovery.
* Use `db.odbc.get[]` for scalable metric collection.
* Combine both methods when appropriate.

Discovery defines *what* exists.
Metric items define *how it behaves*.

Keeping those responsibilities separate improves template clarity and scalability.

---

## Performance and Scalability Considerations

ODBC queries execute real SQL. They consume database resources.

Best practices:

* Use indexed columns
* Avoid full-table scans
* Keep queries lightweight
* Avoid high-frequency polling unless necessary
* Test queries using `EXPLAIN`

Server-wide timeout:

```
Timeout=5
```

Slow queries block pollers and may cascade into monitoring delays.

Use proxies to isolate database monitoring from the central server.

---

##  Connection Pooling

Enable unixODBC pooling to reduce connection overhead.

In `/etc/odbcinst.ini`:

```ini
[ODBC]
Pooling = Yes
```

Pooling reduces TCP handshake and authentication overhead in high-scale environments.

---

##  Security Considerations

Never use database root accounts, always create a dedicated user with limited
permissions. Best even 1 account per application.

Create a dedicated read-only user:

```sql
CREATE USER 'zabbix_mon'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON shop_db.* TO 'zabbix_mon'@'%';
```

Recommendations:

* Use Zabbix macros for credentials
* Limit privileges strictly to SELECT
* Protect DSN files
* Consider external secret vault integration
* Restrict network exposure

Monitoring credentials must never allow modification.

---

##  Character Encoding

Ensure consistent UTF-8 configuration across:

* Database
* Operating system locale
* ODBC driver

Encoding mismatches can result in corrupted output or JSON parsing failures.

---

## Troubleshooting

Common ODBC errors:

IM002
DSN not found — verify `/etc/odbcinst.ini` and `/etc/odbc.ini`

HY000
Authentication or permission error

08001
Network connectivity issue

Increase logging:

```
LogLevel=4
```

Check:

```
/var/log/zabbix/zabbix_server.log
```

Always validate the DSN with `isql` before troubleshooting Zabbix itself.

---

##  Choosing the Right Monitoring Method

Zabbix supports multiple database monitoring approaches. This table can help you
with choosing the best approach.

| Criteria                   | ODBC      | Agent 2 Plugin |
| -------------------------- | --------- | -------------- |
| Requires agent             | No        | Yes            |
| Executes SQL directly      | Yes       | Yes            |
| Best for cloud-managed DB  | Yes       | Sometimes      |
| Risk of poorly written SQL | High      | Low            |
| Setup complexity           | Medium    | Low            |
| Business KPI monitoring    | Excellent | Limited        |
| Infrastructure metrics     | Good      | Excellent      |

### Strategic Guidance

* Use Agent 2 plugins for core database health metrics.
* Use ODBC for custom SQL and business metrics.
* Use HTTP checks for application-level validation.

In mature environments, these methods complement each other.

---

##  Production Hardening

ODBC must be deployed with discipline.

### Query Discipline

Never deploy:

* `SELECT *`
* Full table scans
* Heavy joins without indexing
* Long-running reports

Monitoring queries must be lighter than production workload.

### Poller Capacity Planning

Size `StartODBCPollers` appropriately.

Too low:

* Unsupported items

Too high:

* Database overload

Scale gradually and monitor poller utilization.

### Isolation

Offload ODBC checks to a Zabbix Proxy in medium and large environments. This prevents
database instability from affecting the central monitoring server.

### Monitor the Monitoring

When you use ODBC checks on Zabbix dont't forget to monitor you congiguration in
Zabbix. It's always a goot idea to have a look at the following metrics:

* ODBC poller busy percentage
* Queue size
* Item unsupported count
* Database execution time trends

---

## Common Anti-Patterns

Even experienced administrators fall into predictable traps. Avoid the following:

### 1. Monitoring with Reporting Queries

Using analytical queries designed for reports as monitoring checks. These queries are too heavy for frequent execution.

### 2. High-Frequency Polling of Expensive Metrics

Polling every 10 seconds when 5 minutes would suffice.

### 3. Using Root or Administrative Accounts

Monitoring accounts should never have modification privileges.

### 4. Increasing Pollers Instead of Fixing Queries

Adding pollers to mask slow SQL only increases database pressure.

### 5. Ignoring Timeouts

Failing to tune timeouts leads to blocked pollers and cascading delays.

### 6. Embedding Business Logic in SQL

Monitoring should observe systems, not replicate application logic.

### 7. Skipping DSN Testing

Configuring Zabbix without validating the DSN via `isql`.
Anti-patterns usually stem from convenience. Production systems require discipline.

---

## Conclusion

ODBC provides one of the most flexible and powerful database monitoring mechanisms
in Zabbix. It enables agentless visibility into infrastructure metrics and business
KPIs, supports scalable discovery through JSON processing, and integrates cleanly
with proxy architectures.

However, ODBC is not merely a configuration task, it is an operational responsibility.
The safety and scalability of ODBC monitoring depend entirely on:

* Query design discipline
* Proper poller sizing
* Secure credential handling
* Thoughtful timeout configuration
* Isolation through proxies
* Continuous performance validation

When used correctly, ODBC becomes a strategic observability tool. When misused,
it becomes a silent performance risk.

The difference lies not in the technology, but in the rigor of its implementation.


## Questions

## Useful URLs

- https://www.zabbix.com/forum/zabbix-help/413055-installation-and-configuration-of-mssql-by-odbc-docker
- https://blog.zabbix.com/database-odbc-monitoring-with-zabbix/8076/
- https://www.zabbix.com/documentation/7.4/en/manual/config/items/itemtypes/odbc_checks?hl=ODBC%2Cmonitoring
