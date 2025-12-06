---
description: |
    Optimize Zabbix monitoring with Proxy Groups for automated High Availability
    (HA) and Load Balancing (LB). Master configuration and failover logic.
tags: [advanced]
---
# Proxy groups

## Zabbix Proxy Groups: High Availability and Load Balancing

Zabbix Proxy Groups provide a robust foundation for **enterprise-grade distributed
monitoring**, enabling automatic **High Availability (HA)** and **Load Balancing
(LB)** across multiple proxies. Instead of binding a monitored host to a single
proxy, the host is assigned to a **Proxy Group**. The Zabbix server then determines
dynamically and continuously which proxy within the group is responsible for monitoring
that host.

This approach ensures uninterrupted monitoring during proxy failures and maintains
an even workload across the proxy infrastructure.

---

## Overview and Core Concepts

Proxy groups operate under the control of the **Zabbix Server’s Proxy Group Manager**, which continuously evaluates proxy status, host assignments, and overall group health. Two major capabilities define this feature: **automatic failover** and **workload balancing**.

### 1. High Availability (HA) Through Automatic Failover

**Failover Mechanism:**
If a proxy stops communicating with the Zabbix server and exceeds the configured
**Failover period**, it is marked *Offline*. The Proxy Group Manager then
**immediately reassigns** all hosts monitored by that proxy to the remaining
online proxies in the group.

**Outcome:**
Monitoring continues with minimal disruption and without manual intervention.

### 2. Load Balancing Through Host Redistribution

**Balancing Mechanism:**
The Zabbix server evaluates the number of hosts assigned to each proxy. # Proxy groups

## Zabbix Proxy Groups: High Availability and Load Balancing

Zabbix Proxy Groups provide a robust foundation for **enterprise-grade distributed
monitoring**, enabling automatic **High Availability (HA)** and **Load Balancing
(LB)** across multiple proxies. Instead of binding a monitored host to a single
proxy, the host is assigned to a **Proxy Group**. The Zabbix server then determines
dynamically and continuously which proxy within the group is responsible for monitoring
that host.
                                                                                                                                                             
This approach ensures uninterrupted monitoring during proxy failures and maintains
an even workload across the proxy infrastructure.

---

## Overview and Core Concepts

Proxy groups operate under the control of the **Zabbix Server’s Proxy Group Manager**,Load balancing is triggered if an imbalance is detected, defined by **two simultaneous conditions**:

1.  A difference of **greater than 10 hosts**, **and**
2.  The number of hosts assigned to a proxy is **double the group average or more**.

**Redistribution Logic:**

1. Compute the **average hosts per proxy**.
2. Proxies with excess hosts move them into an **unassigned pool**.
3. Proxies with a deficit receive hosts from this pool.



Example:

| Proxy Host Count | Group Average | Triggered? | Explanation |
| :---: | :---: | :---: | :--- |
| **100** | 50 | **Yes** | Host count is double the average (2×) and difference is 50 (>10). |
| 60 | 50 | No | Difference is 10 (not >10); not sufficient to trigger rebalancing. |
| 40 | 50 | No | Deficit of 10; insufficient to trigger balancing. |
| **25** | 5 | **Yes** | Proxy has 5× the average (≥2×) and difference is 20 (>10). |

---

## Advanced Operational Detail

The following technical details govern the behavior of the Proxy Group Manager and agents.

### Internal Management and Communication

| Mechanism | Description |
| :--- | :--- |
| **Communication Flow** | Proxies communicate **only with the Proxy Group Manager** on the Zabbix server. Proxies **do not communicate with each other**. |
| **Group Membership** | Each proxy can belong **only to a single proxy group**. |
| **State Change Trigger** | Proxy and proxy group states change only **after the configured failover period** has expired. |
| **Shared Knowledge** | All proxies in the group are informed by the server about the status and addresses of other proxies in the same group. |

### Load Balancing Time Window

