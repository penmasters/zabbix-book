---
description: |
    This chapter explains how to effectively use Zabbix's built-in maintenance 
    periods to manage planned downtime without triggering false alerts. Zabbix
    allows you to schedule maintenance windows for hosts, host groups. This is 
    perfect for software updates, hardware replacements, or testing scenarios.
    You'll learn how to configure maintenance types (with or without data collection),
    define time periods, and apply them to specific targets. Using this feature
    correctly ensures your monitoring data remains clean, avoids alert noise,
    and helps teams stay focused during routine operations. Mastering maintenance
    tasks in Zabbix is essential for accurate alerting.
---

# Maintenance

## The Purpose of Maintenance Periods

A **Maintenance Period** in Zabbix is a defined time window for planned work
(e.g., software updates, configuration changes). Its primary goal is to **suppress
problem notifications (alerts)** for the affected hosts or applications to prevent
alert fatigue.

During maintenance, Zabbix still monitors systems, but alert actions (emails,
tickets, etc.) are typically paused.

---

## Key Maintenance Configuration Options

### 1. Maintenance Type

This defines how Zabbix handles data during the maintenance window:

| Type | Description | Trigger Processing | Data Collection | Best Used For |
| :--- | :--- | :--- | :--- | :--- |
| **With data collection** | Data is collected as usual, but **problem notifications are suppressed** (via a default Action condition). | **Processed** | **Collected** | Routine updates where data continuity is important. |
| **No data collection** | Data collection is completely paused for the items on the maintained host(s). | **Not Processed** | **Ignored/Not Collected** | Major hardware upgrades or OS reloads where the host is completely unavailable. |

### 2. Time Window Definition (`Active Since` / `Active Till`)
These dates define the **overall lifespan** (outer bounds) of the maintenance rule.
The specific execution times are defined in the **Periods** tab.

### 3. Maintenance Periods (The Schedule)

This tab defines the precise scheduling:

* **One Time Only:** A single, non-recurring window.
* **Daily:** A recurring schedule every *N* days.
* **Weekly:** A recurring schedule on specific days of the week.
* **Monthly:** The most flexible, allowing selection by **Day of Month** or
  **Day of Week** within a month (e.g., the last Sunday).

### 4. Scope (Hosts and Groups)

You define the scope by selecting the specific **Hosts** and/or **Host Groups**
that the rule applies to.

### 5. Problem Tag Filtering (Advanced Suppression)

This allows you to suppress **only specific problems** during maintenance by matching **Problem Tags** (e.g., `service:database`), which is useful if you need to be alerted to hardware failures during software maintenance.

---

## Time Zones and Maintenance Schedule Logic

Understanding time zones is critical for reliable recurring maintenance:

### Time Zone Rules for Maintenance Periods

| Period Type | Time Zone Used for Execution | Displayed Time Zone | Implication |
| :--- | :--- | :--- | :--- |
| **One Time Only** | **User's Browser Time Zone** | **User's Browser Time Zone** | The absolute UTC time is stored based on the user's view. |
| **Daily, Weekly, Monthly** | **Zabbix Server Time Zone** | **User's Browser Time Zone** | The recurring logic (e.g., "start at 02:00") is executed based on the time zone configured on the **Zabbix Server operating system**. |
| **`Active since` / `Active till`** | **User's Browser Time Zone** | **User's Browser Time Zone** | These bounding dates are based on the time zone of the user who configured them. |

???+ info
    **It's Good Practice:** to use a common time zone (e.g., **UTC**) across the
    Zabbix Server, the database, and the PHP frontend configuration for predictable
    results, especially with recurring periods and DST changes. Another way is
    to add a clock widget to the dashboard with the `Zabbix server` time.

---

## Backend Process and Configuration

### The Timer Process: The Engine of Maintenance

The process responsible for calculating and initiating maintenance periods is the
**Zabbix Timer process** (controlled by `StartTimers`).

1. **Recalculation Interval (The Check):** The Timer process checks whether a host's
   status must change to/from maintenance at **0 seconds of every minute**.
   * This means the maintenance window will start and stop with a **maximum latency
     of 60 seconds** after the scheduled time.
2. **Configuration Cache:** Maintenance definitions are stored in the database
   and loaded into the Zabbix Server's **Configuration Cache**. The Timer
   uses this cache to determine host status.

### Key Zabbix Server Configuration (`zabbix_server.conf`)

The overall efficiency of maintenance logic depends on these parameters:

| Parameter | Zabbix 7.4 Default Value | Purpose in Relation to Maintenance |
| :--- | :--- | :--- |
| **`CacheUpdateFrequency`** | **10** | Defines how often (in seconds) the Zabbix Server updates its configuration cache from the database. A change to a maintenance period will take effect within **10 seconds**. |
| **`StartTimers`** | `1` | The number of **Timer processes** to start. These are the processes that execute the maintenance calculation. |
| **`CacheSize`** | `8M` | The size of the configuration cache. Insufficient size can impact the Timer's ability to quickly process status changes in large environments. |

---

## Example: Monthly Recurring Maintenance Setup

**Scenario:** Routine updates on all **Database Servers** on the **last Sunday of
every month** at midnight for **2 hours**. Only suppress problems related to the
**Database Service**.

