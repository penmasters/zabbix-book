---
description: |
    Respond automatically with Zabbix actions. Define rules to send alerts, run
    scripts, or escalate problems based on trigger conditions.
tags: [expert]
---

# Actions

Actions are the automated response engine of Zabbix. Whenever something happens
in your monitoring environment, a trigger fires, a new host is discovered, an active
agent registers itself, an item goes unsupported, or a service changes status,
Zabbix can respond automatically. Actions define both *when* to respond
*(conditions)* and *what* to do *(operations)*.

Understanding actions deeply is one of the things that separates a Zabbix power
user from someone who just installed the product. The configuration surface is
large, the interaction between escalations and recovery is subtle, and a number
of behaviours only become clear once you know where to look.

This chapter covers all five event sources that can drive an action in Zabbix 8:

- **Trigger actions**: the most common type, responding to problem events raised
  by triggers
- **Discovery actions**: responding to hosts and services found by network discovery
  rules
- **Autoregistration actions**: responding to active Zabbix agents that register
  themselves
- **Internal actions**: responding to Zabbix's own internal state changes (unsupported
  items, unknown triggers)
- **Service actions**: responding to changes in the status of business services

---

## What Makes Up an Action

Every action, regardless of its event source, shares the same three-part structure:

1. **Name and enabled/disabled toggle**: actions can be switched off without deleting
   them, which is useful during maintenance windows or when testing a new alerting
   design
2. **Conditions**: a set of filters that determine whether the action should fire
   for a given event
3. **Operations**: what to actually do: send a message, execute a command, or
   manipulate a host

Trigger actions additionally have **Recovery operations** (what to do when the
problem resolves) and **Update operations** (what to do when someone acknowledges
or comments on the problem). Internal actions also support recovery operations.

You can reach all action types from **Alerts → Actions** in the left-hand menu.
Each event source has its own tab: `Trigger actions`, `Service actions`,
`Autoregistration actions`, `Internal actions`, and `Discovery actions`.

---

## Conditions

Conditions are the gatekeeping layer. An action's conditions are evaluated against
each event, and only if the conditions pass does the operation execute. If you
define no conditions at all, the action fires for every event of that source type,
which is occasionally intentional but usually unwise in a large environment.

### Type of Calculation

When you add more than one condition, Zabbix needs to know how to combine them.
The **Type of calculation** field gives you four options:

| Option | Meaning |
|---|---|
| `AND / OR` | Conditions of the same type are combined with OR; conditions of different types are combined with AND |
| `AND` | All conditions must be true |
| `OR` | Any single condition being true is enough |
| `Custom expression` | You write a logical formula using condition labels (A, B, C…) |

The `AND / OR` default is often misunderstood. Concretely: if you add two **Host
group** conditions, `Host group = Linux servers` and `Host group = Database servers`;
then Zabbix evaluates them as *"host is in Linux servers OR Database servers"*.
If you then also add a **Trigger severity** condition of `>= High`, the full
expression becomes *`"(host is in Linux servers OR Database servers) AND
severity >= High"`*. This is logical and efficient for most alerting designs.

The `Custom expression` mode gives you full control. Conditions are labelled A,
B, C, D and so on as you add them, and you write the formula yourself. For example:
`(A or B) and C and not D`. Use this when the default AND/OR logic does not produce
the correct result.

!!! note

    Condition labels are assigned in the order conditions were added. If you
    delete a condition, the labels do not renumber — the formula must reference
    the correct remaining labels.

### Condition Operators

Depending on the condition type, the available operators vary. String based conditions
(trigger name, host name, tag value, host metadata) support:

- `=` and `<>` (equals / does not equal)
- `contains` and `does not contain` (substring match, **case-insensitive**)
- `matches` and `does not match` (regular expression)

Numeric conditions (severity, discovery uptime/downtime) support: `=`, `<>`, `>`,
`>=`, `<`, `<=`.

The `matches` operator uses POSIX extended regular expressions, the same engine
used elsewhere in Zabbix.

---

## Trigger Actions

Trigger actions are what most people think of when they hear **"action"** in Zabbix.
They respond to **problem events**, moments when a trigger changes from `OK`
to `PROBLEM` and they are the foundation of any meaningful alerting setup.

### Condition Types for Trigger Actions

