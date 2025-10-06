---
description: |
    Learn how to configure and manage SNMP traps in Zabbix for real-time alerts, faster event detection, and efficient network monitoring.
---

# SNMP Trapping

SNMP traps are one of the most powerful features in Zabbix network monitoring.
Unlike traditional SNMP polling, which periodically queries devices for status
updates, SNMP traps deliver real-time alerts directly from network equipment
the moment an event occurs, no waiting for the next polling cycle.

In this chapter, you'll learn how to set up SNMP trap handling in Zabbix, from
installing and configuring snmptrapd to integrating it with the Zabbix server.
You'll also discover how to analyse, filter, and map incoming traps using regular
expressions, and how to link them with triggers and notifications for instant
visibility into network issues.

Whether you're monitoring switches, routers, UPS systems, or firewalls, mastering
SNMP traps in Zabbix gives you faster event detection, reduced network load, and
deeper operational insight.

## Traps versus Polling

In Zabbix, SNMP (Simple Network Management Protocol) is one of the most common
methods for monitoring network devices such as switches, routers, firewalls, and
UPS systems.
There are two main ways Zabbix can receive information from an SNMP-enabled device:

- Polling (active monitoring) See our topic SNMP Polling in Chapter 4.
- Traps (passive monitoring)

To understand the differences between trapping and polling and understand the
advantages and disadvantages lets have a quick overview:

- With SNMP polling, the Zabbix server or proxy periodically queries the device for
specific values using SNMP GET requests. For example, CPU load, interface status,
temperature ... The device responds with the current data, and Zabbix stores it
in the database.

### Polling

Polling is a client initiated and scheduled process. It is predictable, reliable,
and suitable for continuous metrics that change over time.

**Advantages:**

- Easy to control frequency and timing.
- Works even if the device doesn't support traps.
- Historical trend data is consistent.

**Disadvantages:**

- Generates more network traffic on large infrastructures.
- Delays between polls mean slower event detection.
- If a device goes down, Zabbix won't notice until the next polling cycle. (This
can be detected by using the nodata function or using "SNMP agent availability"
item but not for individual items unless every items has the nodata function and
this is also a bad idea.)


### Trapping

SNMP traps work the opposite way. The device itself sends a message (trap) to the
Zabbix system when an event occurs. For example, a power failure, link down, or
temperature alarm. Zabbix listens for incoming traps via the snmptrapd daemon
and processes them through its SNMP trap item type.

Traps are event driven and asynchronous, meaning they are sent immediately when
something happens. No waiting or polling required.

**Advantages:**

- Instant notification of important events.
- Reduces network load (no regular queries).
- Ideal for devices that push alerts rather than respond to queries.

**Disadvantages:**

- Requires external configuration (snmptrapd, scripts, log parsing).
- Not all devices send traps for all events.
- If traps are missed or misconfigured, data is lost. (Traps use UDP)

| Method | Direction | Timing | Example | Pros | Cons |
|:----   |:----      |:----   |:----    |:---- |:---- |
| Polling (Sync)  | Zabbix → Device | Periodic | SNMP GET for CPU load | Predictable, simple |Slower, more traffic |
| Polling (Async) | Zabbix → Device | Parallel | Many SNMP GETs at once | Fast, scalable | More complex tuning |
| Traps | Device → Zabbix | Event-driven | Interface down trap | Instant alerts, low load | Requires trap daemon, can miss events |

---

## SNMP Traps flow in Zabbix

``` mermaid
flowchart TB
    %% --- Polling section ---
    subgraph POLLING[SNMP Polling - Active Monitoring]
        direction LR
        ZBX[Zabbix Server or Proxy]
        DEV[Network Device]
        ZBX -->|SNMP GET UDP 161| DEV
        DEV -->|SNMP Response| ZBX
        ZBX --> DBP[Zabbix Database]
        DBP --> UI1[Zabbix Frontend]
        UI1 -->|Displays polled data| USER1[User]
    end

    %% --- Invisible separator (no box) ---
    %% This line just adds vertical space visually without rendering a node
    %% You can also remove it entirely if your renderer already adds spacing
    %% No visible element will be shown

    %% --- Traps section ---
    subgraph TRAPS[SNMP Traps - Passive Monitoring]
        direction TB
        DEV2[Network Device]
        TRAPD[snmptrapd Daemon]
        HANDLER[Trap Handler or Log File]
        ZBXT[Zabbix Server or Proxy]
        DBT[Zabbix Database]
        UI2[Zabbix Frontend]
        USER2[User]

        DEV2 -->|SNMP Trap UDP 162| TRAPD
        TRAPD -->|Handler Script| HANDLER
        HANDLER -->|Trap Log| ZBXT
        ZBXT --> DBT
        DBT --> UI2
        UI2 -->|Displays event| USER2
    end

    %% --- Styling (color-coded like before) ---
    style POLLING fill:#f0fff0,stroke:#3a3,stroke-width:1px
    style TRAPS fill:#f0f8ff,stroke:#339,stroke-width:1px
    style ZBX fill:#e0ffe0,stroke:#3a3
    style DEV fill:#ffefd5,stroke:#c96
    style DEV2 fill:#ffefd5,stroke:#c96
    style TRAPD fill:#f9f9f9,stroke:#777
    style HANDLER fill:#f0f8ff,stroke:#339
    style ZBXT fill:#e0ffe0,stroke:#3a3
    style DBP fill:#fffbe0,stroke:#996
    style DBT fill:#fffbe0,stroke:#996
    style UI1 fill:#e8e8ff,stroke:#669
    style UI2 fill:#e8e8ff,stroke:#669
    style USER1 fill:#fff0f0,stroke:#c33
    style USER2 fill:#fff0f0,stroke:#c33

```

## Setting up SNMP traps

## Testing and debugging

## Trap mapping and preprocessing


## Conclusion

## Questions

## Useful URLs
