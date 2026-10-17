---
description: |
    If you plan on installing Zabbix Agent2 in a Windows environment, this article is for you!
    Learn from past mistakes to make agent installations seamless and upgrades even easier
tags: [beginner]
---

# Preface

As the previous chapter has stated, the Zabbix Agent 2 service is the recommended install 
for your fleet of Windows Operating Systems. Whether it is a fleet of Windows Servers,
Windows Desktops or both, this article will apply. This page will mainly focus around the
configuration file structure of the agent you install on any Windows OS, in addition to
deploying the agent with initial settings you likely will need or want. 

It is with the highest intentions that this will prevent uneeded overhead when it comes 
time for agent upgrades, or even auto-registration of new/current servers.

# Real-World Example Config

```
# CUSTOM CONFIG FULL
# Place this into C:\Program Files\Zabbix Agent 2
# and then start/restart your agent

# Server Passive Config
Server=zabbixnode1.somedomain.org,zabbixnode2.somedomain.org

# Server Active Config
ServerActive=zabbixnode1.domain.org;zabbixnode2.domain.org

# Preferably, you should fully qualify your hostname, but that is a personal preference of the author
Hostname=hostnameoftheserverlowercase.domain.com

# Include any extra config directories
Include=C:\\Program Files\\Zabbix Agent 2\\zabbix_agent2.d\\

# Required to be in agent conf
ControlSocket=\\.\pipe\agent.sock

# Forces the agent to get its config on start immediately
ForceActiveChecksOnStart=1

# How often list of active checks is refreshed, in seconds.
RefreshActiveChecks=300

# Include configuration files for plugins
Include=.\zabbix_agent2.d\plugins.d\*.conf
Include=C:\\ProgramData\\Zabbix-ext\\conf.d\\*.conf

# Log File Config
LogFile=C:\Program Files\Zabbix Agent 2\zabbix_agent2.log

# Log File Size
LogFileSize=1024
```

