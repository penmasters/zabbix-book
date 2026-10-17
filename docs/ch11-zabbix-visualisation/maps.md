---
description: |
    Learn how to create Zabbix network maps, visualize infrastructure,
    configure link indicators, and monitor network connections in real time.
tags: [beginner]
---

# Creating Maps for better overviews

Network maps give you a graphical view of your environment. Hosts, host groups,
triggers, images and even other maps are placed on a canvas, connected with
links and coloured in real time by the problems that are active at that moment.
Where a dashboard combines many small widgets, a map shows how things relate to
each other: which switch connects which servers, which rack holds which hosts,
which site depends on which link.

Maps are also the part of Zabbix that asks the most manual work. Every element
is placed by hand, every link is drawn by hand and nothing is generated from your
data. For that reason this chapter does not repeat the full configuration
reference, which the Zabbix manual describes well. It explains how maps work,
when they are the right tool and, above all, what has changed since Zabbix 7.0.

---

## Understanding Network Maps

A map is a canvas with a fixed width and height. You fill it with elements, and
an element can be a host, a host group, a trigger, an image or another map.
Each element has an icon, and the icon changes appearance when what it
represents has a problem. Elements are connected by links, and you can add shapes
and lines to give the map some structure, for example a box around all servers in
one datacenter. You manage maps under `Monitoring` | `Maps`.

!!! info "Map icons and image sizes"

    Zabbix renders network maps using SVG, but the icons placed on
    the map are raster images, such as GIF files. Unlike vector
    graphics, raster images do not scale without losing quality.

    This is why Zabbix provides several sizes of the same icons.
    When uploading custom icons, consider providing different
    sizes to ensure they remain clear on maps with different
    dimensions and display resolutions.

Maps can be public or private. A public map is visible to all users, a private
map only to its owner and to the users and groups it is shared with. In both
cases a user only sees the elements they have read permission on. Elements
without permission are shown as a grayed out icon without any text, so if a map
looks empty to a colleague, check their permissions first.

---

## Viewing a Map

Open a map from the list and you see the current state of everything on it. An
element with a problem gets a round background in the color of the problem
severity, and a thick green border appears around it when all problems are
acknowledged. A host in maintenance gets an orange square and a disabled host a
gray one. Small red triangles around an element tell you that a trigger changed
state in the last 30 minutes. Both the highlighting and the triangles are
options in the map properties, so they only appear when you have enabled them.

The title bar of a map has a dropdown to set the lowest severity that is shown.
This is a quick way to take the noise away during a busy moment. If the map
contains another map, the chosen severity is passed on when you navigate into it,
except when it is *Not classified*. Clicking an element opens a menu with the
links you configured, and clicking the host name opens the usual host menu.

A map can also be opened directly with a URL, using either the map name or the
map ID:

```
http://zabbix/zabbix/zabbix.php?action=map.view&mapname=Local%20network
```

If both parameters are present, `mapname` takes priority. This is convenient for
bookmarks and for wall screens.

---

## ## What's New Since Zabbix 7.0

The map improvements all arrived in Zabbix 7.4 and are part of 8.0. In the
release notes and API changes I found nothing new for maps in 7.2, and the
*What's new* page of 8.0 lists no map specific features. If you upgrade from 7.0
or 7.2, the following changes are the ones that matter.

The most useful one is the change to **link indicators**. A link between two
elements could already change style and color when a trigger fired. Since 7.4 a
link can also react to the value of an item. For numeric items you define
thresholds, for text items a regular expression pattern, and when the value
reaches a threshold or matches the pattern the link is drawn with the type and
color you chose for it. A link between two switches can now turn orange or red
when the utilization of the connection passes a threshold, without you having to
create a trigger for every level you want to see. If you keep using trigger based indicators and several
triggers with the same severity are assigned to one link, the trigger with the
lowest ID takes precedence.


A second change helps with readability. A busy map becomes unreadable when every
element and every link carries a label, so the map properties now offer *Auto
hide* for both *Show map element labels* and *Show link labels*. The label only
appears when you hover over the element or link, or when it is selected. The
default is still *Always*.

Background images are handled better too. The *Background scale* setting offers
*None* and *Proportionally*, and the second option, which is the default, covers
the whole map while keeping the proportions of the image. Remember that this
stretches a bitmap, so use a background image that is at least as large as the
map. You can also control the stacking order of elements now, which decides which
one is drawn on top when they overlap. That is handy when you put a small status
icon on top of a larger image, for example a photo of a rack.

Finally, support for problems in nested host groups was added for *Host group*
elements and for *Map* elements.

### Link Labels and Indicators

Links connect elements on a map and can represent physical
connections, network interfaces or logical dependencies.

Each link can have a label that describes the connection.
Labels can contain plain text and Zabbix macros, allowing
you to display information such as the interface name,
operational status or current traffic.

For example, a link between two switches could display
the current traffic and the average traffic over the last
five minutes:

    Interface: GigabitEthernet1/0/24
    Traffic in: {?last(/core-switch-01/net.if.in[ifHCInOctets.1])}
    Traffic out: {?last(/core-switch-01/net.if.out[ifHCOutOctets.1])}
    Average in: {?avg(/core-switch-01/net.if.in[ifHCInOctets.1],5m)}

Expression macros reference a specific host and item key,
using the same syntax as trigger expressions. Only the
last(), avg(), min() and max() functions are supported
in map link labels.

Link indicators provide an additional visual representation
of the connection status. They can change the link colour
and style based on triggers or item values.

For example, a link representing a network interface could
use the following thresholds:

| Interface utilization | Link colour |
|-----------------------|-------------|
| Below 70%             | Green       |
| 70% to 90%            | Orange      |
| Above 90%             | Red         |

This allows network maps to display both connection details
and current utilization without requiring a separate trigger
for every threshold.

To prevent labels from cluttering the map, Zabbix also
supports automatically hiding link labels. When enabled,
labels appear only when hovering over or selecting a link.

---

## Maps in Dashboards

A map becomes more useful when people do not have to go looking for it. The *Map*
widget embeds a map in a dashboard page, the *Map navigation tree* widget lets
users click through a hierarchy of maps, and the *Favourite maps* widget lists
the maps a user has bookmarked. All three are described in the dashboards section
of this chapter.

---

## Tips and Best Practices

Accept that maps are handwork and make it as small as possible. Clone a map
instead of starting over, use export and import to move maps between instances,
and consider the `map.create` API method if you have to build many similar maps.

Keep maps small and focused. A map with fifty elements is no longer an overview.
Create one map per site or service and connect them with *Map* elements, so that
the top level map shows with one glance where to look.

Use a map when the layout carries meaning, such as a floor plan, a rack or a
network topology. If you only need a list of problems, a *Problems* widget is
quicker, and for the location of many hosts the *Geomap* widget needs no manual
work at all.

---

## Conclusion

Maps are not the quickest visualization to build, but nothing else in Zabbix
shows layout and relations as clearly. The improvements of Zabbix 7.4, which are
part of 8.0, take away some of the pain. Links can now change color and style
based on item thresholds, independent of triggers, labels no longer clutter the
canvas and backgrounds scale in a predictable way.

## Questions

* When is a map a better choice than a dashboard?
* What can a link indicator be based on, and how does that differ for numeric and text items?
* Why do icons on a map need to be uploaded in more than one size?

## Useful URLs

* <https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/monitoring/maps>
* <https://www.zabbix.com/documentation/current/en/manual/config/visualization/maps/map>
* <https://www.zabbix.com/documentation/current/en/manual/config/visualization/maps/links>
* <https://www.zabbix.com/documentation/current/en/manual/api/changes>
