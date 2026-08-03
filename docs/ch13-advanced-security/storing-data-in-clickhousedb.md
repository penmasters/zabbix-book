---
description: |
    Learn how to configure ClickHouse for Zabbix to store history data, improve
    performance, reduce database load and scale large monitoring environments.
tags: [advanced]
---

# Storing history data in Clickhouse

Beginning with Zabbix 8, ClickHouse can be used as an external storage backend
for item history. Configuration, events, problems, audit data, and other
operational data remain in the primary PostgreSQL or MySQL database.

When an item value type is stored in ClickHouse, Zabbix does not calculate or
store trend data for that history. Long-term graphing therefore depends on retaining
sufficient raw history in ClickHouse.

For environments collecting large volumes of monitoring data, this architecture
significantly reduces load on the primary database and improves overall scalability.

In this chapter, you will install ClickHouse and configure it for use with
Zabbix 8, import the required history schema, and verify that Zabbix is successfully
storing history in ClickHouse.

## What Moves to ClickHouse — and What Doesn't

ClickHouse stores the raw item history values for the value types assigned
to the ClickHouse history provider:

- Numeric unsigned
- Numeric floating point
- Character
- Log
- Text
- JSON

The following data remains in the primary PostgreSQL or MySQL database:

- Configuration data
- Events and problems
- Audit log
- Users, sessions, actions, and operational tables
- History value types that were not assigned to ClickHouse

!!! warning "Trends are not generated"
    
    Zabbix does not calculate or store trends for history value types stored
    in ClickHouse. 
 
    This means that long-term graphs cannot fall back to hourly
    trend data after the raw history has expired. Configure a sufficiently long
    ClickHouse TTL for the period that must remain available for graphs,
    reports, and historical analysis.

```mermaid
flowchart LR
    A[Zabbix Server] -->|history values| B[(ClickHouse)]
    A -->|config, events, problems, audit| C[(Primary DB
PostgreSQL / MySQL)]
    D[Zabbix Frontend] --> C
    D -->|history queries| B
```

With that distinction in mind, let's set up the backend.

## Lab Environment

The examples in this chapter were tested using:

* Rocky Linux 9
* ClickHouse 26.6.1.1193
* Zabbix 8

## Installing ClickHouse

Begin by installing the official ClickHouse repository and packages.

```bash
dnf install -y dnf-plugins-core
dnf config-manager --add-repo https://packages.clickhouse.com/rpm/clickhouse.repo
dnf install -y clickhouse-server clickhouse-client
```

Enable the ClickHouse service so it starts automatically at boot.

```bash
systemctl enable clickhouse-server
systemctl start clickhouse-server
```

Verify that the service is running before continuing.

```bash
systemctl status clickhouse-server
```

## Configuring ClickHouse

By default, ClickHouse only listens on the loopback interface. That's fine when
Zabbix and ClickHouse run on the same host, but many environments use a dedicated
ClickHouse server or cluster instead.

Create the following configuration file:

`/etc/clickhouse-server/config.d/listen.xml`

```xml
<clickhouse>
    <listen_host>0.0.0.0</listen_host>
</clickhouse>
```

Reload the configuration by restarting ClickHouse.

```bash
systemctl restart clickhouse-server
```

## Correcting Filesystem Permissions

ClickHouse needs write access to its data directory. Incorrect ownership or SELinux
contexts are a common source of startup failures or permission errors during database
creation.

Ensure the directory has the correct ownership and permissions.

```bash
chown -R clickhouse:clickhouse /var/lib/clickhouse
chmod 0750 /var/lib/clickhouse
restorecon -Rv /var/lib/clickhouse
```

## Creating the Database

Connect to ClickHouse:

```bash
clickhouse-client
```

Create the Zabbix database:

```sql
CREATE DATABASE zabbix;
```

## Creating the Zabbix User

Create a dedicated database user for Zabbix:

```sql
CREATE USER zabbix
IDENTIFIED WITH sha256_password
BY 'zabbix';
```

Grant the required privileges:

```sql
GRANT CREATE, ALTER, DROP, INSERT, SELECT, UPDATE, OPTIMIZE
ON zabbix.* TO zabbix;
```

