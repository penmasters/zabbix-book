---
description: |
    Learn how to monitor Windows disk health with Zabbix Agent 2 and Smartmontools,
    including SMART status, temperature, wear level, and disk alerts.
tags: [beginner]
---

# Disk Health Monitoring on Windows with Smartmontools

This guide explains how to enable monitoring of the disk “health” (temperature,
errors, wear level, and alerts) on Windows computers using Zabbix + Smartmontools.

## Install Zabbix Agent 2 (required)

To use Smartmontools with Zabbix, you must install Zabbix Agent 2. The standard
Zabbix Agent does not support this functionality.

[https://cdn.zabbix.com/zabbix/binaries/stable/8.0/latest/](https://cdn.zabbix.com/zabbix/binaries/stable/8.0/latest/)

During installation:

- Enter the Raspberry Pi IP address (your Zabbix Proxy) in both fields that request
  the server IP.
- Complete the installation normally.

![ch16.1-agent_config.jpg](ch16.1-agent_config.jpg){ align=center }

_16.1 Agent configuration_

## Set the Agent service to automatic start

In Windows:

- Open `Services`.
- Find `Zabbix Agent 2`.
- Right-click and select `Properties`.
- Set `Startup type` to `Automatic`.
- Click `Start` if the service is not already running. This ensures
  monitoring continues after PC restarts.

![ch16.2-services.jpg](ch16.2-services.jpg){ align=center }

_16.2 Configure Services_

## Test Smartmontools

Download the latest version of Smartmontools. For example: `smartmontools-7.5.win32-setup.exe`

[https://github.com/smartmontools/smartmontools/releases/](https://github.com/smartmontools/smartmontools/releases/)

After installing Smartmontools, open Command Prompt (CMD) and run:

`smartctl.exe -a /dev/sdX` (where `sdX` is the name of your disk drive)

If everything is correct, it will display detailed information about your SSD/HDD
such as temperature, usage hours, alerts, and more.

![ch16.3-smartmontool.jpg](ch16.3-smartmontool.jpg){ align=center }

_16.3 Smartmontools_

## Configure the Smart plugin in Zabbix Agent 2

Locate the plugin configuration folder:

- `C:\Program Files\Zabbix Agent 2\zabbix_agent2.d\plugins.d`
- Open the file `smart.conf` using Notepad as Administrator, then add the following line:
    - `Plugins.Smart.Path=C:\PROGRA~1\smartmontools\bin\smartctl.exe`

  Save and close the file.


![ch16.4-plugins.jpg](ch16.4-plugins.jpg){ align=center }

_16.4 Plugins_

![ch16.5-plugins.jpg](ch16.5-plugins.jpg){ align=center }

_16.5 Plugin config_

## Test communication between Zabbix Agent 2 and Smartmontools

Inside the Zabbix Agent 2 installation folder, run: `zabbix_agent2.exe -t smart.disk.get`
If successful, it will return the disk information that will be sent to Zabbix.

![ch16.6-communication.png](ch16.6-communication.png){ align=center }

_16.6 Communication check_

## Configure it in the Zabbix Web Interface

In Zabbix, follow these steps:

- Open the host you want to monitor (`Data collection` | `Hosts`)
- Go to Templates
- Add the following template:

![ch16.7-host-add.png](ch16.7-host-add.png){ align=center }

_16.7 Host add_

Wait 1–5 minutes for Zabbix to automatically detect the disk sensors and metrics.
If it does not detect anything:

- Restart the Zabbix Agent 2 service in Windows.
- Execute the discovery rule.
    - Wait a few more minutes.

After collecting all the data, Zabbix will display all relevant disk health data, such as:

- Temperature
- SMART errors
- Wear level
- Critical alerts
- Read/Write status
- Estimated disk lifespan

Let's have a look at our latest data page. `Monitoring` | `Latest data`.

![ch16.8-latestdata.png](ch16.8-latestdata.png){ align=center }

_16.8 Latest data_

