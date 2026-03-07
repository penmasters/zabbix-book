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

We are going to assume you have already installed the Zabbix agent 2 and the plugins on your server. If you do not know how, check out the previous part of this chapter titled `Zabbix Agent installation and Passive monitoring` and the steps above.

## Setting up Microsoft SQL monitoring
Let's have a look at how to monitor a Microsoft SQL server using the Zabbix agent 2 database monitoring. For the default setup with a Microsoft SQL server, things are fairly simple. First, we go to `Data collection` | `Hosts` and create a new host for our Windows server.

![Host creation - Windows server SQL](ch04.x-host-creation-windows-server-sql.png){ align=center }

*4.x Host creation - Windows server SQL*

With the host created, it's important to note here we used the template `MSSQL by Zabbix agent 2`. This is a default template provided by Zabbix which will already include most of the important statistics you'd need monitoring a Microsoft SQL server. It's possible to monitor SQL servers using the Zabbix agent in both `passive` and `active` mode. If you'd like to use `active` mode just clone template `MSSQL by Zabbix agent 2` to `MSSQL by Zabbix agent 2 active` and change all `item types` to `Zabbix agent (active)`.

In the end it does not matter if you use a passive or active agent, as long as you have the agent connection setup we can do the next step. We need to configure our Zabbix agent to connect to the database server via the network. We do this using the macros on the host.

![Windows server SQL host macros](ch04.x-windows-server-sql-macros.png){ align=center }

*4.x Windows server SQL host macros*

Since the agent is installed on the server running Microsoft SQL, we can simply connect to `localhost` or `127.0.0.1`. That means the connection from the Zabbix agent towards the Microsoft SQL server never leaves the server itself and we do not need to expose our SQL server port to the network for our Zabbix server or proxy. Combined with Zabbix agent active mode and encryption, we can guarantee a secure setup that is ready for high-risk environments like banks, hospitals, air traffic and even military applications. This is the biggest advantage of using the Zabbix agent 2 database monitoring, compared to ODBC.

Once we fill out the `{$MSSQL.USER}`, `{$MSSQL.PASSWORD}` and `{$MSSQL.URI}` macros, the Zabbix agent should be able to connect to our SQL server. Navigating to `Monitoring` | `Latest data` should now show us a bunch of data from the SQL server marking the successful configuration of our monitoring.

![Windows server SQL host macros](ch04.x-windows-server-sql-macros.png){ align=center }

*4.x Windows server SQL host macros*

### Custom SQL queries

## Setting up Redis and MongoDB monitoring

## Conclusion

## Questions

## Useful URLs
