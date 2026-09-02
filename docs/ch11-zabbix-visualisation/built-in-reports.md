---
description: |
  Learn how to use the built-in reports in Zabbix 8.0 to review system
  status, availability, trigger activity, audit information and
  notifications.
tags:
- beginner
---

# Using the Zabbix built-in reports

Zabbix collects a large amount of operational information while
monitoring your environment. While dashboards are generally used to
visualize current monitoring data, the **Reports** section provides
several built-in views that help administrators analyze the Zabbix
environment itself, historical availability, trigger activity,
configuration changes and notifications.

The available reports can be found under:

**Reports**

The Reports menu in Zabbix 8.0 contains the following sections:

-   System information
-   Scheduled reports
-   Availability report
-   Top 100 triggers
-   Audit log
-   Action log
-   Notifications

These reports serve different purposes. Some are useful for day-to-day
monitoring, while others are particularly valuable when troubleshooting
configuration changes, notification problems or the overall health of
the Zabbix installation.

!!! note

    Access to individual reports depends on the user type and permissions assigned through the user's role. Some administrative reports are therefore not visible to every Zabbix user.

------------------------------------------------------------------------

## System information

The **System information** report provides a quick overview of the
Zabbix installation and is one of the first places an administrator can
look when checking the general state of a Zabbix server.

Navigate to:

**Reports \> System information**

The page displays information about the Zabbix server and frontend
together with statistics about the monitored environment.

Among other information, the report shows:

-   Zabbix server ID
-   Zabbix server status
-   Zabbix server version
-   Zabbix frontend version
-   number of hosts
-   number of templates
-   number of items
-   number of triggers
-   number of users
-   required server performance in new values per second
-   Zabbix server high availability status

The host, item and trigger statistics are further divided into states
such as monitored, disabled and unsupported where applicable.

![ch11.37-system-information.png](ch11.37-system-information.png)

_ch11.37 system-information_

### Required server performance

One particularly useful value is:

**Required server performance, new values per second**

This is an estimate of the number of new values that Zabbix is expected
to process every second based on the configured monitoring.

It can provide a quick indication of the size of the monitoring
workload, but it should not be interpreted as the actual number of
values currently being processed.

For actual processing statistics, Zabbix internal items such as:

``` text
zabbix[wcache,values,all]
```

are more appropriate.

The value shown in System information is therefore best used as a
configuration-based estimate rather than as a performance measurement.


### Version information

Zabbix 8.0 can also display information about the installed server and
frontend versions and indicate whether a newer release is available.

This information depends on the Zabbix software update check being
enabled.

### High availability

When Zabbix server high availability is enabled, an additional section
displays the configured HA nodes.

Information includes:

-   node name
-   address
-   last access
-   status

A node can, for example, be displayed as **Active**, **Standby**,
**Unavailable** or **Stopped**.

This makes the System information page a useful first check when
investigating the state of a Zabbix server HA cluster.

!!! tip

    System information can also be exported to a JSON file. This can be useful when documenting an installation or collecting basic system information during troubleshooting.

------------------------------------------------------------------------

## Scheduled reports

The **Scheduled reports** section is used to automatically generate PDF
versions of Zabbix dashboards and distribute them by email.

Navigate to:

**Reports \> Scheduled reports**

A scheduled report can generate a dashboard report on a daily, weekly,
monthly or yearly schedule.

The overview shows information such as the report owner, reporting
period, generation frequency, last delivery and current status.

Scheduled reports require additional components, including the **Zabbix
Web Service** and a supported browser used to render the dashboard.

Because scheduled reports require additional installation and
configuration, they are covered separately in:

**Creating automated PDF reports**

------------------------------------------------------------------------

## Availability report

The **Availability report** provides a historical view of how long
triggers have remained in the **OK** and **Problem** states.

Navigate to:

**Reports \> Availability report**

For every displayed trigger, Zabbix calculates the percentage of time
spent in each state.

For example, a trigger could show:

``` text
OK       99.95%
Problem   0.05%
```

This makes the report useful for quickly investigating the historical
availability of monitored components.

The report can operate in two modes:

-   **By host**
-   **By trigger template**

When using **By host**, the report can be filtered by host groups and
hosts.

When using **By trigger template**, results can be filtered using
template groups, templates, template triggers and host groups.

Clicking a trigger name provides access to the latest events for that
trigger.

