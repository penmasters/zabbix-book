# Partitioning PostgreSQL with TimescaleDB

If you're familiar with partitioning a Zabbix database using MySQL or any of the
other forks like MariaDB, you're likely aware of the complexity involved, which
often requires Perl scripts and manual database operations. Fortunately, PostgreSQL
offers a much simpler and more streamlined approach. With the TimescaleDB extension,
partitioning is fully automated. This extension is not only powerful and efficient,
it is also the only method officially supported by Zabbix for database partitioning.
TimescaleDB takes care of the underlying logic, freeing you from custom scripts
and manual tweaks. For this reason, PostgreSQL could be the preferred and most convenient
option for managing large scale Zabbix environments.

## Installing TimescaleDB

First, make sure to download TimescaleDB from the correct source: [https://docs.timescale.com/self-hosted/latest/install/](https://docs.timescale.com/self-hosted/latest/install/).
Avoid using the version available in the standard PostgreSQL package repository,
as it is outdated and not suitable for Zabbix.

TimescaleDB comes in two editions: one released under the Apache license and the
other as the Community edition. For Zabbix, the Community edition is the recommended
choice. It includes all advanced features such as native compression, which are
essential for efficient long term data storage and performance in larger environments.

???+ info

    To use TimescaleDB with Zabbix, make sure PostgreSQL is installed from the official
    PostgreSQL community repositories, as described in our setup guide. **Do not**
    use the PostgreSQL version provided by Red Hat or its derivatives. The TimescaleDB
    extension is not compatible with that version, and attempting to use it will
    lead to failure in the configuration.

???+ note

    Always check in the Zabbix documentation before you start what version of
    PostgreSQL is supported and what version of the TimescaleDB is supported that
    way you don't install any unsupported version that could run you into issues.
    [https://docs.timescale.com/self-hosted/latest/install/installation-linux/#supported-platforms](https://docs.timescale.com/self-hosted/latest/install/installation-linux/#supported-platforms)

### Add the TimescaleDB repository

!!! info "adding the repository"

    Red Hat
    ```
    sudo tee /etc/yum.repos.d/timescale_timescaledb.repo <<EOL
    [timescale_timescaledb]
    name=timescale_timescaledb
    baseurl=https://packagecloud.io/timescale/timescaledb/el/$(rpm -E %{rhel})/\$basearch
    repo_gpgcheck=1
    gpgcheck=0
    enabled=1
    gpgkey=https://packagecloud.io/timescale/timescaledb/gpgkey
    sslverify=1
    sslcacert=/etc/pki/tls/certs/ca-bundle.crt
    metadata_expire=300
    EOL
    ```
    Ubuntu
    ```
    echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
    ```
    ```
    wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey |
     sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
    ```

!!! info "Update your local repository list"

    Red Hat
    ```
    sudo dnf update -y
    ```
    Ubuntu
    ```
    sudo apt update -y
    ```

### Install TimescaleDB

!!! info "Install TimescaleDB"

    Red Hat
    ```
    sudo yum install timescaledb-2-postgresql-17 postgresql17
    ```
    Ubuntu
    ```
    sudo apt install timescaledb-2-postgresql-17 postgresql-client-17
    ```

???+ note

    Of course, you need to match the TimescaleDB version to the version of PostgreSQL
    you installed. For example, if you are using PostgreSQL 14, you must install
    the corresponding TimescaleDB packages for version 14. The installation would
    look like this:
    ```
    dnf install timescaledb-2-postgresql-14 postgresql-client-14
    ```
    Using mismatched versions can lead to compatibility issues, so always make
    sure the TimescaleDB packages align with your PostgreSQL version.

???+ warning

    ```
    Be sure to install the version of TimescaleDB that is supported by Zabbix
    also when you upgrade your OS verify that the new database version and
    timescaledb are supported by Zabbix. It's probably best to exclude them from
    automatic updates.
    ```

!!! info "Check for specific versions"

    Red Hat
    ```
    dnf list timescaledb-2-postgresql-17 --showduplicates
    ```
    Ubuntu
    ```
    apt-cache policy timescaledb-2-postgresql-17
    ```

!!! info "installing a specific version and lock the version"

    Red Hat
    ```
    sudo dnf install timescaledb-2-postgresql-17-2.19.3
    sudo dnf versionlock add timescaledb-2-postgresql-17
    ```
    Ubuntu
    ```
    sudo apt install timescaledb-2-postgresql-17=2.19.3~ubuntu24.04 timescaledb-2-loader-postgresql-17=2.19.3~ubuntu24.04
    sudo apt-mark hold timescaledb-2-postgresql-17
    ```

### Configure TimescaleDB

The next step is to load the TimescaleDB extension into your PostgreSQL database
and tune the configuration. There are two ways to do this: the automated way and
the manual way.

TimescaleDB provides a tuning script that analyses your system and applies recommended
settings to optimize performance. On Red Hat based systems, you can run:

!!! info ""

    ```bash
    sudo timescaledb-tune --pg-config=/usr/pgsql/17/bin/pg_config
    ```

For Ubuntu and Debian based systems, simply run:

!!! info ""

    ```bash
    sudo timescaledb tune
    ```

This script will suggest configuration changes and can update your postgresql
configuration file automatically. If you prefer to tune the settings manually,
which is often recommended for experienced users, you will need to edit your postgresql
configuration file yourself.

At a minimum, make sure to add the following line at the end of the file:

!!! info ""

    ```bash
    shared_preload_libraries = 'timescaledb'
    ```

!!! info "Let's load the library"

    Red Hat
    ```
    echo "shared_preload_libraries = 'timescaledb'" | sudo tee -a /var/lib/pgsql/17/data/postgresql.conf
    ```
    ```
    systemctl restart postgresql-17
    ```
    Ubuntu
    ```
    echo "shared_preload_libraries = 'timescaledb'" | sudo tee -a /etc/postgresql/17/main/postgresql.conf
    ```
    ```
    sudo systemctl restart postgresql
    ```

### Configure Zabbix for timescaledb

Next, we connect to the Zabbix database as the user `zabbixsrv`, or whichever database
user you have configured earlier, and create the TimescaleDB extension. However,
before doing this, it is strongly recommended to stop the Zabbix server. This will
prevent the application from interfering with the database during the process, which
could otherwise cause locks or unexpected behavior.

!!! info "Stop Zabbix server"

    Red Hat and Ubuntu
    ```bash
    sudo systemctl stop zabbix-server
    ```

!!! info "Create timescaledb extension"

    Red Hat and Ubuntu
    ```bash
    psql -Uzabbix-srv zabbix -W
    ```
    ```
    psql (17.5)
    Type "help" for help.

    zabbix=> CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    ```

Make sure the extension is installed by running `\dx`.

!!! info ""

    ```
    zabbix=> \dx
                                                List of installed extensions
    Name     | Version |   Schema   |                                      Description
    -------------+---------+------------+---------------------------------------------------------------------------------------
     plpgsql     | 1.0     | pg_catalog | PL/pgSQL procedural language
     timescaledb | 2.19.3  | public     | Enables scalable inserts and complex queries for time-series data (Community Edition)
    (2 rows)

    zabbix=>
    ```

### Patch Zabbix database

While still connected to the Zabbix database, you can now apply the TimescaleDB
patch. This patch will migrate your existing history, trends, and audit log tables
to the TimescaleDB format. Depending on the amount of existing data, this process
may take some time.

Run the following command inside the database session:

!!! info ""

    ```sql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/timescaledb/schema.sql
    ```

The `schema.sql` script adjusts several important housekeeping parameters:

- Override item history period
- Override item trend period

To use partitioned housekeeping for history and trends, both of these options must
be enabled. However, it is also possible to enable them individually, depending
on your requirements.

In addition, the script sets two TimescaleDB specific parameters:

- Enable compression
- Compress records older than 7 days

These settings help reduce the size of historical data and improve long term performance.
Let's start our zabbix server again before we continue

!!! info "start Zabbix server"

    RedHat and Ubuntu
    ```
    sudo systemctl start zabbix-server
    ```

Let's have a look at them go in our menu to **Administration** -> **Housekeeping**

![TimescaleDB settings](ch13-timescaledb.png)

_13.1 housekeeper
settings_

???+ warning

    ```
    When running the `schema.sql` script on TimescaleDB version 2.9.0 or higher,
    you may see warning messages indicating that certain best practices are not
    being followed. These warnings can be safely ignored. They do not affect the
    outcome of the configuration process.

    As long as everything is set up correctly, the script will complete without
    issue. You should see the following confirmation at the end:
    ```
    ```sql
    psql:/usr/share/zabbix/sql scripts/postgresql/timescaledb/schema.sql:112:
    NOTICE:  TimescaleDB is configured successfully
    ```
    ```
    This confirms that the TimescaleDB extension and related Zabbix settings have
    been applied correctly.
    ```

## Conclusion

Using TimescaleDB with PostgreSQL is the only officially supported method for database
partitioning in Zabbix. It replaces complex manual setups with automated, efficient
handling of historical and trend data. Features like native compression and time
based partitioning significantly reduce storage usage and improve query performance.

By installing PostgreSQL from the correct repository, tuning it properly, and applying
the TimescaleDB schema patch, you ensure that Zabbix can scale reliably with minimal
maintenance overhead. This setup not only optimizes performance but also prepares
your environment for long term growth and data retention.

## Questions

- What are the key advantages of using TimescaleDB compared to partitioning with
  MySQL or MariaDB?
- What might go wrong if you install PostgreSQL from the default Red Hat repositories
  when planning to use TimescaleDB?
- How does enabling compression in TimescaleDB benefit your Zabbix installation?

## Useful URLs

- [https://docs.timescale.com/self-hosted/latest/configuration/](https://docs.timescale.com/self-hosted/latest/configuration/)
- [https://www.zabbix.com/documentation/7.2/en/manual/appendix/install/timescaledb?hl=TimescaleDB](https://www.zabbix.com/documentation/7.2/en/manual/appendix/install/timescaledb?hl=TimescaleDB)
