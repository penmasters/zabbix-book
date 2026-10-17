---
description: |
    If you plan on installing Zabbix Agent2 in a Windows environment, this article is for you!
    Learn from past mistakes to make agent installations seamless and upgrades even easier for
    a Windows OS fleet.
tags: [advanced]
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
holding you back if you are a small shop with 20 servers if you are lacking these tools and
need to log in and run some of these steps manually.

It is with the highest intentions that this will prevent uneeded overhead when it comes Use includes 
time for agent upgrades, or even auto-registration of new/current servers. **Real world
examples will be provided.**

# Tips For Configuring Your Zabbix Agent 2 fleet

Performing this method of config initially will save you loads of time when upgrading the
agent fleet wide, assuming you are using the Microsoft Installer package (MSI).

This section is a tl;dr but also an index. The page will go in the order of the
list below.

Tips:
- Write your own config and use it as a template across the environment
- Keep your `Hostname=` field FQDN and lowercase, i.e. `hostname.domain.org`
- Use PowerShell scripting to your advantage to automate the agent config to set the `Hostname=`
- For your `Server=` and/or `ServerActive=` param values, use FQDN/DNS names.
- Use `ForceActiveChecks` and `RefreshActiveChecks` for if utilizing ServerActive
- Use `Include=C:\\some\\path\\*.conf` to move customizations out of the default configuration file
- Metadata and Autoregistration
- Prioritize using `Active` templates over `Passive` where possible
- Use the MSI installer package for deployment

Examples of the configuration files and PowerShell scripts are provided at the bottom

## Writing your own config

You do not need to use the default `zabbix_agent2.conf` file provided by the installer.
Quite honestly, it's a bit overwhelming. You can trim down the default config file for the 
initial install to make it a bit easier to understand for yourself. 

Just note, that when you go to upgrade via MSI (with `NONMSICONFNAME` param), it will 
merge your initial config file with the default; your parameter values will overwrite 
the default values. By then though, you will not have to worry about the wall of text
in the config file as you will know which params to look for if you have to change them.

Each time you change any config file whether it is the main one of pointed to via the
`Include` parameter, you must restart the Zabbix Agent 2 service to apply the changes.

Feel free to use the config provided at the bottom this page as a start, but I implore
you to continue reading the next few sections before you do.

## Keep Your `Hostname=` parameter value lowercase

This is mainly important if you are using the `ServerActive` method. Your `Hostname=` value
**must match** the hostname field for your host record and it is case sensitive or your
Active agent templates for Windows will not work.

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

## Use DNS for `Server=` and `ServerActive=`

This will future proof yourself if you ever run into a situation where the IP address of your
Zabbix server/proxy must change. If you have it set to a FQDN/DNS name, you won't have to
worry about updating your agent configs fleet wide.

There may be an argument to continue monitoring if you wish to withstand a DNS outage and 
continue monitoring..... However, you have much bigger fish to fry if DNS queries are
timing out.

As a Monitoring System Janitor/Sysadmin/SRE this can be a key design decision you make
for the business but I would heavily lean for DNS regardless to prevent future headache

## Utilizing `ForceActiveChecksOnStart` and `RefreshActiveChecks`

These parameters are important for you to understand from a `ServerActive` based
monitoring perspective and are absolutely essential to be in your agent config.

#### ForceActiveChecksOnStart

This param when set to `1` will immediately query the Zabbix server (or Zabbix Proxy)
to check if it has any changes to the configured monitoring templates when the agent
service is started or restarted.

This will also trigger an immediate Low-Level Discovery (LLD) if configured on the
template. It is highly recommended to set this to `1`.

#### RefreshActiveChecks

Similarly to `ForceActiveChecksOnStart`, this parameter is for you to configure
how often the Zabbix Agent2 checks in with a Zabbix Server (or Zabbix Proxy) for
new/updated Active Monitoring templates. This param value is defined in `seconds`
for time. A good value to start would be `RefreshActiveChecks=300`, which would
be 5 minutes.

If you make a change to a monitoring template or host specific macro override,
this will ensure it is picked up. However, if it is a change that requires
Low-Level Discovery (LLD) to run, you must wait for that LLD's threshold
to trigger.

