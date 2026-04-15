# Zabbix Maintenance

A monitoring system that cannot monitor itself is only half a system.

This chapter covers four operational practices that keep Zabbix reliable over
time. They are independent by nature but share a common purpose: ensuring the
platform you depend on during incidents remains healthy, recoverable, and current.

The chapter opens with **maintenance periods**, Zabbix's built-in mechanism for
suppressing alerts during planned work. A maintenance period defines a time window
and a scope for a specific hosts or host groups, during which problem notifications
can be paused. Zabbix continues collecting data throughout, but alert actions are
held back if we prefer. Maintenance periods can be scheduled as one-time windows
or recurring patterns, scoped to specific problem tags so that only relevant
alerts are suppressed, and created programmatically through the Zabbix API
to integrate with external change management workflows.

From there the chapter moves to **internal health checks**, which allow Zabbix to
monitor its own operational state. Through a set of internal items with keys
beginning with `zabbix[...]`, the server exposes metrics for process utilization,
queue depth, cache usage, and data throughput. These metrics are collected against
a virtual internal host that requires no agent or network interface. Built-in
templates and dashboards surface this data visually, and triggers can raise alerts
when process utilization climbs or queues begin to grow, giving administrators
early warning of performance degradation before it affects monitoring quality.

The third section covers **backup strategies**. Because Zabbix stores all
configuration, history, and trends in a single database, a reliable database
backup is sufficient to recover most of a Zabbix environment. The chapter covers
logical dumps using `mysqldump`, `mariadb-dump`, and `pg_dump` for smaller
installations, and physical backup approaches including WAL archiving and dedicated
tools such as PgBackRest and PgBarman for larger PostgreSQL environments. Alongside
the database, a set of configuration files and custom scripts deserve equal
attention: alert scripts, external checks, and web server configuration are easy
to overlook and time-consuming to rebuild from memory.

The chapter closes with **upgrades**, where the real complexity rarely lies in
Zabbix itself. The Zabbix server applies all missing database schema patches
automatically on startup, making it possible to upgrade directly from much older
versions without intermediate steps. What determines whether an upgrade succeeds
is the surrounding stack: the operating system, database engine, PHP version, and
any extensions such as TimescaleDB. Upgrading all of these layers simultaneously
is the most common cause of upgrade failures. The chapter examines why
migration-based upgrades are often safer than in-place upgrades, how replication
can be used to reduce downtime, and why database index health deserves explicit
attention whenever the underlying OS or database engine changes.
