# Leveraging custom items for extending the Zabbix environment

You've now mastered the core concepts of Zabbix: collecting data with items,
alerting with triggers, dynamically discovering resources with LLD, and automatically
registering new hosts. At this point Zabbix is already a very capable monitoring
system, but it doesn't stop there.

One of Zabbix's greatest strengths is its extensibility. Instead of being limited
to what's available out of the box, you can tailor the platform to your exact
environment and requirements. In this chapter we explore three of the most practical
and powerful ways to extend Zabbix:

## Frontend Scripts

Learn how to run custom scripts directly from the Zabbix frontend with just a
few clicks. This feature is incredibly useful for quick troubleshooting, executing
maintenance tasks, gathering on-the-fly diagnostics, or integrating external
tools, all without leaving the Zabbix web interface.

## User Parameters

Dive deep into extending the Zabbix Agent itself. With User Parameters you can
create your own custom item keys to monitor virtually anything: application-specific
metrics, log files, databases, hardware sensors, business processes, or complex
calculations. This is where Zabbix truly becomes infinitely flexible.

## MCP Server

Connect AI applications to Zabbix through the Model Context Protocol (MCP).
We'll cover how to configure the Zabbix MCP server and control which tools
those applications can use.

By mastering Frontend Scripts, User Parameters, and the MCP server, you move
from being a Zabbix *user* to a Zabbix *builder*, capable of shaping the system to perfectly fit your
infrastructure and operational needs.
