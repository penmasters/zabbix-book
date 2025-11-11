---
description: |
    Monitor your Zabbix server and proxies using built-in health checks, templates,
    and dashboards to ensure top performance.
tags: [advanced]
---

# Zabbix internal health check

## **1. Introduction**

While Zabbix is known for monitoring infrastructure, it can also monitor itself.
Through *internal checks*, Zabbix continuously measures its own operational state — from poller load and queue length to cache usage and data throughput.

Monitoring these internal metrics allows administrators to detect overload conditions, database bottlenecks, and sizing issues early, ensuring the monitoring system remains reliable and performant.

---

## **2. The Zabbix Internal Host**

Each Zabbix installation automatically creates a **virtual internal host**:

* **Zabbix server** – represents the server process itself
* **Zabbix proxy** – represents each proxy instance

These hosts are not linked to any physical device or network interface.
They exist entirely within the Zabbix backend and collect self-monitoring data through *internal items* with keys beginning with `zabbix[...]`.

Examples:

```text
zabbix[process,poller,avg,busy]
zabbix[queue,all]
zabbix[wcache,values,free]
zabbix[values_processed]
```

These items require no agent or SNMP interface — they are gathered internally by Zabbix.

---

## **3. Categories of Internal Metrics**

### **3.1 Process Performance**

Each type of internal process (poller, trapper, alerter, etc.) reports how busy it is.
Consistently high utilization indicates that the configured number of processes may be too low.

| Example Key                             | Description                |
| --------------------------------------- | -------------------------- |
| `zabbix[process,poller,avg,busy]`       | Average poller utilization |
| `zabbix[process,trapper,avg,busy]`      | Trapper process load       |
| `zabbix[process,alerter,avg,busy]`      | Notification sender load   |
| `zabbix[process,preprocessor,avg,busy]` | Preprocessing queue usage  |

**Tip:**
If process utilization exceeds 75–80% for a sustained period, increase the corresponding `Start<Process>` parameter (e.g. `StartPollers`, `StartAlerters`) in `zabbix_server.conf`.

---

### **3.2 Queue Metrics**

Queue metrics indicate whether Zabbix is keeping up with data collection.

| Example Key             | Description                                  |
| ----------------------- | -------------------------------------------- |
| `zabbix[queue,all]`     | Total number of items waiting for processing |
| `zabbix[queue,high,5m]` | Items delayed for more than 5 minutes        |

If the queue grows consistently, Zabbix is falling behind — typically due to database performance, too few pollers, or overloaded networks.

---

### **3.3 Cache and Database Performance**

Zabbix relies on multiple in-memory caches to minimize database load.
If these caches fill up, Zabbix must query the database more frequently, impacting performance.

| Example Key                  | Description                                    |
| ---------------------------- | ---------------------------------------------- |
| `zabbix[wcache,values]`      | History values currently stored in write cache |
| `zabbix[wcache,values,free]` | Free space in the write cache                  |
| `zabbix[rcache,buffer,free]` | Free read-cache buffer                         |
| `zabbix[values_processed]`   | Values processed per second                    |

If cache free space approaches zero, increase the relevant `CacheSize` parameters (e.g. `HistoryCacheSize`, `TrendCacheSize`).

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

It provides ready-to-use graphs, triggers, and dashboards to visualize Zabbix's performance.
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
> Since Zabbix **7.0**, proxies are automatically monitored for *availability* (online/offline) out of the box.
> However, these basic checks do **not** include internal performance statistics.
> To collect proxy internal metrics, you still need to:
>
> 1. Install a **Zabbix agent** on each proxy host.
> 2. Configure that agent to be **monitored by the proxy itself** (not by the server).

Only then can the *Template App Zabbix Proxy* correctly collect proxy performance data.

---

### **5.3 Template App Zabbix Remote**

The **Remote Zabbix Server Health** and **Remote Zabbix Proxy Health** templates allow internal metrics to be collected by *another* Zabbix instance or a third-party system.

These templates are not related to active agents.
Instead, they expose internal statistics via the Zabbix protocol, enabling **remote supervision** in distributed or multi-tenant environments.

Typical use cases:

* A service provider monitoring client Zabbix instances remotely
* A centralized monitoring system aggregating health data from multiple independent Zabbix installations
* Integration with an umbrella monitoring solution where Zabbix is not the main system

---

## **6. Dashboards and Visualization**

Starting from Zabbix 6.0, the **Zabbix Server Health** dashboard provides a preconfigured visual overview of:

* Poller busy %
* Queue size
* Cache usage
* Values processed per second
* Event processing rate

You can clone or extend this dashboard to track both server and proxy performance side by side.

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

Zabbix's internal health checks provide full insight into how the monitoring platform itself performs.
Combined with the built-in health templates and dashboards, these metrics help administrators:

* Detect overload and capacity issues
* Verify proxy performance
* Tune process and cache parameters
* Integrate Zabbix self-monitoring into broader enterprise systems

By keeping the Zabbix server and proxies healthy, you ensure the reliability of every other monitored component.

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
