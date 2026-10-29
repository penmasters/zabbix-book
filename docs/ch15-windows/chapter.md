# Monitoring Windows

Windows remains one of the most widely deployed operating systems in enterprise
environments. From Active Directory domain controllers and Microsoft SQL Server
to IIS web servers, file servers, and end-user workstations, Windows systems
are a critical part of many IT infrastructures. Monitoring them effectively
requires understanding not only Zabbix, but also the Windows-specific
technologies that expose system health and performance.

Unlike Linux, Windows provides several native interfaces for collecting
monitoring data. Performance Counters expose detailed performance metrics, the
Windows Event Log records operating system and application events, the Service
Control Manager reports service health, while Windows Management Instrumentation
(WMI) and the Windows Registry provide access to hardware, software, and
configuration information. Zabbix integrates directly with these interfaces
through dedicated Windows item keys, allowing you to collect rich monitoring
data without relying on external scripts or third-party tools.

In this chapter, you'll learn how to monitor Windows systems using Zabbix
Agent 2, work with Performance Counters, Event Logs, Windows Services, WMI,
and Registry monitoring, and understand when to use each approach. Along the
way, you'll also learn practical troubleshooting techniques and best practices
for building efficient and maintainable Windows monitoring solutions.
