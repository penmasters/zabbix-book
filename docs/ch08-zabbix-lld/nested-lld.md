---
description: |
    Nested Low-Level Discovery (LLD) in Zabbix enables multi-level discovery
    hierarchies from a single JSON payload using discovery prototypes of type Nested.
tags: [beginner, advanced]
---

# Nested LLD

Automation via Low-Level Discovery (LLD) rarely stops at a single infrastructure
layer. In complex environments you frequently deal with hierarchical structures:
a database server hosting multiple instances, each containing multiple tablespaces;
a hypervisor running virtual machines that each have multiple virtual disks; or a
storage array with pools, volumes and LUNs.

Previously, monitoring these layered structures required separate discovery rules
or custom multi-stage scripts. Starting with **Zabbix 7.4**, Nested LLD (discovery
prototypes of type Nested) lets you build multi-level discovery hierarchies from
a single data stream. A nested discovery rule reuses the JSON payload of its parent
and applies preprocessing to extract and process a specific slice of that same data.

In this chapter we explore how Nested LLD works, walk through a complete
configuration example, and briefly cover its use with host prototypes.

???+ note
    This chapter assumes you are already familiar with the core concepts of
    Low-Level Discovery and Dependent Items. If you need a refresher, refer to
    the previous section on LLD with dependent items.

    Nested LLD requires **Zabbix 7.4 or later**.

## Creating Our Example Data

Before implementing the discovery rules we need structured data. Consider a
database server that returns a JSON payload containing database instances and
their tablespaces.

Log in to your Zabbix server or agent host via SSH and create the following file:

```bash
echo '[
  {
    "database": "db_sales",
    "status": "online",
    "tablespaces": [
      { "name": "ts_sales_data", "size_mb": 10240 },
      { "name": "ts_sales_idx", "size_mb": 4096 }
    ]
  },
  {
    "database": "db_hr",
    "status": "online",
    "tablespaces": [
      { "name": "ts_hr_data", "size_mb": 2048 }
    ]
  }
]' | sudo tee /home/db-cluster-status.json > /dev/null
```

Verify the file:

```bash
cat /home/db-cluster-status.json
```

The structure has two clear levels:

- **Level 1 (Parent):** Database instances (`db_sales`, `db_hr`)
- **Level 2 (Nested):** Tablespaces belonging to each database

## Step 1: Master Item and Parent LLD Rule

### 1. Create the Master Item

In the Zabbix frontend go to **Data collection → Hosts**, select your host, then
**Items → Create item**.

| Field | Value |
|-------|-------|
| Name | RAW: Database cluster metrics |
| Type | Zabbix agent |
| Key | `vfs.file.contents[/home/db-cluster-status.json]` |
| Type of information | Text |

??? tip
    Use the **Test** button to confirm that the agent can read the file and
    returns the expected JSON.

Any item that produces valid JSON can serve as master item (HTTP agent, trapper,
script item, etc.). A file-based item is used here purely for simplicity.

### 2. Create the Parent Discovery Rule

Navigate to **Discovery rules** on the same host and click **Create discovery rule**.

| Field | Value |
|-------|-------|
| Name | Discover databases |
| Type | Dependent item |
| Master item | RAW: Database cluster metrics |
| Key | `db.discovery` |

On the **LLD macros** tab map:

```
{#DB} → $.database
```

### 3. Create an Item Prototype for Level 1

Under the parent discovery rule go to **Item prototypes → Create item prototype**.

