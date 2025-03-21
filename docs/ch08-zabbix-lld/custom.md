# Custom Low Level Discovery

???+ note 
    For this chapter we start with a working system with a proper configured agent
    in passive mode. If you have no clue how to do this go back to chapter 01.

Zabbix **Low-Level Discovery** (LLD) provides a dynamic mechanism for automatically
creating monitoring elements based on discovered entities within your infrastructure.

**Core Functionality :**

LLD enables Zabbix to detect changes in your environment and create corresponding
items, triggers, and graphs without manual intervention. This automation is particularly
valuable when monitoring elements with fluctuating quantities or identifiers.

**Discovery Targets:**
The discovery process can identify and monitor various system components including:

- File systems
- CPUs
- CPU cores
- Network interfaces
- SNMP OIDs
- JMX objects
- Windows services
- Systemd services
- Host interfaces
- Anything based on custom scripts

Through LLD, administrators can implement scalable monitoring solutions that automatically
adapt to infrastructure changes without requiring constant template modifications.

## Implementing Low-Level Discovery in Zabbix

### The Challenge of Manual Configuration

We could manually create each item but this would be a very time-consuming task
and impossible to manage in large environments. To enable automatic discovery of
our items or entities, we need discovery rules.

### Discovery Rules

These rules send the necessary data to Zabbix for our discovery process. There 
is no limit to the various methods we can employ, the only requirement is that
the end result must be formatted in JSON. This output information is crucial as
it forms the foundation for creating our items.

### Prototypes and Automation

Once our discovery rule is in place, we can instruct Zabbix to automatically generate
items, triggers, graphs, and even host prototypes. These function as blueprints
directing Zabbix how to create those entities.

### LLD Macros

To enhance flexibility, Zabbix implements LLD macros. These macros always begin
with a # character before their name (e.g., {#FSNAME}). Acting as placeholders for
the values of discovered entities, Zabbix replaces these macros with the actual
discovered names of the items during the implementation process.

### The Zabbix Low-Level Discovery Workflow

The workflow that Zabbix follows during Low-Level Discovery consists of four
distinct phases:

**Discovery Phase**
* Zabbix executes the discovery item according to the defined discovery rule
* The item returns a JSON list of discovered entities

**Processing Phase**
* Zabbix parses the JSON data and extracts the necessary information

**Creation Phase**
* For each discovered entity, Zabbix creates items, triggers, and graphs based on
  the prototypes
* During this process, LLD macros are replaced with the actual discovered values

**Monitoring Phase**
* Zabbix monitors the created items using standard monitoring procedures

### Advantages of LLD Implementation

The benefits of implementing Low-Level Discovery are substantial:

* **Automation** - Creation of items, triggers, graphs, and hosts becomes fully
  automated
* **Scalability** - Enables monitoring of large numbers of hosts or items without
  manual intervention
* **Adaptability** - Zabbix can dynamically adjust to environmental changes by 
  creating or removing entities as needed

### Learning Path Rationale

We begin our series with LLD based on custom scripts because, while it represents
one of the more complex topics, mastering this concept provides a solid foundation.
Once you understand this implementation approach, the other LLD topics will be
considerably easier to comprehend.

Below is a sample JSON structure that Zabbix can interpret for Low-Level Discovery:

!!! info ""
    ``` yaml
    {
      "data": [
        {
          "{#FSNAME}": "/",
          "{#FSTYPE}": "ext4"
        },
        {
          "{#FSNAME}": "/boot",
          "{#FSTYPE}": "ext4"
        },
        {
          "{#FSNAME}": "/data",
          "{#FSTYPE}": "xfs"
        }
      ]
    }
    ```
Upon receiving this JSON data, Zabbix processes the discovery information to identify
distinct file systems within the monitored environment. The system extracts and
maps the following elements:

- File system mount points: /, /boot, and /data
- File system types: ext4 and xfs

Zabbix automatically associates these discovered values with their corresponding
LLD macros {#FSNAME} for the mount points and {#FSTYPE} for the file system types.
This mapping enables dynamic creation of monitoring objects tailored to each specific
file system configuration.


## Creating a custom script.

In this example, we will develop a custom script to monitor user login activity on
our systems. This script will track the number of users currently logged into each
monitored host and report their login status.

The implementation requires placing a custom script in the appropriate location on
systems running Zabbix Agent (either version 1 or 2). Create the following script
in the `/usr/bin/` directory on each agent installed system:

!!! info "create our script"
    ``` yaml
    sudo vi /usr/bin/users-discovery.sh
    ```
paste the following content in the file:

!!! info "users-discovery.sh"
    ``` yaml
    #!/bin/bash

    # Find all users with UID ≥ 1000 of UID = 0 from /etc/passwd, except "nobody"
    ALL_USERS=$(awk -F: '($3 >= 1000 || $3 == 0) && $1 != "nobody" {print $1}' /etc/passwd)
    
    # Find all active users
    ACTIVE_USERS=$(who | awk '{print $1}' | sort | uniq)
    
    # Begin JSON-output
    echo -n '{"data":['
    FIRST=1
    for USER in $ALL_USERS; do
        # Check if the user is active
        if echo "$ACTIVE_USERS" | grep -q "^$USER$"; then
            ACTIVE="yes"
        else
            ACTIVE="no"
        fi
    
        # JSON-format
        if [ $FIRST -eq 0 ]; then echo -n ','; fi
        echo -n "{\"{#USERNAME}\":\"$USER\", \"{#ACTIVE}\":\"$ACTIVE\"}"
        FIRST=0
    done
    echo ']}'
    ```
Once you have created the script don't forget to make it executable.

!!! info ""
    ``` yaml
    sudo chmod +x /usr/bin/users-discovery.sh
    ```
The script will be executed by the Zabbix agent and will return discovery data
about user sessions in the JSON format required for Low-Level Discovery processing.

Once deployed, this script will function as the data collection mechanism for our
user monitoring solution, enabling Zabbix to dynamically discover user sessions
and track login/logout activities across your infrastructure.

**User Provisioning for Testing**

Let's establish additional test user accounts on our system to ensure we have
sufficient data for validating our monitoring implementation. This will provide
a more comprehensive testing environment beyond the default root account and your
personal user account. Feel free to add as many users as you like.

!!! info "create some users"
    ``` yaml
    sudo for user in sven brian cartman kenny; do sudo useradd $user; done
    ```