| Condition type | Notes |
|---|---|
| Host group | Matches the host's direct group membership (nested groups are not automatically included) |
| Host | Exact host match |
| Trigger | Exact trigger match |
| Trigger name | String match on the trigger display name |
| Trigger severity | Compares with the trigger's configured severity |
| Trigger tag | Matches a tag name and optionally a tag value |
| Time period | A Zabbix time period string such as `1-5,08:00-18:00` (Monday–Friday, 8am–6pm) |
| Problem is suppressed | Whether the problem is currently suppressed (in maintenance) |
| Host inventory field | Match against any host inventory field |

!!! tip

    The **Trigger tag** condition is extremely powerful in combination with templates.
    If all your database templates tag their triggers with `component: database`,
    you can write a single action that routes database alerts to the DBA team
    without maintaining a list of specific triggers or host groups.

### The "Pause Operations for Suppressed Problems" Option

At the top of the action form there is a checkbox labelled **Pause operations for
suppressed problems**. When this is enabled (which it is by default), Zabbix will
not send notifications for problems that are currently suppressed. For example,
because the host is in a scheduled maintenance window. Crucially, the escalation
does not restart from the beginning once maintenance ends; it resumes from where
it was paused. This prevents a flood of "catch-up" notifications after a maintenance
window closes.

If you disable this option, notifications fire regardless of maintenance status.
This is occasionally useful for infrastructure teams who want to receive all alerts
even during planned work.

### Operations and Escalations

This is where most of the complexity lives. Each operation in a trigger action
has:

- **Steps**: which escalation step this operation should fire on (e.g., step 1,
  or steps 2–4, or 3–0 meaning "step 3 and all following steps")
- **Step duration**: how many seconds each step lasts before advancing to the
  next one (0 means use the action's default escalation period)
- **Operation type**: Send message or global script (remote command)
- **Target**: the user or user group to notify, or the script to run

The **default escalation period** is set at the action level with a field called
**Default operation step duration**. Its default value is 3600 seconds (1 hour).
Every operation step that has its own duration set to 0 will inherit this value.

#### How Escalation Works in Practice

Consider this configuration:

- Action default step duration: `3600` (1 hour)
- Step 1: Send message to user `oncall_engineer`
- Step 2: Send message to user `team_lead`
- Steps 3–0: Send message to user group `management`

When a problem event fires:

1. Immediately: step 1 fires, `oncall_engineer` gets notified.
2. After 1h, if the problem still exists: step 2 fires, `team_lead`
   gets notified.
3. After another hour, if still unresolved: step 3 fires, `management`
   gets notified.
4. After another hour, if still unresolved: step 4 fires (because steps
   3–0 means "step 3 to infinity"), `management` gets notified again.
5. This continues indefinitely until the problem resolves.

!!! warning

    If the problem resolves before a step fires, that step is skipped. The escalation
    is not retroactive, no notifications are sent for steps that never fired before
    the recovery.

#### Sending Notifications

When you add a **Send message** operation, you must choose:

- **Send to users** and/or **Send to user groups**: These are additive; you can
  have both in the same operation step
- **Send only to**: You can restrict to a specific media type (e.g., only send
  via Email, not SMS), or leave it as *All* to use every media type configured
  for those users

If you check **Custom message**, you can write a specific subject and body for
this action using Zabbix macros. If you leave **Custom message** unchecked, Zabbix
uses the default message template defined on the media type itself.

!!! note

    A subtle but important point: leaving **Custom message** unchecked means the
    message template comes from the media type configuration, not the action.
    Different media types can have completely different templates. This is intentional.
    You probably want a different message format for an SMS (short, plain text)
    than for an email (longer, HTML-formatted).

#### Remote Commands via Global Scripts

The **Run global script** operation type executes a global script on a target.
The targets available are:

- **Current host** — the host that triggered the problem
- **Hosts of a host group** — all hosts in a specific host group
- A **specific host** — a statically named host

The global script itself must already exist under **Alerts → Scripts**. Crucially,
all execution permissions and the execution context (run on Zabbix server, run
on agent) are configured in the script definition, not in the action. The action
only selects *which* script to run and *where* (current host, a host group, etc.).

For scripts that execute on a Zabbix agent, the agent must have `AllowKey=system.run[*]`
(or a more specific key pattern) in its configuration file. This applies to both
the classic Zabbix Agent and Zabbix Agent 2. Both use the `AllowKey` directive.
There is no separate server-side toggle for this; access is controlled at the `agent
level` and by the global script's permission settings (which user groups are allowed
to run it).

