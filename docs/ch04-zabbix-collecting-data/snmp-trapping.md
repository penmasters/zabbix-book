---
description: |
    Learn how to configure and manage SNMP traps in Zabbix for real-time alerts, faster event detection, and efficient network monitoring.
---

# SNMP Trapping

SNMP traps are one of the most powerful features in Zabbix network monitoring.
Unlike traditional SNMP polling, which periodically queries devices for status
updates, SNMP traps deliver real-time alerts directly from network equipment
the moment an event occurs, no waiting for the next polling cycle.

In this chapter, you'll learn how to set up SNMP trap handling in Zabbix, from
installing and configuring snmptrapd to integrating it with the Zabbix server.
You'll also discover how to analyse, filter, and map incoming traps using regular
expressions, and how to link them with triggers and notifications for instant
visibility into network issues.

Whether you're monitoring switches, routers, UPS systems, or firewalls, mastering
SNMP traps in Zabbix gives you faster event detection, reduced network load, and
deeper operational insight.

## Traps versus Polling

In Zabbix, SNMP (Simple Network Management Protocol) is one of the most common
methods for monitoring network devices such as switches, routers, firewalls, and
UPS systems.
There are two main ways Zabbix can receive information from an SNMP-enabled device:

- Polling (active monitoring) See our topic SNMP Polling in Chapter 4.
- Traps (passive monitoring)

To understand the differences between trapping and polling and understand the
advantages and disadvantages lets have a quick overview:

- With SNMP polling, the Zabbix server or proxy periodically queries the device for
specific values using SNMP GET requests. For example, CPU load, interface status,
temperature ... The device responds with the current data, and Zabbix stores it
in the database.

### Polling

Polling is a client initiated and scheduled process. It is predictable, reliable,
and suitable for continuous metrics that change over time.

**Advantages:**

- Easy to control frequency and timing.
- Works even if the device doesn't support traps.
- Historical trend data is consistent.

**Disadvantages:**

- Generates more network traffic on large infrastructures.
- Delays between polls mean slower event detection.
- If a device goes down, Zabbix won't notice until the next polling cycle. (This
can be detected by using the nodata function or using "SNMP agent availability"
item but not for individual items unless every items has the nodata function and
this is also a bad idea.)


### Trapping

SNMP traps work the opposite way. The device itself sends a message (trap) to the
Zabbix system when an event occurs. For example, a power failure, link down, or
temperature alarm. Zabbix listens for incoming traps via the snmptrapd daemon
and processes them through its SNMP trap item type.

Traps are event driven and asynchronous, meaning they are sent immediately when
something happens. No waiting or polling required.

**Advantages:**

- Instant notification of important events.
- Reduces network load (no regular queries).
- Ideal for devices that push alerts rather than respond to queries.

**Disadvantages:**

- Requires external configuration (snmptrapd, scripts, log parsing).
- Not all devices send traps for all events.
- If traps are missed or misconfigured, data is lost. (Traps use UDP)

| Method | Direction | Timing | Example | Pros | Cons |
|:----   |:----      |:----   |:----    |:---- |:---- |
| Polling (Sync)  | Zabbix → Device | Periodic | SNMP GET for CPU load | Predictable, simple |Slower, more traffic |
| Polling (Async) | Zabbix → Device | Parallel | Many SNMP GETs at once | Fast, scalable | More complex tuning |
| Traps | Device → Zabbix | Event-driven | Interface down trap | Instant alerts, low load | Requires trap daemon, can miss events |

---

## SNMP Traps flow in Zabbix

