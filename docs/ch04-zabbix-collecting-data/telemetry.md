---
description: |
    Set up Zabbix 8.0 APM with OpenTelemetry: configure the proxy collector and
    ClickHouse, then alert on span latency with Telemetry query items.
tags: [advanced]
---

# Application Performance Monitoring in Zabbix 8.0 with OpenTelemetry.

Until Zabbix 8.0, the platform was mainly known for solid infrastructure monitoring.
With version 8.0 it takes a clear step into application performance monitoring by
adding native support for OpenTelemetry. This chapter explains how that works,
what you need to configure on the Zabbix side, and walks through a lab you can
run yourself.

We assume you already have a working ClickHouse instance available. Setting up
ClickHouse itself is covered in Chapter 13, Advanced setup and security. For the
official item reference, see the Zabbix documentation page *Telemetry query*.

---

## How APM works in Zabbix

OpenTelemetry is an open standard that lets applications and services export three
kinds of telemetry data:

- Traces: the path a request takes through your services
- Metrics: measurements such as request duration or error counts
- Logs: structured log records

Zabbix 8.0 can receive this data and turn it into something you can view, graph
and alert on.

The data flow differs from classic Zabbix checks.

In the Zabbix proxy ingestion path, applications or an OpenTelemetry Collector send
OTLP/gRPC data to a Zabbix proxy. Its APM collector writes that data directly to
the telemetry data source (ClickHouse). An OpenTelemetry Collector may also write
telemetry to the data source without using the Zabbix proxy APM collector, provided
it is configured with a compatible exporter and schema. This alternative is mentioned
in the official APM documentation; its deployment is outside this lab. The Zabbix
server has no OTLP collector of its own:
its configuration has no APM listen parameters. The frontend reads from the telemetry
data source and shows the data under a new top-level menu called APM, with separate
views for Traces, Metrics and Logs.

If you want to create triggers or graphs from this data, you use a new item type
called *Telemetry query*. The component that monitors the host (Zabbix server or
Zabbix proxy) runs the query against the telemetry data source and stores the
result as a normal item value. From that point on you can use the full Zabbix
toolbox: triggers, actions, dashboards and escalations.

In short:

``` mermaid
flowchart TB
    APP["Applications"]
    PROXY["Zabbix Proxy<br/>APM Collector"]
    SERVER["Zabbix Server"]
    PG["PostgreSQL / TimescaleDB"]
    CH["ClickHouse"]
    UI["Zabbix Frontend"]

    APP -->|"OpenTelemetry (OTLP)"| PROXY
    PROXY -->|"Monitoring data (TCP 10051)"| SERVER
    PROXY -->|"Telemetry data (HTTP/S)"| CH
    SERVER --> PG
    UI -->|"APM queries"| CH
    UI -->|"Monitoring data"| SERVER

    classDef app fill:#e3f2fd,stroke:#1976d2,color:#0d47a1
    classDef zabbix fill:#e8f5e9,stroke:#388e3c,color:#1b5e20
    classDef database fill:#fff3e0,stroke:#f57c00,color:#e65100

    class APP app
    class PROXY,SERVER,UI zabbix
    class PG,CH database
```

Two roles are worth keeping separate:

- **Receiving OTLP in Zabbix** is supported by the proxy APM collector, not the
  Zabbix server. An external OpenTelemetry Collector can also populate the store.
- **Querying** stored telemetry with *Telemetry query* items is done by the server
  or by a proxy, depending on which one monitors the host.

If you already use ClickHouse for item history (Chapter 13), keep the two settings
apart. **HistoryProvider** is about classic item history. **TelemetryProvider**
is about OpenTelemetry traces, metrics and logs for APM. Same database product
is fine; the roles in the config are different.

---

## Architecture considerations for distributed environments

APM introduces a separate data path from ordinary proxy monitoring. In the
traditional setup, an active Zabbix proxy sends collected monitoring values to
the Zabbix server over the proxy-server connection (typically TCP 10051). With
APM enabled, the proxy's APM collector instead writes telemetry **directly to
its configured ClickHouse data source**. Raw traces, metrics and logs are not
forwarded through the ordinary proxy-server protocol. A *Telemetry query* item
is different: its resulting item value follows the normal Zabbix monitoring path.