!!! tip

    A common use of remote commands in trigger actions is automated remediation.
    For example, restarting a service the moment Zabbix detects it is down. Be
    careful: if the problem condition is intermittent and flaps, the restart command
    will fire repeatedly. Use the `Problem is suppressed` condition or a trigger
    dependency to guard against this.

### Recovery Operations

Recovery operations fire when the trigger returns from `PROBLEM` to `OK`. They
do not escalate. They fire once, at step 1 of the recovery operations section,
regardless of which escalation step the problem had reached.

You can configure recovery operations to send a "resolved" notification, run a
script, or both. If you want recovery notifications to go to everyone who was
notified during the escalation (not just the first step), you need to add each
`user/group` separately in the recovery operation, or use the **Notify all involved**
checkbox. This sends the recovery notification to every `user and group` that
received a notification during any escalation step of this problem.

!!! tip

    **Notify all involved** is a small but genuinely useful checkbox that is easy
    to miss. Without it, a recovery notification only goes to whoever you explicitly
    list in the recovery operation, which may not be the same people as the last
    escalation step.

### Update Operations

Update operations fire whenever a problem event is updated. Updates include:

- Adding an acknowledgment
- Adding a comment
- Changing the problem severity manually
- Suppressing or unsuppressing the problem

You can check any combination of these triggers in the **Conditions** section of
an update operation. This allows you to do things like: "when someone acknowledges
the problem, send a notification to the oncall channel confirming the acknowledgment."

Update operations also support **Send message** and **Run global script**.

---

## Discovery Actions

Network discovery in Zabbix works by running a discovery rule (configured under
**Data collection → Discovery**) that scans IP ranges using a variety of checks.
When something is found, or when something previously found disappears, a discovery
event is generated. Discovery actions respond to those events.

### Discovery Event Conditions

| Condition type | Notes |
|---|---|
| Discovery rule | Filter to events from a specific discovery rule |
| Discovery check | Filter to a specific check within that rule (e.g., only the HTTP check) |
| Discovery object | Either `Host` or `Service` |
| Discovery status | `Up`, `Down`, `Discovered`, `Lost` |
| Uptime / Downtime | How long the object has been continuously up or down (in seconds) |
| Received value | The value returned by the discovery check |
| Proxy | Which Zabbix proxy performed the discovery |
| Host IP | Match on the IP address of the discovered host |
| Service type | Protocol of the discovered service (HTTP, FTP, SSH, SMTP, POP, IMAP, HTTPS, Telnet, LDAP, HTTPS, SNMP, ICMP, Zabbix agent, etc.) |
| Service port | The port number |

The distinction between `Discovered` and `Up` is subtle. `Up` fires every time a
check for an already known device returns a successful result. `Discovered` fires
only the first time a device is seen. It will not fire again on subsequent scans
until the device had been in `Lost` state and then returns. This distinction matters
enormously for your action design: use `Discovered` if you want to add a host once;
use `Up` if you want to react every time a service check succeeds.

### Discovery Action Operations

Discovery actions can modify the Zabbix inventory directly:

| Operation | Effect |
|---|---|
| Add host | Creates the host in Zabbix using the discovered IP/DNS name |
| Remove host | Deletes the host from Zabbix |
| Enable host / Disable host | Changes the host's monitoring state |
| Add to host group | Adds the host to a specified host group |
| Remove from host group | Removes from a group (does not delete the host) |
| Link to template | Links the host to a template |
| Unlink from template | Removes the template link (items added by the template remain as standalone items) |
| Unlink from template and clear | Removes the template link *and deletes* all items, triggers, graphs, and LLD rules that came from that template |
| Set host inventory mode | Sets to Disabled, Manual, or Automatic |
| Send message | Notifies a user or group |
| Run global script | Executes a script |

!!! warning

    The difference between **Unlink from template** and **Unlink from template
    and clear** is critical. Plain *unlink* leaves orphaned items behind. All the
    items that came from the template continue to collect data but are no longer
    governed by template updates. *Unlink and clear* removes everything the template
    contributed. Choose carefully based on whether you need the historical data.

### A Practical Discovery Action Design

**A common real-world pattern:**
automatically onboard any newly discovered host that responds to ICMP and has
`Zabbix agent` running on port 10050, and then clean up hosts that have been down
for more than 24 hours.

**Action 1: Auto-add discovered hosts**

``` bash
- Conditions: `Discovery check = ICMP ping` AND `Discovery status = Discovered` AND `Service type = Zabbix agent`
- Operations:
   1. Add host
   2. Add to host group: `Discovered hosts`
   3. Link to template: `Linux by Zabbix agent`
   4. Enable host
```

