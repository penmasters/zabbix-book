---
description: |
    Automate responses with Zabbix scripts. Execute remote commands or integrations
    directly from triggers, actions, or the web interface.
tags: [advanced, expert]
---

# Custom Alert Scripts

The previous section covered media types in full, including the **Script** type.
This chapter goes one level deeper. You will learn exactly how Zabbix hands
off data to an external script, what constraints apply, and how to write a script
that does something genuinely useful. By the end you will have a working alert
logger running on your Zabbix server that you can inspect, extend, and reuse as
a foundation for your own integrations.

---

## What Is a Custom Alert Script?

A custom alert script is any executable file, a shell script, a Python script,
a compiled binary, anything the operating system can run, that Zabbix calls when
it needs to deliver a notification through a **Script** media type.

When a notification is triggered, the Zabbix server:

1. Resolves all macros in the configured script parameters.
2. Locates the script file inside `AlertScriptsPath`.
3. Executes it as the `zabbix` system user, passing the resolved parameters as
   positional arguments.
4. Waits for the script to exit.
5. Treats exit code `0` as success and any non-zero exit code as failure.
6. Logs the outcome in **Reports → Action log**.

That is the entire contract between Zabbix and your script. Everything else,
what language you write it in, what the script does with the data, whether it
talks to an API, writes a file, or sends an email, is entirely up to you.

---

## Why Use a Script Instead of a Webhook?

Webhooks (covered in the previous section) are the preferred modern approach for
integrating with external HTTP services. So when does a custom script make more
sense?

- **No HTTP endpoint exists.**: If your target system does not expose an API.
  For example, a legacy ticketing system you interact with via a command-line
  tool, a script is your only option.
- **Complex local logic is required.**: A script can read local files, query a
  local database, call multiple external tools in sequence, or make decisions
  based on the state of the Zabbix server host itself. JavaScript inside a webhook
  is sandboxed and cannot do any of this.
- **You need shell-level access.**: Writing to a file, rotating logs, calling
  `logger` to push entries into syslog, or invoking system commands all require
  a real process running on the server. Exactly what the Script type provides.
- **Learning and debugging.**: A logging script that simply writes every alert to
  a file is invaluable when you are learning how Zabbix constructs notifications
  or when you are troubleshooting why a more complex integration is not receiving
  the data it expects.

---

## How Zabbix Passes Data to a Script

Understanding the exact mechanics saves a lot of confusion. Zabbix passes data
to your script exclusively through **positional arguments**, the same `$1`, `$2`,
`$3` you use in any shell script.

You define which data Zabbix passes, and in which order, using the **Script
parameters** list in the media type configuration. Each line in that list becomes
one argument. Zabbix resolves any macros in the parameter value before calling
the script, so by the time your script runs, `$1` is already the actual host name,
not the string `{HOST.NAME}`.

Three macros are used almost universally in Script media types:

| Macro | What it contains | Argument |
|:--- |:--- |:--- |
| `{ALERT.SENDTO}` | The value from the user's **Send to** field | `$1` |
| `{ALERT.SUBJECT}` | The notification subject from the message template | `$2` |
| `{ALERT.MESSAGE}` | The full notification body from the message template | `$3` |

`{ALERT.SENDTO}` is the contact address the user entered in their media assignment.
For email that is an email address. For a script it can be anything you choose
to put there, a username, a file path, a team name, a routing key. Your script
decides how to use it.

---

## The AlertScriptsPath Directory

All scripts must live inside the directory defined by `AlertScriptsPath` in
`/etc/zabbix/zabbix_server.conf`. Usually the default value is:

``` bash
AlertScriptsPath=/usr/lib/zabbix/alertscripts
```

You can verify the value on your system with:

```bash
grep AlertScriptsPath /etc/zabbix/zabbix_server.conf
```

If the line is commented out, the default above applies. Zabbix will refuse to
execute any script located outside this directory, even if you supply a full path.
This is a deliberate security boundary.

The script file must meet two requirements:

1. It must be **executable** by the `zabbix` system user.
2. It must be **owned** appropriately, world-writable scripts are rejected as
   a security measure.

The correct ownership and permissions for most scripts are:

```bash
chown root:zabbix /usr/lib/zabbix/alertscripts/your-script.sh
chmod 750 /usr/lib/zabbix/alertscripts/your-script.sh
```