| Field | Value |
|-------|-------|
| Name | Status of database {#DB} |
| Type | Dependent item |
| Master item | RAW: Database cluster metrics |
| Key | `db.status[{#DB}]` |
| Type of information | Text |

**Preprocessing:**

```
JSONPath → $..[?(@.database=='{#DB}')].status.first()
```

## Step 2: Configuring the Nested Discovery Prototype

We now want to discover the tablespaces of each database **without** an extra
agent check or external query. This is done with a discovery prototype of type
**Nested**.

### How Nested type works

When the type is set to Nested, Zabbix does **not** re-fetch data. Instead it
passes the individual JSON object that belongs to the currently discovered parent
entity to the nested rule.

For the database `db_sales` the nested rule therefore receives:

```json
{
  "database": "db_sales",
  "status": "online",
  "tablespaces": [
    { "name": "ts_sales_data", "size_mb": 10240 },
    { "name": "ts_sales_idx", "size_mb": 4096 }
  ]
}
```

Preprocessing on the nested rule can then extract the next level (`$.tablespaces`).

### 1. Create the Discovery Prototype

Inside the parent rule **Discover databases**, open the **Discovery prototypes**
tab and click **Create discovery prototype**.

| Field | Value |
|-------|-------|
| Name | Discover tablespaces for {#DB} |
| Type | Nested |
| Key | `db.tablespace.discovery[{#DB}]` |

Including `{#DB}` in the key guarantees uniqueness per parent entity.

### 2. Preprocessing on the Discovery Prototype

On the **Preprocessing** tab add:

```
JSONPath → $.tablespaces
```

This extracts the tablespace array from the single database object that the
Nested type already provided.

### 3. Nested LLD Macros

On the **LLD macros** tab of the discovery prototype:

```
{#TSNAME} → $.name
```

??? note
    LLD macros defined on the parent rule (`{#DB}`) are automatically inherited
    and remain available inside nested discovery prototypes and all of their
    child prototypes.

### 4. Item Prototypes for the Nested Level

Inside the discovery prototype go to **Item prototypes → Create item prototype**.

| Field | Value |
|-------|-------|
| Name | Size of tablespace {#TSNAME} on {#DB} |
| Type | Dependent item |
| Master item | RAW: Database cluster metrics |
| Key | `db.ts.size[{#DB},{#TSNAME}]` |
| Type of information | Numeric (unsigned) |

**Preprocessing:**

```
JSONPath → $..[?(@.database=='{#DB}')].tablespaces[?(@.name=='{#TSNAME}')].size_mb.first()
```

JSONPath Breakdown:

- $.. searches recursively through the original master item JSON.
- [?(@.database=='{#DB}')] filters the specific database instance.
- .tablespaces[?(@.name=='{#TSNAME}')] filters down to the matching tablespace object.
- .size_mb.first() extracts the integer value without returning array brackets.

Because the item is a dependent item of the original master item, the JSONPath
must locate the correct value inside the full original payload. Parent and nested
macros (`{#DB}` and `{#TSNAME}`) make the path unique.

## Nested LLD on Discovered Hosts (Host Prototypes)

Nested LLD also extends to Host Prototypes. When Zabbix generates a new host entity
from a Host Prototype, it passes the JSON object of that discovered entity down to
any template attached to the host prototype.

If a template attached to a host prototype contains a Nested LLD rule:

Typical pattern:

1. Root host runs a discovery rule that creates host prototypes (one host per
   database, for example).
2. The template linked to those host prototypes contains a Nested LLD rule that
   discovers the next level (tablespaces, disks, …).
3. Items and triggers for the nested level appear directly on the generated hosts.

This combination is powerful for multi-level inventory (hypervisors → VMs → disks,
clusters → nodes → services, etc.).

## Key Advantages of Nested LLD

- **Unlimited hierarchical depth** – Server → Database → Tablespace → Table, or
  any other hierarchy you need.
- **Zero extra network or agent overhead** – every level is extracted from the
  single JSON payload collected by the master item.
- **Context preservation** – parent LLD macros stay available at deeper levels,
  keeping item keys unique and readable.
- **Cleaner configuration** – one master item and a tree of discovery prototypes
  replace multiple independent discovery rules or custom scripts.

## Questions

- What is the primary operational benefit of selecting the Nested type on a
  discovery prototype compared to creating a standard LLD rule?
- How are LLD macros from a parent discovery rule made available to nested LLD
  item prototypes?
- What role does the preprocessing step play on a Nested discovery prototype when
  the parent JSON contains nested arrays?

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery/discovery_prototypes](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery/discovery_prototypes)
- [https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery/discovery_prototypes#nested-lld-rules-on-discovered-hosts](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery/discovery_prototypes#nested-lld-rules-on-discovered-hosts)

