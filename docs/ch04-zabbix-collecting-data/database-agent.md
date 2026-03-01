---
description: |
    Monitor databases easily with Zabbix Agent 2 plugins — collect metrics from
    MySQL, PostgreSQL, and more without external scripts or complex setup.
tags: [advanced]
---

# Database checks via Zabbix agent 2
Now that we have covered database monitoring by ODBC, you might have some security questions. Because with ODBC, you will always have to open up your database for remote connections by our Zabbix server or proxy. For some environments, this might be out of the question. ODBC monitoring also requires additional tooling to be installed, which is something you will need to maintain.

The Zabbix agent 2 however, comes with built-in functionality to monitor some of the most popular SQL and no-SQL databases.
- MariaDB
- MySQL
- PostgreSQL
- Microsoft SQL
- Oracle
- Redis
- MongoDB

The great part about using the Zabbix agent for monitoring your database is, you most likely already have the Zabbix agent installed on the Windows or Linux server running that database. Since the Zabbix agent is running on the local machine, the Zabbix agent can now be used to connect using localhost (127.0.0.1) to the database.

![Zabbix ODBC vs Agent Database connection*](ch04.xx-odbc-vs-agent.png){ align=center }
*4.x Zabbix ODBC vs Agent Database connection*


## Plugin installation
It's important to note that for Zabbix agent 2 to support database monitoring, you might have to install some additional plugin packages. This is the case specifically for:

- PostgreSQL
- Microsoft SQL
- MongoDB

To install the packages on Linux is not too much additional work, as we should already have the Zabbix repository available. Simply issues the following command to install the additional package(s) and you should be ready to go.

!!! info "Install Zabbix agent 2 database monitoring plugins"

    RHEL-based:

    ``` dnf install zabbix-agent2-plugin-mongodb zabbix-agent2-plugin-mssql zabbix-agent2-plugin-postgresql
    ```

    Debian based:

    ``` apt install zabbix-agent2-plugin-mongodb zabbix-agent2-plugin-mssql zabbix-agent2-plugin-postgresql
    ```

    SUSE:

    ``` zypper in zabbix-agent2-plugin-mongodb zabbix-agent2-plugin-mssql zabbix-agent2-plugin-postgresql
    ```

On Windows we do have some additional steps, as we need to download an additional MSI. We can find the MSI at the following URL.

[https://cdn.zabbix.com/zabbix/binaries/stable/](https://cdn.zabbix.com/zabbix/binaries/stable/)

It's also possible to download the packages from [https://www.zabbix.com/download_agents?](https://www.zabbix.com/download_agents?). At this website simply select `OS Distribution` as `Windows` and at `Encryption` select `No encryption`. This will show you the `Zabbix agent2 plugins vx.x.x` MSI download link for your selected Windows version.

## Setting up Microsoft SQL monitoring
Let's have a look at how to monitor a Microsoft SQL server using the Zabbix agent 2 database monitoring. 

### Custom SQL queries

## Setting up Redis and MongoDB monitoring

## Conclusion

## Questions

## Useful URLs