The **Show** link in the Graph column can also display the availability
information graphically, with bars representing the OK and Problem time.

### Availability is based on trigger state

**Important:** this report only shows how long a trigger spent in OK or Problem
state. It is not a business SLA and it does not equal the availability of a
whole service. An ICMP trigger and an application trigger on the same host
can easily produce very different percentages depending on how the triggers
were written.

The result depends directly on how the trigger has been designed.

For example, an ICMP availability trigger and an application
availability trigger can produce very different availability percentages
for the same host.

For formal service availability calculations, Zabbix also provides the
Services and SLA functionality.

### Maintenance periods

Maintenance periods are also important when interpreting this report.

Maintenance does not automatically remove time from the Availability
report. Maintenance configured with normal data collection can still
result in trigger state changes and therefore influence the calculated
percentages.

A maintenance period configured with **No data collection** stops data
collection for the affected entities, preventing new problems from being
generated from that data during the maintenance period.

Keep this behavior in mind when using Availability reports for
historical analysis.

![ch11.38-availability-report.png](ch11.38-availability-report.png)

_ch11.38 availability-report_

------------------------------------------------------------------------

## Top 100 triggers

The **Top 100 triggers** report identifies the triggers that generated
the highest number of problems during a selected period.

Navigate to:

**Reports \> Top 100 triggers**

This report is useful for finding monitoring objects that generate
problems repeatedly.

The results can be filtered by:

-   host group
-   host
-   problem name
-   tags
-   trigger severity

A time period selector determines the period over which the number of
problems is calculated.

Both the host and trigger names are interactive. The host name provides
access to the host menu, while the trigger name provides links to
information such as its latest events and related monitoring data.

### Finding noisy triggers

This report is especially useful for spotting noisy triggers. A trigger at the
top of the list is not necessarily the most critical problem, it just means it
fired a lot of events in the selected period. That often points to overly
sensitive thresholds, missing hysteresis, or monitoring that doesn't really
help operations.

This can reveal configuration that deserves further investigation, such
as:

-   unstable monitored services
-   interfaces repeatedly changing state
-   thresholds that are too sensitive
-   intermittent connectivity
-   triggers that require better hysteresis
-   monitoring that produces little operational value

The report is therefore useful not only for finding infrastructure
problems, but also for improving the quality of the monitoring
configuration itself.

![ch11.39-triggers-100.png](ch11.39-triggers-100.png)

_ch11.39 triggers Top 100.png_

------------------------------------------------------------------------

## Audit log

The **Audit log** records user and system activity within Zabbix.

Navigate to:

**Reports \> Audit log**

The report contains information including:

-   time
-   user
-   source IP address
-   affected resource
-   resource ID
-   action
-   recordset ID
-   details

Recorded actions can include operations such as adding, updating and
deleting configuration, logins and logouts, failed logins, executing
operations and clearing history.

### Tracking configuration changes

The Audit log is particularly valuable when investigating configuration
changes.

Consider a situation where monitoring for a host suddenly changes. An
administrator can use the Audit log to investigate whether someone
recently modified the host, template, item, trigger or another related
configuration object.

The **Details** field can show what was changed, making the Audit log
one of the most important troubleshooting tools for environments with
multiple Zabbix administrators.

### Recordset ID

Some operations result in multiple audit records.

For example, linking a template to a host can affect multiple inherited
objects. Zabbix assigns records created as part of the same operation a
common **Recordset ID**.

Filtering on this ID makes it easier to view the related changes as a
single administrative operation.

### Filtering and exporting

Audit records can be filtered using information including:

-   user
-   resource
-   resource ID
-   Recordset ID
-   IP address
-   action

A time period can also be selected.

Audit log records can be exported to CSV. When a filter is active, the
export contains the filtered records.

!!! warning

    Audit records are only collected when audit logging is enabled under **Administration > Audit log**. If audit logging is disabled, user and system activities are not recorded in the audit log database records.

------------------------------------------------------------------------

## Action log

The **Action log** shows operations that Zabbix executed as part of
configured actions.

Navigate to:

**Reports \> Action log**

These operations can include:

-   notifications
-   remote commands

For each operation, the report can display information such as:

-   time
-   action
-   media type
-   recipient
-   message or command
-   status
-   additional information

Possible operation states include **In progress**, **Sent**,
**Executed** and **Failed**.

### Troubleshooting notifications

