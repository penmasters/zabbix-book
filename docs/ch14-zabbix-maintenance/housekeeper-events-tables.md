```
description: |
    A deep dive into the events and event_tag tables: the five event types
    Zabbix stores, how the housekeeper deletes them per source, why internal
    events can flood a large database, and how a bloated events table slows
    down the frontend and history widgets. Includes a SQL check to monitor
    table sizes from Zabbix itself, a safe batched procedure to purge internal
    events when the housekeeper falls behind, and notes on reclaiming disk
    afterwards with pg_repack and autovacuum tuning.
tags: [expert]
```

# Housekeeping, the events tables, and internal events

In small and medium installations the housekeeper quietly does its job and we
never think about it. In large environments, or after a single misbehaving
template starts generating millions of rows a day, the `events` table can grow
faster than the housekeeper can clean it. Once that happens the symptoms are
rarely obvious: the *Monitoring → Problems* page loads slowly, history widgets
on dashboards time out, autovacuum runs constantly, and in the worst case the
database server runs out of memory.

This chapter explains what actually lands in the `events` and `event_tag`
tables, how the housekeeper removes it, how to monitor table growth from
Zabbix itself, and what to do when the housekeeper can no longer keep up.

!!! info "Where this knowledge comes from"
    Much of what follows is **not part of the official Zabbix documentation**. It
    is based on operational experience running large environments and on reading
    the Zabbix server source code (event processing) and the PostgreSQL internals.
    Treat it as field-tested guidance rather than a specification: table names,
    internal behaviour, and defaults can change between versions, so verify
    against your own version before acting, and always take a backup before any
    bulk database operation.

---

## The five event types

Everything in the `events` table belongs to one of five **sources**. The
`source` column (and the related `object` column) tells us where the event
came from:

| `source` | Event source       | Generated when…                              |
|:--------:|:------------------ |:-------------------------------------------- |
|    0     | Trigger            | A trigger changes state (problem / resolved) |
|    1     | Network discovery  | A discovery rule finds/loses a host or service |
|    2     | Autoregistration   | An active agent registers itself             |
|    3     | Internal           | An item becomes *not supported*, or a trigger goes to *unknown* |
|    4     | Service            | A business service changes state             |

The `object` column refines this further. For internal events (source `3`) the
object distinguishes an **item** that became not supported (`object = 4`) from
a **trigger** that became unknown (`object = 0`) or an **LLD rule** that failed
(`object = 5`).

For most environments, trigger events (source `0`) are the meaningful signal,
and there are not many of them, perhaps a few tens of thousands per day. The
source that tends to explode is **internal** (source `3`). Every poll of a
broken item writes a *not supported* event, and every trigger that depends on
that item writes an *unknown* event right after it. A single template applied
to hundreds of hosts that polls one OID the hardware does not implement, or one
file that does not exist, can produce millions of internal events per day, all
of them noise.

!!! warning "Do not run `count(*)` on a large events table"
    It is tempting to check the split with
    `SELECT source, count(*) FROM events GROUP BY source;`, but on a table with
    tens of millions of rows that is a full sequential scan and can hurt an
    already busy server. Use the planner's estimate instead (see the *SQL check*
    further down): it reads `reltuples` and the most-common-values statistics and
    costs almost nothing. If `source = 3` dominates, you have an internal-event
    problem, not a monitoring problem.

---

## The events and event_tag tables

The events themselves live in `events`, but they are never alone:

- **`event_tag`** stores the tags attached to each event. Because a single
  event can carry many tags (inherited from the trigger, the template, and the
  host), this table is almost always **several times larger than `events`
  itself**, both in rows and in index size. It is usually the single biggest
  table in a busy Zabbix database.
- **`event_recovery`** links a problem event to its recovery event.
- **`problem`** and **`problem_tag`** hold the currently open problems and
  their tags (a working set that the frontend reads constantly).

These tables are connected by foreign keys. Deleting a row from `events`
cascades automatically to its `event_tag` and `event_recovery` rows through
`ON DELETE CASCADE`. A few references, such as the `cause_eventid` used for
problem correlation, are **not** cascaded, which matters when we purge events
manually (see below).

The practical consequence: when you delete one million internal events, you are
really deleting that plus several million `event_tag` rows and maintaining their
indexes. This is why bulk cleanup of the events tables is heavier than the row
count suggests, and why it is the housekeeper's most expensive job.

---

## How the housekeeper cleans events

The retention of events is configured under **Administration → Housekeeping**,
and crucially the *Events and problems* section has **separate storage periods
per source**: Trigger, Internal, Network discovery, and Autoregistration. The
default for internal events is short (often `1d`), while trigger events are kept
for much longer. This is deliberate: internal events are high-volume and
low-value, so Zabbix expects to throw them away quickly.

