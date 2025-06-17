# System Requirements

## Requirements

Zabbix has specific hardware and software requirements that must be met, and
these requirements may change over time. They also depend on the size of your
setup and the software stack you select. Before purchasing hardware or
installing a database version, it's essential to consult the Zabbix
documentation for the most up-to-date requirements for the version you plan to
install. You can find the latest requirements
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Make sure to select the correct Zabbix version from the list.

For smaller or test setups, Zabbix can comfortably run on a system with 2 CPUs
and 8 GB of RAM. However, your setup size, the number of items you monitor, the
triggers you create, and how long you plan to retain data will impact resource
requirements. In today's virtualised environments, my advice is to start small
and scale up as needed.

You can install all components (Zabbix server, database, web server) on a single
machine or distribute them across multiple servers. For simplicity, take note of
the server details:

| Component       | IP Address |
| --------------- | ---------- |
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

???+ note

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Basic OS Configuration

Operating systems, so many choices, each with its own advantages and loyal user
base. While Zabbix can be installed on a wide range of platforms, documenting
the process for every available OS would be impractical. To keep this book
focused and efficient, we have chosen to cover only the most widely used
options: Ubuntu and Red Hat based distributions.

Since not everyone has access to a Red Hat Enterprise Linux (RHEL) subscription
even though a developer account provides limited access we have opted for Rocky
Linux as a readily available alternative. For this book, we will be using Rocky
Linux 9.x and Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://ubuntu.com/>

### Firewall

Before installing Zabbix, it's essential to properly prepare the operating
system. The first step is to ensure that the firewall is installed and
configured.

To install and enable the firewall, run the following command:

!!! info "Install and enable the firewall"

    Red Hat
    ```yaml
    dnf install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```yaml
    sudo apt install ufw -y
    sudo ufw enable
    ```

Once installed, you can configure the necessary ports. For Zabbix, we need to
allow access to port `10051/tcp`, which is where the Zabbix trapper listens for
incoming data. Use the following command to open this port in the firewall:

!!! info "Allow Zabbix trapper access"

    Red Hat
    ```yaml
    firewall-cmd --add-service=zabbix-server --permanent
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    ```

If the service is not recognized, you can manually specify the port:

!!! info "Add port instead of the service name"

    ```yaml
    firewall-cmd --add-port=10051/tcp --permanent
    ```

???+ note

    "Firewalld is the replacement for iptables in RHEL-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps."
    Ubuntu makes use of UFW and is merely a frontend for iptables.

An alternative approach is to define dedicated firewall zones for specific use
cases. For example...

!!! info "Create a firewalld zone"

    ```yaml
    firewall-cmd --new-zone=postgresql-access --permanent
    ```

You can confirm the creation of the zone by executing the following command:

!!! info "Verify the zone creation"

    ```yaml
    firewall-cmd --get-zones
    ```

block dmz drop external home internal nm-shared postgresql-access public trusted
work

Using zones in firewalld to configure firewall rules for PostgreSQL provides
several advantages in terms of security, flexibility, and ease of management.
Here’s why zones are beneficial:

- **Granular Access Control :**
  - firewalld zones allow different levels of trust for different network
    interfaces and IP ranges. You can define which systems are allowed to
    connect to PostgreSQL based on their trust level.
- **Simplified Rule management:**
  - Instead of manually defining complex iptables rules, zones provide an
    organized way to group and manage firewall rules based on usage scenarios.
- **Enhanced security:**
  - By restricting PostgreSQL access to a specific zone, you prevent
    unauthorized connections from other interfaces or networks.
- **Dynamic configuration:**
  - firewalld supports runtime and permanent rule configurations, allowing
    changes without disrupting existing connections.
- **Multi-Interface support:**
  - If the server has multiple network interfaces, zones allow different
    security policies for each interface.

Bringing everything together it would look like this:

!!! info "Firewalld with zone config"

    ```yaml
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Where the `source IP` is the only address permitted to establish a connection to
the database.