The Action log is one of the most useful places to investigate
notification problems.

For example, suppose a trigger generated a problem and an administrator
expected an email notification, but the email was never received.

The Action log can help determine whether Zabbix attempted the
notification and whether the operation succeeded or failed.

The report can be filtered by:

-   recipient
-   action
-   media type
-   status
-   message or remote command content

This allows administrators to narrow a large action history down to a
specific notification or action.

If an operation failed, the **Info** column can contain information
about the failure.

### Audit log versus Action log

The Audit log and Action log serve different purposes and should not be
confused.

**Audit log**

Answers questions such as:

``` text
Who changed this configuration?
When was this host modified?
Which user deleted this object?
Where did this login originate?
```

**Action log**

Answers questions such as:

``` text
Did Zabbix attempt to send the notification?
Which action generated it?
Which media type was used?
Did the notification or remote command succeed?
```

The Audit log focuses primarily on activity and configuration changes
within Zabbix, while the Action log focuses on operations executed by
the Zabbix action system.

The Action log can also be exported to CSV.

------------------------------------------------------------------------

## Notifications

The **Notifications** report provides an aggregated view of the number
of notifications sent to Zabbix users.

Navigate to:

**Reports \> Notifications**

Unlike the Action log, this report is not intended to show the details
of individual messages. Instead, it provides an overview of notification
volume per user.

The report can be viewed for:

-   a specific media type or all media types
-   daily, weekly, monthly or yearly periods
-   a selected year

Each user is represented separately, allowing administrators to see how
notifications are distributed between users over time.

### Understanding notification volume

This report can be useful when reviewing an alerting configuration.

For example, a user receiving significantly more notifications than
expected may indicate that:

-   the user participates in many action operations
-   a user group is included in several actions
-   the environment is generating a high number of events
-   notification rules may require further review

The Notifications report shows the volume of notifications, while the
Action log should be used when the details or delivery status of
individual operations need to be investigated.

------------------------------------------------------------------------

## Choosing the right report

The reports overlap in some areas, but each answers a different
operational question.

  -----------------------------------------------------------------------
  Report                              Typical question
  ----------------------------------- -----------------------------------
  System information                  What is the current state and size
                                      of this Zabbix installation?

  Scheduled reports                   Which dashboard reports are
                                      generated and distributed
                                      automatically?

  Availability report                 How long was this trigger in an OK
                                      or Problem state?

  Top 100 triggers                    Which triggers generated the most
                                      problems?

  Audit log                           Who or what changed something in
                                      Zabbix?

  Action log                          What happened when Zabbix executed
                                      an action?

  Notifications                       How many notifications were sent to
                                      each user?
  -----------------------------------------------------------------------

Learning which report answers which question makes troubleshooting
considerably faster.

For example, when investigating a missing notification, checking the
Notifications report alone provides little information about the
individual message. The Action log is the more appropriate starting
point.

Similarly, when investigating why a trigger suddenly behaves
differently, the Top 100 triggers report may reveal that it is
generating many events, but the Audit log can help determine whether its
configuration was recently changed.

------------------------------------------------------------------------

## Conclusion

The built-in Zabbix reports provide several useful views of information
that is already available inside the monitoring system.

The **System information** report provides a quick overview of the
Zabbix installation itself. **Availability report** and **Top 100
triggers** help analyze historical monitoring behavior. **Audit log**
records administrative and system activity, while **Action log**
provides detailed information about notifications and remote commands
executed by actions. Finally, the **Notifications** report provides an
aggregated view of notification volume per user.

These reports do not replace dashboards, Services, SLAs or external
reporting tools. Instead, they provide focused operational views that
are especially useful for administration, troubleshooting and reviewing
the behavior of a Zabbix environment.

Knowing where to look is often more important than the amount of
information available. The Reports menu provides several of those
starting points directly in the Zabbix frontend.

## Questions

1.  What is the difference between the estimated required server
    performance and the actual number of values processed by Zabbix?
2.  Why should the Availability report not automatically be interpreted
    as an SLA report?
3.  Which report would you use to identify triggers that repeatedly
    generate problems?
4.  Which report can help determine who modified a Zabbix configuration
    object?
5.  What is the purpose of the Recordset ID in the Audit log?
6.  Which report would you use to troubleshoot a failed notification?
7.  What is the difference between the Action log and the Notifications
    report?
8.  How do maintenance periods affect the Availability report?