Two server parameters in `zabbix_server.conf` govern how the housekeeper runs:

- **`HousekeepingFrequency`** (default `1h`) is how often the housekeeper runs.
- **`MaxHousekeeperDelete`** (default `5000`) caps how many rows are removed per
  cycle for a given cleanup rule, so a single cycle cannot lock the database for
  too long.

For each table the housekeeper finds the rows older than the configured period
and deletes them in bounded batches. You can watch it work in the server log:

```text
housekeeper [deleted 0 hist/trends, 8560 items/triggers, 221730 events,
297920 problems, 796 sessions, 0 records in 4711.454 sec, idle for 1 hour(s)]
```

The key numbers are `events` and `problems`, and the time it took. If a cycle
runs for almost as long as `HousekeepingFrequency`, or you see the deleted
counts staying high cycle after cycle without the table shrinking, the
housekeeper is **falling behind**: it is deleting as fast as it can but new
internal events arrive faster.

!!! warning
    A housekeeper that never catches up is a symptom, not the disease. The
    disease is the rate of internal events being generated. Purging helps once,
    but unless you stop the source (see *The real fix* below) the table will
    simply fill again.

---

## Why a bloated events table hurts the frontend

It is easy to think of the events tables as write-only archives, but the
frontend reads them constantly:

- **Monitoring → Problems** queries `problem` and `event_tag` on every refresh.
  When those tables are bloated with dead rows, the `SELECT` slows down, and
  several operators opening the page at once can pile up long-running queries.
- **Item value** and **history/SVG graph** widgets on dashboards read from
  `events` (and history) to draw their data and markers. On a bloated table
  these widgets become slow or time out, which users experience as "the
  dashboard is broken".
- On PostgreSQL, a table with hundreds of millions of dead rows keeps
  **autovacuum** busy for hours and inflates planner estimates, making
  unrelated queries slower too.

In other words, an events table that has been allowed to grow unchecked does
not just waste disk; it degrades the interactive experience of the whole
product.

---

## Monitoring table sizes from Zabbix (large environments)

In a large environment you want to know the events tables are growing *before*
the frontend slows down. You can monitor this from Zabbix itself with a single
low-cost SQL check, using estimates rather than expensive `count(*)` scans.

On PostgreSQL, sizes come from the catalog and row counts from the planner's
`reltuples` estimate, both essentially free:

```sql
SELECT relname AS name,
       pg_total_relation_size(c.oid) AS bytes,
       round(c.reltuples)::bigint    AS approx_rows
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND relname IN ('events', 'event_tag', 'event_recovery', 'problem');
```

To see the per-source breakdown without scanning the table, read the
most-common-values statistics that `ANALYZE` already collects:

```sql
SELECT s.val AS source,
       round(c.reltuples * s.freq)::bigint AS approx_rows
FROM pg_class c
CROSS JOIN LATERAL unnest(
    (SELECT most_common_vals::text::int[] FROM pg_stats
       WHERE tablename = 'events' AND attname = 'source'),
    (SELECT most_common_freqs FROM pg_stats
       WHERE tablename = 'events' AND attname = 'source')
) AS s(val, freq)
WHERE c.relname = 'events';
```

Wire this into Zabbix with the **Zabbix agent 2** PostgreSQL plugin
(`Plugins.PostgreSQL.CustomQueriesPath`) or a `UserParameter`, returning the
result as JSON from a single master item. Then create dependent items that
extract each table size and each per-source row count, and add triggers such as:

- `events` table larger than a chosen ceiling,
- internal-event rows above a threshold (the housekeeper is losing the race),
- daily growth rate of `events` exceeding what the housekeeper deletes per day.

The point is to turn "the database feels slow" into a graph you can see trending
days in advance.

---

## Purging internal events when the housekeeper cannot keep up

Sometimes you inherit a database with a backlog of hundreds of millions of
internal events, far more than the housekeeper can clear at `MaxHousekeeperDelete`
rows per cycle. In that case a one-off, controlled bulk purge is appropriate.

The rules for doing this safely are:

1. **Take a backup first**, and ideally test on a copy.
2. **Delete in small batches with a commit per batch.** A single
   `DELETE` of tens of millions of rows generates enormous WAL, bloats the table
   instantly, and can take the database down. Batches of 50k–100k rows keep each
   transaction short.
3. **Clear the non-cascading references first** (`cause_eventid`), then delete
   from `events` and let `ON DELETE CASCADE` remove the `event_tag` and
   `event_recovery` children.