* If a proxy group is flagged as unbalanced, the Proxy Group Manager will **wait until the grace period of $10 \times$ the failover delay has expired**.
* This grace period prevents redistribution based on temporary spikes. If the imbalance persists, host redistribution is performed.

### Agent Configuration Rules

#### Passive Agents (`Server=`)
A Zabbix agent in passive mode **must accept connections from all members of its proxy group**.
* Configure the `Server` parameter with a comma-separated list of all node IP addresses or DNS names.
* It is also possible to specify entire network segments if appropriate.

#### Active Agents (`ServerActive=`)
The active agent (v7.0+) will dynamically learn the optimal proxy. It is configured in one of two ways:

1.  **Specify Multiple Proxies:** Specify multiple proxy addresses using **semicolons**. Any proxy group member the agent connects to can redirect the agent to the currently assigned proxy.
2.  **Specify Zabbix Server:** Specify the **Zabbix server address** instead of the proxy addresses. The Proxy Group Manager will redirect the agent to the assigned proxy. The active agent will then add all known proxies to its runtime `ServerActive` parameter.

### Handling Proxy Network Loss

* If a proxy loses its network connection to the Zabbix server, the Proxy Group Manager will automatically reassign the proxy's hosts to other online proxies.
* The disconnected proxy will mark itself as offline and will **redirect any active agents** attempting to connect to it toward the other proxies in the group.

---

## Configuration Workflow

Deploying proxy groups effectively involves three main steps.

### Step 1: Create the Proxy Group

In the Zabbix frontend:

1.  Navigate to **Administration → Proxy groups**.
2.  Click **Create proxy group**.

| Parameter | Description | Recommendation |
| :--- | :--- | :--- |
| **Name** | Descriptive group name (e.g., `EMEA_Prod_Proxies`). | Use consistent naming tied to region, function, or environment. |
| **Failover period** | Maximum downtime allowed before proxy becomes *Offline* and failover is triggered. | Default: **1m**. Supports `s`, `m`, `h`. |
| **Minimum number of proxies** | Minimum required online proxies for the group to be considered *Online*. | Use $N-1$ if you want one proxy failure tolerance. |
| **Proxies** | Members participating in load sharing and HA. | Add all intended proxies. |

### Step 2: Assign Hosts to the Proxy Group

Hosts must be explicitly assigned to the proxy group:

1.  Select hosts in **Hosts**.
2.  Use **Mass Update**.
3.  Set **Monitored by proxy = <Proxy Group Name\>**.

Only hosts assigned to the group are eligible for automated failover and load balancing.

---

## Architecture Diagram

```mermaid
flowchart LR
    subgraph Server["Zabbix Server"]
        PGM["Proxy Group Manager"]
    end

    subgraph ProxyGroup["Proxy Group"]
        PX1["Proxy 1"]
        PX2["Proxy 2"]
        PX3["Proxy 3"]
    end

    subgraph Hosts["Monitored Hosts"]
        H1["Host A"]
        H2["Host B"]
        H3["Host C"]
        H4["Host D"]
    end

    PGM --> PX1
    PGM --> PX2
    PGM --> PX3

    PX1 <---> H1
    PX2 <---> H2
    PX3 <---> H3
    PX2 <---> H4

    %% Failover arrows
    PX1 -.Failover/Load Balancing.-> PX2
    PX2 -.Failover/Load Balancing.-> PX3
```

## Important Considerations and Limitations

* **Version Requirements:** All proxies must run Zabbix **7.0 or later** and match the server version.
* **Firewall Requirements:** Agents must be able to communicate with **every proxy** in the group.
* **SNMP Traps Not Supported:** Proxy groups **cannot process SNMP traps**. Traps must be routed to a dedicated, non-grouped proxy.
* **External Dependencies Must Be Identical:** If proxies use external check scripts, ODBC configuration, or third-party integrations, ensure **all proxies have identical configurations**.
* **VMware Monitoring Impact:** VMware hypervisors may be distributed across proxies, and each proxy will retrieve cached data from vCenter, increasing load.

---

## Some Good Practices

