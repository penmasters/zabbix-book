---
description: |

tags:[beginner]
---
# Using the built-in Graphs

Before you reach for a dashboard widget or start exporting data to an external
tool, Zabbix already ships with a full graphing toolkit out of the box. In
this chapter, we'll **explore the built-in graphing capabilities of Zabbix**,
starting with the zero-configuration graphs you get for free on every numeric
item, and progressively moving into **custom graphs** that you configure
yourself for specific use cases.

You'll learn the difference between simple graphs, ad-hoc graphs, and custom
graphs, when to reach for each one, and how to view them from both
**Monitoring → Latest data** and **Monitoring → Hosts**. By the end of this
chapter, you'll be comfortable building comparison graphs, combining multiple
items on a single chart, and filtering graphs by tags to quickly find what
you're looking for in a large environment.

Let's get started!

## Why built-in graphs still matter

It's tempting to skip straight to Dashboards (covered in the next chapter)
since that's where most day-to-day monitoring happens. But built-in graphs
remain useful for a few reasons:

- They require **no configuration effort** for simple graphs — every numeric
  item gets one automatically.
- They're the fastest way to do an **ad-hoc comparison** of two or three
  items without building a dashboard widget first.
- Custom graphs let you define reusable, purpose-built visualizations (for
  example, combined inbound/outbound network traffic) that can be attached to
  a host or template once and reused everywhere that host or template is
  applied.

Think of built-in graphs as your investigative toolkit, and dashboards as
your presentation layer. You'll often reach for a simple or ad-hoc graph
while troubleshooting, then formalize the useful ones into a custom graph or
a dashboard widget afterwards.

## Simple graphs

Simple graphs are the graphs you get without lifting a finger. Every numeric
item in Zabbix automatically has one.

To view a simple graph:

1. Go to **Monitoring → Latest data**.
2. Find the item you're interested in.
3. Click the **Graph** link next to it.

That's it — Zabbix immediately plots the historical data for that item. For
textual items (logs, strings), there's no graph, but you'll find a
**History** link instead, which shows the raw values.

Above the graph, you'll find the time period selector. It lets you jump to
commonly needed ranges (last hour, last 24 hours, last 7 days, and so on)
with a single click, or drag the slider to define a custom window. We'll come
back to the time period and host selectors in more detail later in this
chapter, since it's shared behavior across all graph types.

!!! tip
    If you only remember one shortcut from this chapter, make it this one:
    **Latest data → Graph** is almost always the fastest way to sanity-check
    a single metric while troubleshooting, before you even think about
    building anything more elaborate.

## Ad-hoc graphs

Simple graphs are great for a single item, but what if you want to compare
two or three items on the same chart — say, CPU load and memory usage — 
without going through the effort of configuring a custom graph first? That's
exactly what ad-hoc graphs are for.

To build an ad-hoc graph:

1. Go to **Monitoring → Latest data**.
2. Tick the checkboxes next to the items you want to compare.
3. At the bottom of the page, open the action dropdown and choose **Display
   graph**.
4. Select whether you want a **normal** graph (each item as its own line) or
   a **stacked** graph (values stacked on top of each other, useful for
   totals made up of parts).

The result is a graph built on the fly, with no configuration saved
anywhere. Close the tab and it's gone — which is exactly the point. Ad-hoc
graphs are disposable by design, meant for quick investigation rather than
long-term reuse.

!!! note
    Ad-hoc graphs can also be reached directly through a crafted URL, which
    is handy if you want to bookmark a specific comparison or link to it from
    an external tool. Multiple items are passed as `itemids[]` parameters.
    This is a lower-level mechanism most people won't need day-to-day, but
    it's worth knowing it exists if you're scripting around the Zabbix
    frontend.

## Custom graphs

When you find yourself building the same ad-hoc comparison over and over, or
when you need more control than a simple line chart offers — different line
styles, a pie chart, stacked areas with specific colors — it's time to
configure a **custom graph**.

Unlike simple and ad-hoc graphs, custom graphs are configured manually and
saved, either on a host or on a template (in which case every host using
that template inherits the graph).

### Creating a custom graph

1. Navigate to **Data collection → Hosts** (or **Templates**, if you want the
   graph to be reusable across every host the template is linked to).
2. Click **Graphs** for the relevant host or template.
3. Click **Create graph** in the upper-right corner.
4. Give the graph a descriptive name — you'll thank yourself later when
   you're scrolling through a long list of graphs.
5. Set the **Width** and **Height**, or leave them at the defaults.
6. Under **Items**, click **Add** to bring in the items you want to plot.
   - If the first item you add comes from a template, you can only add
     further items from that same template.
   - If the first item comes from a host directly, you can add items from
     any host, but no longer from templates.
