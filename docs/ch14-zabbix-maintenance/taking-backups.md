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
Creating database backups


## PostgreSQL

## Other important (config) files

## Conclusion

## Questions

## Useful URLs