!!! note

    Why root:zabbix and not zabbix:zabbix? The zabbix user needs to execute the
    script, not own it. Ownership by root means only root can modify the file. If
    the zabbix process were ever compromised, an attacker could not alter scripts
    in AlertScriptsPath to execute arbitrary code. This is the same principle that
    applies to system binaries — readable and executable by unprivileged users,
    but modifiable only by root.

---

## Step-by-Step: Building an Alert Logger

This example builds a script that writes every Zabbix alert to a structured log
file. It is useful in two concrete ways:

- As a **permanent audit trail** of every notification Zabbix attempted to send,
  independent of the Action log retention period in the database.
- As a **debugging aid** when building more complex integrations, you can see
  exactly what data Zabbix is sending before you point a script at a real endpoint.

### Step 1 — Create the Script

Create the script file:

```bash
vi /usr/lib/zabbix/alertscripts/alert_logger.sh
```

Paste the following content:

```bash
#!/bin/bash
# alert_logger.sh
# Writes every Zabbix alert notification to a structured log file.

# ── Arguments ────────────────────────────────────────────────────────────────
# Zabbix passes the three parameters we define in the media type as positional
# arguments. We assign them to named variables immediately so the rest of the
# script is readable.
SENDTO="$1"       # The value from the user's "Send to" field
SUBJECT="$2"      # The notification subject
MESSAGE="$3"      # The full notification body

# ── Configuration ─────────────────────────────────────────────────────────────
# The file we write to. The zabbix user must be able to write here.
# /var/log/zabbix/ already exists and is owned by the zabbix user on a standard
# installation.
LOG_FILE="/var/log/zabbix/alert_logger.log"

# ── Timestamp ─────────────────────────────────────────────────────────────────
# $(date ...) runs the date command and substitutes its output inline.
# +"%Y-%m-%d %H:%M:%S" formats it as: 2026-03-30 14:22:05
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# ── Write the log entry ───────────────────────────────────────────────────────
# The >> operator appends to the file (a single > would overwrite it each time).
# The lines between the two EOF markers are a "here document" — a convenient
# way to write a multi-line block of text without lots of echo statements.
# Each variable is expanded when the line is written.
cat >> "$LOG_FILE" << EOF
────────────────────────────────────────────────────
Timestamp : $TIMESTAMP
Send To   : $SENDTO
Subject   : $SUBJECT
Message   :
$MESSAGE
EOF

# ── Exit cleanly ──────────────────────────────────────────────────────────────
# Exit code 0 tells Zabbix the notification was delivered successfully.
# Any non-zero exit code causes Zabbix to mark the attempt as failed and retry.
exit 0
```

Save and close the file.

### Step 2 — Set Permissions

```bash
chown root:zabbix /usr/lib/zabbix/alertscripts/alert_logger.sh
chmod 750 /usr/lib/zabbix/alertscripts/alert_logger.sh
```

Verify:

```bash
ls -l /usr/lib/zabbix/alertscripts/alert_logger.sh
```

Expected output:

``` bash
-rwxr-x--- 1 root zabbix ... alert_logger.sh
```

### Step 3 — Verify the Log Directory

The script writes to `/var/log/zabbix/`. On a standard Zabbix installation this
directory already exists and is owned by the `zabbix` user.

Confirm:

```bash
ls -ld /var/log/zabbix/
```

Expected output:

``` bash
drwxr-xr-x 2 zabbix zabbix ... /var/log/zabbix/
```

If the directory does not exist, create it:

```bash
mkdir -p /var/log/zabbix/
chown zabbix:zabbix /var/log/zabbix/
chmod 755 /var/log/zabbix/
```

### Step 4 — Test the Script Manually

Before touching the Zabbix frontend, test the script directly as the `zabbix` user.
This confirms the permissions are correct and the script runs without errors,
independently of Zabbix itself.

```bash
sudo -u zabbix /usr/lib/zabbix/alertscripts/alert_logger.sh \
  "ops-team" \
  "Problem: High CPU on web01" \
  "Host web01 has exceeded 90% CPU for 5 minutes."
```

Then check the log:

```bash
cat /var/log/zabbix/alert_logger.log
```

You should see:

```bash
────────────────────────────────────────────────────
Timestamp : 2026-03-30 14:22:05
Send To   : ops-team
Subject   : Problem: High CPU on web01
Message   :
Host web01 has exceeded 90% CPU for 5 minutes.
```

