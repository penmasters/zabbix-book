---
description: |
    blabla todo
tags: [beginner]
---

# Nested LLD

Automation via Low-Level Discovery (LLD) rarely stops at a single infrastructure
layer. In complex environments, you frequently deal with hierarchical structures:
think of a database server hosting multiple database instances, each containing
multiple tablespaces, or a hypervisor running virtual machines that each have
multiple virtual disks attached.

Previously, monitoring these layered structures required separate discovery rules or custom multi-stage scripts. With Nested LLD (discovery prototypes using the Nested type), you can construct multi-level discovery hierarchies within a single data stream. The nested discovery rule reuses the JSON payload from the parent discovery rule and applies preprocessing to extract and process a specific slice of that same data payload.

In this chapter, we will explore how Nested LLD works, step-by-step configuration of discovery prototypes, and how to apply this technique to both regular hosts and dynamically generated host prototypes.

???+ note

    For this chapter, we assume you are already familiar with the core concepts
    of Low-Level Discovery and Dependent Items. If you need a refresher, feel
    free to refer back to the previous section LLD with dependent items.

Creating Our Example Data
Before we can implement our Low-Level Discovery (LLD) rules, we first need structured data to work with. Consider a scenario where a database server provides a JSON response containing both the database instances and their underlying tablespaces.

Log in to your Zabbix server or agent via SSH and create a text file containing the JSON structure that will serve as the master item payload:

Run the following command:

``` bash
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

Verify that the file was created correctly:

```bash
cat /home/db-cluster-status.json
```

# Save the markdown content to a file
markdown_text = """# Nested LLD

Automation via Low-Level Discovery (LLD) rarely stops at a single infrastructure layer. In complex environments, you frequently deal with hierarchical structures: think of a database server hosting multiple database instances, each containing multiple tablespaces, or a hypervisor running virtual machines that each have multiple virtual disks attached.

Previously, monitoring these layered structures required separate discovery rules or custom multi-stage scripts. With **Nested LLD** (discovery prototypes using the *Nested* type), you can construct multi-level discovery hierarchies within a single data stream. The nested discovery rule reuses the JSON payload from the parent discovery rule and applies preprocessing to extract and process a specific slice of that same data payload.

In this chapter, we will explore how Nested LLD works, step-by-step configuration of discovery prototypes, and how to apply this technique to both regular hosts and dynamically generated host prototypes.

---

> **Note**  
> For this chapter, we assume you are already familiar with the core concepts of Low-Level Discovery and Dependent Items. If you need a refresher, feel free to refer back to the previous section *LLD with dependent items*.

---

## Creating Our Example Data

Before we can implement our Low-Level Discovery (LLD) rules, we first need structured data to work with. Consider a scenario where a database server provides a JSON response containing both the database instances and their underlying tablespaces.

Log in to your Zabbix server or agent via SSH and create a text file containing the JSON structure that will serve as the master item payload:

Run the following command:

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
