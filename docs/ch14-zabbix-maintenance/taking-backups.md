---
description : |
    Learn how to back up Zabbix using PostgreSQL, MySQL, or MariaDB. Covers logical
    and physical backups, retention, restore testing, and best practices.
tags: [advanced]
---

# Backup strategies
Zabbix relies heavily on the underlying database not only for the collected items
(metrics), but also for storing the Zabbix configuration we create in the Zabbix
frontend. This database should either be a MariaDB, PostgreSQL or MySQL database
in Zabbix 8.0 as those are the official production supported database types.

Since our history, trends and configuration data is all stored in this central
database, taking a meaningful backup of our Zabbix environment is fairly simple.
All we have to do is pick a backup method we like for our chosen database and then
use that to backup the database. Giving you a backup you can easily restore 99%
of your Zabbix environment with.

Easily forgotten, there are also some important configuration files and you might
even have some scripts hanging around on your filesystem that you need to backup.
The configuration files could be restored manually with not too much effort, but
those scripts could especially take a long time to restore. As such it is always
important to also backup these additional files. We will explore both the database
and file backups in this topic within the book.

Various options exist for creating a database backup.

- **`mariadb-dump utility`:** This is a built-in tool shipped with MariaDB, allowing you
  to create reliable .sql file backups of the MariaDB database. It creates a file
  with SQL statements, allowing us to restore our database fully.
- **`mysqldump utility`:** This tool allows us to do the same as mariadb-dump, but is
  the official MySQL variant. Keep in mind that MariaDB and MySQL are going in
  different directions with their codebase, so it is recommended to use the right
  tool for your database.
- **`pg_dump utility`:** PostgreSQL also has a built-in tool to allow us to create .sql
  file backups of our PostgreSQL database. This creates a very similar .sql file
  with SQL statements, allowing us to restore our database fully.
- **`(Virtual) Machine disk snapshots`:** There are various utilities on the market to
  create (incremental) snapshots of a database server. Some examples are snapshots
  built into Azure/Amazon AWS, Proxmox PBS server, Veeam, Rubrik and more.


## MariaDB
Creating database backups on MariaDB using the official `mariadb-dump` utility
is fairly simple. When we have the mariadb-client installed we should already
have the `mariadb-dump` utility installed as well. Double-check on your Zabbix
database server CLI with the command below.

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

### Creating a Logical Database Backup

If the `mariadb-dump` tool is installed, a basic logical backup of a Zabbix database
can be created with a single command. The options used below are specifically chosen
to balance consistency, performance, and compatibility during restore operations.

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

The `--single-transaction` option ensures a consistent snapshot for transactional
tables without locking them for extended periods, which is especially important
for active Zabbix systems. The `--quick` option reduces memory usage during the dump
process, making the backup more predictable under load.

This will login using MariaDB Unix socket authentication and create a database
backup in your current working directory. It is also possible to pass your `username`
and `password` directly, if password-based authentication is required,

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

One more issue with creating the database backup like this, it takes up a lot of
space on your disk. There is one more improvement to recommend here to make sure
the backup is created as efficiently as possible. We can compress the backup before
storing it to disk. To do this, we can install a compression tool like `lz4`.

!!! info "Install lz4 compression tool"

    Red Hat
    ```bash
    dnf install lz4
    ```

    Ubuntu
    ```bash
    sudo apt install lz4
    ```

Using lz4, we can now compress our database backup by using a quick pipe in our
`mariadb-dump` command.

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

This backup will include all tables of our `zabbix` database and compress it with
lz4 to store it as `zabbix.sql.lz4`. Keep in mind, it is always recommended to store
the database backup somewhere away from our database server. There are several
options to make this work in a safe manner.

- Attach a separate backup disk to store the backups on (still within the same
  server however)
- Store to separate disk and then transfer to remote storage (more secure)
- Directly pipe the lz4 compressed data to a tool like `rsync` to send it over
  SSH to a remote storage location (takes up the least amount of duplicated
  resources)

### Limitations of Logical Backups

While logical backups are simple and reliable, they do not scale indefinitely.
On large Zabbix installations with high data retention, dump times and restore
times can become significant. Logical backups also do not support point-in-time
recovery, meaning restores can only be performed to the moment the backup completed.

For this reason, logical dumps are best suited for:

- Small to medium-sized Zabbix installations
- Environments with modest recovery time objectives
- Systems without strict availability requirements

Larger environments may benefit from physical or snapshot-based backup solutions,
provided database consistency is guaranteed.

## PostgreSQL

When Zabbix uses PostgreSQL as its backend database, the database becomes the most
critical component of the entire monitoring system. All configuration, state, history,
and trends are stored there, and without a usable database backup, recovery of a
failed Zabbix server is effectively impossible.

Unlike file-based backups, PostgreSQL requires database-aware backup methods. Simply
copying the data directory while the database is running will almost certainly
result in a corrupted and unusable backup. For this reason, PostgreSQL provides
its own backup mechanisms, and choosing the correct one depends largely on the size
of the Zabbix environment and the acceptable recovery time.

### Logical Backups with pg_dump