``` mermaid
flowchart TB
    %% --- Traps section (top) ---
    subgraph TRAPS[Traps]
        direction TB
        TITLET["SNMP Traps<br/>Acrive Monitoring"]
        WIDE["                                                                 "]
        DEV2[Network Device]
        TRAPD[snmptrapd Daemon]
        HANDLER[SNMPTT or perl script]
        ZBXT[Zabbix Server or Proxy]
        DBT[Zabbix Database]
        UI2[Zabbix Frontend]
        USER2[User]

        TITLET --> DEV2
        DEV2 -->|SNMP Trap UDP 162| TRAPD
        TRAPD -->|Handler Script| HANDLER
        HANDLER -->|Trap Log| ZBXT
        ZBXT --> DBT
        DBT --> UI2
        UI2 -->|Displays event| USER2
    end

    %% --- Invisible connector to force vertical stacking ---
    TRAPS -.-> POLLING

    %% --- Polling section (bottom) ---
    subgraph POLLING[Polling]
        direction LR
        TITLEP["SNMP Polling<br/>Passive Monitoring"]
        ZBX[Zabbix Server or Proxy]
        DEV[Network Device]
        TITLEP --> ZBX
        ZBX -->|SNMP GET UDP 161| DEV
        DEV -->|SNMP Response| ZBX
        ZBX --> DBP[Zabbix Database]
        DBP --> UI1[Zabbix Frontend]
        UI1 -->|Displays polled data| USER1[User]
    end

    %% --- Styling ---
    style POLLING fill:#f0fff0,stroke:#3a3,stroke-width:1px
    style TRAPS fill:#f0f8ff,stroke:#339,stroke-width:1px
    style WIDE fill:none,stroke:none
    style TITLEP fill:transparent,stroke:transparent
    style TITLET fill:transparent,stroke:transparent
    style ZBX fill:#e0ffe0,stroke:#3a3
    style DEV fill:#ffefd5,stroke:#c96
    style DEV2 fill:#ffefd5,stroke:#c96
    style TRAPD fill:#f9f9f9,stroke:#777
    style HANDLER fill:#f0f8ff,stroke:#339
    style ZBXT fill:#e0ffe0,stroke:#3a3
    style DBP fill:#fffbe0,stroke:#996
    style DBT fill:#fffbe0,stroke:#996
    style UI1 fill:#e8e8ff,stroke:#669
    style UI2 fill:#e8e8ff,stroke:#669
    style USER1 fill:#fff0f0,stroke:#c33
    style USER2 fill:#fff0f0,stroke:#c33
```
### SNMP Trap Flow (Active Monitoring)

In an SNMP Trap setup, communication is device initiated. Meaning the network device
sends an event message to Zabbix the moment something happens.
This is called active monitoring because Zabbix doesn't need to query the device
periodically.

**Step-by-step flow:**

- **Network Device:**
When an event occurs (for example, a power failure, interface down, or temperature
alarm), the device immediately sends an SNMP Trap to the configured destination
on UDP port 162.

- **snmptrapd Daemon:**
The Net-SNMP daemon **snmptrapd**  listens for incoming traps.
It acts as a relay between the device and Zabbix, executing a handler script whenever
a trap is received.

- **Trap Handler / Log File:**
The handler script (often zabbix_trap_receiver.pl or SNMPTT) processes the trap
and writes it into a log file, usually "/var/log/snmptrap/snmptrap.log."
This file contains the raw trap data including timestamps, source IPs, and OIDs.

- **Zabbix Server or Proxy:**
The Zabbix component (server or proxy) monitors the trap log for new entries and
matches them against configured SNMP trap items. These items use regular expressions
or string filters to extract relevant data.

- **Zabbix Database:**
Once processed, the trap information is stored in the database like any other
item value.

- **Zabbix Frontend:**
The event becomes visible in the Zabbix frontend almost instantly showing up in
Latest Data, Problems, or triggering actions and notifications based on your configuration.

???+ note

    SNMP traps deliver real-time alerts without polling overhead, making them
    ideal for event driven devices like UPSs, firewalls, or network switches.


### **SNMP Polling Flow (Passive Monitoring)**

In contrast, SNMP Polling is Zabbix initiated.
This is called passive monitoring because the Zabbix server (or proxy)  queries
the device at a set interval to retrieve values.

**Step-by-step flow:**

