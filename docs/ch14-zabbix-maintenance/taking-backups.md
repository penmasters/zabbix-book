---
description : |
    In this chapter, you'll learn how to implement reliable Zabbix backup strategies
    to safeguard your configuration, historical data, and overall system integrity.
    Backups are critical for disaster recovery and ensure minimal downtime in case
    of data loss or server failure. We'll cover what components need to be backed
    up (such as the database, configuration files, and custom scripts), how often
    to perform backups, and common tools and methods to automate the process. By
    following these best practices, you'll be prepared to restore your Zabbix
    instance quickly and confidently, minimizing risk to your monitoring environment.
---

# Backup strategies
Zabbix relies heavily on the underlying database not only for the collected items (metrics), but also for storing the Zabbix configuration we create in the Zabbix frontend. This database should either be a MariaDB, PostgreSQL or MySQL database in Zabbix 8.0 as those are the official production supported database types. 

Since our history, trends and configuration data is all stored in this central database, taking a meaningful backup of our Zabbix environment is fairly simple. All we have to do is pick a backup method we like for our chosen database and then use that to backup the database. Giving you a backup you can easily restore 99% of your Zabbix environment with.

Easily forgotten, there are also some important configuration files and you might even have some scripts hanging around on your filesystem that you need to backup. The configuration files could be restored manually with not too much effort, but those scripts could especially take a long time to restore. As such it is always important to also backup these additional files. We will explore both the database and file backups in this topic within the book.

Various options exist for creating a database backup.

- mariadb-dump utility: This is a built-in tool shipped with MariaDB, allowing you to create reliable .sql file backups of the MariaDB database. It creates a file with SQL statements, allowing us to restore our database fully.
- mysqldump utility: This tool allows us to do the same as mariadb-dump, but is the official MySQL variant. Keep in mind that MariaDB and MySQL are going in different directions with their codebase, so it is recommended to use the right tool for your database.
- pg_dump utility: PostgreSQL also has a built-in tool to allow us to create .sql file backups of our PostgreSQL database. This creates a very similar .sql file with SQL statements, allowing us to restore our database fully.
- (Virtual) Machine disk snapshots: There are various utilities on the market to create (incremental) snapshots of a database server. Some examples are snapshots built into Azure/Amazon AWS, Proxmox PBS server, Veeam, Rubrik and more. 


## MariaDB
Creating database backups on MariaDB using the official `mariadb-dump` utility is fairly simple. When we have the mariadb-client installed we should already have the `mariadb-dump` utility installed as well. Double-check on your Zabbix database server CLI with the command below.

!!! info "Check if mariadb-dump is installed"

    Linux
    ```bash
    mariadb-dump --version
    ```

If your get no result, try to install the MariaDB client.

!!! info "Install MariaDB client"

    Red Hat
    ```bash
    dnf install mariadb
    ```

    Ubuntu
    ```bash
    sudo apt install mariadb-client
    ```

If the `mariadb-dump` tool is installed, creating a backup at this point is simple. We simple have to execute the command and point it to the right database. 

!!! info "Create a Zabbix MariaDB database backup"

    Linux
    ```bash
    mysqldump zabbix \
    --add-drop-table \
    --add-locks \
    --extended-insert \
    --single-transaction \
    --quick
    ```

This will login using MariaDB Unix socket authentication and create a database backup in your current working directory. It is also possible to pass your username and password directly.

!!! info "Create a Zabbix MariaDB database backup with username and password"

    Linux
    ```bash
    mysqldump zabbix \
    --add-drop-table \
    --add-locks \
    --extended-insert \
    --single-transaction \
    --quick \
    -u<USER> \
    -p<PASSWORD> 
    ```

Keep in mind that passing plain text passwords on the CLI might not be secure.

One more issue with creating the database backup like this, it takes up a lot of space on your disk. There is one more improvement to recommend here to make sure the backup is created as efficiently as possible. We can compress the backup before storing it to disk. To do this, we can install a compression tool like `lz4`.

Red Hat
```bash
dnf install lz4
```

Ubuntu
```bash
sudo apt install lz4
```

Using lz4, we can now compress our database backup by using a quick pipe in our `mariadb-dump` command.

!!! info "Create a Zabbix MariaDB database backup with compression"

    Linux
    ```bash
    mysqldump zabbix \
    --add-drop-table \
    --add-locks \
    --extended-insert \
    --single-transaction \
    --quick | lz4 > zabbix.sql.lz4
    ```

This backup will include all tables of our `zabbix` database and compress it with lz4 to store it as `zabbix.sql.lz4`. Keep in mind, it is always recommended to store the database backup somewhere away from our database server. There are several options to make this work in a safe manner.

- Attach a separate backup disk to store the backups on (still within the same server however)
- Store to separate disk and then transfer to remote storage (more secure)
- Directly pipe the lz4 compressed data to a tool like `rsync` to send it over SSH to a remote storage location (takes up the least amount of duplicated resources)


## PostgreSQL

## Other important (config) files

## Conclusion

## Questions

## Useful URLs