| Field/Tab | Setting | Explanation |
| :--- | :--- | :--- |
| **Name** | `Monthly DB Patching - Last Sunday` | Descriptive name. |
| **Maintenance type** | **With data collection** | Continue data collection. |
| **Periods Tab** | **Period type:** `Monthly` | Selects the schedule type. |
| **Periods Tab** | **Day of week:** `Sunday` / **Week of month:** `Last` | Defines the precise day. |
| **Periods Tab** | **Start time:** `00:00` / **Duration:** `2 hours` | Defines the 00:00 to 02:00 window. |
| **Hosts & Groups Tab** | **Host Group:** `Database Servers` | Defines the scope. |
| **Tags Tab** | **Tag evaluation:** `AND` | Ensures both conditions (maintenance and tag) are met for suppression. |
| **Tags Tab** | **Tag:** `service` **Operator:** `=` **Value:** `database` | **Crucial:** Only problems with the tag `service:database` are suppressed. |

### Execution Summary

1. At 00:00 (Server Time Zone), the **Timer** changes the host status to "Maintenance."
2. Data collection continues.
3. Any problem event is filtered by the Action: If the host is in maintenance AND
   the problem has the tag `service:database`, the alert is **suppressed**.
4. If a hardware problem (e.g., no matching tag) occurs, the alert **will still
   be sent**, as only the database service issues are suppressed.
5. At 02:00, the Timer ends the maintenance, and all alerting resumes.

---

## API Integration for Maintenance Management

For professional Zabbix monitoring setups that require dynamic scheduling, integration
with change management workflows, or complex multi-system orchestration, the
**Zabbix API** is the primary tool for managing maintenance periods.

The key method used for maintenance management is **`maintenance.create`** (and
corresponding `.get`, `.update`, and `.delete` methods).

### Why Use the API for Maintenance?

* **ITSM Integration:** Allows automated creation of maintenance windows when
  a Change Request (CR) is approved in an external system (e.g., ServiceNow, Jira),
  ensuring alerts are suppressed only during authorized work.
* **Automation:** Facilitates the management of maintenance templates using
  infrastructure-as-code tools (like Ansible or Terraform).
* **Dynamic Scheduling:** Enables the creation of immediate, short-term maintenance
  windows directly from operational scripts.

### Key Parameters for `maintenance.create`

When calling the `maintenance.create` method, you send a JSON-RPC request containing
several crucial parameters that mirror the frontend configuration:

| API Parameter | Frontend Equivalent | Description |
| :--- | :--- | :--- |
| **`name`** | Name | The name of the maintenance period. |
| **`active_since`** | Active Since | **Unix timestamp** (seconds) when the maintenance rule becomes active. |
| **`active_till`** | Active Till | **Unix timestamp** (seconds) when the maintenance rule is deactivated. |
| **`maintenance_type`** | Maintenance Type | **`0`** for "With data collection" (default), **`1`** for "No data collection". |
| **`hostids`** | Hosts | An array of **Host IDs** (`hostid`) to be put into maintenance. |
| **`groupids`** | Host Groups | An array of **Host Group IDs** (`groupid`) to be put into maintenance. |
| **`timeperiods`** | Periods Tab | An array defining the precise recurring or one-time schedule. |
| **`tags`** | Tags Tab | An array defining the problem tags for filtering (optional). |

### The `timeperiods` Parameter (Schedule Definition)

The **`timeperiods`** array defines the exact schedule. Key elements include:

1. **`timeperiod_type`**: The type of schedule (`0` for one-time, `4` for monthly,
   etc.).
2. **`start_time`**: The time of day the maintenance starts (in seconds from midnight,
   **based on Zabbix Server Time Zone**).
3. **`period`**: The duration of the maintenance window in seconds.
4. **`dayofweek` / `dayofmonth`**: Used for recurring schedules.

---

## Practical Example: Creating Maintenance via the API

This `curl` command demonstrates how to programmatically create the "Last Sunday
of the Month" maintenance window, which runs at midnight for 2 hours, and applies
to host group ID `42`.

???+ note
    You must replace `<ZABBIX_SERVER_IP_OR_DNS>` with your server's address and
    `"your_auth_token"` with an active token from a successful `user.login` API
    call. The **Host Group ID** (e.g., `"42"`) must be known beforehand.

```bash
curl -i -X POST -H 'Content-Type: application/json-rpc' -d '{
    "jsonrpc": "2.0",
    "method": "maintenance.create",
    "params": {
        "name": "Monthly DB Patching via API",
        "active_since": 1748822400,
        "active_till": 1780444800,
        "maintenance_type": 0,
        "groupids": ["42"],
        "timeperiods": [
            {
                "timeperiod_type": 4,   // Monthly schedule
                "start_time": 0,        // Start at 0 seconds past midnight (00:00:00)
                "period": 7200,         // Duration of 2 hours (2 * 3600 seconds)
                "dayofweek": 128        // API code for the Last Sunday
            }
        ]
    },
    "auth": "your_auth_token",
    "id": 1
}' http://<ZABBIX_SERVER_IP_OR_DNS>/api_jsonrpc.php
```

## Conclusion

## Questions

## Useful URLs
