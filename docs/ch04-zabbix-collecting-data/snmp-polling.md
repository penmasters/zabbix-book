# SNMP Polling

In the previous chapter, we explored monitoring strategies that relied on both
active and passive Zabbix agents. This chapter introduces an alternative approach
monitoring via SNMP (Simple Network Management Protocol) which does not require
the installation of a Zabbix agent on the monitored device. This method is
especially useful in environments where agent based monitoring is impractical,
restricted or simply not allowed.

Simple Network Management Protocol (SNMP) is a widely adopted protocol designed
for monitoring and managing devices on IP networks. Despite the word "management"
in its name, SNMP is predominantly employed for monitoring purposes. Its widespread
support across networking hardware and embedded systems has made it a cornerstone
of modern network visibility solutions.

Originally developed in the late 1980s, SNMP has undergone several revisions.
Early versions, such as SNMPv1 and SNMPv2c, were hampered by significant security
limitations. As a result, while SNMP includes functionality for remote device
configuration, its use has remained largely to status monitoring rather than
active management of devices.

SNMP is especially valuable for monitoring resource constrained or embedded devices
that lack the capacity to run a full monitoring agent.

Common examples include:

- Printers
- Network switches, routers, and firewalls
- Uninterruptible Power Supplies (UPSs)
- NAS (Network-Attached Storage) appliances
- Environmental sensors (e.g., temperature, humidity sensors)

These devices often provide built-in SNMP support, making them accessible for monitoring
with minimal configuration. Additionally, SNMP can be employed on standard servers
where installing or maintaining a Zabbix agent is either impractical or not permitted.
This could be due to administrative policies, software compatibility or security
concerns, or simply a desire to reduce system footprint.

Recognizing the ubiquity of SNMP, Zabbix provides native SNMP support. This
capability is powered by the open-source Net-SNMP suite, available at
http://net-snmp.sourceforge.net. The integration allows Zabbix to retrieve
metrics from SNMP-enabled devices using industry-standard mechanisms.

In this chapter, we will cover the following:

- An introduction to the Net-SNMP toolkit and its core utilities.
- How to integrate MIB (Management Information Base) files into Zabbix, enabling
  the platform to interpret SNMP data correctly.
- The process of SNMP polling within Zabbix, including how to define SNMP-based
  items and retrieve data from devices.

This chapter serves as the foundation for SNMP-based monitoring in Zabbix. While
we begin with the essentials such as polling, MIB usage, and SNMP item
configuration this is just the start.

Later in this book, we will build upon this knowledge by exploring Low-Level
Discovery (LLD) mechanisms using SNMP. LLD allows Zabbix to automatically detect
and create monitoring items for dynamic or repetitive structures, such as
network interfaces, power supplies, ...

---

## Net-SNMP

The Simple Network Management Protocol (SNMP) is a widely used protocol for monitoring
and managing networked devices. It operates primarily over UDP port 161, though in
certain cases, SNMP agents or proxies may also support TCP port 161 for enhanced
reliability or integration with specific tools. SNMP allows administrators to query
information or trigger actions on remote devices using structured data identified
by Object Identifiers (OIDs).

To begin working with SNMP in a lab or testing environment, you may choose between
two approaches:

- Use an existing SNMP capable device already present in your network infrastructure.
- Deploy a lightweight SNMP agent on a general-purpose server, such as your Zabbix
  server or a dedicated virtual machine.

In this chapter, we will walk through the installation and configuration of a basic
SNMP agent on a Rocky or Ubuntu based Zabbix server. However, the same setup can
be applied to any compatible Linux system.

Note: If you're using a device already present on your network, ensure:

- You have network access to the device (verify routing and firewall settings).
- SNMP access is allowed from your Zabbix server’s IP address.
- The correct community string is configured, and your IP is included in the SNMP
  access control rules of the device.

---

### Testing an SNMP Device: Where to Start?

When you're looking to test an SNMP device, it's crucial to understand the available
SNMP versions and which ones you should prioritize. Currently, there are three
commonly used versions: **SNMPv1**, **SNMPv2c**, and **SNMPv3**.

- **SNMPv1**: This is the oldest version and should generally be avoided unless
  absolutely necessary. It's quite limited in functionality and has serious security
  vulnerabilities.