``` mermaid
flowchart TB
    subgraph Traditional["Traditional Zabbix Monitoring"]
        direction TB
        SPACE1[" "]
        P1["Customer Proxy"]
        S["Zabbix Server"]
        DB["History Storage"]

        P1 -->|"TCP 10051"| S
        S --> DB
    end

    subgraph APM["Application Performance Monitoring"]
        direction TB
        APP["Application"]
        P2["Customer Proxy<br/>APM Collector"]
        CH["ClickHouse<br/>Telemetry Store"]
        UI["Zabbix Frontend"]
        Q["Telemetry Query Poller"]

        APP -->|"OTLP/gRPC (4317)"| P2
        P2 -->|"ClickHouse HTTP(S)"| CH
        UI -->|"HTTP(S)"| CH
        Q -->|"HTTP(S)"| CH
    end

    Traditional ~~~ APM

    classDef proxy fill:#e8f5e9,stroke:#388e3c,color:#1b5e20
    classDef storage fill:#fff3e0,stroke:#f57c00,color:#e65100
    classDef server fill:#e3f2fd,stroke:#1976d2,color:#0d47a1

    class P1,P2 proxy
    class DB,CH storage
    class S,UI,Q server
```
The ClickHouse endpoint can be remote or local to the proxy: the documented
`TelemetryProvider` configuration accepts an HTTP(S) URL, including `localhost`.
For a central APM deployment, each proxy that ingests telemetry must therefore
be able to reach the selected ClickHouse endpoint. This matters for MSPs and
other environments where proxies run behind customer firewalls: the usual
proxy-server connection alone is not sufficient for APM ingestion.

A local ClickHouse instance avoids the proxy-to-central-ClickHouse write path,
but it does **not** automatically replicate raw telemetry to a central store.
The central frontend or query component would need access to the relevant data
source, or an independently designed replication/forwarding solution. Running
ClickHouse locally is not a replacement for the proxy's ordinary database:
Zabbix explicitly does not support ClickHouse for proxy history storage.

An external OpenTelemetry Collector can write to the telemetry data source
instead of the Zabbix proxy. This can centralize ingestion, but the application
or customer-side collector still needs a network path to that ingestion service.
It does not turn OTLP traffic into the existing Zabbix proxy-server protocol.

Plan TLS, access control, retention, availability and network reachability for
this separate pipeline. The Zabbix documentation also notes that the Zabbix
housekeeper does not remove ClickHouse data; configure retention in ClickHouse.

---

## Setting up the Zabbix side

### 1. Proxy configuration (for collecting OTLP data)

On the proxy that will receive OpenTelemetry traffic, create `/etc/zabbix/zabbix_proxy.d/telemetry.conf`:

```conf
StartAPMCollectors=1
APMListenPort=4317
TelemetryProvider=clickhouse;url=http://clickhouse.example.com:8123,db=zabbix,username=zabbix,password=your_password
```

- `StartAPMCollectors=1` starts the APM collector. The range is 0–1; the default
  is 0, so collection is off until you set this.
- `APMListenPort` is the port the collector listens on. `4317` is the usual OpenTelemetry
  OTLP/gRPC port. If you omit `APMListenIP`, the collector listens on all interfaces
  (default `0.0.0.0`). Set `APMListenIP` only when you want to bind to specific addresses.
- `TelemetryProvider` is a single parameter in the form `clickhouse;` plus
  comma-separated options (`url`, `db`, `username`, `password`, and optional TLS
  options). On the proxy it is both the destination for the APM collector and the
  source for any *Telemetry query* items that this proxy executes.

Restart the proxy after the change.

For incoming OTLP over TLS, use the proxy parameters `APMTLSCAFile`, `APMTLSCertFile`
and `APMTLSKeyFile` as described in the official proxy parameter list.

For a TLS connection from the proxy to ClickHouse, use the `ssl_*` options on the
`TelemetryProvider` line, together with the global SSL location parameters
(`SSLCertLocation`, `SSLKeyLocation`, `SSLCALocation`) where your package expects
them.

To store credentials in Vault instead of the config file, set `vault_path` on the
provider line. That path replaces **both** `username` and `password`. It only works
if the Vault-related parameters on that same component are configured.

