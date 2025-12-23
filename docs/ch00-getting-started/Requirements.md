---
description: |
    Learn Zabbix system requirements: supported OS, database options, hardware
    specs, firewall ports, and time sync needed for a smooth installation.
tags: [beginner]
---

# System Requirements

## Requirements

Zabbix has specific hardware and software requirements that must be met,
and these requirements may change over time. They also depend on the size of your
setup and the software stack you select.
Before purchasing hardware or installing a database version, it's essential to
consult the Zabbix documentation for the most up-to-date requirements for the
version you plan to install.
You can find the latest requirements [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Make sure to select the correct Zabbix version from the list.

For smaller or test setups, Zabbix can comfortably run on a system with 2 CPUs
and 8 GB of RAM. However, your setup size, the number of items you monitor,
the triggers you create, and how long you plan to retain data will impact
resource requirements.
In today's virtualised environments, my advice is to start small and scale up
as needed.

You can install all components (Zabbix server, database, web server) on a single
machine or distribute them across multiple servers.
For simplicity, take note of the server details:

| Component       | IP Address |
| :-------------- | :--------- |
| Zabbix Server   |            |
| Database Server |            |
| Web Server      |            |

???+ tip

    Zabbix package names often use dashes (`-`) in their names, such as `zabbix-get`
    or `zabbix-sender`, but the binaries themselves may use underscores (`_`),
    like `zabbix_sender` or `zabbix_server`. This naming discrepancy can sometimes
    be confusing, particularly if you are using packages from non-official Zabbix
    repositories.

    Always check if a binary uses a dash or an underscore when troubleshooting.

???+ warning

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Basic OS Configuration

Operating systems, so many choices, each with its own advantages and loyal user base.
While Zabbix can be installed on a wide range of platforms, documenting the process
for every available OS would be impractical. To keep this book focused and efficient,
we have chosen to cover only the most widely used options: Ubuntu, Red Hat and Suse 
based distributions.

Since not everyone has access to a Red Hat Enterprise Linux (RHEL) or a SUSE Linux
Enterprise Server (SLES) subscription even though a developer account provides limited 
access we have opted for Rocky Linux respectively openSUSE Leap as a readily available
alternative. For this book, we will be using Rocky Linux 9.x, openSUSE Leap 16 and
Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    OS installation steps are outside the scope of this book, but a default or even a
    minimal installation of your preferred OS should be sufficient. Please refrain from
    installing graphical user interfaces (GUIs) or desktop environments, as they are
    unnecessary for server setups and consume valuable resources.

Once you have your preferred OS installed, there are a few essential configurations
to perform before proceeding with the Zabbix installation. Perform the following
steps on **all** the servers that will host Zabbix components (i.e., Zabbix server, 
database server, and web server).

---

### Update the System

Before installing the Zabbix components, or any new software, it's a best practice to ensure
your operating system is up-to-date with the latest patches and security fixes.
This will help maintain system stability and compatibility with the software you're
about to install.
Even if your OS installation is recent, it's still advisable to run an update
to ensure you have the latest packages.

To update your system, run the following command based on your OS:

!!! info "Update your system"

    Red Hat
    ```bash
    dnf update
    ```

    SUSE
    ```bash
    zypper refresh
    zypper update
    ```

    Ubuntu
    ```bash
    sudo apt update
    sudo apt upgrade
    ```
???+ note "What is apt, dnf or zypper"

    - DNF (Dandified YUM) is a package manager used in recent Red Hat-based systems (invoked as `dnf`).
    - ZYpp (Zen / YaST Packages Patches Patterns Products) is the package manager 
    used on SUSE-based systems (invoked as `zypper`) and 
    - APT (Advanced Package Tool) is the package manager used on Debian/Ubuntu-based systems (invoked as `apt`). 

    If you're using another distribution, replace `dnf`/`zypper`/`apt` with your appropriate 
    package manager, such as `yum`, `pacman`, `emerge`, `apk` or ... .

    Do note that package names may also vary from distribution to distribution.

???+ tip

    Regularly updating your system is crucial for security and performance.
    Consider setting up automatic updates or scheduling regular maintenance windows
    to keep your systems current.

---

### Sudo

By default the Zabbix processes like the Zabbix server and agent run under their
own unprivileged user accounts (e.g., `zabbix`). However, there are scenarios where
elevated privileges are required, such as executing custom scripts or commands
that need root access.
Also throughout this book, we will perform certain administrative tasks that
require `sudo` on the system.

Usually, `sudo` is already present on most systems, but when you performed
a minimal installation of your OS, it might be missing. Therefore we need to
ensure it's installed.

This will also allow the Zabbix user to execute specific configured commands
with elevated privileges without needing to switch to the root user entirely.

!!! info "What is sudo"

    `sudo` (short for "superuser do") is a command-line utility that allows
    permitted users to execute commands with the security privileges of another
    user, typically the superuser (root). It is commonly used in Unix-like
    operating systems to perform administrative tasks without needing to log in
    as the root user.

To install `sudo`, run the following command based on your OS:

!!! info "Install sudo"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    On Ubuntu, `sudo` is normally installed by default. Root access is managed
    through `sudo` for the initial user created during installation.

If `sudo` is already installed, these commands will inform you that the latest version
is already present and no further action is needed. If not, the package manager
will proceed to install it.

---

### Firewall

Next, we need to ensure that the firewall is installed and configured. 
A firewall is a crucial security component that helps protect your server
from unauthorized access and potential threats by controlling incoming and
outgoing network traffic based on predetermined security rules.

To install and enable the firewall, run the following command:

!!! info "Install and enable the firewall"

    Red Hat
    ```bash
    dnf install firewalld
    systemctl enable firewalld --now
    ```
    SUSE
    ```bash
    zypper install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```bash
    sudo apt install ufw
    sudo ufw enable
    ```
???+ note "What is firewalld / ufw"

    Firewalld is the replacement for iptables in RHEL- and SUSE-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps.
    Ubuntu makes use of UFW which is merely a frontend for iptables.

During the Zabbix installation in the next chapters, we will need to open specific
ports in the firewall to allow communication between Zabbix components.

Alternatively to just opening ports, as we will do in the next chapters, you can
also choose to define dedicated firewall zones for specific use cases. This 
approach enhances security by isolating services and restricting access based on
trust levels.
For example...

!!! example "Create a firewalld zone for database access"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

You can confirm the creation of the zone by executing the following command:

!!! example "Verify the zone creation"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Using zones in firewalld to configure firewall rules provides several
advantages in terms of security, flexibility, and ease of management.
Here’s why zones are beneficial:

- **Granular Access Control :**

:   Firewalld zones allow different levels of trust for different network interfaces
    and IP ranges. You can define which systems are allowed to connect to PostgreSQL
    based on their trust level.

- **Simplified Rule management:**

:   Instead of manually defining complex iptables rules, zones provide an organized
    way to group and manage firewall rules based on usage scenarios.

- **Enhanced security:**

:   By restricting application access to a specific zone, you prevent unauthorized
    connections from other interfaces or networks.

- **Dynamic configuration:**

:   Firewalld supports runtime and permanent rule configurations, allowing changes
    without disrupting existing connections.

- **Multi-Interface support:**

:   If the server has multiple network interfaces, zones allow different security
    policies for each interface.

Bringing everything together to add a zone for, in this example, PostgreSQL it
would look like this:

!!! example "Firewalld with zone config for PostgreSQL database access"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Where the `source IP` is the only address permitted to establish a connection to
the database.

If you wish to use zones when using firewalld, ensure to adapt the instructions
in the following chapters accordingly.

---

### Time Server

Another crucial step is configuring the time server and syncing the Zabbix server
using an NTP client.
Accurate time synchronization is vital for Zabbix, both for the server and the
devices it monitors.
If one of the hosts has an incorrect time zone, it could lead to confusion, such
as investigating an issue in Zabbix that appears to have happened hours earlier
than it actually did.

To install and enable chrony, our NTP client, use the following command:

!!! info "Install NTP client"

    Red Hat
    ```bash
    dnf install chrony
    systemctl enable chronyd --now
    ```

    SUSE
    ```bash
    zypper install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```bash
    sudo apt install chrony
    ```

After installation, verify that Chrony is enabled and running by checking its
status with the following command:

!!! info "Check status chronyd"

    ```bash
    systemctl status chronyd
    ```

???+ note "what is Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Once Chrony is installed, the next step is to ensure the correct time zone is set.
You can view your current time configuration using the `timedatectl` command:

!!! example "Check the time config"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 15:09:14 UTC
               Universal time: Thu 2023-11-16 15:09:14 UTC
                     RTC time: Thu 2023-11-16 15:09:15
                    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

Ensure that the Chrony service is active (refer to the previous steps if needed).
To set the correct time zone, first, you can list all available time zones with
the following command:

!!! info "List the timezones"

    ```bash
    timedatectl list-timezones
    ```

This command will display a list of available time zones, allowing you to select
the one closest to your location. For example:

!!! example "List of all the timezones available"

    ```shell-session
    localhost:~ # timedatectl list-timezones
    Africa/Abidjan
    Africa/Accra
    ...
    Pacific/Tongatapu
    Pacific/Wake
    Pacific/Wallis
    UTC
    ```

Once you've identified your time zone, configure it using the following command:

!!! info "Set the timezone"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

To verify that the time zone has been configured correctly, use the `timedatectl`
command again:

!!! example "Check the time and zone"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 16:13:35 CET
               Universal time: Thu 2023-11-16 15:13:35 UTC
                     RTC time: Thu 2023-11-16 15:13:36
                    Time zone: Europe/Brussels (CET, +0100)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

???+ note

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

#### Verifying Chrony Synchronization

To ensure that Chrony is synchronizing with the correct time servers, you can
run the following command:

!!! info "Verify chrony"

    ```bash
    chronyc
    ```

The output should resemble:

!!! example "Verify your chrony output"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Once inside the Chrony prompt, type the `sources` command  to check the used time sources:

Example output:

!!! example "Check your time server sources"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In this example, the NTP servers in use are located outside your local region.
It is recommended to switch to time servers in your country or, if available,
to a dedicated company time server. You can find local NTP servers here:
[www.ntppool.org](https://www.ntppool.org/).

---

#### Updating Time Servers

To update the time servers, modify the Chrony configuration file:

!!! info "Edit chrony config file"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    On SUSE, the pool configuration is located in a separate file. You can
    edit that file directly or add a new configuration file in the same directory.
    In the latter case, ensure to disable or remove the existing pool configuration
    to avoid conflicts.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Replace the existing NTP server pool with one closer to your location.

Example of the current configuration:

!!! example "Example ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Change the pools you want to a local time server:

!!! info "Change ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

After making this change, restart the Chrony service to apply the new configuration:

!!! info "Restart the chrony service"

    ```bash
    systemctl restart chronyd
    ```

#### Verifying Updated Time Servers

Check the time sources again to ensure that the new local servers are in use:

!!! info "Check chrony sources"

    ```
    chronyc> sources
    ```

Example of expected output with local servers:

!!! example "Example output"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

This confirms that the system is now using local time servers.

## Conclusion

As we have seen, before even considering the Zabbix packages, attention must be
paid to the environment in which it will reside. A properly configured and up-to-date operating
system, an open path through the firewall, and accurate timekeeping are not mere
suggestions, but essential building blocks. Having laid this groundwork, we can
now proceed with confidence to the Zabbix installation, knowing that the underlying
system is prepared for the task.

## Questions

- Why do you think accurate time synchronization is so crucial for a monitoring
  system like Zabbix?
- Now that the groundwork is laid, what do you anticipate will be the first step
  in the actual Zabbix installation process?
- As we move towards installing Zabbix, let's think about network communication.
  What key ports do you anticipate needing to allow through the firewall for the
  Zabbix server and agents to interact effectively?

## Useful URLs

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)