---

### Time Server

Another crucial step is configuring the time server and syncing the Zabbix
server using an NTP client. Accurate time synchronization is vital for Zabbix,
both for the server and the devices it monitors. If one of the hosts has an
incorrect time zone, it could lead to confusion, such as investigating an issue
in Zabbix that appears to have happened hours earlier than it actually did.

To install and enable chrony, our NTP client, use the following command:

!!! info "Install NTP client"

    Red Hat
    ```yaml
    dnf install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```yaml
    sudo apt install chrony -y
    ```

After installation, verify that Chrony is enabled and running by checking its
status with the following command:

!!! info "Check status chronyd"

    ```yaml
    systemctl status chronyd
    ```

???+ note "what is apt or dnf"

    dnf is a package manager used in Red Hat-based systems. If you're using another
    distribution, replace `dnf` with your appropriate package manager, such as `zypper`,
    `apt`, or `yum`.

???+ note "what is Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Once Chrony is installed, the next step is to ensure the correct time zone is
set. You can view your current time configuration using the `timedatectl`
command:

!!! info "check the time config"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 15:09:14 UTC
    Universal time: Thu 2023-11-16 15:09:14 UTC
    RTC time: Thu 2023-11-16 15:09:15
    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
    NTP service: active
    RTC in local TZ: no
    ```

Ensure that the Chrony service is active (refer to the previous steps if
needed). To set the correct time zone, first, you can list all available time
zones with the following command:

!!! info "list the timezones"

    ```yaml
    timedatectl list-timezones
    ```

This command will display a list of available time zones, allowing you to select
the one closest to your location. For example:

!!! info "List of all the timezones available"

    ```yaml
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

    ```yaml
    timedatectl set-timezone Europe/Brussels
    ```

To verify that the time zone has been configured correctly, use the
`timedatectl` command again:

!!! info "Check the time and zone"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 16:13:35 CET
    Universal time: Thu 2023-11-16 15:13:35 UTC
    RTC time: Thu 2023-11-16 15:13:36
    **Time zone: Europe/Brussels (CET, +0100)**
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

### Verifying Chrony Synchronization

To ensure that Chrony is synchronizing with the correct time servers, you can
run the following command:

!!! info "Verify chrony"

    ```yaml
    chronyc
    ```

The output should resemble:

!!! info "Verify your chrony output"

    ```yaml
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Once inside the Chrony prompt, type the following to check the sources:

!!! info ""

    ```yaml
    chronyc> sources
    ```

Example output:

!!! info "Check your time server sources"

    ```bash
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In this example, the NTP servers in use are located outside your local region.
It is recommended to switch to time servers in your country or, if available, to
a dedicated company time server. You can find local NTP servers here:
[www.ntppool.org](https://www.ntppool.org/).

---

### Updating Time Servers

To update the time servers, modify the `/etc/chrony.conf` file for Red Hat based
systems, and if you use Ubuntu edit `/etc/chrony/chrony.conf`. Replace the
existing NTP server with one closer to your location.

Example of the current configuration:

!!! info "example ntp pool config"

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

    Change the pools you want to a local time server:

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

After making this change, restart the Chrony service to apply the new
configuration:

!!! info "restart the chrony service"

    ```yaml
    systemctl restart chronyd
    ```

### Verifying Updated Time Servers

Check the time sources again to ensure that the new local servers are in use:

!!! info "Check chrony sources"

    ```yaml
    chronyc> sources
    ```

Example of expected output with local servers:

!!! info "Example output"

    ```yaml
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
paid to the environment in which it will reside. A properly configured operating
system, an open path through the firewall, and accurate timekeeping are not mere
suggestions, but essential building blocks. Having laid this groundwork, we can
now proceed with confidence to the Zabbix installation, knowing that the
underlying system is prepared for the task.

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
