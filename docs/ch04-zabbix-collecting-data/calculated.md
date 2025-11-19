---
description: |
    Simplify data analysis with Zabbix calculated items. Create formulas from existing
    metrics to generate new insights without extra load or checks.
tags: [advanced]
---

# Calculated items

As monitoring environments grow, so does the need to transform raw metrics into
meaningful, actionable information. Not every value you need exists on the host
itself. Sometimes the most important insights come from deriving new values, ratios,
differences, rates, percentages, or complex expressions combining several items.

In Zabbix, this capability is provided through calculated items. A calculated item
does not collect data from the host; instead, it produces values based on an
expression evaluated by the Zabbix server. This makes calculated items extremely
powerful for analytics, SLA reporting, performance ratios, and synthetic metrics
across multiple data sources.

In earlier Zabbix versions, calculated metrics were split into two different item
types:

- Calculated items
- Aggregate items

Both were powerful but came with inconsistent syntax and separate configuration
workflows. This led to confusion, especially when building larger monitoring
models or template driven designs.

Starting with Zabbix 7.0, these functions were unified into a single item type:
Calculated with a single expression syntax. All former aggregation logic per host,
per group, or cross group is now accessed directly through functions such as:

```bash
avg()
sum()
percentile()
grpavg()
grpsum()
groupcount()
etc.
```

This unification dramatically simplifies the platform:

- One place to create derived values
- One syntax to learn
- One template model for all calculations
- More powerful LLD integration

Zabbix 8.0 continues this streamlined approach, making calculated items a
cornerstone for building analytics, SLA metrics, and higher-level abstractions.

---

## What Are Calculated Items?

A calculated item is a an item whose value is produced entirely by the Zabbix
server. Instead of collecting external data, it uses:

- Other item values (last(), avg(), max(), etc.)
- Arithmetic operations
- Built-in functions
- Data aggregation across hosts or host groups

The formula is evaluated at a defined interval, and results are stored exactly
like any other metric.

**Calculated items are especially useful when:**

- You need ratios (e.g., CPU steal % vs. total CPU time)
- You want to convert units (bytes → megabytes)
    - can also be done with preprocessing steps.
- You want to calculate deltas (difference between two counters)
    - can also be done with preprocessing steps.
- You want to aggregate values across multiple interfaces, disks, or services
- You want to normalize data (e.g., dividing by CPU count)
- You want to create synthetic KPIs that do not exist natively

---

## Where Calculated Items Fit in the Zabbix Data Model

Calculated items are part of the broader set of Zabbix item types. They behave like:

- Dependent items (no host communication)
- Preprocessed items (transformation of raw data)
- Internal/virtual metrics (local to Zabbix)

... but with a key distinction:

The source data does not trigger an update, only the calculated item's own
interval does. This means calculated items must be configured carefully to ensure:

- Their update interval matches the freshness of source data
- Their formulas reference items that exist and return numeric values
- They do not introduce unnecessary load through excessive recalculation

---

## How to create a Calculated Item

To create a calculated item:

1. Open Data collection → Hosts → <your host> → Items
2. Click Create item
3. Set Type: Calculated
4. Define:
    - Name
    - Type: Calculated
    - Key (unique identifier)
    - Value type (Numeric, float, etc.)
    - Formula
    - Units (optional)
    - Update interval
    - History/Trend storage
5. Save the item

![ch04.60-calculated-item.png](ch04.60-calculated-item.png)

_calculated-item_

**Example Formula :**

```bash
last(/host/net.if.in[eth0]) + last(/host/net.if.out[eth0])
```

Using this in our formula would calculate the total traffic by combining traffic
in with traffic out. This will only work if we have 2 exact items like this on
our host.

Another more useful example as the item net.if.total exists for the example
above could be the calculation of the interface utilization.

```bash
( last(/host/net.if.total[eth0]) * 100 ) / last(/host/net.if.speed[eth0])
```

Again on our host we would need the item `net.if.total[eth0]` and
`net.if.speed[eth0]` for this to work.

