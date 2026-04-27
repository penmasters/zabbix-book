---
description: |
    Monitor your Zabbix server and proxies using built-in health checks, templates,
    and dashboards to ensure top performance.
tags: [advanced]
---

# Understanding Zabbix Internal Processes and Health Monitoring

## Introduction

While Zabbix is known for monitoring infrastructure, it can also monitor itself.
Through *internal checks*, Zabbix continuously measures its own operational state,
from poller load and queue length to cache usage and data throughput. Monitoring
these internal metrics allows administrators to detect overload conditions, database
bottlenecks, and sizing issues early, ensuring the monitoring system remains reliable
and performant.

Zabbix is not a single process. It is a collection of specialized worker processes,
each responsible for a specific stage of the monitoring pipeline. At scale, performance
is rarely limited by a single factor — it depends on how well these processes keep
up with the flow of incoming data. When one part of the pipeline becomes overloaded,
visible symptoms emerge: queue growth, delayed metrics, or slow alerting.

---

## The Zabbix Internal Host

Each Zabbix installation automatically creates a **virtual internal host**:

- **Zabbix server** — represents the server process itself
- **Zabbix proxy** — represents each proxy instance

These hosts are not linked to any physical device or network interface. They exist
entirely within the Zabbix backend and collect self-monitoring data through *internal
items* with keys beginning with `zabbix[...]`.

Examples:

```text
zabbix[process,poller,avg,busy]
zabbix[queue,all]
zabbix[wcache,values,free]
zabbix[items]
```

These items require no agent or SNMP interface — they are gathered internally by
Zabbix itself.

---

## The Processing Pipeline

At a high level, Zabbix operates as a sequential pipeline:

``` text
Data collection → Preprocessing → Storage → Trigger evaluation → Alerting
```

Each stage is handled by a different group of specialized processes. Understanding
how these processes relate to each other is the key to diagnosing performance problems.
Monitoring their utilization allows you to quickly identify where bottlenecks occur.

!!! tip

    Each stage in this pipeline introduces its own scaling limits. When troubleshooting,
    the goal is not to optimize everything at once, but to identify which stage
    is currently the bottleneck.
---

## Internal Processes

### Pollers — Data Collection

Pollers are responsible for actively collecting data from monitored targets, including
agent checks, SNMP polling, and simple checks. They form the entry point of the
pipeline.

When pollers are overloaded:

- Item checks are delayed
- The queue starts growing
- Collected data becomes stale

Relevant metric: `zabbix[process,poller,avg,busy]`

!!! tip

    Sustained poller utilization above 75–80% usually indicates that more pollers are
    required (`StartPollers`), or that item design needs to be optimized.

---

### Preprocessing — The Hidden Bottleneck

Preprocessing is one of the most critical and often underestimated parts of the
Zabbix pipeline. Whenever an item uses JSONPath, XPath, regular expressions, value
mapping, or dependent items, its data is handled by preprocessing workers before
being written to the database.

In modern Zabbix environments — especially with HTTP checks, API monitoring, LLD,
or bulk SNMP/JSON collection — preprocessing becomes a central component of the
system. It is easy to overlook because the bottleneck is invisible until the queue
starts growing or trigger evaluation begins to lag.

When preprocessing is overloaded:

- Dependent items fall behind their master items
- Data appears delayed or out of order
- Trigger evaluation is postponed
- Queue growth may occur even if pollers are not overloaded

Relevant metric: `zabbix[process,preprocessor,avg,busy]`

!!! tip

    If preprocessing load is high, increasing `StartPreprocessors` is often required.
    However, reducing unnecessary preprocessing steps or simplifying expressions
    can have a larger impact than simply adding more workers.

!!! tip

    Delayed proxy synchronization introduces latency into the entire monitoring
    pipeline, even if collection on the proxy itself is functioning correctly.

---

### Trappers — Incoming Data

Trappers process incoming data pushed to Zabbix, such as active agent data, `zabbix_sender`
values, and proxy-forwarded data.

When overloaded:

