# Monitoring Windows

Monitoring a Windows host with Zabbix means installing the Zabbix agent (or agent 2) on the host and then leaning on a handful of Windows-specific item keys that give you access to data sources unique to the platform: performance counters, the Windows Event Log, the Service Control Manager, and WMI. None of this is exotic or new — these item keys have existed for a long time and the underlying Windows interfaces (Perflib, the event log API, WMI) haven't fundamentally changed either. What this chapter focuses on is putting those pieces together correctly.

## Getting the agent onto the host

Zabbix agent 2 is the recommended choice for new Windows installs. All item keys available on the classic C agent are also available on agent 2, including the Windows-specific ones covered in this chapter, so there's no functional gap to worry about.

The agent ships as an MSI package, which makes unattended installs straightforward. A typical silent install looks like:

```
msiexec /qn /i zabbix_agent2-8.0.0-windows-amd64-openssl.msi ^
  SERVER=10.0.0.1 ^
  SERVERACTIVE=10.0.0.1 ^
  HOSTNAME=WIN-DC01 ^
  ENABLEPATH=1
```

`SERVER` controls who is allowed to perform passive checks against the agent; `SERVERACTIVE` is where the agent sends active check data. `HOSTNAME` must match the host name configured in the Zabbix frontend exactly — this is the single most common cause of "host shows as unreachable but the service is clearly running" support tickets. `ENABLEPATH=1` adds the agent's install directory to the system `PATH`, which is convenient if you ever need to run `zabbix_agent2.exe -t <key>` from a command prompt to test an item key directly on the host — and you will want to do that, repeatedly, while working through this chapter.

The agent installs as a Windows service ("Zabbix Agent 2"), and its configuration file lives at `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf` by default. If something isn't working, the agent's own log file (path set by `LogFile` in that conf, typically alongside it) is the first place to look — it will tell you plainly if a key is unsupported, if a WMI query failed, or if TLS negotiation with the server is failing.

One firewall note: passive checks arrive on TCP 10050 (inbound to the Windows host), while active checks are initiated by the agent itself toward the server on TCP 10051 (outbound from the Windows host). Get this backwards and items will simply sit at "no data" with nothing obviously wrong in the agent log.

With the agent running and talking to the server, the rest of this chapter is about using three Windows-specific capabilities: performance counters, the event log, and service/WMI queries.

## Performance counters

Windows exposes a huge amount of system and application telemetry through Perflib — the same data source behind `perfmon` and `typeperf`. The Zabbix agent talks to this interface directly through two item keys: `perf_counter` and `perf_counter_en`.

The difference between the two matters more than it might first appear. `perf_counter` uses the counter names as they're localized on the host — on a Dutch-language Windows install, the processor object might be named something other than "Processor". `perf_counter_en` always uses the English counter names regardless of the host's locale, which is what you want for any template that's meant to be reusable across hosts. There's no reason to use `perf_counter` over `perf_counter_en` unless you're working with a counter that genuinely has no English equivalent — which in practice is rare.

A worked example: monitoring total CPU time as a performance counter rather than via the generic `system.cpu.util` key (useful when you want to match exactly what an admin sees in Task Manager, or when you're after a more specific counter that doesn't have a dedicated cross-platform key):

```
perf_counter_en["\Processor(_Total)\% Processor Time"]
```

The counter path syntax is `\<object>(<instance>)\<counter>`. `_Total` is the instance name Windows uses for the aggregate across all logical processors. If you need a specific core instead, the instance becomes the core index, e.g. `\Processor(0)\% Processor Time`.

If you're not sure what a counter is called, don't guess — open `perfmon` on the target host, add a counter through its UI, and read the exact object/instance/counter names from there. Alternatively, `typeperf -q` from a command prompt on the host will dump the full list of available counters in the host's local language, and on Windows Server 2008/Vista and later you can rely on `perf_counter_en` to give you the English names without needing a separate lookup.

One practical note for a book aimed at people coming from Linux monitoring: on Windows, "a counter doesn't exist" and "a counter exists but currently has no instances" are different failure modes, and both will surface as the item going unsupported. If a service-specific counter set (e.g. for IIS or SQL Server) isn't showing up, check first whether that service's performance counter category was actually registered — this is a Windows-side issue, not a Zabbix one, and usually means reinstalling or repairing the counters for that component (`lodctr` is the relevant Windows tool, though this is squarely outside Zabbix's remit and won't be covered further here).

## Event log monitoring

The Windows Event Log is arguably the most Windows-specific — and most valuable — thing covered in this chapter. Almost every "is something wrong with this server" question an admin asks ultimately comes down to "did an error get logged somewhere," and Zabbix can watch the event log natively without shelling out to anything.

The item key is `eventlog`, and it requires the item type **Zabbix agent (active)** — this is not optional; event log monitoring does not work as a passive check. The full syntax is:

```
eventlog[name,<regexp>,<severity>,<source>,<eventid>,<maxlines>,<mode>]
```

Only `name` (the log name, e.g. `Application`, `System`, `Security`) is mandatory; everything else is an optional filter. A few worked examples that illustrate how the filters combine:

**Watch the System log for any Warning or Error entries:**
```
eventlog[System,,"Warning|Error"]
```
The `severity` parameter is a case-insensitive regular expression matched against the severity values Windows reports: Information, Warning, Error, Critical, and Verbose (the latter two only on Vista/Server 2008 and later).

**Watch the Security log for failed logon attempts (event ID 4625), skipping anything that predates the item's first run:**
```
eventlog[Security,,,,4625,,skip]
```
The `skip` mode tells Zabbix not to process the entire historical backlog of the log when the item is first activated — without it, an item on a busy Security log can generate a flood of historical matches the moment it's created.

**Filter on event source as well as severity, and exclude specific noisy event IDs:**
```
eventlog[Application,,"Error",MyAppService,,,]
```
`source` matches against the "Source" column you'd see in Event Viewer — the component or service that logged the event. This is useful for isolating events from one application without having to write a regex against the message body.

A word of caution that's worth stating plainly in a book: broad event log items — particularly on the Security log of a domain controller, which can log thousands of events per minute under normal load — have a real performance cost, both on the agent (which has to evaluate every new entry against your regex) and on the Zabbix server (which has to ingest and store every match as log data). Filter as specifically as you can at the item level (severity, source, event ID) rather than relying on broad regexes against the message text. If you only care about three or four specific event IDs, say so explicitly — `eventid` accepts a regex, so `^(4625|6008|41)$` is both precise and cheap.

The `maxlines` parameter, if set on the item, overrides the agent-wide `MaxLinesPerSecond` configuration setting for that specific item — useful if you have one log source that's known to be noisy and you want to cap it without affecting every other log item on the host.

## Services and WMI

The third pillar is asking Windows "what state is X in" — where X is a service, a disk, a network adapter, or any of the hundreds of other things WMI can describe.

### Service state via `service.info`

For the simple, extremely common case of "is this service running," `service.info` is the right tool:

```
service.info[<service name>,<param>]
```

The first parameter is the **service name** — not the display name. These are often different: the display name "DNS Client" corresponds to the service name `Dnscache`. You can find the service name in the Services MMC snap-in, in the General tab of a service's properties.

`param` defaults to `state` if omitted, returning an integer: 0 = running, 1 = paused, 2 = start pending, 3 = pause pending, 4 = continue pending, 5 = stop pending, 6 = stopped, 7 = unknown, and 255 if the service doesn't exist at all. Other useful values for `param` are `startup` (the configured startup type — automatic, manual, disabled, etc.) and `displayname`, `path`, `user`, and `description` for descriptive/text information.

A practical pattern: combine `state` with `startup` in a trigger. A service with `startup=stopped` (disabled) sitting at `state=stopped` is expected and not a problem. A service configured as `startup=automatic` but currently at `state=stopped` is exactly the kind of thing you want to alert on — and that distinction is why monitoring `state` alone, without also knowing the intended startup type, tends to either miss real problems or generate noise about services that were deliberately disabled.

For mapping the numeric state values to readable text in the frontend, Zabbix ships value maps for this as part of the official "Windows services by Zabbix agent" / "Windows services by Zabbix agent active" templates — linking one of those templates to a host (or just copying its value map) saves you from redefining the 0–255 mapping yourself.

### Discovering services automatically

Rather than hand-configuring `service.info` items for every service you care about, `service.discovery` returns the full list of installed services as a JSON array suitable for low-level discovery, exposing macros such as `{#SERVICE.NAME}`, `{#SERVICE.STARTUP}`, `{#SERVICE.STARTUPNAME}`, `{#SERVICE.STATE}`, and `{#SERVICE.STATENAME}` for use in the discovery rule's filter and in item/trigger prototypes. A typical item prototype built on this is `service.info[{#SERVICE.NAME},<param>]`.

Combined with an LLD filter — for example, including only services where `{#SERVICE.STARTUPNAME}` matches "automatic" — this gives you a rule that automatically picks up new auto-start services as they're installed and creates the corresponding state/startup items and "service should be running but isn't" triggers without any manual item creation. This is the mechanism behind the official Windows services templates mentioned above, and reusing those templates (or cloning them) — including their pre-built filter regexes for excluding known-noisy services — is generally preferable to building the discovery rule from scratch.

### WMI queries with `wmi.get` and `wmi.getall`

For anything that doesn't have a dedicated item key — disk health and serial numbers, network adapter status, installed hotfixes, NLB cluster node state, and so on — the agent can run a WMI query directly via WQL (the WMI Query Language, a SQL-like syntax for querying WMI classes).

`wmi.get[<namespace>,<query>]` returns a single value — the first property of the first matching object:

```
wmi.get[root\cimv2,"select Status from Win32_DiskDrive where Name like '%PHYSICALDRIVE0%'"]
```

This returns the `Status` property (a string like "OK") of the first physical disk. Note the query itself needs to be wrapped in its own quotes when it contains special characters like `%` or when tested from a shell — when testing with `zabbix_agent2.exe -t`, wrap the entire key argument in quotes too, or you'll get inconsistent "invalid key" or "not supported" results depending on how the shell parses the embedded quotes and spaces.