In the frontend, open **Administration → Proxies**, select the proxy and use the
**APM** tab to enable data collection. Depending on your version, this tab may
also expose rate limits and resource attributes (for example `environment=lab`).
Resource attributes attached here are useful later in *Telemetry query* conditions.

---

### 2. Global data source

Go to **Administration → Data source** and enable the global telemetry data source.
Point it at ClickHouse. The frontend uses this for the APM views (Traces, Metrics,
Logs). Configure it so that what you see in the UI matches the store your proxy
writes to.

---

### 3. Telemetry query on server or proxy

*Telemetry query* items are executed by the component that monitors the host.

`StartTelemetryQueryPollers` defaults to **1** on both server and proxy. Items
are therefore polled without an extra change in a normal install. Raise the
value only if you run many *Telemetry query* items and need more parallel workers.
Check that it is not set to `0` if queries never run.

On the **Zabbix server**, there is no APM collector. For *Telemetry query* items
monitored by the server, configure `TelemetryProvider` in `zabbix_server.conf`
so the server can read from ClickHouse:

```conf
TelemetryProvider=clickhouse;url=http://clickhouse.example.com:8123,db=zabbix,username=zabbix,password=your_password
```

On a **proxy** that both collects OTLP and monitors hosts with *Telemetry query*
items, the same `TelemetryProvider` line already covers write (collector) and
read (query pollers).

---

## Telemetry query items in brief

A *Telemetry query* item asks the telemetry data source for a slice of data and
returns the result as a normal item value.

Important parameters:

| Parameter | What it does |
|-----------|--------------|
| **Category** | Traces, Metrics or Logs |
| **Metric points** | Only for Metrics: Sum, Gauge, Histogram or Exponential histogram |
| **Columns** | Raw columns to include in the result as-is |
| **Aggregated columns** | Calculate a value with min, max, avg, count, sum or percentile. For percentile, set **Percentage**. Set an **Alias** for each calculated value. **count** does not need a column |
| **Conditions** | Filter records. Operators such as Equals are case-sensitive. For key-value columns, set **Attribute key** as well |
| **Type of calculation** | And/Or, And, Or, or a custom expression when you have two or more conditions |
| **Granularity** | Length of each piece the full time range is split into (for example `1m`) |
| **Time shift** | How far before “now” the query’s time range ends (for example `2m`). That is why the first value often appears only after one or two minutes |
| **Lookback limit** | How far back to look when there is no previous query (first run) or when the previous query is older than the update interval. It is not a window that keeps returning values after traffic stops. A large lookback on a busy data source (for example more than a million records per hour) can hurt performance |

For **Traces**, columns you will use often include:

| Column | Columns | Aggregated columns | Conditions |
|--------|---------|--------------------|------------|
| Duration | ✓ | ✓ | – |
| ServiceName | ✓ | – | ✓ |
| SpanName | ✓ | – | ✓ |
| StatusCode | ✓ | – | ✓ |
| SpanAttributes | ✓ | – | ✓ |
| ResourceAttributes | ✓ | – | ✓ |
| ParentSpanId | ✓ | – | ✓ |
| TraceId / SpanId | ✓ | – | ✓ |
| Timestamp | ✓ | ✓ | – |

Similar sets exist for Metrics and Logs. They follow the OpenTelemetry ClickHouse
exporter schema. Full lists are in the official *Telemetry query* documentation.

**Type of information** is the type of the value after preprocessing. If you keep
the raw JSON, use Text. If you extract a number with JSONPath (and optionally
a multiplier), set Numeric (float) directly.

When a host moves to another proxy (for example in a proxy group), the item may
no longer know where the previous query ended. That can produce duplicate values.
Be aware of this in highly available proxy setups.

---

## Lab: generate traces and alert on span latency

This lab is meant to be followed end to end. You do not need a real application.
You generate sustained OpenTelemetry traffic, confirm it in Zabbix, build one
*Telemetry query* item, and add a trigger.

---

### Prerequisites

- Proxy with `StartAPMCollectors=1`, `APMListenPort` and `TelemetryProvider` set,
and the proxy restarted
- Global data source configured for the frontend APM views
- Host monitored by a server or proxy that has `TelemetryProvider` set for queries
(and `StartTelemetryQueryPollers` not set to 0)
- Network access to the proxy's APM listen port and from the proxy to ClickHouse