- Incoming data is delayed
- Push-based monitoring becomes unreliable
- Proxy synchronization may lag

Relevant metric: `zabbix[process,trapper,avg,busy]`

---

### Alerters — Notifications

Alerters execute media types and send notifications. They are the final stage of
the pipeline after a trigger fires.

When overloaded:

- Alerts are delayed
- Escalations fail or are dropped
- Notifications may never be delivered

Relevant metric: `zabbix[process,alerter,avg,busy]`

!!! note

    Alerting delays are often mistaken for configuration problems, while the
    root cause is actually alerter saturation.

---

### Housekeeper — Data Cleanup

The housekeeper is responsible for removing outdated data from the database, including
item history and trends, events and problems, user sessions, and data from deleted
objects.

When overloaded:

- Database size grows uncontrollably
- Queries become slower
- Overall system performance degrades

Relevant metric: `zabbix[process,housekeeper,avg,busy]`

**How housekeeping works internally:** The housekeeper does not immediately delete
data when objects are removed. Instead, Zabbix creates cleanup tasks internally
and processes them in cycles. Deletion tasks are stored in the `housekeeper` table,
each referencing an object type (item, trigger, service, etc.). The housekeeper
removes related data in batches across multiple tables, limited per cycle by
configuration parameters.

This design prevents large blocking database operations, but introduces a delay
between object deletion and actual data cleanup. In large environments, deleting
many hosts or items can create a backlog of housekeeping tasks that may take multiple
cycles to complete.

> **Warning:** Setting housekeeping limits too low, or running large cleanup operations
without tuning, can lead to prolonged database growth and degraded performance.

---

### Other Important Processes

While the processes above are the most commonly observed bottlenecks, Zabbix includes
several other internal workers that play important roles:

- **History syncers**: Write collected values to the database
- **Trend syncers**: Aggregate historical data into trends
- **Escalators**: Mmanage multi-step alert escalations
- **Configuration syncers**: Distribute configuration changes across the system
- **Availability managers**: Track host and service availability

These processes are usually less visible during normal operation but can become
critical in large or complex environments.

---

## Queue Metrics

The internal queue is the most immediate indicator of the health of the entire monitoring
pipeline. Every item check, regardless of how it is collected, enters this queue
before being processed, pre-processed, and written to the database.

If the server is functioning correctly, the total queue length should remain low
and stable. Zabbix categorizes queued items by their delay, providing buckets for
items waiting more than 1 minute, 5 minutes, or 10 minutes (visible in the *Queue
overview* page). Items in these high-delay buckets are a direct sign of trouble:
the monitoring system is collecting stale data.

| Example Key           | Description                                                                 |
| --------------------- | --------------------------------------------------------------------------- |
| `zabbix[queue,0,1s]`  | Items waiting less than 1 second — the normal, immediate flow of the system |
| `zabbix[queue,10m]`   | Items delayed by at least 10 minutes — the primary indicator of a severe backlog |

If the queue grows consistently, Zabbix is falling behind. The root cause is usually
one of three things: data collection processes are undersized, the database cannot
accept data quickly enough, or the network between Zabbix and the database is
saturated. A rapidly growing queue should trigger an immediate investigation.

---

## Cache and Database Performance

Zabbix relies on multiple in-memory caches to operate efficiently. Their primary
goal is to minimize load on the backend database by storing frequently accessed
data; such as host inventory, item configurations, and recent history values.
If processes need data that is not in memory, they must perform expensive,
synchronous database queries, which severely impacts throughput.

The most critical cache is the **Configuration Cache**, which holds the entire
monitoring setup (hosts, items, triggers, etc.). Zabbix does not expose a
direct internal item for its utilization — its health is inferred from general
performance issues and log file warnings. Its size is controlled by the `CacheSize`
parameter in `zabbix_server.conf`.

Other caches, such as the **History Cache** and **Trend Cache**, do report their
status directly:

| Example Key                  | Description                                    |
| ---------------------------- | ---------------------------------------------- |
| `zabbix[wcache,values]`      | History values currently stored in write cache |
| `zabbix[wcache,values,free]` | Free space in the write cache                  |
| `zabbix[rcache,buffer,free]` | Free read-cache buffer                         |
| `zabbix[values_processed]`   | Values processed per second                    |

If free space in the History Cache (`wcache,values,free`) approaches zero while the
queue is growing, the server is under memory pressure. Increase the relevant cache
size parameters: `CacheSize` for Configuration Cache issues, and `HistoryCacheSize`
or `TrendCacheSize` for data processing bottlenecks.

---

## General Statistics

Zabbix's internal host also provides overall system information:

- Total number of hosts, items, and triggers
- Number of unsupported items
- Average values processed per second (NVPS)
- Event processing rate

These metrics are invaluable for capacity planning and performance validation
over time.

---

## Viewing Internal Metrics

Zabbix provides several ways to inspect internal checks, each serving a
different purpose:

- **Monitoring → Latest data → Host: Zabbix server**: Is the quickest way to view
live current values of every internal item. It is ideal for immediate troubleshooting,
checking recent busy percentages or confirming the current queue size. Filters
can be applied to focus on specific groups (like "Queue" or "Cache").

- **Configuration → Hosts → Zabbix server → Items**: Allows you to inspect the
item configuration itself. You can verify the exact syntax of an internal key
(e.g., `zabbix[queue,10m]`), check the collection interval, and view the full
history over long time periods — essential for diagnosing recurring or historical
issues.

- **Official Zabbix health templates**: (explained below) Offers the most complete
experience: data pre-organized into graphs, dashboards, and pre-configured alerts.
This is the standard method for proactive monitoring.

---

## Built-in Health Templates

### Template Zabbix Server Health

This template is the cornerstone of Zabbix self-monitoring. It is pre-configured
to monitor the operational health of the Zabbix server process and automatically
links to the internal *Zabbix server* host upon installation, providing immediate
visibility without any manual item creation.

It collects metrics across several critical areas:

- **Process utilization**: Tracks busy percentage for pollers, trappers, alerters,
history writers, and other components
- **Queue health**: Monitors delay windows to instantly identify whether Zabbix
is falling behind
- **Cache usage**: Provides free-space metrics for in-memory stores like the
History and Trend caches
- **Data throughput**: Tracks the rate of processed values (NVPS) for capacity
planning

The template provides ready-to-use graphs, triggers, and dashboard widgets to
visualize performance over time. If missing, it can be imported from:

[https://github.com/zabbix/zabbix/tree/master/templates/app/zabbix_server](https://github.com/zabbix/zabbix/tree/master/templates/app/zabbix_server)

---

### Zabbix proxy health

This template monitors the internal state of a **Zabbix proxy**, including:

- Proxy pollers and data senders
- Proxy queue and cache utilization
- Items and hosts processed by the proxy

!!! note

    Since Zabbix 7.0, proxies are automatically monitored for *availability* (online
    /offline) out of the box. However, these basic checks do **not** include internal
    performance statistics. To collect proxy internal metrics, you still need to:
      > 1. Install a **Zabbix agent** on each proxy host.
      > 2. Configure that agent to be **monitored by the proxy itself** (not by the server).
    
    Only then can the *Zabbix proxy health* correctly collect proxy performance data.

---

### Template Remote Zabbix Server/Proxy Health

The **Remote Zabbix server health** and **Remote Zabbix proxy health** templates
allow internal metrics to be collected by *another* Zabbix instance or a third-party
system. These templates expose internal statistics via the Zabbix protocol, enabling
remote supervision in distributed or multi-tenant environments.

Typical use cases:

- A service provider monitoring client Zabbix instances remotely
- A centralized monitoring system aggregating health data from multiple independent
Zabbix installations
- Integration with an umbrella monitoring solution where Zabbix is not the primary
system

---

## Dashboards and Visualization

Starting from Zabbix 6.0, the **Zabbix Server Health** dashboard provides a preconfigured
visual overview of poller busy percentage, queue size, cache usage, values processed
per second, and event processing rate. You can clone or extend this dashboard to
track both server and proxy performance side by side.

---

## Tuning Based on Internal Metrics

| Problem              | Indicator                              | Recommended Action                                  |
| -------------------- | -------------------------------------- | --------------------------------------------------- |
| Pollers >80% busy    | `zabbix[process,poller,avg,busy]`      | Increase `StartPollers`                             |
| Preprocessing high   | `zabbix[process,preprocessor,avg,busy]`| Increase `StartPreprocessors`, simplify expressions |
| Long queue           | `zabbix[queue,10m]`                    | Add more pollers, tune database                     |
| Cache nearly full    | `zabbix[wcache,values,free]`           | Increase `HistoryCacheSize` or `TrendCacheSize`     |
| Unsupported items    | `zabbix[items_unsupported]`            | Fix item keys or credentials                        |
| Proxy delay          | Proxy internal metrics                 | Tune `ProxyOfflineBuffer` or increase sender count  |
| Database growth      | Housekeeper busy                       | Tune housekeeping limits, investigate DB performance|

**The big picture**: Zabbix performance issues are rarely caused by a single component.
They emerge when one or more processes cannot keep up with the monitoring load.

| Symptom                | Likely Cause              | What to Check                          |
|-----------------------|---------------------------|----------------------------------------|
| Queue growing         | Pollers or DB bottleneck  | poller busy %, DB performance          |
| Data delayed          | Preprocessing overloaded  | preprocessor busy %, dependent items   |
| Alerts delayed        | Alerters overloaded       | alerter busy %                         |
| Gaps in graphs        | Proxy delay               | proxy queue / delay                    |
| DB growing fast       | Housekeeper / retention   | housekeeper busy %, retention settings |

---

## Alerting on Internal Health

Triggers can automatically warn about performance degradation before it becomes
critical. Example:

```text
Problem:   avg(/Zabbix server/zabbix[process,poller,avg,busy],10m) > {$ZABBIX.SERVER.UTIL.MAX:"poller"}
Recovery:  avg(/Zabbix server/zabbix[process,poller,avg,busy],10m) < {$ZABBIX.SERVER.UTIL.MIN:"poller"}

Where:
  {$ZABBIX.SERVER.UTIL.MAX} = 75
  {$ZABBIX.SERVER.UTIL.MIN} = 65
```

Similar triggers can be created for queues, caches, preprocessing workers, or proxy
synchronization delays. The ultimate goal is to ensure the monitoring system never
fails silently.

---

## Conclusion

Zabbix's internal health checks provide full insight into how the monitoring platform
itself performs. Combined with the built-in health templates and dashboards, these
metrics help administrators detect overload and capacity issues, verify proxy
performance, tune process and cache parameters, and integrate Zabbix self-monitoring
into broader enterprise systems.

By keeping the Zabbix server and proxies healthy, you ensure the reliability of
every other monitored component.

---

## Review Questions

1. What is the purpose of the "Zabbix server" internal host, and why does it require
no agent or SNMP interface?
2. Why does Zabbix 7.0+ still require a special setup to collect proxy *performance*
statistics, even though proxy availability is monitored out of the box?
3. Why must a Zabbix proxy's agent be monitored by the proxy itself rather than
by the server?
4. What are the key differences between the *Zabbix proxy health* and the
*Remote Zabbix Server/Proxy Health* templates?
5. Which internal metric indicates poller utilization, and at what threshold
should you act?
6. What are the three most common root causes of a growing item queue?
7. Why is preprocessing often called a "hidden bottleneck," and what symptoms
does it cause when overloaded?
8. In what scenario would you use the *Remote Zabbix Server Health* template?
9. Why does the Configuration Cache have no direct utilization metric, and how
do you infer its health?
10. How can triggers help you detect Zabbix server performance problems automatically?

---

## Useful Resources

- [Zabbix Internal Items Documentation](https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/internal)
- [Zabbix Server Health Template (GitHub)](https://github.com/zabbix/zabbix/tree/master/templates/app/zabbix_server)