* Use at least three proxies for stable HA and load balancing.
* Ensure **symmetric configuration** across all proxies (scripts, credentials, ODBC drivers, time sync).
* Monitor proxy performance using built-in templates to understand load and redistribution frequency.
* Keep failover periods short for high-criticality environments.
* Test failover events regularly in non-production environments.

---
## Practical Example

This example utilizes a single Zabbix Server and a three node Proxy Group to provide
superior High Availability (HA) and load balancing for a large remote location.
This configuration allows for failure tolerance and demonstrates mixed Active/Passive
monitoring modes.

You don't need multiple virtual machines but of course we won't stop you if you
want too. :) An easy alternative is containers. Or running proxies with different
configuration files manually from the command line with the option `-c` or `--config-file`.
If you don't know how have a look at our previous chapter `Running proxies as containers`.

### Environment Overview

| Component | Quantity | Role |
|:---       |:---      |:---  |
| Zabbix Server | 1 (zbx-server-main) | Central hub for all collected data. |
| Zabbix Proxies | 3 (zbx-proxy-A1, A2, A3) | Collect data locally at the branch office. |
| Hosts | 300 | Monitored devices in the branch office. |
| Monitoring Group | Branch-A_HA_Group      | The Zabbix entity responsible for distributing the |
| | |300 hosts across the 3 proxies for redundancy.|


### Zabbix Proxy Configuration File (zabbix_proxy.conf)

The IPs are just examples, adapt them to your own setup.

| Parameter | zbx-proxy-A1 (Active) | zbx-proxy-A3 (Passive) | zbx-proxy-A2 (Active) | Critical Note |
|:---       |:---                   |:---                    |:---                   |:---           |
| IP       | 10.0.0.1              | 10.0.0.2               | 10.0.0.3              | IP/DNS of the the Proxy server. |
| Hostname | zbx-proxy-A1 | zbx-proxy-A3 | zbx-proxy-A2 | Must match the Proxy Name defined in the Zabbix Frontend. |
| ProxyMode | 1 | 0 | 1 | 1 = Active (proxy connects to server). 0 = Passive (server connects to proxy).|
| DBName | /tmp/proxy_a1.db | /tmp/proxy_a3.db | /tmp/proxy_a2.db | Each proxy must use a unique database file when use SQlite3 .|

### Zabbix Frontend Setup (Administration)

Follow these steps in the Zabbix Web Interface (Administration section) to create and assign the Proxy Group.

#### Define Individual Proxies (Administration -> Proxies)

- Navigate to `Administration`-> `Proxies`.
- Click `Create proxy`.
- Define all three proxies one by one:
    - Proxy name: Enter the `Hostname` (e.g., `zbx-proxy-A1`).
    - Proxy mode: Select Active (1) for A1 and A2, and Passive (0) for A3.
    - Proxy group: Leave as None for now.
- Click Add.

![ch03-add-proxy.png](ch03-add-proxy.png)
_ch03 Add proxy_

#### Create the Proxy Group (Administration -> Proxy groups)

- Navigate to `Administration`-> `Proxy groups`.
- Click `Create proxy group`.
- Configure the group parameters for High Availability:
    - Name: `Branch-A_HA_Group`
    - Minimum proxies: Set to 2. This ensures if only one proxy remains, the group
      will enter a Degrading state, preventing the single remaining proxy from
      being overloaded.
    - Failover period: `1m` (The time the server waits before redistributing hosts
      from an offline proxy).

![ch03-create-proxy-group.png](ch03-create-proxy-group.png)
_ch03 Create Proxy groups_

#### Assign Proxies to the Group (Administration -> Proxies)