---

!!! note "IMPORTANT BEFORE YOU START"

    At the time of writing only RedHat 10 had support for APM in the proxy
    packages and needed EPEL for the installation. Proxies where not able to
    create the needed structure in the ClickHouse database and no SQL files where
    provided by Zabbix.

    This script should help you fix the ClickHouse database:

    ```
    cat otel_traces.sql
    CREATE TABLE IF NOT EXISTS zabbix.otel_traces
    (
        Timestamp DateTime64(9),
        TraceId String,
        SpanId String,
        ParentSpanId String,
        TraceState String,
        SpanName String,
        SpanKind String,
        ServiceName String,
        ResourceAttributes Map(String,String),
        ScopeName String,
        ScopeVersion String,
        SpanAttributes Map(String,String),
        Duration Int64,
        StatusCode String,
        StatusMessage String,
        `Events.Timestamp` Array(DateTime64(9)),
        `Events.Name` Array(String),
        `Events.Attributes` Array(Map(String,String)),
        `Links.TraceId` Array(String),
        `Links.SpanId` Array(String),
        `Links.TraceState` Array(String),
        `Links.Attributes` Array(Map(String,String))
    )
    ENGINE = MergeTree()
    PARTITION BY toYYYYMM(Timestamp)
    ORDER BY (ServiceName, Timestamp, TraceId, SpanId)
    TTL toDateTime(Timestamp) + INTERVAL 30 DAY;
    ```

### Step 1: Generate sustained baseline traces

A practical way to produce traffic is the OpenTelemetry `telemetrygen` tool. Install
with Go, or run a container image if you prefer not to install Go on the lab machine.

Pin the version you have actually tested in your environment, for example:

```bash
go install github.com/open-telemetry/opentelemetry-collector-contrib/cmd/telemetrygen@v0.120.0
```

Container alternative (tag to the same version you trust):

```bash
docker run --rm ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen:0.120.0 \
  traces --help
```

A short burst is not enough for stable buckets or for an `avg(...,3m)` trigger.
Use `--rate` and `--duration`.

Baseline (about 200 ms per span), several minutes:

```bash
telemetrygen traces \
  --otlp-endpoint zabbix-proxy.example.com:4317 \
  --otlp-insecure \
  --service checkout \
  --rate 5 \
  --duration 5m \
  --child-spans 2 \
  --span-duration 200ms
```

Each trace has a root span plus child spans. **Duration is measured per span**,
not per whole trace.

`--otlp-insecure` is for a closed lab only. In production, drop it and configure
TLS on both the client and the proxy (`APMTLS*` parameters).

---

### Step 2: Add datasources in the Administration

In the frontend go to **Data source** | **APM**

- select "Enable global data source"
- URL: Add the ClickHouse url Ex: http://127.0.0.1:8123

---

### Step 3: Confirm data in the APM menu

In the frontend go to **APM → Traces**.

- Set the time period to the last 15 or 30 minutes
- Filter on ServiceName = `checkout`

You should see traces and be able to open spans. If the list stays empty, check:

- Proxy log for APM collector messages
- That `StartAPMCollectors=1` is set and the proxy was restarted
- That `TelemetryProvider` on the proxy points at the ClickHouse instance you expect
- That **Administration → Data source** points the frontend at the same store
- Firewall and connectivity to the APM listen port

---

### Step 4: Create a host for the item

Create a host, for example `otel-lab`, monitored by the server or proxy that should
run the *Telemetry query*. No agent is required for this item type.

---

### Step 5: Create the Telemetry query item

On `otel-lab` create an item:

| Field | Value |
|-------|-------|
| Name | Checkout span p95 duration |
| Type | Telemetry query |
| Key | `telemetry.checkout.p95` |
| Category | Traces |
| Aggregated columns | percentile of Duration, Percentage 95, Alias `p95`<br>avg of Duration, Alias `avg`<br>count, Alias `cnt` |
| Conditions | Type `ServiceName`, Operator Equals, Attribute value `checkout` |
| Granularity | 1m |
| Time shift | 2m |
| Lookback limit | 15m (keep this modest) |
| Update interval | 1m |
| Type of information | Numeric (float), after preprocessing |
| Units | ms |