The simplest way to back up a PostgreSQL database is by using pg_dump. This tool
performs a logical backup, meaning it exports the contents of the database as SQL
statements or a structured archive format.

For small Zabbix installations or non-production environments, pg_dump can be sufficient.
It is easy to use, requires no special PostgreSQL configuration, and produces backups
that are portable across systems and PostgreSQL minor versions.

A typical backup of a Zabbix database using pg_dump looks like this:

``` bash
sudo -u postgres pg_dump \
  --format=custom \
  --file=/backup/zabbix.dump \
  zabbix
```

Restoring such a backup is equally straightforward:

``` bash
sudo -u postgres pg_restore \
  --clean \
  --dbname=zabbix \
  zabbix.dump
```

While convenient, logical backups have important limitations in a Zabbix context.
On systems with large history or trend tables, backups can take a long time to
complete and may put noticeable load on the database server. Logical backups also
do not support point-in-time recovery, meaning it is impossible to restore the
database to a specific moment before a failure.

For these reasons, pg_dump should be viewed as an entry-level solution rather than
a long-term strategy for production Zabbix systems.

### Physical Backups and WAL Archiving

For medium and large Zabbix installations, physical backups are generally more
appropriate. A physical backup captures the PostgreSQL data files directly, together
with the write-ahead log (WAL) files required to replay changes. This approach
allows for significantly faster restores and enables point-in-time recovery (PITR).

Physical backups are usually created using pg_basebackup, while WAL files are
archived continuously in the background. From PostgreSQL’s perspective, this
is the same mechanism used for replication, which makes it both reliable and well
tested.

Once WAL archiving is enabled in PostgreSQL, a base backup of the Zabbix database
cluster can be taken without stopping the database. In the event of a failure,
PostgreSQL can be restored to a precise moment in time by replaying WAL files
up to the desired point.

This approach scales much better than logical backups and is well suited for
Zabbix installations that generate a large volume of monitoring data. However,
it requires more careful planning and disciplined retention management, as both
base backups and WAL files must be preserved consistently.

### PgBackRest and PgBarman: The Preferred Production Solution

For production Zabbix environments, especially those with large databases or high
availability requirements, dedicated PostgreSQL backup frameworks are strongly
recommended. Among these, PgBackRest and PgBarman are the two most widely adopted
and battle-tested solutions.

Both tools are designed specifically for physical PostgreSQL backups with continuous
WAL archiving, providing features that go far beyond what is possible with manual base
backups. They support point-in-time recovery, enforce retention policies, and ensure
backup integrity through automated verification steps.

PgBackRest is often favored in environments where performance and flexibility are
key concerns. It supports full, differential, and incremental backups, efficient
compression, and parallel processing, which makes it particularly suitable for Zabbix
databases with high write rates. PgBackRest integrates well with modern PostgreSQL
high-availability setups and is commonly used in combination with cluster managers
and load balancers.

PgBarman, on the other hand, follows a more centralized backup model. It is typically
deployed on a dedicated backup server that manages backups for one or more PostgreSQL
instances. This approach can be attractive in environments where backup operations
must be isolated from database servers or managed by a separate operations team.
PgBarman also provides reliable WAL management and point-in-time recovery, making
it a solid choice for enterprise Zabbix installations.

From a Zabbix perspective, both tools solve the same fundamental problem: they allow
the PostgreSQL database to be backed up consistently while Zabbix continues to
ingest monitoring data. The choice between PgBackRest and PgBarman is usually
driven by operational preferences, existing PostgreSQL standards, and infrastructure
design rather than functional limitations.

Regardless of which tool is chosen, the key requirement remains the same: backups
must be automated, retained according to policy, and restored successfully during
regular testing. Either PgBackRest or PgBarman meets these requirements and should
be considered the baseline for serious, production-grade Zabbix deployments.

### Backup Size and Zabbix Data Characteristics

Zabbix databases grow continuously by design. History and trend tables receive
constant inserts, and without proper housekeeping, backups can quickly become very
large. This is not a backup problem but a data lifecycle issue.

Before designing a PostgreSQL backup strategy for Zabbix, it is important to ensure
that database retention settings are aligned with business needs. Keeping excessive
history in the database not only increases backup size but also slows down backup
and restore operations, directly affecting recovery time objectives.

One way to better control database growth is the use of TimescaleDB, which is supported
by Zabbix for handling historical data. By storing history and trends in hypertables,
TimescaleDB allows for more efficient data management and automated data retention
policies. This can significantly reduce the volume of data that must be retained
and, by extension, the size of database backups.

Another approach, typically reserved for advanced or highly specialized environments,
is to exclude history and trend tables from certain backups. In such designs, configuration
data is backed up separately from monitoring data, with the understanding that
historical metrics can be discarded or rebuilt if necessary. This reduces backup
size and restore time but comes at the cost of losing historical visibility after
a recovery.

A well-tuned Zabbix database, whether using native PostgreSQL tables or TimescaleDB,
combined with physical backups and WAL archiving, results in manageable backup
sizes and predictable recovery times.

## Storage and Off-Host Backups

