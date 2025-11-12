---
description: |
    Monitor your Zabbix server and proxies using built-in health checks, templates,
    and dashboards to ensure top performance.
tags: [advanced]
---

# Zabbix internal health check

## **1. Introduction**

While Zabbix is known for monitoring infrastructure, it can also monitor itself.
Through *internal checks*, Zabbix continuously measures its own operational state
from poller load and queue length to cache usage and data throughput.

Monitoring these internal metrics allows administrators to detect overload
conditions, database bottlenecks, and sizing issues early, ensuring the monitoring
system remains reliable and performant.

---

## **2. The Zabbix Internal Host**

Each Zabbix installation automatically creates a **virtual internal host**:

* **Zabbix server** – represents the server process itself
* **Zabbix proxy** – represents each proxy instance

These hosts are not linked to any physical device or network interface.
They exist entirely within the Zabbix backend and collect self monitoring data
through *internal items* with keys beginning with `zabbix[...]`.

Examples:

```text
zabbix[process,poller,avg,busy]
zabbix[queue,all]
zabbix[wcache,values,free]
zabbix[values_processed]
```

These items require no agent or SNMP interface — they are gathered internally
by Zabbix.

---

## **3. Categories of Internal Metrics**

### **3.1 Process Performance**

Zabbix Server is a multi-process application. It relies on a dedicated set of
specialized processes such as the pollers for active data collection, trappers
for passive incoming data, and alerters for sending notifications to perform its
core duties efficiently and concurrently.

Each type of internal process reports its load via internal checks, indicating
the percentage of time it spends working versus waiting. Consistently high
utilization (approaching 100%) is a critical performance indicator, suggesting
that the configured number of processes (Start<Process>) is insufficient to handle
the current monitoring load.

If a process like the poller remains overloaded, it directly causes item collection
delays, pushing new check requests into the queue. If the alerter is overloaded,
users won't receive timely notifications about problems. Monitoring these metrics
is thus the primary way to ensure data collection and alerting remain timely.


| Example Key                             | Description                |
| --------------------------------------- | -------------------------- |
| `zabbix[process,poller,avg,busy]`       | Average poller utilization |
| `zabbix[process,trapper,avg,busy]`      | Trapper process load       |
| `zabbix[process,alerter,avg,busy]`      | Notification sender load   |
| `zabbix[process,preprocessor,avg,busy]` | Preprocessing queue usage  |

!!! tip
    If process utilization exceeds 75–80% for a sustained period, increase the
    corresponding Start<Process> parameter (e.g., StartPollers, StartAlerters)
    in zabbix_server.conf. A common bottleneck is the Housekeeper process, which
    cleans up historical data; if it is consistently busy, database performance
    will suffer significantly.

---

### **3.2 Queue Metrics**

The Zabbix internal queue is the most immediate indicator of the health of the
entire monitoring pipeline. Every item check, regardless of how it's collected,
first enters this queue before being processed, pre-processed, and eventually
written to the database.

Monitoring the queue helps to determine whether Zabbix is keeping pace with
the influx of data. If the server is functioning correctly, the total queue
length `zabbix[queue,5m]` should remain low and stable.

Zabbix categorizes queued items by their delay, providing buckets for items
waiting for more than 1 minute, 5 minutes, 10 minutes (as seen
in the internal metric `zabbix[queue,<from>,<to>]` and the `Queue overview` page).
The presence of items in these high delay queues is an immediate sign of trouble,
as it means the monitoring system is collecting stale data.

| Example Key             | Description                                |
| ----------------------- | ------------------------------------------ |
| `zabbix[queue,all]`     | Total number of items waiting for processing |
| `zabbix[queue,high,5m]` | Items delayed for more than 5 minutes        |

If the queue grows consistently, it signals that Zabbix is falling behind. The
root cause is usually one of three things: either the data collection processes
(pollers, etc.) are undersized, the database cannot accept data quickly enough
(database write bottleneck), or the network connection between Zabbix and the
database is saturated. A rapidly growing queue should trigger an immediate
investigation.

---

### **3.3 Cache and Database Performance**

Zabbix relies on multiple in memory caches to operate efficiently. The primary
goal of these caches is to minimize the load on the backend database by storing
frequently accessed data, such as host inventory, item configurations, and recent
history values. If Zabbix processes need data that isn't in memory, they must
perform expensive, synchronous database queries, severely impacting the overall
throughput.

The most critical cache is the Configuration Cache. This cache holds the entire
monitoring setup (hosts, items, triggers, etc.). Its size is governed by the
primary CacheSize parameter in the zabbix_server.conf file. Crucially, Zabbix
does not expose a direct internal item to monitor the free space or utilization
of the Configuration Cache. Its health is inferred from general server performance
issues and related log file warnings.

Other essential caches, such as the History Cache and the Trend Cache, do report
their status. These provide direct visibility into memory pressure caused by data
volume processing.

| Example Key                  | Description                                    |
| ---------------------------- | ---------------------------------------------- |
| `zabbix[wcache,values]`      | History values currently stored in write cache |
| `zabbix[wcache,values,free]` | Free space in the write cache                  |
| `zabbix[rcache,buffer,free]` | Free read-cache buffer                         |
| `zabbix[values_processed]`   | Values processed per second                    |