7. For each item, you can set its **draw style** (line, filled region,
   staircase, and so on), color, and Y-axis side (left or right — handy when
   combining metrics with very different scales, such as latency in
   milliseconds alongside throughput in megabits).
8. Switch to the **Preview** tab at any point to see exactly what you're
   building before you save.

A common real-world example is combining `net.if.in` and `net.if.out` for a
network interface into a single graph, one drawn as a positive area and the
other inverted below the axis — instantly showing you asymmetry between
inbound and outbound traffic that would be much harder to spot in two
separate simple graphs.

### Graph types

Custom graphs support a few different chart types, selectable when you
create the graph:

- **Normal** — the standard line/area graph, most common by far.
- **Stacked** — values are stacked on top of one another, useful when the
  sum of the parts matters as much as the individual values.
- **Pie** and **Exploded** — proportional views, useful for a snapshot
  comparison (for example, disk space usage split by mount point) rather
  than a trend over time.

Choose the type based on the question you're trying to answer: *how did this
change over time* points you toward normal or stacked, while *what's the
current split* points you toward pie or exploded.

## Viewing graphs from Monitoring → Hosts

So far we've looked at graphs starting from Latest data. There's a second,
equally important entry point: **Monitoring → Hosts**, then clicking
**Graphs** for the relevant host. This view shows you both the custom graphs
configured for that host and its simple graphs, all in one place — useful
when you don't remember which items have a custom graph and which don't.

At the top of the page, the filter lets you narrow things down by host,
graph name, and a **Show** option (all graphs, host graphs only, or simple
graphs only). Note that if no host is selected in the filter, no graphs are
displayed at all — a common point of confusion for people new to this page.

Below the main filter, you'll find the **subfilter**. If your graphs are
associated with tagged entities, the subfilter shows clickable tag
name/value combinations, letting you narrow the graph list without touching
the main filter or clicking Apply. Selecting a tag highlights it and
immediately filters the results; selecting it again removes the filter.
Clicking a second tag adds it to the current selection, narrowing further.
This is one of the more underused features on this page, especially once
your tagging strategy (see the tagging section in an earlier chapter) is
consistent across hosts.

## Best practices

A few habits that will save you time as your Zabbix instance grows:

- **Name custom graphs descriptively.** "Network Traffic - eth0" is far more
  useful six months from now than "Graph 1", especially once you have
  dozens of hosts.
- **Prefer templates over per-host graphs** wherever possible. A custom
  graph defined on a template is instantly available on every host that
  template is linked to, and stays consistent as your fleet grows.
- **Reach for ad-hoc graphs first.** Don't configure a custom graph until
  you've confirmed, via an ad-hoc comparison, that it's actually a
  combination you'll want again.
- **Use tags on the underlying items**, not just on triggers. This is what
  makes the subfilter on the Monitoring → Hosts → Graphs page genuinely
  useful, rather than just another dropdown to scroll through.

## Conclusion

Built-in graphs are often overlooked in favor of dashboards, but they remain
the fastest path from "I want to see this metric" to an actual chart on your
screen. Simple graphs need no setup at all, ad-hoc graphs let you compare
items on the fly without saving anything, and custom graphs give you a
reusable, configurable visualization once you know exactly what you need.
Combined with tagging and the subfilter on the Monitoring → Hosts page,
these tools scale surprisingly well even in larger environments — and they
form a natural stepping stone toward the dashboard widgets we'll cover next.

## Questions

1. What's the key difference between a simple graph and an ad-hoc graph, and
   when would you reach for one over the other?
2. You need to compare inbound and outbound traffic on a network interface,
   with outbound plotted as a negative value below the axis. Which graph
   type and draw style settings would you use?
3. Why might you prefer to configure a custom graph on a template rather
   than directly on a host?
4. How does the subfilter on the Monitoring → Hosts → Graphs page behave
   when you click a second tag after already selecting one?
5. Why do textual items show a History link instead of a Graph link on the
   Latest data page?

## Useful URLs

- [Zabbix documentation — Simple graphs](https://www.zabbix.com/documentation/8.0/en/manual/config/visualization/graphs/simple)
- [Zabbix documentation — Ad-hoc graphs](https://www.zabbix.com/documentation/8.0/en/manual/config/visualization/graphs/adhoc)
- [Zabbix documentation — Custom graphs](https://www.zabbix.com/documentation/8.0/en/manual/config/visualization/graphs/custom)
- [Zabbix documentation — Monitoring → Hosts → Graphs](https://www.zabbix.com/documentation/8.0/en/manual/web_interface/frontend_sections/monitoring/hosts/graphs)
