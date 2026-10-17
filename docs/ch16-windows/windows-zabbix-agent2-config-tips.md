---
description: |
    If you plan on installing Zabbix Agent2 in a Windows environment, this article is for you!
    Learn from past mistakes to make agent installations seamless and upgrades even easier for
    a Windows OS fleet.
tags: [beginner]
---

# Preface

As the previous chapter has stated, the Zabbix Agent 2 service is the recommended install 
for your fleet of Windows Operating Systems. Whether it is a fleet of Windows Servers,
Windows Desktops or both, this article will apply. This page will mainly focus around the
configuration file structure of the agent you install on any Windows OS, in addition to
deploying the agent with initial settings you likely will need or want. 

This page assumes you are a Sysadmin of some type and have a means of deploying an
MSI package with PowerShell scripts in steps. Examples of a product that would do this
would be PDQ Deploy or Ivanti Endpoint Manager (formerly Landesk). Though, there is nothing
holding you back if you are a small shop with 20 servers if you are lacking these tools.

It is with the highest intentions that this will prevent uneeded overhead when it comes Use includes 
time for agent upgrades, or even auto-registration of new/current servers. **Real world
examples will be provided.**

# Tips For Configuring Your Zabbix Agent 2 fleet

Performing this config initially will save you loads of time when upgrading the
agent fleet wide, assuming you are using the Microsoft Installer package (MSI)

Tips:
- Write your own config and use it as a template across the environment
- For your `Server=` and/or `ServerActive=` param values, use FQDN/DNS names and all lowercase
- Use PowerShell scripting to your advantage to automate the agent config to set the `Hostname=`
- Use `ForceActiveChecks` and `RefreshActiveChecks` for if utilizing ServerActive
- Use `Include=C:\\some\\path\\*.conf` to move customizations out of the default configuration file
- Use the MSI installer package for deployment
- Prioritize using `ServerActive` templates over `Server` where possible
- Metadata and Autoregistration


Examples of the configuration files and PowerShell scripts are provided if you scroll further.

## Writing your own config

You do not need to use the default `zabbix_agent2.conf` file provided by the installer.
Quite honestly, it's a bit overwhelming. You can trim down the default config file for the 
initial install to make it a bit easier to understand for yourself. 

Just note, that when you go to upgrade via MSI (with `NONMSICONFNAME` param), it will 
merge your initial config file with the default; your parameter values will overwrite 
the default values. By then though, you will not have to worry about the wall of text
in the config file as you will know which params to look for if you have to change them.

Feel free to use the config provided further down this page as a start, but I implore
you to continue reading the next few sections before you do.

## Keep Your `Hostname=` all lowercase

This is mainly important if you are using the `ServerActive` method. Your `Hostname=` value
**must match** the hostname field for your host record.

## Use PowerShell Scripting To Your Advantage

When you write your intial config for `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf`
do so in the context of a template so you can use PowerShell later on to replace the
`Hostname=` value with the current FQDN host name.

Code snippit:
```
$file="C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf"
$FQDNHostName = [System.Net.Dns]::GetHostEntry($env:COMPUTERNAME).HostName
$FQDNHostNameToLower = $FQDNHostName.ToLower()
$FQDNHostNameToLower += ".domain.org" # Your domain name but also lowercase
(Get-Content $file) -replace "Hostname=REPLACEME","Hostname=$FQDNHostNameToLower" | Set-Content $file
```

## Real-World Example Config - Single HA Zabbix Environment

### C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf
```
# C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf
# Place this into C:\Program Files\Zabbix Agent 2
# and then start/restart your agent

# Server Passive Config (Zabbix server/proxy polls this endpoint)
Server=zabbixnode1.somedomain.org,zabbixnode2.somedomain.org

# Server Active Config (Endpoint sends telemetry to Zabbix server/proxy)
ServerActive=zabbixnode1.domain.org;zabbixnode2.domain.org

# Preferably, you should fully qualify your hostname and make it lowercase
# For ServerActive configurations, this field is REQUIRED and is case sensitive! 
Hostname=REPLACEMEBUTLOWERCASE.domain.com

# Include any extra config directories
Include=C:\\Program Files\\Zabbix Agent 2\\zabbix_agent2.d\\
Include=C:\\ProgramData\\Zabbix-ext\\conf.d\\*.conf

# Required to be in agent conf
ControlSocket=\\.\pipe\agent.sock

# Include configuration files for plugins
Include=.\zabbix_agent2.d\plugins.d\*.conf

# Log File Config
LogFile=C:\Program Files\Zabbix Agent 2\zabbix_agent2.log

# Log File Size
LogFileSize=1024
```

### C:\ProgramData\Zabbix-ext\conf.d\active_agent.conf
```
# Forces the agent to get its config on start immediately
ForceActiveChecksOnStart=1

# How often list of active checks is refreshed, in seconds.
RefreshActiveChecks=300
```
