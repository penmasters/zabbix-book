---
description: |
    test
tags: [beginner]
---
# Disk Health Monitoring on Windows with Smartmontools

This guide explains how to enable monitoring of the disk “health” (temperature,
errors, wear level, alerts) on Windows computers using Zabbix + Smartmontools.

## Install Zabbix Agent 2 (required)

To use Smartmontools with Zabbix, you must install Zabbix Agent 2. The standard
Zabbix Agent does not support this functionality

[https://cdn.zabbix.com/zabbix/binaries/stable/8.0/latest/](https://cdn.zabbix.com/zabbix/binaries/stable/8.0/latest/)

During installation:

- Enter the Raspberry Pi IP address (your Zabbix Proxy) in both fields that request
  the server IP.
- Complete the installation normally.

![ch15_01_agent_config.jpg](ch15_01_agent_config.jpg)
_15.1_agent_config_

## Set the Agent service to automatic start

In Windows:

- Open Services
- Find Zabbix Agent 2
- Right-click → Properties
- Set Startup type to Automatic
- Click Start if the service is not already running This ensures

monitoring continues after PC restarts

![ch15_02_services.jpg](ch15_02_services.jpg)
_15.2 Configure Services_

## Test Smartmontools

Download the smartmontools latest version. Ex: smartmontools-7.5.win32-setup.exe

[https://github.com/smartmontools/smartmontools/releases/](https://github.com/smartmontools/smartmontools/releases/)

After installing Smartmontools, open Command Prompt (CMD) and run:

`smartctl.exe -a /dev/sdX (where sdX is the name of your diskdrive)`

If everything is correct, it will display detailed information about your SSD/HDD
such as temperature, usage hours, alerts, and more.

![ch15_03_smartmontool.jpg](ch15_03_smartmontool.jpg)
_15.3 Smartmontools_

## Configure the Smart plugin in Zabbix Agent 2

Locate the plugin configuration folder:

- C:\Program Files\Zabbix Agent 2\zabbix_agent2.d\plugins.d
- Open the file smart.conf using Notepad as Administrator, then add the following line:
    - Plugins.Smart.Path=C:\PROGRA~1\smartmontools\bin\smartctl.exe Save and close the file.


![ch15_04_plugins.jpg](ch15_04_plugins.jpg)
_15.4 Plugins_

![ch15_05_plugins.jpg](ch15_05_plugins.jpg)
_15.5 plugin config_

## Test communication between Zabbix Agent 2 and Smartmontools

Inside the Zabbix Agent 2 installation folder, run: zabbix_agent2.exe -t smart.disk.get
If successful, it will return the disk information that will be sent to Zabbix.

![ch15_06_communication.jpg](ch15_06_communication.jpg)
_15.6 communicaton check_

## Configure it in the Zabbix Web Interface

In Zabbix do the following steps:

- Open the Host you want to monitor (Data collection -> Hosts)
- Go to Templates
- Add the following template:

![ch15_07_host-add.jpg](ch15_07_host-add.jpg)
_15.7 Host add_