Exit the client and verify connectivity over HTTP:

```bash
curl -u zabbix:zabbix \
"http://127.0.0.1:8123/?database=zabbix&query=SELECT%201"
```

The command should return:

``` bash
1
```

This confirms the HTTP interface is working and the user has sufficient permissions.

## Importing the Zabbix History Schema

The Zabbix source distribution contains helper scripts that automatically create
the required ClickHouse tables.

Navigate to the ClickHouse database scripts:

```bash
cd database/clickhouse
```

Execute each schema script:

```bash
./history_schema.sh \
    --server http://127.0.0.1:8123 \
    --db zabbix \
    --user zabbix \
    --password zabbix
```

Repeat the process for the remaining history types:

``` bash
history_uint_schema.sh
history_str_schema.sh
history_text_schema.sh
history_log_schema.sh
history_json_schema.sh
```
You can also use `history_all.sh` instead of running the script one by one.

Once complete, ClickHouse will contain a separate table for every supported Zabbix
history value type.

## Configuring Retention and Partitioning

The schema generation scripts let you customize both data retention and partitioning
at creation time.

### Configuring Retention (TTL)

Each history table includes a Time-To-Live (TTL) expression that automatically
removes old history data. By default, the scripts retain history for 31
days (2,678,400 seconds).

To retain history for 90 days instead, specify:

```bash
--ttl 7776000
```

The generated table will include:

```sql
TTL clock_ns + toIntervalSecond(7776000)
```

Unlike traditional databases, ClickHouse removes expired data automatically during
background merge operations, there's no housekeeping job to schedule or monitor.

### Choosing a Partitioning Strategy

The default partitioning strategy creates one partition per day:

```bash
--partition toDate
```

Daily partitions work well for smaller installations, but can result in a very
large number of partitions over time. Larger environments generally benefit
from monthly partitions instead:

```bash
--partition toYYYYMM
```

This produces tables similar to:

```sql
ENGINE = MergeTree
PARTITION BY toYYYYMM(clock_ns)
PRIMARY KEY (itemid, clock_ns)
ORDER BY (itemid, clock_ns)
TTL clock_ns + toIntervalSecond(7776000)
```

Monthly partitions typically strike the best balance between:

* partition count
* merge efficiency
* retention management
* query performance

For most production deployments, monthly partitions combined with an appropriate
TTL are recommended.

**Example:**

```bash
./history_uint_schema.sh \
    --server http://127.0.0.1:8123 \
    --db zabbix \
    --user zabbix \
    --password zabbix \
    --ttl 7776000 \
    --partition toYYYYMM
```

## Configuring Zabbix

Edit the Zabbix server configuration file:

`/etc/zabbix/zabbix_server.conf`

Configure ClickHouse as the history provider:

```
HistoryProvider=clickhouse;value_types="uint,dbl,str,log,text,json",url=http://127.0.0.1:8123,db=zabbix,username=zabbix,password="zabbix"
```

When using ClickHouse 26.6 or another version newer than officially supported,
also set:

```
AllowUnsupportedDBVersions=1
```

Save the configuration file.

## Verifying the Configuration

Before restarting the server, validate the configuration:

```bash
zabbix_server -T
```

Restart the Zabbix server:

```bash
systemctl restart zabbix-server
```

Monitor the log:

```bash
tail -f /var/log/zabbix/zabbix_server.log
```

A successful connection produces output similar to:

```bash
retrieving history provider "clickhouse" information
history provider "clickhouse" version "26.6.1.1193"
```

At this point, newly collected history values are being written directly
to ClickHouse.

## Verifying ClickHouse

A few simple commands confirm that ClickHouse is functioning correctly.

Check the installed version:

```bash
clickhouse-client --query "SELECT version()"
```

Verify that the HTTP interface is operational:

```bash
curl http://127.0.0.1:8123/ping
```

Expected output:

```bash
Ok.
```

List the imported tables:

```sql
SHOW TABLES;
```

Expected output:

```bash
history
history_uint
history_str
history_text
history_log
history_json
```