If the free space in the History Cache (wcache,values,free) approaches zero, or
if the queue starts growing, the Zabbix server is under memory pressure. The
critical step is to increase the relevant CacheSize parameters. Specifically,
issues with the Configuration Cache are resolved by increasing the main `CacheSize`
parameter, while data processing bottlenecks are resolved by increasing parameters
like HistoryCacheSize and TrendCacheSize.

---

### **3.4 General Statistics**

Zabbix's internal host also provides overall system information, including:

* Total number of hosts, items, and triggers
* Number of unsupported items
* Average values processed per second
* Event processing rate

These metrics are invaluable for capacity planning and performance validation.

---

## **4. Viewing Internal Metrics**

You can inspect internal checks directly via:

* **Monitoring → Latest data → Host: Zabbix server**
* **Configuration → Hosts → Zabbix server → Items**
* or through the official **Zabbix health templates** (explained below)

---

## **5. Built-in Health Templates**

Zabbix includes several templates for self-monitoring.

### **5.1 Template App Zabbix Server**

This template monitors all internal server metrics, including:

* Process utilization (pollers, trappers, alerters, etc.)
* Queue length
* Cache usage
* Values processed per second

It provides ready-to-use graphs, triggers, and dashboards to visualize Zabbix's
performance.
It is automatically linked to the *Zabbix server* host after installation.
If missing, it can be imported from:

```
/usr/share/zabbix/templates/app/zabbix_server/
```

---

### **5.2 Template App Zabbix Proxy**

This template monitors the internal state of a **Zabbix proxy**.
It includes metrics for:

* Proxy pollers and data senders
* Proxy queue and cache utilization
* Items and hosts processed by the proxy

> ⚠️ **Note:**
> Since Zabbix **7.0**, proxies are automatically monitored for *availability*
  (online/offline) out of the box.
> However, these basic checks do **not** include internal performance statistics.
> To collect proxy internal metrics, you still need to:
>
> 1. Install a **Zabbix agent** on each proxy host.
> 2. Configure that agent to be **monitored by the proxy itself** (not by the server).

Only then can the *Template App Zabbix Proxy* correctly collect proxy performance
data.

---

### **5.3 Template App Zabbix Remote**

The **Remote Zabbix Server Health** and **Remote Zabbix Proxy Health** templates
allow internal metrics to be collected by *another* Zabbix instance or a third-party system.

These templates are not related to active agents.
Instead, they expose internal statistics via the Zabbix protocol, enabling **remote supervision**
in distributed or multi-tenant environments.

Typical use cases:

* A service provider monitoring client Zabbix instances remotely
* A centralized monitoring system aggregating health data from multiple independent
  Zabbix installations
* Integration with an umbrella monitoring solution where Zabbix is not the main
  system

---

## **6. Dashboards and Visualization**

Starting from Zabbix 6.0, the **Zabbix Server Health** dashboard provides a
preconfigured visual overview of:

* Poller busy %
* Queue size
* Cache usage
* Values processed per second
* Event processing rate

You can clone or extend this dashboard to track both server and proxy performance
side by side.

---

## **7. Tuning Based on Internal Metrics**

| Problem           | Indicator                         | Recommended Action                                 |
| ----------------- | --------------------------------- | -------------------------------------------------- |
| Pollers >80% busy | `zabbix[process,poller,avg,busy]` | Increase `StartPollers`                            |
| Long queue        | `zabbix[queue,all]`               | Add more pollers, tune DB                          |
| Cache nearly full | `zabbix[wcache,values,free]`      | Increase cache parameters                          |
| Unsupported items | `zabbix[items,not_supported]`     | Fix item keys or credentials                       |
| Proxy delay       | Proxy internal metrics            | Tune `ProxyOfflineBuffer` or increase sender count |

---

## **8. Alerting on Internal Health**

Triggers can automatically warn about performance degradation.
Example:

```text
{Zabbix server:zabbix[process,poller,avg,busy].last()}>0.75
```

This will raise an event if the pollers are overloaded.
Similar triggers can be created for queues, caches, or proxy synchronization delays.

---

## Conclusion

Zabbix's internal health checks provide full insight into how the monitoring platform
itself performs.vCombined with the built-in health templates and dashboards, these
metrics help administrators:

* Detect overload and capacity issues
* Verify proxy performance
* Tune process and cache parameters
* Integrate Zabbix self-monitoring into broader enterprise systems

By keeping the Zabbix server and proxies healthy, you ensure the reliability of
every other monitored component.

---

## Questions

1. What is the purpose of the “Zabbix server” internal host?
2. Why does Zabbix 7.0+ no longer require a special setup to detect proxy availability?
3. Why must a Zabbix proxy’s agent be monitored by the proxy itself?
4. What are the key differences between “Template App Zabbix Proxy” and “Template App Zabbix Remote”?
5. Which internal metric indicates poller utilization?
6. What can cause the item queue to grow over time?
7. How can triggers help you detect Zabbix server performance problems automatically?
8. In what scenario would you use the “Remote Zabbix Server Health” template?

---

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/internal](https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/internal)