If the file is empty or does not exist, the most likely cause is a permissions
problem, or things like SeLinux or AppArmor. Run the command above without
`sudo -u zabbix` as root first to confirm the script itself works, then re-check
the ownership of both the script and the
log directory.

### Step 5 — Create the Media Type in Zabbix

Go to **Alerts → Media types** and click **Create media type**.

| Field | Value |
|:--- |:--- |
| Name | `Alert Logger` |
| Type | `Script` |
| Script name | `alert_logger.sh` |
| Description | `Writes all alert notifications to /var/log/zabbix/alert_logger.log` |

Under **Script parameters**, click **Add** three times and enter one value per line:

| Parameter | Value |
|:--- |:--- |
| 1 | `{ALERT.SENDTO}` |
| 2 | `{ALERT.SUBJECT}` |
| 3 | `{ALERT.MESSAGE}` |

The order matters, these become `$1`, `$2`, and `$3` in the script exactly as
listed.

Leave **Concurrent sessions** at `1`, **Attempts** at `3`, and **Attempt interval**
at `10s`.

Under **Message templates**, add a template for the **Problem** event type:

Subject:

```bash
Problem: {EVENT.NAME}
```

Message body:

``` bash
Host       : {HOST.NAME}
Severity   : {EVENT.SEVERITY}
Problem    : {EVENT.NAME}
Started    : {EVENT.DATE} {EVENT.TIME}
Event ID   : {EVENT.ID}
Operational: {EVENT.OPDATA}
URL        : {EVENT.URL}
```

Add a second template for **Problem recovery**:

Subject:

``` bash
Resolved: {EVENT.NAME}
```

Message body:

```bash
Host       : {HOST.NAME}
Severity   : {EVENT.SEVERITY}
Problem    : {EVENT.NAME}
Resolved   : {EVENT.RECOVERY.DATE} {EVENT.RECOVERY.TIME}
Duration   : {EVENT.DURATION}
Event ID   : {EVENT.ID}
URL        : {EVENT.URL}
```

Click **Add** to save the media type.

### Step 6 — Assign to a User

Go to **Users → Users**, open your user, click the **Media** tab, and click **Add**.

| Field | Value |
|:--- |:--- |
| Type | `Alert Logger` |
| Send to | `ops-team` |
| When active | `1-7,00:00-24:00` |
| Use if severity | all severities checked |
| Status | Enabled |

The value in **Send to** becomes `$1` (`SENDTO`) inside the script. In this example
the script does not use it for routing, but it is written to the log entry so you
can see which user or team the alert was destined for — useful when multiple users
share the same log file.

Click **Add** then **Update**.

### Step 7 - Verify an Action Is in Place

The media type and user assignment are ready, but Zabbix will not call the script
until an Action decides to send a notification. Go to `Alerts` → `Actions`
→ `Trigger actions` and confirm that at least one enabled action exists that:

- Has the Operation set to Send message
- Targets the user you assigned the Alert Logger media type to (either directly
  or via a group they belong to)
- Matches the conditions under which your test trigger will fire (severity, host
  group, etc.)

If no such action exists, create one. Without it, the trigger in Step 8 will fire
and appear in the problem list, but the Action log will be empty and the script
will never be called.

### Step 8 — Trigger a Test Alert

The quickest way to produce a real notification is a dummy trigger. Go to
**Data collection → Hosts**, choose any monitored host, open its **Triggers** tab,
and click **Create trigger**.

| Field | Value |
|:--- |:--- |
| Name | `Test alert logger` |
| Severity | `Warning` |
| Expression | `last(/your-host/system.uptime)>0` |

Replace `your-host` with the actual host name. `system.uptime` returns the number
of seconds the host has been running. It will always be greater than zero on a
live host, so the trigger fires immediately and stays in a problem state
continuously, which is exactly what you want for a one-off test.

Click **Add** to save. Within a few seconds the trigger should fire. Go to
**Reports → Action log** and confirm an entry appears with status **Sent**.

!!! note

    For this to work you need the standard `Zabbix server` working with the
    standard templates still applied to your host. If not create a new item with
    the item key system.uptime.

Then check the log file on the Zabbix server:

```bash
tail -f /var/log/zabbix/alert_logger.log
```

You should see a new entry for the test alert. Once confirmed, disable or delete
the dummy trigger.

---