!!! note
    Zabbix does not have an Built-in item net.if.speed but we can usually read
    the speed from network devices like switches. In Linux you could use as
    alternative method `vfs.file.contents["/sys/class/net/{#IFNAME}/speed"]
    where you replace `{#IFNAME}` with the correct interface name.

## Some good practices for Calculated items

1. **Align Update Intervals:** If your source item updates every 60 seconds, avoid recalculating every 5 seconds.
2. **Always Validate Item Existence:** If one referenced item is missing, the calculated item returns unsupported.
3. **Use Templates, Not Hosts:** Especially important when building:
    - CPU utilization ratios
    - Disk usage summaries
    - Network traffic rollups
   By using templates, calculated items become reusable and consistent across infrastructure.
4. **Use Value Type Carefully:**
    - Floating point is usually safer unless you specifically need integers.
5. **Combine with LLD (Low-Level Discovery)**
   Calculated LLD prototypes allow:
    - Per-disk KPIs
    - Per-interface utilization percentages
    - Storage pool ratios
    - Multi-core CPU computations
`
## Practical Example

### Percentile 95 Network Latency (ICMP Ping)

Why Percentiles Matter

Just like with website performance analysis, average latency can be extremely
misleading.

**Suppose :**

- 99% of all ICMP responses are 5 ms
- 1% spike to 500 ms due to congestion

The average latency still appears excellent, while users may experience intermittent
slowness. A P95 or P99 percentile immediately exposes congestion, bufferbloat,
microbursts, and jitter spikes. Percentile analysis is one of the most accurate
indicators of real network quality.

**Required Item: ICMP Response Time**

Zabbix provides a built-in Simple Check for ICMP response time (fping-based):

| Field | Value |
| ----  |----   |
| Name  | Icmpping               |
| Type  | Simple check           |
| Key   | icmppingsec[<target-IP\>] |
| Units | s                      |
| Update interval | typically 1–10 seconds |

The next step is to create our calculated item.

---

**Calculated Item: P99 Network Latency (15 minutes)**

We compute the 99th percentile over the last 15 minutes.

| Field | Value |
| ----  |----   |
| Name  | Network Latency P99 (15m) |
| Type  | Calculated |
| Key   | icmppingsec.p99 (example key) |
| Value type | Numeric (float) |
| Units | s |
| Update interval | 30–60 seconds |

**Formula:**

```bash
percentile(/<HOST\>/icmppingsec[<target-IP>],15m,99)
```

Once our item is created we can also add a trigger to the item so that we get an
alert if the network quality degrades.

```
last(/<HOST\>/icmppingsec.p99)>0.150
```

This will alert us if the P99 ping latency goes above 150 ms.

#### What This Trigger Detects

This is not a simple reachability check (up/down).
This trigger detects:

- Congestion
- Bufferbloat
- Packet-queue delays
- Bursty latency
- Intermittent slow responses
- Micro-outages impacting users

It measures quality, not availability.
Average latency might look fine, but P99 tells you:

```bash
“1% of the packets are delayed more than 150 ms — users notice this.”
or
This trigger fires if the worst latency (top 1%) over the last 15 minutes is higher than 150 ms.
```

This is far more meaningful for:

- Internet links
- VPNs
- WiFi infrastructure
- Cloud interconnects
- SD-WAN
- VoIP/Video systems

If we now go to latest data page we can take a look at our item and click on the
graph button at the end of the screen.

![ch04.61-calculated-p99.png](ch04.61-calculated-p99.png)

_p99 graph_

We now have a nice overview of the quality of our network thanks to our
calculated item.



### Troubleshooting Calculated Items

1. Unsupported Item

**Check :**

- Does the formula reference items that do not exist?
- Are value types compatible?
- Does the function return something numeric?

2. Incorrect Values

**Check :**

- Unit mismatch (bytes vs bits)
- Wrong interval compared to source data
- Missing parentheses in expression

3. No Graphs Displaying

**Ensure :**

- Value type is numeric
- Units are properly set
- History/trends retention is not zero

## Conclusion

## Questions

## Useful URLs