## Using the `Include=` param to your advantage

In the event of the Zabbix Agent 2 upgrade process, via MSI commandline execution, you 
will find that it will do its best to merge the old `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf`
file into the newly generated file.

When this happens, it is important to note even with the `NONMSICONFNAME` param provided
it will not merge/carry-over all the parameters that are set as of 7.0 LTS. In fact, consider the 
`C:\Program Files\Zabbix Agent 2\` directory a "no-go" zone besides what is needed initially 
for the MSI to perform the install. (Server,ServerActive,ControlSock,Hostname will be saved)

Params such as `ForceActiveChecksOnStart` and `RefreshActiveChecks` are not brought over. The 
solution to this is to use `%PROGRAMDATA%` directory to our advantage. Put your custom conf
files in a "Zabbix Extended" directory so they persist even through a full agent uninstall.

### Solution: Split Custom Configurations To Be Under %PROGRAMDATA%

Directory Structure:
```
C:\ProgramData\Zabbix-ext
├── conf.d
│   ├── active_agent.conf
│   ├── custom_config.conf
│   └── metadata.conf
└── scripts
    └── Invoke-ActiveDirectoryChecks.ps1
```

Include one-liner for your `C:\Program Files\Zabbix Agnet 2\zabbix_agent2.conf` that will get
all three configs under the `conf.d` directory
```
Include=C:\\ProgramData\\Zabbix-ext\\conf.d\\*.conf
```

## Metadata and Autoregistration

If you are considering using Metadata strings, these should also be split out (via `Include=`)
especially if you are allowing agent auto-registration.

Metadata can help you control and direct auto-registration actions to apply different templates
based on whatever you put in `HostMetadata`

Some organizations will just use a single string and call it a day. Other organizations may
choose to set their metadata string based on server role. If you are splitting by role,
obviously this will be set per server install or changed after the install.

Please note, if the `HostMetadata` value is ever changed, upon the agent restarting, the
Zabbix Server will kick off an auto-registration action if one is defined for it. If the
`HostMetadata` value never changes for the agent/endpoint's life time, auto-registration
will never execute again after executing for the first time.

Of course, you still must configure auto-registration actions via the Zabbix Server.

Example 1:
```
HostMetadata=WindowsServer
```

Example 2:
```
HostMetadata=WindowsServer_DomainController
```

Example 3:
```
HostMetadata=WindowsServer_MSSQLServer
```

## Active vs Passive Monitoring Templates

If you have made it this far, you are probably under the impression that
the author(s) of this page are heavily leaning towards Active based checks.

There are scenarios for both and thankfully both can be used at the same time.

From a design/architectural standard, Active checks should always be used. However,
In some cases, you may not be able to send data from a DMZ subnet back to internal,
but the policy states connections that originate from internal the internal WAN/LAN
enterprise network may communicate out to the DMZ.

By default, in your agent config you should be prepared for both scenarios by
setting `Server=` (Passive) and `ServerActive=` (Active) by default.

### When to use Active Templates

Anything that requires LLD for discovering disks (C:\\...D:\\ etc...) or Windows
Services, CPU, RAM... all your basic monitoring needs should be placed onto the
agent to collect to take the load off of your Zabbix Server/Proxy.

Active Checks are heavily preferred especially in Windows environments where
querying `perfmon` can be slow during high CPU loads or disk I/O contention.

### When to use Passive Templates

This can be tricky but a specific scenario came up where one organization needed
to monitor the status of a Microsoft SQL Always-On Availability group. The problem
with this is, that consists of multiple hosts that already exist in Zabbix and are
sending information. A cluster can be healthy overall, but a specific node can
be not healthy. How do you monitor the cluster health and the node health?

**The solution:**
The organization created a separate Passive Template to query the Microsoft SQL
Always-On Listeners specifically (which is a Virtual IP that migrates between 
the hosts). They then created new hosts in Zabbix for each listener and used
a Passive check against the Always-On Listener IP. If the Availability group
failed over to a new node, the Zabbix Server/Proxy still is querying the same
IP, even though it's now gathering information about the cluster from a different
server/zabbix agent.

`To do: Put a picture here of the solution to help the readers picture the scenario`

## Using the MSI Installer is Preferred

This goes without saying too much so we won't spend too much time here.

When it comes to deployment of the Zabbix Agent 2, you need an installation package
that can perform the installation & upgrade with a few requirements in mind for Windows:
- Standardized Silent Installations
- Standard Switches for install options
- Standard switch for repair/installing more agent plugins
- Easier Management via PDQ Deploy/Ivanti Endpoint Manager/SCCM/Group Policy/Intune

MSI meets those requirements easily especially with detecting whether it's installed already.

### Example Install Command (General):
```
msiexec.exe /i "C:\temp\zabbix_agent2-7.0.30-windows-amd64-openssl.msi" HOSTNAME="someendpoint.domain.com" SERVER="zabbixnode1.domain.com,zabbixnode2.domain.com" SERVERACTIVE="zabbixnode1.domain.com,zabbixnode2.domain.com" /qn /silent
```

### Example Upgrade Command (You'd use this for upgrades):
```
msiexec.exe /i "zabbix_agent2-7.0.31-windows-amd64-openssl.msi" NONMSICONFNAME="C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf" /qn /silent
```

### Order for MSI/Script Install

If you are going full PowerShell 5.1 (Windows Powershell) for installing the agent, creating the "Zabbix-ext" directory and applying a templated zabbix_agent2.conf go in the following order:

1. Install the Agent via MSI normally, even with fake values to start.
2. Have a Powershell Script create the "Zabbix-ext" directory under `%PROGRAMDATA%` with the `.conf` files
3. Have a final PowerShell script overwrite `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf` with your template + replace the `Hostname=` field
4. Restart the agent to apply all changes
5. Tell Windows to attempt to restart the Zabbix Agent 2 service if it fails

```
# PowerShell One Liner Set service to restart itself if it fails to start.
& "$env:SystemRoot\System32\sc.exe" failure "Zabbix Agent 2" actions= "restart/60000/restart/60000/restart/60000" reset= 86400
```

## Real-World Example Configs - Single Highly-Available Zabbix Environment

This includes the standard configuration in the default location in addition to adding the "Zabbix Extended" directory that persists through agent uninstalls

You would use a Powershell command to first copy/overwrite zabbix_agent2.conf and then use PowerShell to overrite `Hostname=` matching on `Hostname=REPLACEMEBUTLOWERCASE.domain.com`

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

### The "Zabbix-ext" Directory / Config Files / Custom Scripts

Directory Structure of Zabbix-ext under `%PROGRAMDATA%`:
```
C:\ProgramData\Zabbix-ext
├── conf.d
│   ├── active_agent.conf
│   ├── custom_config.conf
│   └── metadata.conf
└── scripts
    └── Invoke-ActiveDirectoryChecks.ps1
```

#### C:\ProgramData\Zabbix-ext\conf.d\metadata.conf
```
# This file shall be placed as such C:\ProgramData\Zabbix-ext\conf.d\metadata.conf
HostMetadata=WindowsServer
```

#### C:\ProgramData\Zabbix-ext\conf.d\active_agent.conf
```
# To be used with the deployment package, this file is intended to be changed
# per server or fleet wide if all agents must have it changed.
# I.E. WindowsServer_ActiveDirectoryServers ---> Autoregistration Action puts it into Host group
# This file shall be placed as such C:\ProgramData\Zabbix-ext\conf.d\active_agent.conf

# Forces the agent to get its config on start immediately
ForceActiveChecksOnStart=1

# How often list of active checks is refreshed, in seconds.
RefreshActiveChecks=300
```

#### C:\ProgramData\Zabbix-ext\conf.d\custom_checks.conf
```
# You can put custom UserParameters here or split them out per .conf file
UserParameter=powershell.ps_dcdiag_checks,powershell -ExecutionPolicy Bypass -File "C:\ProgramData\Zabbix-ext\scripts\Invoke-ActiveDirectoryChecks.ps1"
```