## Log Rotation

The log file will grow indefinitely without rotation. On most linux distros
`logrotate` is the standard tool for this. Create a configuration file:

```bash
vi /etc/logrotate.d/zabbix-alert-logger
```

```bash
/var/log/zabbix/alert_logger.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 0640 zabbix zabbix
}
```

Each directive does the following:

- `daily`: rotate once per day.
- `rotate 30`: keep 30 days of compressed archives before deleting the oldest.
- `compress`: gzip old log files to save disk space.
- `missingok`: do not raise an error if the log file does not exist yet.
- `notifempty`: skip rotation if the file is empty (no alerts that day).
- `create 0640 zabbix zabbix`: after rotating, create a fresh empty log file
  with the correct ownership so the script can continue writing immediately.

Test the configuration:

```bash
logrotate -d /etc/logrotate.d/zabbix-alert-logger
```

The `-d` flag runs a dry run and prints what would happen without actually rotating
anything. Confirm the output references the correct file, then let the system
scheduler handle it going forward.

---

## Security Considerations

A few points worth keeping in mind when writing or deploying alert scripts:

**Scripts run as the `zabbix` user.** This is an unprivileged system account.
If your script needs to do something that requires elevated privileges — writing
to a directory owned by root, restarting a service — you will need to grant
specific `sudo` permissions for that action only, via `/etc/sudoers.d/`. Never
run the Zabbix server as root to work around this.

**Never place scripts outside `AlertScriptsPath`.** Zabbix enforces this boundary
intentionally. If you find yourself needing to call a script elsewhere on the
filesystem, place a thin wrapper inside `AlertScriptsPath` that calls the other
script, and ensure the `zabbix` user has permission to execute it.

!!! warning

    Do not make scripts world-writable. If any unprivileged user on the system
    can modify a script in AlertScriptsPath, they could insert arbitrary code
    that the Zabbix server will execute. The root:zabbix ownership with chmod
    750 described above prevents this entirely.

!!! tip

    **Treat `{ALERT.MESSAGE}` as untrusted input.** If your script passes the message
    body to a shell command, an external API, or a database query, sanitise it
    first. In a simple logging script this is not a concern, but in more complex
    integrations it matters.

---

## Extending the Example

Once the basic logger is working, several natural extensions become straightforward:

- **Route by severity.**: Parse `$2` (the subject) for keywords like `DISASTER`
  or `HIGH` and write those entries to a separate file or send an additional
  notification.
- **Push to syslog.**: Replace the `cat >> $LOG_FILE` block with
  `logger -t zabbix-alert "$SUBJECT: $MESSAGE"` to send alerts into the system
  journal, where they become visible in `journalctl` and can be forwarded by
  `rsyslog` or `fluentd`.
- **Call a secondary script.**: Once you are confident the data Zabbix passes
  looks correct (confirmed by inspecting the log), replace or supplement the
  logging block with a `curl` call to a REST API, passing `$MESSAGE` as the
  request body.

The logger pattern, write first, act second. This is a reliable development workflow
for any custom script integration.

---

## Useful URLs

- https://www.zabbix.com/documentation/current/en/manual/config/notifications/media/script
- https://www.zabbix.com/documentation/current/en/manual/appendix/macros/supported_by_location
- https://www.gnu.org/software/bash/manual/bash.html
- https://linux.die.net/man/8/logrotate

---

## Questions

1. What exit code must a script return to tell Zabbix the notification was
   delivered successfully? What happens if it returns a different value?

2. Where must alert scripts be placed on the Zabbix server, and why does Zabbix
   enforce this restriction?

3. In the media type configuration, you define three script parameters:
   `{ALERT.SENDTO}`, `{ALERT.SUBJECT}`, and `{ALERT.MESSAGE}`. Inside the script,
   what are the corresponding variable names for each?

4. You run the alert logger script manually as the `zabbix` user and it works
   correctly, but no log entries appear when a real Zabbix alert fires. The Action
   log shows the notification status as **Sent**. What is the most likely
   explanation?

5. A colleague suggests making the alertscripts directory writable by the `zabbix`
   user so the scripts can update themselves. Why is this a bad idea?

6. You want the alert logger to write **Disaster** severity alerts to a separate
   file so they are never mixed with lower-severity entries. Which argument
   (`$1`, `$2`, or `$3`) would you inspect in the script to determine severity,
   and why?