4. **Watch replication.** If you run replicas, pause when they fall behind.
5. **Run it close to the database** (on the DB host or as an in-cluster job),
   not over a slow remote connection.

The following is a **bash** script (not SQL) that drives `psql` in a loop,
following these rules. Run it from a shell on, or close to, the database server:

```bash
SRC=3                  # 3 = internal events
DAYS=1                 # keep the last day, delete everything older
BATCH=100000
CUTOFF=$(psql -qtAc "SELECT extract(epoch from now())::int - $DAYS*86400")

while : ; do
  out=$(psql -v ON_ERROR_STOP=1 -c "BEGIN;
    CREATE TEMP TABLE _d ON COMMIT DROP AS
      SELECT eventid FROM events
       WHERE source=$SRC AND clock < $CUTOFF
       LIMIT $BATCH;
    UPDATE problem SET cause_eventid = NULL
      WHERE cause_eventid IN (SELECT eventid FROM _d);
    DELETE FROM events
      WHERE eventid IN (SELECT eventid FROM _d);
    COMMIT;")
  n=$(echo "$out" | grep -oE 'DELETE [0-9]+' | awk '{print $2}' | tail -1)
  [ "${n:-0}" -eq 0 ] && break          # nothing left to delete
  sleep 0.1                              # let other work through
done
```

The `LIMIT` plus the loop is what makes this safe: each iteration is a short
transaction, the temporary table is dropped on commit, and the cascade keeps the
child tables consistent without us touching them directly. Adjust `SRC` and
`DAYS` to target a different source or retention.

!!! danger
    This deletes data permanently. Double-check `SRC` and the `clock` cutoff
    before running, and never point it at trigger events (`source = 0`) unless
    you really mean to discard your problem history.

---

## After the purge: reclaiming disk

Deleting rows does **not** return disk space to the operating system. PostgreSQL
marks the rows dead; the space is reused by future inserts but the files stay the
same size. After a large purge you will see the row count drop while
`pg_total_relation_size` stays flat.

To actually shrink the files:

- **`pg_repack`** rebuilds a table and its indexes online, with only brief locks,
  and returns the freed space to the OS. This is the right tool on a production
  database for `event_tag`, `events`, and `event_recovery`.
- **`VACUUM FULL`** does the same but takes an exclusive lock for the whole
  operation, which on a multi-hundred-gigabyte table means hours of downtime.
  Avoid it on production.

Two tuning notes learned the hard way:

- A plain `VACUUM` after a huge delete can run for many hours because the default
  `autovacuum_work_mem` / `maintenance_work_mem` is too small to hold all the dead
  tuple identifiers at once, forcing the vacuum to scan every index many times
  over. Raising `autovacuum_work_mem` (a few GB) lets it do a single index pass.
- A long-running vacuum holds back the oldest transaction id, which can trip the
  "oldest XID" health alert in the PostgreSQL template. That alert is usually
  cosmetic in this situation: it clears as soon as the vacuum finishes and
  releases its snapshot.

---

## The real fix is upstream

Purging and repacking treat the symptom. The lasting fix is to stop generating
internal events in the first place:

- **Do not collect what you cannot read.** Tighten low-level discovery filters so
  virtual or absent entities are never discovered, and use the *Check for not
  supported value* preprocessing step with *Discard value* for the errors you
  cannot filter out. This is covered in detail in the preprocessing section of
  [Chapter 4](../ch04-zabbix-collecting-data/preprocessing.md).
- **Use trigger dependencies for downstream noise.** A dependent trigger whose
  master is already in a problem state does **not** generate a problem event at
  all, so no row is written. This is fundamentally different from maintenance
  suppression, which still writes the event (and a row in `event_suppress`) and
  merely hides it from view. If your goal is to keep the `events` table small,
  dependencies reduce what is written; suppression does not.

Get the source rate under control and the housekeeper, on its default settings,
will keep the events tables healthy on its own.

---

## Questions

  * What is stored in the `events` table, and how do the five `source` values
    differ?
  * Why is `event_tag` usually larger than `events`, and what happens to it when
    you delete an event?
  * Where do you configure how long internal events are kept, and why is that
    period shorter than for trigger events?
  * How can you tell from the server log that the housekeeper is falling behind?
  * Why does deleting millions of rows not shrink the database on disk, and what
    do you use to actually reclaim the space?
  * Why does a trigger dependency reduce the size of the `events` table while a
    maintenance period does not?

---

## Useful URLs

  * [https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/administration/housekeeping](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/administration/housekeeping)
  * [https://www.zabbix.com/documentation/current/en/manual/config/events](https://www.zabbix.com/documentation/current/en/manual/config/events)
  * [https://github.com/reorg/pg_repack](https://github.com/reorg/pg_repack)