**Action 2: Remove long-lost hosts**

``` bash
- Conditions: `Discovery object = Host` AND `Discovery status = Lost` AND `Downtime > 86400` (24 hours)
- Operations: Remove host
```

!!! tip

    Be careful with the `Remove host` operation. It permanently deletes the host
    and all its historical data from Zabbix. Many organisations prefer `Disable host`
    instead, to preserve the data and allow manual review before deletion.

---

## Autoregistration Actions

Autoregistration is specifically for **active Zabbix agents** that initiate contact
with the Zabbix server or proxy. Unlike passive agents (which are polled by Zabbix),
an active agent sends a registration request when it starts up. The server stores
this as an autoregistration event, and your autoregistration action can then act
on it.

For autoregistration to work, the agent must have `ServerActive` pointing to the
`Zabbix server` or `proxy address`. You do not need to pre-create the host in
Zabbix. That is the whole point.

### Identifying Hosts with Host Metadata

The most powerful feature of autoregistration is **host metadata**. In the agent
configuration file, the `HostMetadata` parameter can be set to a static string.
For example, `linux production webserver`. Alternatively, `HostMetadataItem` can
be set to a Zabbix item key whose value will be used as the metadata at registration
time, such as `system.uname` to include the kernel version.

This metadata is then available in autoregistration action conditions, allowing
you to route different types of agents to different host groups and templates
automatically.

### Autoregistration Condition Types

| Condition type | Notes |
|---|---|
| Host name | The hostname reported by the agent (`Hostname` parameter) |
| Host metadata | The metadata string reported by the agent |
| Proxy | The proxy that received the registration |
| Host IP | The IP address the registration came from |

The `Host metadata` condition supports `contains`, `does not contain`, `matches`,
and `does not match`. This lets you do things like:

- `Host metadata contains "linux"`: Link to Linux template
- `Host metadata contains "windows"`: Link to Windows template
- `Host metadata matches "prod.*web"`: Add to production web server group

### Autoregistration Operations

The available operations are identical to discovery actions:

- Add host, Remove host, Enable host, Disable host
- Add to host group, Remove from host group
- Link to template, Unlink from template, Unlink and clear
- Set host inventory mode
- Send message
- Run global script

### A Practical Autoregistration Design

Suppose your Linux team uses `HostMetadata = linux` and your Windows team uses
`HostMetadata = windows`. You have multiple environments tagged in the metadata
as `prod`, `staging`, or `dev`.

**Autoregistration action for Linux production servers:**

``` bash
- Conditions (AND):
  - `Host metadata contains "linux"`
  - `Host metadata contains "prod"`
- Operations:
  1. Add host
  2. Add to host group: `Linux servers`
  3. Add to host group: `Production`
  4. Link to template: `Linux by Zabbix agent`
  5. Enable host
```

**Autoregistration action for Windows dev servers:**

``` bash
- Conditions:
  - `Host metadata contains "windows"`
  - `Host metadata contains "dev"`
- Operations:
  1. Add host
  2. Add to host group: `Windows servers`
  3. Add to host group: `Development`
  4. Link to template: `Windows by Zabbix agent`
  5. Disable host *(development hosts start disabled until approved)*
```

!!! tip

    When a host re-registers (for example after a reboot or agent restart), the
    autoregistration action fires again. This is normally harmless, adding a host
    that already exists will update its configuration rather than creating a duplicate.
    However, if you have an operation that adds the host to a group, and someone
    has since moved the host out of that group, the re-registration will add it
    back. Design your metadata and groups with this in mind.

!!! tip

    There is no built-in deduplication delay for autoregistration. If an agent
    rapidly restarts and re-registers many times, the action will fire many times.
    In practice this is rarely a problem, but it is worth knowing.

---

## Internal Actions

Internal actions respond to state changes inside Zabbix itself. Not to monitored
infrastructure, but to the health of Zabbix's own data collection. There are three
internal event types:

| Event | Fires when... |
|---|---|
| Item state changed to Not supported | An item fails to collect data and enters the "not supported" state |
| Item state changed to Normal | An item recovers from "not supported" back to normal collection |
| LLD rule state changed to Not supported | A low-level discovery rule enters "not supported" |
| LLD rule state changed to Normal | An LLD rule recovers |
| Trigger state changed to Unknown | A trigger enters "unknown" state (usually because the items it depends on are not supported) |
| Trigger state changed to Normal | A trigger recovers from "unknown" |