If all six tables are present and Zabbix reports a successful connection, the
history backend is correctly configured.

## Frontend

In our frontend file `zabbix.conf.php` we also need to make some changes so that
the frontend knows where to find the history data.

`Restart PHP-FPM or Apache after modifying zabbix.conf.php if configuration caching is enabled.`

```
$HISTORY_PROVIDERS[] = [
    'types' => ['uint', 'dbl', 'str', 'log', 'text', 'json'],
    'provider' => 'clickhouse',
    'url' => 'http://127.0.0.1:8123',
    'db' => 'zabbix',
    'username' => 'zabbix',
    'password' => 'zabbix'
];
```


!!! note

    ClickHouse history storage is supported by the Zabbix server only.
    It cannot be configured as the local database or history backend of a
    Zabbix proxy.


### Important limitations

- Binary history values are not supported by ClickHouse.
- JSON arrays cannot be stored as JSON item values.
- Data stored in ClickHouse is not managed by the Zabbix housekeeper. Retention
  must be configured using ClickHouse TTL policies.
- Both the Zabbix server and the frontend must be able to connect to the ClickHouse
  server.
- Trend functions are unavailable for value types stored in ClickHouse.

## Backups

It's worth treating ClickHouse's backup strategy as a separate decision from your
primary database's backup strategy, rather than assuming they should mirror each
other.

For many organizations, raw history data is effectively disposable: it's valuable
for troubleshooting and short-term analysis, but it isn't the system of record
for configuration or for the current state of problems, that all lives in the
primary database, which still needs rigorous, tested backups. Depending on your
retention requirements and risk tolerance, ClickHouse history may warrant a
lighter-weight approach, such as periodic snapshots or simply relying on TTL-based
expiry and re-collection, rather than the same RPO/RTO targets you'd apply to
PostgreSQL or MySQL.

If you do need durable ClickHouse backups, for example, to satisfy a compliance
requirement around historical data retention — tools like `clickhouse-backup` can
perform consistent backups of MergeTree tables without stopping the server. Weigh
this against your actual retention needs before adding the operational overhead.

## Looking Ahead: Clusters and High Availability

This chapter covers a single-node ClickHouse instance, which is sufficient for many
lab and small production environments. For larger or high-availability deployments,
ClickHouse supports clustering through **ClickHouse Keeper** (for coordination),
**ReplicatedMergeTree** tables (for data redundancy across nodes), and **distributed
tables** (to query across shards transparently).

## Troubleshooting

### Frontend Shows Empty History

If graphs or Latest data do not display history after enabling ClickHouse:

- verify the `$HISTORY_PROVIDERS` configuration in `zabbix.conf.php`
- verify the frontend can reach the ClickHouse HTTP endpoint
- confirm that new history is being written to the ClickHouse tables

### ClickHouse Cannot Create Tables — Permission Denied

If ClickHouse reports a permission error such as:

``` bash
Permission denied
```

verify the ownership and SELinux contexts:

```bash
chown -R clickhouse:clickhouse /var/lib/clickhouse
restorecon -Rv /var/lib/clickhouse
```

Restart ClickHouse afterwards.

### Zabbix Cannot Connect to ClickHouse

Verify connectivity manually:

```bash
curl -u zabbix:zabbix \
"http://127.0.0.1:8123/?database=zabbix&query=SELECT%201"
```

When Zabbix and ClickHouse run on the same server, prefer `http://127.0.0.1:8123`
over a hostname, this avoids potential DNS or hostname resolution issues.

## questions



## Useful URLs

[https://clickhouse.com/docs/faq/operations/delete-old-data](https://clickhouse.com/docs/faq/operations/delete-old-data)
[https://clickhouse.com/docs/](https://clickhouse.com/docs/)
[https://www.zabbix.com/documentation/8.0/en/manual/appendix/install/clickhouse_setup?hl=ClickHouse%2Cclickhouse%2CCLICKHOUSE](https://www.zabbix.com/documentation/8.0/en/manual/appendix/install/clickhouse_setup?hl=ClickHouse%2Cclickhouse%2CCLICKHOUSE)