- **Zabbix Server or Proxy:**
Periodically sends an SNMP GET request to the device using UDP port 161.
Each SNMP item in Zabbix corresponds to a specific OID (Object Identifier) that
defines which metric is requested (e.g., CPU usage, interface status).

- **Network Device:**
Responds to the SNMP GET request with the current value of the requested OID.

- **Zabbix Database:**
The response data is stored in the database with a timestamp for trend analysis
and historical graphing.

- **Zabbix Frontend:**
Displays the collected values in graphs, dashboards, and triggers thresholds if
defined.

???+ note

    Polling provides consistent, periodic data collection. Ideal for metrics like
    bandwidth usage, temperature, or CPU load. However, it may have a small delay
    between data updates depending on the polling interval (e.g., every 30s,
    1min, etc.).

### Summary

| Feature            | SNMP Traps (Active)              | SNMP Polling (Passive)        |
| ------------------ | -------------------------------- | ----------------------------- |
| **Initiator**      | Network Device                   | Zabbix                        |
| **Direction**      | Device → Zabbix                  | Zabbix → Device               |
| **Transport Port** | UDP 162                          | UDP 161                       |
| **Frequency**      | Event-driven (immediate)         | Periodic (configurable interval) |
| **Resource Usage** | Lower (only on events)           | Higher (regular queries)      |
| **Data Type**      | Event notifications              | Continuous metrics            |
| **Best for**       | Fault and alert notifications    | Performance and trend monitoring |


!!! Tip

    In production Zabbix environments, many administrators combine both methods:
    - Use SNMP polling for regular metrics (e.g., interface traffic, system uptime).
    - Use SNMP traps for immediate events (e.g., link down, power failure).
    This hybrid approach gives you both real-time alerts and historical performance
    data, achieving complete SNMP visibility with minimal overhead.

---

## Setting up SNMP traps with zabbix_trap_receiver

In this section, we'll configure Zabbix to receive and process SNMP traps using
the Perl script zabbix_trap_receiver.pl. SNMP traps allow network devices to actively
send event information to the Zabbix server, enabling near real-time alerting without
periodic polling.

### **Open the Firewall for SNMP Trap Traffic**

By default, SNMP traps are received on UDP port 162.
Make sure this port is open on your Zabbix server:

```bash
sudo firewall-cmd --add-port=162/udp --permanent
```

```bash
sudo firewall-cmd --reload
```

This allows incoming traps from SNMP-enabled devices.

### **Install Required SNMP Packages**

The snmptrapd daemon and Perl bindings are needed for trap handling.

```bash
sudo dnf install -y net-snmp-utils net-snmp-perl net-snmp
```

This installs the SNMP tools, daemon, and Perl modules used by Zabbix's receiver
script.

### **Install zabbix_trap_receiver.pl**