Open the item, use **Test → Get value**, and copy the real JSON you receive. Build
JSONPath preprocessing from that payload (for example extract the `p95` field).
If Duration is in nanoseconds, add a multiplier such as `0.000001` to store milliseconds.

With the baseline still running, wait for **Time shift** and **Granularity**. After
one or two minutes you should see values around the baseline span duration. That
gives the item history before you raise latency.

Optional: one master *Telemetry query* item that returns the full JSON, plus
**dependent items** with JSONPath for `p95`, `avg` and `cnt`, so ClickHouse is
queried once per interval.

If you add a second condition (for example ResourceAttributes with Attribute key
`environment`), set **Type of calculation** to And/Or or a custom expression.

---

### Step 6: Create a trigger and raise latency

Prefer a short average over a single `last()` sample, and add a check for missing data:

```
avg(/otel-lab/telemetry.checkout.p95,3m)>500
```

```
nodata(/otel-lab/telemetry.checkout.p95,10m)=1
```

When the baseline run finishes, or after you stop it with Ctrl-C, start a slower
sustained run. Keep it long enough to fill several 1m buckets under **Time shift**
(at least about 10 minutes is a practical target):

```bash
telemetrygen traces \
  --otlp-endpoint zabbix-proxy.example.com:4317 \
  --otlp-insecure \
  --service checkout \
  --rate 5 \
  --duration 10m \
  --child-spans 2 \
  --span-duration 600ms
```

Do not mix baseline and slow traffic in the same minutes if you want a clean rise
above 500 ms. After enough slow buckets, the 3m average should be able to cross
the threshold. For the `nodata()` trigger, stop all generators and confirm in
Problems whether the item goes silent within the window you configured.

---

### Step 7: Clean up

Stop generating traffic. Disable or remove the lab host and items when you are
finished. *Lookback limit* only defines how far back the first query (or a query
after a long gap) may read; it does not keep inventing values after traffic stops.

---

### What this lab proves

- The proxy APM collector accepts OTLP traffic and stores it via `TelemetryProvider`
- Traces are visible under APM → Traces
- A *Telemetry query* item can aggregate span Duration filtered by ServiceName
- Triggers can use that item when traffic is sustained long enough to fill several buckets

From here you can point a real application or an OpenTelemetry Collector at the
same proxy endpoint and reuse the same pattern with your own service names, span
names and resource attributes.

---

## Closing thoughts

APM in Zabbix 8.0 is not a full replacement for every specialised commercial
platform, but it provides a way to combine infrastructure monitoring with application
telemetry. The proxy collector, ClickHouse-backed telemetry data source and
*Telemetry query* item provide a path from OpenTelemetry data to alerts and dashboards.
Unlike traditional proxy monitoring, however, raw telemetry uses a separate ingestion
and storage path. In distributed environments, especially MSP deployments, verify
network access to the telemetry store or collector before adopting this design.

---

## Questions

- What is the role of OpenTelemetry in Zabbix 8.0, and which types of telemetry
data does it support?

- Why is a Zabbix proxy required to receive OpenTelemetry data, and can the Zabbix
server receive it directly?

- What additional network requirements should be considered when enabling APM on
proxies deployed at remote sites?

- What is the purpose of a Telemetry query item, and how can its results be used
in triggers and dashboards?
---

## Useful URLs

- [https://www.zabbix.com/documentation/8.0/en/manual/config/items/itemtypes/telemetry_query](https://www.zabbix.com/documentation/8.0/en/manual/config/items/itemtypes/telemetry_query)
- [https://www.zabbix.com/documentation/8.0/en/manual/config/templates_out_of_the_box/otlp](https://www.zabbix.com/documentation/8.0/en/manual/config/templates_out_of_the_box/otlp)
- [https://www.zabbix.com/documentation/8.0/en/manual/appendix/install/clickhouse_setup](https://www.zabbix.com/documentation/8.0/en/manual/appendix/install/clickhouse_setup)
- [https://opentelemetry.io/docs/specs/otlp/](https://opentelemetry.io/docs/specs/otlp/)
- [https://opentelemetry.io/docs/what-is-opentelemetry/](https://opentelemetry.io/docs/what-is-opentelemetry/)
- [https://opentelemetry.io/docs/collector/](https://opentelemetry.io/docs/collector/)
