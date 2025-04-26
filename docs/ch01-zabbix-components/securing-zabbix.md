# Security

!!! Topic in progress !!!



In today's interconnected IT landscape, monitoring systems like Zabbix have become
critical infrastructure components, offering visibility into the health and performance
of entire networks. However, these powerful monitoring tools also represent potential
security vulnerabilities if not properly secured. This chapter will explores the
essential combination of SELinux and security best practices to harden your Zabbix
deployment against modern threats.

Security is not an optional feature but a fundamental requirement for any monitoring
solution. Zabbix, with its extensive reach across your infrastructure, has access
to sensitive system information and often operates with elevated privileges.
Without proper security controls, a compromised monitoring system can become a
launchpad for lateral movement across your network, potentially exposing critical
business data and systems.

We'll explore how SELinux's mandatory access control framework provides an additional
security layer beyond traditional permissions, and how proper configuration can
dramatically reduce your attack surface. You'll learn practical, implementable
security measures that balance protection with functionality, ensuring your monitoring
capabilities remain intact while defending against both external and internal threats.

Whether you're a system administrator, security professional, or IT manager, understanding
these security principles will help you transform your Zabbix deployment from a
potential liability into a secure asset within your security architecture.


## SELinux and Zabbix

SELinux (Security-Enhanced Linux) provides mandatory access control for Zabbix by
enforcing security policies that restrict what the Zabbix processes can do, even
when running as root.

SELinux contexts are a core component of how SELinux implements security control.
Think of contexts as labels that are assigned to every object in the system (files, processes, ports, etc.).
These labels determine what can interact with what.

### SELinux Enforcement Mode
For SELinux to actually provide security protection, it needs to be set to "enforcing" mode. There are three possible modes for SELinux:

- **Enforcing** - SELinux security policy is enforced. Actions that violate policy are blocked and logged.
- **Permissive** - SELinux security policy is not enforced but violations are logged. This is useful for debugging.
- **Disabled** - SELinux is completely turned off.

You can check the current SELinux mode with the getenforce command:
```yaml
# getenforce
Enforcing
```
To properly secure Zabbix with SELinux, the system should be in "Enforcing" mode. If it's not, you can change it temporarily:

##### Set to enforcing immediately (until reboot)
``` yaml
``` yaml
sudo setenforce 1
```
For permanent configuration, edit /etc/selinux/config and set:
``` yaml
SELINUX=Enforcing
```
```

### Basic Structure of an SELinux Context

An SELinux context typically consists of four parts:

- **User**: The SELinux user identity (not the same as Linux users)
- **Role**: What roles the user can enter
- **Type**: The domain for processes or type for files (most important part)
- **Level**: Optional MLS (Multi-Level Security) sensitivity level

When displayed, these appear in the format: user:role:type:level

### How Contexts Work in Practice

For Zabbix, files and processes related to it would typically have a type like
zabbix_t or similar. For example:

- The Zabbix server process runs in the zabbix_t domain
- Configuration files might have the zabbix_conf_t type
- Log files could have the zabbix_log_t type

When Zabbix tries to access a file or network resource, SELinux checks if the context
of the Zabbix process is allowed to access the context of that resource according to
policy rules.

### Viewing Contexts

You can view the contexts of files using:
ls -Z /path/to/zabbix/files

And for processes:
``` yaml
# ps -eZ | grep zabbix
system_u:system_r:unconfined_service_t:s0 691 ?  00:02:20 zabbix_agent2
system_u:system_r:zabbix_t:s0       707 ?        00:00:59 zabbix_server
system_u:system_r:zabbix_t:s0      1203 ?        00:02:00 zabbix_server
```

And for log files
``` yaml
# ls -alZ /var/log/zabbix/zabbix_server.log
-rw-rw-r--. 1 zabbix zabbix system_u:object_r:zabbix_log_t:s0 11857 Apr 26 22:02 /var/log/zabbix/zabbix_server.log
```

### Zabbix-selinux-policy Package

The zabbix-selinux-policy package is a specialized SELinux policy module designed
specifically for Zabbix deployments. It provides pre-configured SELinux policies
that allow Zabbix components to function properly while running in an SELinux enforced
environment.

Key Functions of the Package

- **Pre-defined Contexts** : Contains proper SELinux context definitions for Zabbix
  binaries, configuration files, log directories, and other resources.
- **Port Definitions** : Registers standard Zabbix ports (like 10050 for agent, 10051 for server)
  in the SELinux policy so they can be used without triggering denials.
- **Access Rules: Defines which operations Zabbix processes can perform, like writing
  to log files, connecting to databases, and communicating over networks.
- **Boolean Toggles: Provides SELinux boolean settings specific to Zabbix that can
  enable/disable certain functionalities without having to write custom policies.

Benefits of Using the Package

- **Simplified Deployment** : Reduces the need for manual SELinux policy adjustments when
installing Zabbix.
- **Security by Default**: Ensures Zabbix operates with minimal required permissions rather than running in permissive mode.
- **Maintained Compatibility**: The package is updated alongside Zabbix to ensure compatibility with new features.

Installation and Usage

The package is typically installed alongside other Zabbix components:
``` yaml
dnf install zabbix-selinux-policy
```
After installation, the SELinux contexts are automatically applied to standard Zabbix
paths and ports. If you use non-standard configurations, you may still need to make
manual adjustments.
This package essentially bridges the gap between Zabbix's operational requirements
and SELinux's strict security controls, making it much easier to run Zabbix securely
without compromising on monitoring capabilities.

### For Zabbix to function properly with SELinux enabled:

Zabbix binaries and configuration files need appropriate SELinux labels (typically zabbix_t context)
Network ports used by Zabbix must be properly defined in SELinux policy
Database connections require defined policies for Zabbix to communicate with MySQL/PostgreSQL
File paths for monitoring, logging, and temporary files need correct contexts

When issues occur, they typically manifest as denied operations in SELinux audit logs. Administrators can either:

Use audit2allow to create custom policy modules for legitimate Zabbix operations
Apply proper context labels using semanage and restorecon commands
Configure boolean settings to enable specific Zabbix functionality

This combination creates defense-in-depth by ensuring that even if Zabbix is compromised,
the attacker remains constrained by SELinux policies, limiting potential damage to
your systems.

### Zabbix SELinux Booleans
One of the most convenient aspects of the SELinux implementation for Zabbix is the
use of "booleans" - simple on/off switches that control specific permissions. These
allow you to fine-tune SELinux policies without needing to understand complex policy
writing. Key Zabbix booleans include:

- **zabbix_can_network** - Controls whether Zabbix can initiate network connections
- **httpd_can_connect_zabbix** - Controls whether the web server can connect to Zabbix
- **zabbix_run_sudo** - Controls whether Zabbix can execute sudo commands

You can view these settings with:

``` yaml
getsebool -a | grep zabbix
```
And toggle them as needed:

### Enable Zabbix network connections (persistent across reboots)
```yaml
setsebool -P zabbix_can_network on
```
These booleans make it much easier to securely deploy Zabbix while maintaining SELinux
protection, as you can enable only the specific capabilities that your Zabbix implementation
needs without compromising overall system security.


## Securing zabbix admi

## HTTPS 

## DB certs