!!! note

    Internal actions support **Recovery operations** but **do not support Update
    operations** (acknowledgements). They also do not support **Run global script**,
    Only **Send message** is available.

This last point is easy to miss in the documentation. You cannot run an automated
remediation script in response to an item going unsupported; you can only send a
notification.

### Why Internal Actions Matter

In a large Zabbix deployment, items go unsupported more often than expected, a
remote system changes its SNMP OID structure, a cloud API endpoint moves, a JMX
target loses its credentials. Without internal actions, these failures are silent.
Zabbix continues to show the last known value for the item while the actual collection
has stopped.

A minimal internal action, **"send me a notification when any item enters not
supported state"**, is one of the most valuable low-effort configurations you can
make. It turns silent data collection failures into visible alerts.

### Condition Types for Internal Actions

| Condition type | Notes |
|---|---|
| Host group | Filters by host group |
| Host | Filters by specific host |
| Template | Filters by template — only items/triggers inherited from that template |
| Event type | Selects which of the six internal event types this condition applies to |

---

## Service Actions

Service actions were introduced to support Zabbix's business service monitoring
feature. A service in Zabbix is a node in a service tree that aggregates the status
of hosts, triggers, or other services into a single business-level health indicator.
When a service's status changes, a service event is generated, and service actions
can respond.

### Service Condition Types

| Condition type | Notes |
|---|---|
| Service | The specific service by name |
| Service name | String match on service name (supports contains/matches) |
| Service tag name | Presence of a tag on the service |
| Service tag value | Value of a specific service tag |

### Service Action Operations

Service actions support **Send message** and **Run global script**. They do not
have discovery-style host manipulation operations.

Service actions support **Recovery operations** (when the service returns to an
OK status) and **Update operations** (when the service event is acknowledged).

### A Practical Service Action Design

Consider a service called `E-commerce platform` that aggregates status across web
servers, database servers, and payment gateway checks. You want different notification
channels depending on severity:

**Service action: E-commerce degraded**

``` bash
- Conditions: `Service name = E-commerce platform` AND status changes to `Warning`
- Operations: Send message to `team_lead` via Slack
```

**Service action: E-commerce down**

``` bash
- Conditions: `Service name = E-commerce platform` AND status changes to `High` or `Disaster`
- Operations: 
  - Step 1: Send message to `oncall_engineer` via PagerDuty
  - Step 2 (after 900 seconds): Send message to `team_lead` via PagerDuty
  - Step 3 (after 1800 seconds): Send message to `management_group` via Email
```

!!! tip

    Service actions and trigger actions are independent. A trigger action will
    send notifications about individual host problems. A service action will send
    notifications about the aggregated business service status. In a mature setup
    you often want both: engineers care about individual trigger details, while
    management wants to know the business impact.

---

## How Zabbix Processes Actions

Understanding the processing model helps when debugging why notifications do or
do not arrive.

**Multiple actions can match the same event.** Zabbix does not stop processing
after the first matching action. If three trigger actions all match a given problem
event, all three will fire. There is no priority ordering and no "stop processing"
mechanism. This is different from firewall rules or some other monitoring tools.

**Actions are evaluated asynchronously.** After a trigger fires, the event is written
to the database and then picked up by the **escalator** process, which evaluates
all enabled actions of the matching type. The escalator is responsible for scheduling
and executing each step. The **alerter** process handles the actual delivery of
notifications.

**Escalation state is stored in the database.** This means escalations survive a
`Zabbix server` restart. If the server restarts while an escalation is in
progress (say, between step 1 and step 2), the escalation will resume correctly
after restart.

**Disabled actions are skipped entirely.** A disabled action does not accumulate
pending operations. If you disable an action during a live problem and re-enable
it later, no retroactive operations are fired.

**Time period conditions are evaluated at the moment each step fires.** If you
have a time period condition (`1-5,09:00-17:00`) and escalation step 2 fires on
a Saturday night, that step will be skipped because the condition fails at that
moment. This is the expected behaviour for business-hours alerting, but it can
be surprising when a problem persists across a weekend. Multiple escalation steps
may silently skip until Monday morning.

!!! note

    There is one specific re-evaluation nuance for the **Maintenance** condition:
    if the problem was suppressed when step 1 fired and "Pause operations for suppressed
    problems" is enabled, the escalation was paused. When suppression ends, Zabbix
    resumes the escalation from the step that was waiting. It does not restart from step 1.