- **SNMPv2c**: Still the most prevalent version today, SNMPv2c offers improvements
  over v1, especially in data retrieval and performance. It's relatively straightforward
  to configure and use.
- **SNMPv3**: This version is rapidly gaining popularity and is considered the most
  secure and advanced option. It provides encryption, authentication, and user
  management, which are essential for secure networks.

#### Your First Test Attempt: SNMPv2c and the 'public' Community String

To begin your testing, we recommend trying to connect to your device using **SNMPv2c**
and the standard **community string 'public'**. Many devices ship with these default
settings, though it's certainly insecure for production environments.

You can use the `snmpstatus` command for this. Here’s an example of how you might
do this in your terminal:

```bash
snmpstatus -v 2c -c public [IP-address_of_the_device]
```

Replace `[IP-address_of_the_device]` with the actual IP address or hostname of the
device you wish to test.

#### What if You Get No Information Back?

If you don't receive any information after this attempt, don't panic. It simply means
the default settings likely don't apply to your device, or there might be a network
related issue. You'll need to dig deeper into your device's configuration or troubleshoot
your network.

**First, check the device's configuration:**

1. **SNMP Version**: Which SNMP version (v1, v2c, or v3) is configured and enabled?
2. **Community String (for v1/v2c)**: If your device uses SNMPv1 or SNMPv2c, what
   is the configured community string (similar to a password) for read-only and
   potentially read- write access? It's rarely 'public' in a properly configured
   environment.
3. **Username, Authentication, and Privacy (for v3)**: If your device uses SNMPv3,
   you'll need more specific information:
   - **Username**: What username has been created for SNMPv3?
   - **Authentication Protocol and Password**: Which authentication protocol (e.g.,
     MD5, SHA) is used, and what is its corresponding password?
   - **Privacy Protocol and Password**: Which encryption protocol (e.g., DES, AES)
     is used, and what is its corresponding password?

**Next, consider potential network issues:**

Even if your device is correctly configured, network obstacles can prevent SNMP communication.
Check for:

- **Firewall Blocking**: A firewall (either on your testing machine, the network,
  or the SNMP device itself) might be blocking the UDP port 161, which SNMP typically
  uses. Ensure the necessary ports are open.
- **ACL Settings on the Device**: The SNMP device itself might have Access Control
  List (ACL) settings configured to restrict access only to specific IP addresses.
  Verify that your testing machine's IP address is permitted.
- **Network Connectivity**: Basic network issues like incorrect IP addresses, subnet
  masks, or routing problems can also prevent communication. Ensure there's a clear
  network path between your testing machine and the SNMP device.

#### Examples of SNMPv3 Commands

Once you have the necessary information (and have ruled out network issues), you
can try connecting with SNMPv3. Here are some examples of how you might use `snmpstatus`
with SNMPv3 (depending on your configuration):

- **Authentication only (no encryption):**

  ```bash
  snmpstatus -v 3 -l authNoPriv -u [username] -a [authentication_protocol] -A [authentication_password]
  [IP-address_of_the_device]
  ```

  (Replace `[authentication_protocol]` with `MD5` or `SHA`)

- **Authentication and Encryption:**

  ```bash
  snmpstatus -v 3 -l authPriv -u [username] -a [authentication_protocol] -A [authentication_password]
  -x [privacy_protocol] -X [privacy_wachtwoord] [IP-address_of_the_device]
  ```

  (Replace `[authentication_protocol]` with `MD5` or `SHA` and `[privacy_protocol]`
  with `DES` or `AES`)

#### Next, consider potential network issues

Even if your device is correctly configured, network obstacles can prevent SNMP
communication. Check for:

**Firewall Blocking:** A firewall (either on your testing machine, the network, or
the SNMP device itself) might be blocking the UDP port 161, which SNMP typically
uses. Ensure the necessary ports are open.

**ACL Settings on the Device:** The SNMP device itself might have Access Control
List (ACL) settings configured to restrict access only to specific IP addresses.
Verify that your testing machine's IP address is permitted.