- Go back to `Administration -> `Proxies`.
- Edit each proxy (`zbx-proxy-A1`, `zbx-proxy-A2`, and `zbx-proxy-A3`).
- Change the Proxy group dropdown from `None` to `Branch-A_HA_Group`.
- Define `Address for active agents` add the IP of the proxy.
- Click `Update`.

![ch03-add-proxy-to-group.png](ch03-add-proxy-to-group.png)
_ch03 Add proxy to proxy group_

![ch03-all-proxy-linked.png](ch03-all-proxy-linked.png)
_ch03 All proxies linked with a proxy group_

### Zabbix Agent Configuration (zabbix_agentd.conf)

To ensure hosts can be monitored by any proxy in the group, the `Zabbix Agent`
configuration on the 300 hosts must be aware of all proxy IP addresses. Don't
worry we will not install 300 hosts. Just one agent is fine, we will use a
passive agent and just create 300 dummy agents in the frontend.

| Parameter | Configuration Value Example | Rationale for HA/Load Balancing |
| :---      |:---                         |:---                             |
| Server | "IP_A1,IP_A2,IP_A3,10.0.0.1" | "Passive Checks: Allows the host to accept |
| | | incoming connections (checks) from any IP address in the group (and the Server,|
| | | for redundancy or occasional checks)." |
| ServerActive | IP_A1;IP_A2;IP_A3 | "Active Checks: The agent will attempt to |
| | | send data to the first proxy in the semi-colon list. If that fails, it automatically |
| | | tries the next one, providing agent-side failover."|
| Hostname    | [ Not too important ] | We will use passive agents to the name is not important.|

As a final step you now have to create 300 hosts in the frontend and select
`Monitored by proxy` field to the `proxy group :` `Branch-A_HA_Group`.

Just here is a script for you that will handle those things. Just create an API
token for the Zabbix Administrator account or any account with enough privileges
and fill in the API token and the URL of the zabbix frontend. Make the script
executable `chmod +x create_hosts.py` or whatever you used as name for the
script. Verify also the `Host_group_id`, `Template_id` and the `Proxy_group_id`. 
This can be done by looking at the URL when clicking on them.

???+ note
     For this script to work you need to have python3 and you probably need
     to install pip and the requests module.


``` python
#!/bin/python3
import requests
import json
import random

# --- Configuration ---
ZABBIX_URL = "http://<Server URL>/api_jsonrpc.php"
AUTH_TOKEN = "<API TOKEN>"  # Replace with your Zabbix API token
HOST_COUNT = 300
HOST_GROUP_ID = "2"  # Replace with the actual ID of your target Host Group (e.g., 'Branch A Servers')
TEMPLATE_ID = "10561" # Replace with a common template ID (e.g., 'Template Module Zabbix agent')
PROXY_GROUP_ID = "1" # Replace with the actual ID of your 'Branch-A_HA_Group'

