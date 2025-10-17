---
description: | This chapter from The Zabbix Book, titled "Host Groups," explains
how to organize and manage monitored hosts effectively in Zabbix. It covers the
creation of host groups, their role in permission management, and how they
simplify large environments by structuring hosts for better visibility and
control. tags: [beginner]
---

# Host Groups

In Zabbix, **host groups** serve as a foundational mechanism for organizing
monitored entities. They allow you to logically categorize hosts for easier
management, simplified permissions, and streamlined configuration, especially
useful in larger environments.

Common examples include:

- Grouping all **Linux servers** together.
- Separating **database servers** (e.g., PostgreSQL, MySQL).
- Organizing hosts by **team**, **location**, or **function**.

Host groups are not only for structuring your monitored hosts, they also play an
important role in assigning templates, setting up user permissions, and
filtering hosts in dashboards or maps.

## Accessing Host Groups

You can manage host groups by navigating to:

**Menu → Data collection → Host groups**

![Host Groups Menu Screenshot](ch02-host-grouops.png)

_2.19 Host Groups menu_

In this menu under `Data collection`, you'll notice two distinct sections:

- **Host groups**: Groups that contain hosts.
- **Template groups**: A newer addition, specifically created for organizing
  templates.

???+ info

    **If you're migrating from an older Zabbix version:**
    In previous versions, templates and hosts were often placed in the same groups.
    This led to confusion, particularly for new users, as templates don't technically
    belong to host groups in Zabbix. As of recent versions (starting from Zabbix
    6.x), template groups are separated out for better clarity.

## Understanding the Host Groups Overview

When you open the **Host groups** menu, you'll see a list of predefined groups.
Each group entry includes:

- **Group name** (e.g., `Linux servers`)
- **Number of hosts** in the group (displayed as a number in front)
- **Host names** currently assigned to that group

Clicking on a host name will take you directly to the host's configuration
screen, providing a convenient way to manage settings without navigating through
multiple menus.

## Creating a Host Group

There are two main ways to create host groups:

### 1. During Host Creation

When adding a new host:

1. Go to **Data collection → Hosts**.
2. Click **Create host** (top right).
3. In the **Host groups** field, select an existing group or type a new name to
   create one on the fly.

### 2. From the Host Groups Page

1. Navigate to **Data collection → Host groups**.
2. Click **Create host group** in the top right.
3. Enter a **Group name** and click **Add**.

![Create new host group](ch02-new-host-group.png)

_2.20 Create new host groups_

## Nested Host Groups

Zabbix supports **nested host groups** using forward slashes (`/`) in group
names. This allows you to represent hierarchies such as:

- `Europe/Belgium`
- `Europe/France`
- `Datacenters/US/Chicago`

These nested group names are **just names** Zabbix does not require that parent
folders (e.g., `Europe`) physically exist as separate groups unless you
explicitly create them.

???+ note

    - You cannot escape the `/` character.
    - Group names **cannot** contain leading/trailing slashes or multiple consecutive
      slashes.
    - `/` is reserved for nesting and cannot be used in regular group names.

## Applying Permissions and Tag Filters to Nested Groups

Once you've created nested groups, the **Host group overview** screen provides
an option to apply permissions and tag filters to all subgroups:

1. Click on a parent group (e.g., `Europe`).
2. A box appears: **Apply permissions and tag filters to all subgroups**.
3. Enabling this will cascade any rights assigned to the parent group down to
   its subgroups.

![Apply subgroup permissions](ch02-sub-groups.png)

_2.21 subgroup permissions_

This is especially useful for user groups. For example:

- If **Brian** is in a user group with access to `Europe/Belgium`, enabling this
  option allows Brian to see all hosts in subgroups like `Europe/Belgium/Gent`
  or `Europe/Belgium/Brussels`, including their tags and data.

## Best Practices

- Use a consistent naming convention: `Location/Function`, `Team/Environment`,
  etc.
- Assign hosts to **multiple groups** if they logically belong in more than one.
- Avoid overly deep nesting keep it readable and manageable.
- Regularly review group usage and clean up unused or outdated groups.

???+ tip

    You can even try adding **emojis** to group names for a fun visual touch! 🎉
    For example: `🌍 Europe/🇧🇪 Belgium` or `📦 Containers/Docker`.

## Conclusion

Host groups are a key organizational tool in Zabbix. With the introduction of
**template groups**, clearer group separation, and support for **nested
structures**, modern versions of Zabbix offer great flexibility for tailoring
your monitoring setup to your organization's structure and workflows.

## Questions

- What are host groups used for in Zabbix?
- Can you assign a host to more than one group?
- How are nested groups created in Zabbix?
- What happens when you apply permissions to subgroups?
- Why are slashes (/) special in host group names?
- Can a parent group exist only logically (i.e., not created in Zabbix)?

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/config/hosts/host_groups](https://www.zabbix.com/documentation/current/en/manual/config/hosts/host_groups)