---

## Using Macros in Actions

Both the subject and body of Send message operations support a wide range of
macros. Some of the most frequently used:

| Macro | Resolves to |
|---|---|
| `{TRIGGER.NAME}` | The name of the trigger (with resolved macros) |
| `{HOST.NAME}` | The visible name of the host |
| `{HOST.IP}` | The IP address of the host |
| `{ITEM.VALUE}` | The most recent value of the item that caused the trigger to fire |
| `{ITEM.LASTVALUE}` | Same as above (both exist for historical compatibility) |
| `{EVENT.SEVERITY}` | The severity label (e.g., High, Disaster) |
| `{EVENT.DATE}` | Date of the event |
| `{EVENT.TIME}` | Time of the event |
| `{EVENT.AGE}` | How long the problem has existed at the time the notification fires |
| `{EVENT.TAGS}` | All tags on the event in `tag: value, tag: value` format |
| `{EVENT.TAGSJSON}` | Same, but as a JSON array — useful for webhook payloads |
| `{TRIGGER.URL}` | The URL field of the trigger (great for linking to a runbook) |
| `{ZABBIX.URL}` | The base URL of the Zabbix frontend (configured in the frontend URL setting in Zabbix server settings) |
| `{ESC.HISTORY}` | The escalation history: a log of which step fired when and to whom |
| `{ALERT.SENDTO}` | The recipient's Send To value from their media type configuration |
| `{ALERT.SUBJECT}` | The notification subject (only usable in the body) |

`{ESC.HISTORY}` is a particularly useful macro to include in escalation notifications.
It gives the recipient context about what already happened. For example, "Step 1,
sent to oncall_engineer at 14:32:00. No response. Step 2 sending to team_lead now."

`{EVENT.TAGSJSON}` and `{EVENT.RECOVERY.TAGSJSON}` are worth remembering if you
use Zabbix actions to drive a webhook. Parsing `{EVENT.TAGS}` as a string
in your receiving system is fragile; using the JSON variant is much cleaner.

---

## Common Mistakes and How to Avoid Them

- **Sending to a user with no configured media.**: If a user has no active media
type (or their media type is disabled), the notification silently disappears. Zabbix
logs a warning in the server log, but no error is surfaced in the UI. Always verify
user media configuration before relying on actions for critical alerts.

- **Using AND/OR without understanding the grouping**: The default AND/OR logic
groups same type conditions with OR and different-type conditions with AND. This
is correct most of the time, but if you add two Host conditions expecting both to
be required, they will actually be OR'd together. Switch to `AND` or `Custom expression`
if you need different behaviour.

- **Forgetting that discovery conditions `Discovered` vs `Up` are different.**: Using
`Up` in a discovery action that provisions hosts will attempt to re-provision the
host on every successful discovery scan. Use `Discovered` for one-time provisioning.

- **Over relying on trigger actions for host management.**: Trigger actions cannot
add or remove hosts from host groups. If you need dynamic group membership based
on trigger state, you need a combination of discovery/autoregistration actions
and host metadata, not trigger actions.

- **Not configuring internal actions.**: Silent item failures are one of the most
common sources of monitoring blind spots. A simple internal action that sends
email when any item in any group becomes "not supported" takes five minutes to
configure and can save hours of debugging.

- **Setting step duration too short.**: Very short escalation step durations
(below 60 seconds) can cause the escalator to fall behind under heavy load. Zabbix
does not guarantee sub-minute escalation precision. For anything below one minute,
consider whether the escalation design is appropriate.

---

## Conclusion

Actions are the automation layer that connects Zabbix's data collection engine
to your response workflows. Each of the five event sources: **triggers, discovery,
autoregistration, internal, service**. Has its own set of conditions and operations,
with trigger actions offering the most depth through escalations, recovery operations,
and update operations.

A few principles to keep in mind as you build your action configuration:

- Use **trigger tags** to build flexible, template driven routing rules rather
than maintaining long lists of specific triggers or hosts
- Use **host metadata** in autoregistration to automatically classify and configure
newly registered agents
- Use `AND/OR` conditions consciously and switch to `Custom expression` when the
default grouping does not match your intent
- Always configure at least one **internal action** to catch silent data collection
failures
- Include `{ESC.HISTORY}` in escalation messages so recipients know what already
happened before the notification reached them

## Questions

## Useful URLs