**Network Connectivity:** Basic network issues like incorrect IP addresses, subnet
masks, or routing problems can also prevent communication. Ensure there's a clear
network path between your testing machine and the SNMP device.

#### A Note on SNMPv1: Avoid if Possible

While you can technically test with SNMPv1, we strongly advise against using it
in production. SNMPv1 is an outdated and insecure protocol version vulnerable to
various attacks. Always try to connect with v2c or v3 first. Only if you are absolutely
certain that the device exclusively supports SNMPv1 and you have no other option,
you can try using it:

```bash
snmpstatus -v 1 -c [community_string] [IP-address_of_the_device]
```

However, remember that using SNMPv1 in a production environment poses a significant
security risk.

---

### Installing SNMP Agent on a Linux Host

To install the SNMP agent and utilities on your Zabbix server or another compatible
system, follow the steps below.

1. Install Required Packages

```bash
# Optional: Update the package list
sudo dnf update -y
```

```bash
# Install Net-SNMP agent and utilities
sudo dnf install -y net-snmp net-snmp-utils
2. Configure the SNMP Agent
First, create a clean configuration file for the SNMP daemon:
```

```bash
sudo vi /etc/snmp/snmpd.conf
# Or
sudo nano /etc/snmp/snmpd.conf
```

Paste the following example configuration, which is optimized for SNMP-based
discovery and testing in Zabbix:

```bash
tee /etc/snmp/snmpd.conf <<EOF
# --------------------------------------------------------------------------
# SNMP AGENT CONFIGURATION FOR LAB ENVIRONMENTS
# Target: Rocky Linux SNMP host used with Zabbix LLD
# --------------------------------------------------------------------------

# Basic access control — WARNING: 'public' is insecure and should only be used
# in isolated lab environments.
rocommunity public

# Alternative: Restrict community string access to a specific subnet
# rocommunity my_secure_community 192.168.56.0/24

# Optional system metadata
syslocation  "Rocky Linux Zabbix SNMP Lab Server"
syscontact   "Your Name <your.email@example.com>"
sysname      "RockySNMPHost01"

# Enable essential MIB modules for Zabbix LLD (Low-Level Discovery)
view systemview included .1.3.6.1.2.1.1    # SNMPv2-MIB (System info)
view systemview included .1.3.6.1.2.1.25   # HOST-RESOURCES-MIB
view systemview included .1.3.6.1.2.1.2    # IF-MIB (Interfaces)
view systemview included .1.3.6.1.2.1.4    # IP-MIB
view systemview included .1.3.6.1.2.1.6    # TCP-MIB
view systemview included .1.3.6.1.2.1.7    # UDP-MIB

# Optional: Extend SNMP with exec commands (custom LLD support)
# exec dockerContainers /opt/scripts/docker_lld.sh

# Enable syslog logging
dontLogTCPWrappers no
EOF
```

Start the SNMP Service and Configure the Firewall

```bash
# Start the SNMP daemon
sudo systemctl start snmpd
```

```bash
# Enable it to start on boot
sudo systemctl enable snmpd
```

```bash
# Check that the service is running
sudo systemctl status snmpd
If your system uses firewalld, ensure that SNMP traffic is allowed:
```

```bash
# Add SNMP to permanent firewall rules
sudo firewall-cmd --add-service=snmp --permanent
```

```bash
# Reload the firewall configuration
sudo firewall-cmd --reload
```

```bash
# Confirm that SNMP is listed
sudo firewall-cmd --list-services --permanent
```

```bash
Verifying SNMP Functionality
From your Zabbix server or any SNMP client system with net-snmp-utils installed:

# General system info (sysDescr, sysUptime, etc.)

snmpwalk -v2c -c public <IP_ADDRESS> .1.3.6.1.2.1.1

# List interface names (useful for interface LLD)

snmpwalk -v2c -c public <IP_ADDRESS> .1.3.6.1.2.1.2.2.1.2

# List filesystem descriptions

snmpwalk -v2c -c public <IP_ADDRESS> .1.3.6.1.2.1.25.2.3.1.3

# Get CPU load per processor core

snmpwalk -v2c -c public <IP_ADDRESS> .1.3.6.1.2.1.25.3.3.1.2
```

## Conclusion

## Questions

## Useful URLs