def api_call(method, params, id_val=1):
    """
    Generic function to make a Zabbix API call for 7.2+.
    - Token is passed via Authorization: Bearer header.
    - 'auth' is NOT included in the JSON body anymore.
    """
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {AUTH_TOKEN}",
    }

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id_val
    }

    try:
        # using json= lets requests handle encoding
        response = requests.post(ZABBIX_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Error on method {method}: {e}")
        return None

def create_hosts():
    """Creates the bulk hosts using the host.create API method."""
    print(f"Starting host creation for {HOST_COUNT} hosts...")

    # --- AUTHENTICATION CHECK ---
    auth_check_response = api_call(
        "user.get",
        {"output": ["username"]},
        id_val=1000
    )

    if auth_check_response and 'result' in auth_check_response:
        if auth_check_response['result']:
            user_alias = auth_check_response['result'][0]['username']
            print(f" Authenticated successfully as: {user_alias}")
        else:
            print(" Auth success, but no users returned. Check the token's permissions.")
            return
    elif auth_check_response and 'error' in auth_check_response:
        print(f" Initial Authentication Error. Received: {auth_check_response['error']['data']}")
        print("Please double-check your ZABBIX_URL and AUTH_TOKEN.")
        return
    else:
        print(" Failed to establish connection for authentication check. Check ZABBIX_URL.")
        return

    # --- END AUTHENTICATION CHECK ---

    hosts_created_count = 0
    for i in range(1, HOST_COUNT + 1):
        host_name = f"SIM-HOST-{i:03d}"

        params = {
            "host": host_name,
            "name": host_name,
            "groups": [{"groupid": HOST_GROUP_ID}],
            "templates": [{"templateid": TEMPLATE_ID}],

            # If you are using proxy groups in 7.x:
            "proxy_groupid": int(PROXY_GROUP_ID),
            "monitored_by": 2,

            "interfaces": [{
                "type": 1,  # Zabbix Agent interface
                "main": 1,
                "useip": 1,
                "ip": "127.0.0.1",
                "dns": "",
                "port": "10050"
            }],
            "status": 0  # enabled
        }

        response = api_call("host.create", params, id_val=i + 1)

        if response and 'result' in response:
            host_id = response['result']['hostids'][0]
            print(f"✅ Created host {host_name} (ID: {host_id})")
            hosts_created_count += 1
        elif response and 'error' in response:
            print(f" Error creating {host_name}: {response['error']['data']}")
            if "already exists" in response['error']['data']:
                break
        else:
            print(f" Unknown API error creating {host_name}.")
            break

    print(f"\n--- Script Finished ---")
    print(f"Total Hosts Created: {hosts_created_count}")

if __name__ == "__main__":
    create_hosts()
```

![ch03-proxy-groups.png](ch03-proxy-groups.png)
_ch03 proxy groups_

## Troubleshooting Tips

| Symptom | Possible Cause | Resolution |
| :--- | :--- | :--- |
| **Hosts remain on a failed proxy** | Proxy is still within the **Failover period** OR proxy group is *Offline*. | **Reduce `Failover period`** in the group configuration. Ensure `Minimum number of proxies` is set correctly (e.g., $N-1$). |
| **Load balancing does not occur** | Host difference is below the imbalance threshold (less than 10 hosts difference **or** less than $2\times$ average). | This is **expected behavior**. The imbalance must exceed the $10$ host and $2\times$ factor rules. |
| **Proxy not receiving new configuration** | Proxy is running a version older than the Zabbix server. | **Upgrade the proxy** to match the Zabbix server's major version. |
| **Active agents fail to report after failover** | Incorrect **`ServerActive`** setting OR firewall blocks the redirected proxy. | Ensure the agent can connect to *every* proxy IP address. Verify `ServerActive` includes all proxies or the Zabbix server IP. |
| **SNMP devices not monitored** | Proxy group is being used for SNMP Traps. | Proxy groups **do not support SNMP traps**. Use a dedicated SNMP trap proxy. |

---

## Questions

1.  **What is the minimum Zabbix version required** for both the proxy and agent to fully support Proxy Groups, including Active checks?
2.  Describe the difference between the **High Availability (HA) mechanism** and the **Load Balancing (LB) mechanism** in Zabbix Proxy Groups. When does each occur?
3.  What are the two specific conditions that must be met to trigger **automatic host redistribution** (Load Balancing) within a proxy group?
4.  When configuring a Zabbix Agent for a host assigned to a proxy group, why must the `ServerActive` parameter list **multiple proxy IPs** or the Zabbix server IP?
5.  What is the function of the **`Minimum number of proxies`** setting, and what happens when the number of online proxies drops below this value?
6.  Why is it critical that external dependencies (like custom scripts or ODBC configurations) are **identical** across all proxies within the group?

---

## Conclusion

Zabbix Proxy Groups significantly enhance the resilience and scalability of distributed monitoring environments. Through seamless failover and intelligent workload balancing, they allow enterprises to maintain consistent monitoring coverage even during proxy outages or uneven load distribution. When combined with proper agent configuration, firewall rules, and aligned proxy setups, proxy groups form a foundational component of modern Zabbix deployments.

---

## Useful URLs

- `https://www.zabbix.com/documentation/current/en/manual/distributed_monitoring
- `https://www.zabbix.com/documentation/current/en/manual/distributed_monitoring/proxies/ha
- https://www.zabbix.com/documentation/current/en/manual/concepts/proxy
- https://www.zabbix.com/documentation/current/en/manual/config/items/zabbix_agent/config