`wmi.getall[<namespace>,<query>]` returns the *entire* result set as a JSON array, with one object per matching WMI instance and one field per selected property. This is the key to use for low-level discovery. The official "Windows by Zabbix agent active" template uses exactly this pattern for network interface discovery:

```
wmi.getall[root\cimv2,"select Name,Description,NetConnectionID,Speed,AdapterTypeId,NetConnectionStatus,GUID from win32_networkadapter where PhysicalAdapter=True and NetConnectionStatus>0"]
```

The `where PhysicalAdapter=True and NetConnectionStatus>0` clause is doing useful filtering work here — it excludes virtual/tunnel adapters and adapters that are present but not connected, which is exactly the kind of thing that, without filtering, turns Windows network interface discovery into a confusing list of forty mostly-irrelevant pseudo-adapters. The same template then runs the JSON result through a JavaScript preprocessing step to map the WMI field names onto the `{#IFNAME}`, `{#IFDESCR}`, `{#IFALIAS}`, and `{#IFGUID}` LLD macros used by the rest of the discovery rule's item prototypes.

The same `wmi.getall` pattern, with a different query, is the basis for physical disk discovery via `Win32_DiskDrive` — useful for getting disk model, serial number, and SMART-derived status without needing SNMP or a separate agent plugin.

One limitation worth being explicit about: WMI access through Zabbix is always local to the host the agent runs on. There's no "query WMI on a remote host" item — if you want WMI data from a given Windows machine, the agent has to be installed on that machine. This rules out using WMI as a way to monitor Windows hosts without deploying an agent to them at all.

### `registry.get` as a complement to WMI

For data that lives in the registry rather than being exposed through WMI or a performance counter — version strings, installed-software lists under `Uninstall` keys, or arbitrary configuration values written by an application — `registry.get[<key>,<mode>]` reads registry keys and values directly, and like `wmi.getall` can return a JSON structure suitable for discovery (for example, enumerating all subkeys under `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` to build an inventory of installed software). It's a narrower tool than WMI, but for the specific case of "I need to know if this registry value is set to X," it's more direct than writing a WQL query against `StdRegProv`.

## Putting it together: a small worked scenario

To tie the three pillars together, consider a typical "is this application server healthy" set of checks for a Windows host running a custom service:

- **Service health** — `service.info[MyAppService,state]` with a trigger comparing against the service's `startup` value, so a deliberately-stopped service doesn't fire an alert.
- **Resource pressure** — `perf_counter_en["\Process(MyAppService)\% Processor Time"]` and `perf_counter_en["\Process(MyAppService)\Working Set"]`, giving you per-process CPU and memory figures specific to that application rather than the whole-system aggregates.
- **Application errors** — `eventlog[Application,,"Error",MyAppService,,,skip]`, catching anything the application itself writes to the Application log under its own source name.
- **Disk space for its data volume** — handled through the standard `vfs.fs.size` key (not Windows-specific, and already covered in the storage monitoring chapter), but worth cross-referencing here since "app server ran out of disk" is so often the actual root cause behind the other three alerts firing.

None of these four items individually is complicated, but together they cover the categories of failure — "the process died," "the process is unhealthy but still running," "the application logged that something went wrong," and "the underlying resource it depends on is exhausted" — that account for the overwhelming majority of real Windows server incidents.

## Troubleshooting checklist

A short list of the issues you're most likely to hit, in roughly the order you're likely to hit them:

- **Item shows "Not supported."** Test the key directly on the host with `zabbix_agent2.exe -t "<key>"` (quote the whole key). This tells you immediately whether the problem is the key itself (typo, wrong counter/service/WMI class name) or something on the Zabbix side (permissions, item configuration).
- **`eventlog` item created but never returns data.** Confirm the item type is "Zabbix agent (active)" and that `ServerActive` in the agent config points at the right server/proxy. Passive-only event log items simply won't work, and this is easy to get wrong if you're used to configuring everything as passive on Linux.
- **`perf_counter_en` returns nothing for a counter you can see in `perfmon`.** Check whether the counter belongs to a category that needs to be (re)registered on this particular host — application-specific counter sets (IIS, SQL Server, custom .NET apps) sometimes fail to register properly during install, independent of anything Zabbix-related.
- **`wmi.get`/`wmi.getall` returns an error or "unsupported."** Double-check namespace and quoting first — `root\cimv2` is correct for the vast majority of classes, and the entire query generally needs to be inside its own quotes within the key. If the namespace and quoting are right, test the same WQL query locally with `wbemtest.exe` or PowerShell's `Get-CimInstance` to confirm the class/property names themselves are correct on that host — WMI class availability does vary slightly between Windows versions.
- **Event log item floods with historical data on creation.** Add `skip` as the `mode` parameter. This is easy to miss the first time and hard to miss the second time, once you've seen what a Security log backlog looks like in Zabbix's log item view.