Regardless of the backup method used, storing backups exclusively on the database
server itself is insufficient. Hardware failures, filesystem corruption, or
security incidents can render both the database and its backups unusable.

Common approaches include:

- Writing backups to a dedicated backup disk
- Transferring backups to remote storage after creation
- Streaming compressed backups directly to a remote system over SSH

The exact method is less important than ensuring that backups are stored independently
of the database server and can be accessed during a full system failure.


## Other important (config) files
Often overlooked, since we focus so much on the database, are the Zabbix configuration files and possibly custom scripts. For a full restore of your Zabbix environment, these files can not be missed as they are vital to getting Zabbix back online in case of an issue. Of course, configuration files are easy to rebuild with a bit of time. However, it is best practice to also include these to make sure a speedy restoration can happen.

Let's create a quick working folder to place our backups in.

!!! info "Create a Zabbix backup folder"

    Linux
    ```bash
    mkdir /opt/zabbix-backup/
    ```

When Zabbix is installed from packages, it will always store the configuration files in a single location. That location `/etc/zabbix/` should contain most of our important files already. We can take a manual backup with the following command.

!!! info "Create a Zabbix configuration files backup"

    Linux
    ```bash
    cp -R /etc/zabbix/* /opt/zabbix-backup/
    ```

You can run this command on all of your Zabbix server, Frontend, Database and Proxy hosts. This should cover the most important configuration files already, but there is another folder that could contain very important files.

!!! info "Create other Zabbix files backup"

    Linux
    ```bash
    cp -R /usr/share/zabbix/ /opt/zabbix-backup/
    ```

The /usr/share/zabbix/ folder contains important PHP files and Zabbix binaries. A similar folder we should backup is the `/usr/lib/zabbix` folder, which contains our custom `alertscripts` and `externalscripts`.

!!! info "Create other Zabbix files backup"

    Linux
    ```bash
    cp -R /usr/lib/zabbix/ /opt/zabbix-backup/
    ```

Lastly, it is also recommended to create a backup of your webserver configuration. Depending on if you have `httpd`, `apache2` or `nginx` we will need to create the backup slightly differently. 

!!! info "Install MariaDB client"

    Red Hat HTTPD
    ```bash
    cp -R /etc/httpd/ /opt/zabbix-backup/
    cp -R /var/www/ /opt/zabbix-backup/
    cp /etc/httpd/conf.d/zabbix.conf  /opt/zabbix-backup/    ```

    Ubuntu Apache2
    ```bash
    cp -R /etc/apache2/ /opt/zabbix-backup/
    cp -R /var/www/ /opt/zabbix-backup/
    cp /etc/httpd/conf.d/zabbix.conf  /opt/zabbix-backup/
    ```

    NGINX
    ```bash
    cp -R /etc/nginx/ /opt/zabbix-backup/
    ```

That should cover all the important files here, but they are only written to a separate folder on the same Linux server now. To create a truly resilient backup, we should write these files somewhere else. There are various solutions here as well.

- Write the files to `/opt/zabbix-backup/` and copy the folder to a remote location daily
- Grab the files from the filesystem and store them in a Git repository (bonus: You get a nice diff)
- The simple method, ...

## Conclusion

Backing up the Zabbix database is a fundamental part of any maintenance strategy,
regardless of whether PostgreSQL or MySQL/MariaDB is used as the backend. While
the specific tools and mechanisms differ between database engines, the underlying
principles remain the same: backups must be consistent, automated, and aligned with
the size and criticality of the environment.

For PostgreSQL-based Zabbix installations, logical backups are suitable only for
small or non-critical systems. Larger environments benefit from physical backups
with WAL archiving, with dedicated tools such as PgBackRest or PgBarman providing
the reliability, performance, and recovery options required in production. Database
growth must be managed deliberately, whether through retention tuning, the use of
TimescaleDB, or, in advanced cases, separating configuration data from historical
data in backup design.

For MySQL and MariaDB backends, equivalent considerations apply. Logical dumps may
be sufficient for small systems, but physical or hot backup solutions are preferred
as data volume and availability requirements increase. Regardless of the database engine,
uncontrolled data growth directly affects backup size and recovery time and must be
addressed as part of the overall strategy.

Finally, a backup that has never been restored successfully cannot be considered
reliable. Regular restore testing is essential to verify backup integrity, confirm
recovery procedures, and establish realistic recovery time expectations. Only
backups that have been tested end-to-end should be trusted to protect a Zabbix
installation in production.

## Questions

- Why is backing up the Zabbix database sufficient to restore most of a Zabbix environment?
- What role do WAL files play in PostgreSQL point-in-time recovery?
- What risks exist if backups are never tested by performing a restore?
- Why is database growth considered a data lifecycle issue rather than a backup issue?

## Useful URLs

- https://www.postgresql.org/docs/current/backup.html
- https://pgbarman.org/
- https://pgbackrest.org/
- https://mariadb.com/docs/server/clients-and-utilities/backup-restore-and-import-clients/mariadb-dump
- https://www.percona.com/mysql/software/percona-xtrabackup