Download the latest zabbix_trap_receiver.pl script from the official
Zabbix source archive [https://cdn.zabbix.com/zabbix/sources/stable/](https://cdn.zabbix.com/zabbix/sources/stable/)

```bash
sudo wget https://cdn.zabbix.com/zabbix/sources/stable/7.0/zabbix-8.0.0.tar.gz
```

Once downloaded, extract the file and copy the script to /usr/bin and make it executable:

```bash
sudo tar -xvf zabbix-8.0.0.tar.gz
sudo cp zabbix-7.0.0/misc/snmptrap/zabbix_trap_receiver.pl /usr/bin/.
sudo chmod +x /usr/bin/zabbix_trap_receiver.pl
```

This script receives traps from snmptrapd and writes them to a log file that Zabbix
can read.

### **Configure snmptrapd**

Edit the SNMP trap daemon configuration file:

```bash
sudo vi /etc/snmp/snmptrapd.conf
```

Append the following lines:

```bash
authCommunity execute public
perl do "/usr/bin/zabbix_trap_receiver.pl";
```

### **Explanation:**

- authCommunity execute public allows traps from devices using the community
  string public.
- The perl do line executes the Zabbix Perl handler for each incoming trap.

### **Edit the perl script**

```bash
vi /usr/bin/zabbix_trap_receiver.pl
```

Replace $SNMPTrapperFile = '/tmp/zabbix_traps.tmp'; with:

```bash
$SNMPTrapperFile = '/var/log/zabbix_traps_archive/zabbix_traps.log';
```

### **Enable SNMP Trap Support in Zabbix**

Edit the Zabbix server configuration file:

```bash
sudo vi /etc/zabbix/zabbix_server.conf
```

Uncomment or add the following parameters:

```bash
StartSNMPTrapper=1
SNMPTrapperFile=/var/log/zabbix_traps_archive/zabbix_traps.log
```

???+ note

    - StartSNMPTrapper=1 enables the Zabbix SNMP trapper process.
    - The SNMPTrapperFile path must match exactly the path used inside zabbix_trap_receiver.pl.

Restart the Zabbix server to apply changes:

```bash
sudo systemctl restart zabbix-server
```

### **Enable and Start snmptrapd**

Activate and start the SNMP trap daemon so it launches at boot:

```bash
systemctl enable snmptrapd --now
```

This service will now listen on UDP 162 and feed incoming traps to Zabbix.

### **(Optional) Rotate the Trap Log File**

Zabbix writes all traps into a temporary log file.
To prevent this file from growing indefinitely, configure log rotation.

Create the directory:

```bash
sudo mkdir -p /var/log/zabbix_traps_archive
sudo chmod 755 /var/log/zabbix_traps_archive
```

Next wecreate a logrotate configuration file /etc/logrotate.d/zabbix_traps:

```bash
sudo vi /etc/logrotate.d/zabbix_traps
```

Add the folowing content to this file.

``` bash
/var/log/zabbix_traps_archive/zabbix_traps.log {
    weekly
    size 10M
    compress
    notifempty
    dateext
    dateformat -%Y%m%d
    missingok
    olddir /var/log/zabbix_traps_archive
    maxage 365
    rotate 10
}
```

### **Conclusion**

You've now configured Zabbix to:

- Listen for SNMP traps on UDP 162
- Use snmptrapd and zabbix_trap_receiver.pl to capture traps
- Write traps to a Zabbix-monitored log file
- Rotate the trap log automatically
- Verify correct trap delivery and troubleshoot via SELinux if needed

Once traps are arriving, you can create SNMP trap items in Zabbix (type SNMP trap,
key snmptrap[regex]) to trigger events, alerts, and dashboards.

## Testing and debugging

### To test rotation manually

```bash
logrotate --force /etc/logrotate.d/zabbix_traps
```

### Testing SNMP Trap Reception

You can simulate a trap manually using the snmptrap command.

``` bash
Example 1: SNMP v1 Test Trap
snmptrap -v 1 -c public 127.0.0.1 '.1.3.6.1.6.3.1.1.5.4' '0.0.0.0' 6 33 '55' .1.3.6.1.6.3.1.1.5.4 s "eth0"
```

``` bash
Example 2: SNMP v2c Test Trap
snmptrap -v 2c -c public localhost '' 1.3.6.1.4.1.8072.2.3.0.1 1.3.6.1.4.1.8072.2.3.2.1 i 123456
```

### SELinux Considerations

If SELinux is enabled and traps are not being processed, check for denied actions:
``` bash
ausearch -m AVC,USER_AVC -ts recent
```

Adjust SELinux policies or create exceptions for /usr/bin/zabbix_trap_receiver.pl and the trap log directory as needed.

### (Optional) SNMPv3 Trap Configuration

If using SNMPv3 for secure traps, you can define users directly in snmptrapd.conf:

``` bash
createUser -e <engineid> <user> SHA <key> AES <key>
authUser log,execute <user>
perl do "/usr/bin/zabbix_trap_receiver.pl";
```

This adds authentication and encryption for trap communication.


## Trap mapping and preprocessing


## Conclusion

## Questions

## Useful URLs
