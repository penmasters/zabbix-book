# Installing the Zabbix server

Now that we've added the Zabbix repository with the necessary software, we are
ready to install both the Zabbix server and the web server. Keep in mind that the
web server doesn't need to be installed on the same machine as the Zabbix server;
they can be hosted on separate systems if desired.

To install the Zabbix server components, run the following command:

!!! info "Install the zabbix server"

    Red Hat
    ``` bash
    # For MySQL/MariaDB backend:
    dnf install zabbix-server-mysql
    # For PostgreSQL backend:
    dnf install zabbix-server-pgsql
    ```

    SUSE
    ``` bash
    # For MySQL/MariaDB backend:
    zypper install zabbix-server-mysql
    # For PostgreSQL backend:
    zypper install zabbix-server-pgsql
    ``` 

    Ubuntu
    ``` bash
    # For MySQL/MariaDB backend:
    sudo apt install zabbix-server-mysql
    # For PostgreSQL backend:
    sudo apt install zabbix-server-pgsql
    ```

After successfully installing the Zabbix server package, we need to
configure the Zabbix server to connect to the database. This requires modifying the
Zabbix server configuration file.

The Zabbix server configuration file offers an option to include additional
configuration files for custom parameters. For a production environment, it's
often best to avoid altering the original configuration file directly. Instead,
you can create and include separate configuration files for any additional or
modified parameters. This approach ensures that your original configuration
file remains untouched, which is particularly useful when performing upgrades
or managing configurations with tools like Ansible, Puppet, or SaltStack.

On SUSE 16 and later, this feature is already enabled and configured by default.
(see also [SUSE documentation](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Hence, on SUSE systems, the Zabbix server configuration file is located at
`/usr/etc/zabbix/zabbix_server.conf`, and it is set up to include all `.conf` files from
the `/etc/zabbix_server/zabbix_server.d/` directory.

On other distributions, you may need to enable it manually:

To enable this feature, ensure the next line exists and is not commented 
(with a `#` in front of it) in `/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```

The path `/etc/zabbix/zabbix_server.d/` should already be created by the
installed package, but ensure it really exists.

Now we will create a custom configuration file `database.conf` in the `/etc/zabbix/zabbix_server.d/`
directory that will hold our database connection settings:

!!! info "Add Zabbix database connection settings"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```

    Add the following lines in the configuration file to match your database setup:

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```

Replace `<database-host>`, `<database-name>`, `<database-schema>`, `<database-user>`,
`<database-password>`, and `<database-port>` with the appropriate values for your
setup. This ensures that the Zabbix server can communicate with your database.

Ensure that there is no `#` (comment symbol) in front of the configuration parameters,
as Zabbix will treat lines beginning with `#` as comments, ignoring them during execution.
Additionally, double-check for duplicate configuration lines; if there are multiple
lines with the same parameter, Zabbix will use the value from the last occurrence.

For our setup, the configuration will look like this:

!!! example "Example database.conf"

    MariaDB/MySQL:
    ```ini
    # MariaDB database configuration
    DBHost=<ip or dns of your MariaDB server>
    DBName=zabbix
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=3306
    ```

    PostgreSQL:
    ```ini
    # PostgreSQL database configuration
    DBHost=<ip or dns of your PostgreSQL server>
    DBName=zabbix
    DBSchema=zabbix_server
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=5432
    ```

In this example:

- DBHost refers to the host where your database is running (use localhost if it's
  on the same machine).
- DBName is the name of the Zabbix database.
- DBSchema is the schema name used in PostgreSQL (only needed for PostgreSQL).
- DBUser is the database user.
- DBPassword is the password for the database user.
- DBPort is the port number on which your database server is listening (default for
  MySQL/MariaDB is 3306 and PostgreSQL is 5432).

Make sure the settings reflect your environment's database configuration.

---

## Populate the Zabbix database instance

During the installation of the database software earlier, we created the 
necessary users and database for Zabbix, however, Zabbix expects certain tables,
schemas, images, and other elements to be present in the database.
To set up the database correctly, we need to populate it with the required schema.

Execute next steps on the machine where the database is installed. 

???+ note

    If this is not the same machine as the Zabbix server, you will need to install 
    the Zabbix repository on the database server to gain access to the necessary SQL
    scripts.  Refer to [Install the Zabbix repository](preparation.md#install-the-zabbix-repository) for instructions on
    adding the Zabbix repository also in this system.

When the repository is added we can install the package:

!!! info "Install SQL scripts"

    Red Hat
    ``` bash
    dnf install zabbix-sql-scripts
    ```

    SUSE
    ``` bash
    zypper install zabbix-sql-scripts
    ```

    Ubuntu
    ``` bash
    sudo apt install zabbix-sql-scripts
    ```

???+ tip

    If you have already installed the Zabbix server package on this machine,
    the SQL scripts package may already be installed as a dependency.
    You can verify this by checking if the `/usr/share/zabbix/sql-scripts/`
    directory exists on your system.

---

### Populate MariaDB/MySQL Database

???+ warning

    When using a recent version of MySQL or MariaDB as the database backend for 
    Zabbix, you may encounter issues related to the creation of triggers during
    the schema import process. This is particularly relevant if binary logging
    is enabled on your database server. (Binary logging is often enabled by default)
    To address this, you need to set the `log_bin_trust_function_creators` option to `1`
    in the MySQL/MariaDB configuration file or temporarily at runtime.
    This allows non-root users to create stored functions and triggers without requiring
    `SUPER` privileges, which are restricted when binary logging is enabled.

    Normally we won't need the setting after the initial import of the Zabbix schema is done,
    so we will disable it again after the import is complete.

    !!! info "Activate temporarily extra privileges for non root users"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```

Now lets upload the data from zabbix (db structure, images, user, ... )
for this we make use of the user `zabbix-srv` and we upload it all in our DB `zabbix`.

!!! info "Populate the database"

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```

!!! warning

    Depending on the speed of your hardware or virtual machine, the process may
    take anywhere from a few seconds to several minutes without any visual feedback
    after entering the root password.

    Please be patient and avoid cancelling the operation; just wait for the linux 
    prompt to reappear.

???+ note

    Zabbix seems to like to change the locations of the script to populate the
    DB every version or even in between versions. If you encounter an error take a
    look at the Zabbix documentation, there is a good chance that some location was
    changed.



Once the import of the Zabbix schema is complete, you should no longer need the
`log_bin_trust_function_creators` global parameter. It is a good practice to remove
it for security reasons.

To revert the global parameter back to 0, use the following command in the 
MySQL/MariaDB shell:

!!! info "Disable function log_bin_trust again"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```

This command will disable the setting, ensuring that the servers security
posture remains robust.

---

### Populate the PostgreSQL Database

First you need to prepare the database schema: unzip the necessary schema files 
by running the following command:

!!! info "Unzip the DB patch"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

???+ note

    Zabbix seems to like to change the locations of the script to populate the
    DB every version or even in between versions. If you encounter an error take a
    look at the Zabbix documentation, there is a good chance that some location was
    changed.

This will extract the database schema required for the Zabbix server.

Next we will execute the SQL file to populate the database. Open a `psql` shell:

!!! info "Open psql shell"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```

???+ warning "Ensure correct search_path is set"

    Make sure you performed previous steps as outlined in [Creating the Zabbix database instance with PostgreSQL](postgresql.md#creating-the-zabbix-database-instance)
    carefully so that you have set the correct `search_path`.

    If you did not set the default `search_path` for the `zabbix-srv` user,
    ensure you set it manually in the current session before proceeding:
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```

Now run the following commands:

!!! info "Upload the DB schema to db zabbix"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```

???+ warning

    Depending on your hardware or VM performance, this process can take anywhere
    from a few seconds to several minutes. Please be patient and avoid cancelling
    the operation.

Monitor the progress as the script runs. You will see output similar to:

!!! example "Output example"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    ...
    ...
    ...
    INSERT 0 10444
    DELETE 90352
    COMMIT
    ```

Once the script completes and you return to the `zabbix=>` prompt, the database
should be successfully populated with all the required tables, schemas,
images, and other elements needed for Zabbix.

However, `zabbix-web` still cannot perform any operations on the tables or sequences.
To allow basic data interaction without giving too many privileges, grant the
following permissions:

- For tables: SELECT, INSERT, UPDATE, and DELETE.
- For sequences: SELECT and UPDATE.

!!! info "Grant rights on the schema to user zabbix-web"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```

Verify if the rights are correct on the schema :

!!! example "Example schema rights"

    ```psql
    zabbix=> \dn+
                                               List of schemas
         Name      |       Owner       |           Access privileges            |      Description
    ---------------+-------------------+----------------------------------------+------------------------
     public        | pg_database_owner | pg_database_owner=UC/pg_database_owner+| standard public schema
                   |                   | =U/pg_database_owner                   |
     zabbix_server | zabbix-srv        | "zabbix-srv"=UC/"zabbix-srv"          +|
                   |                   | "zabbix-web"=U/"zabbix-srv"            |
    ```

???+ note

    If you encounter the following error during the SQL import:
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: no
        schema has been selected to create in` It indicates that the `search_path` setting
    might not have been correctly applied. This setting is crucial because it specifies
    the schema where the tables and other objects should be created. By correctly
    setting the search path, you ensure that the SQL script will create tables
    and other objects in the intended schema.

To ensure that the Zabbix tables were created successfully and have the correct
permissions, you can verify the table list and their ownership using the `psql` command:

- List the Tables: Use the following command to list all tables in the `zabbix_server` schema:

!!! info "List tables"

    ```psql
    zabbix=# \dt
    ```

You should see a list of tables with their schema, name, type, and owner.
For example:

???+ example "List table with relations"

    ```psql
    zabbix=> \dt
                            List of relations
        Schema     |            Name            | Type  |   Owner
    ---------------+----------------------------+-------+------------
     zabbix_server | acknowledges               | table | zabbix-srv
     zabbix_server | actions                    | table | zabbix-srv
     zabbix_server | alerts                     | table | zabbix-srv
     zabbix_server | auditlog                   | table | zabbix-srv
     zabbix_server | autoreg_host               | table | zabbix-srv
     zabbix_server | changelog                  | table | zabbix-srv
     zabbix_server | conditions                 | table | zabbix-srv
    ...
    ...
    ...
     zabbix_server | valuemap                   | table | zabbix-srv
     zabbix_server | valuemap_mapping           | table | zabbix-srv
     zabbix_server | widget                     | table | zabbix-srv
     zabbix_server | widget_field               | table | zabbix-srv
    (203 rows)
    ```

- Verify Permissions: Confirm that the zabbix-srv user owns the tables and has
  the necessary permissions. You can check permissions for specific tables using
  the \dp command:

!!! info "Verify table permissions"

    ```psql
    zabbix=> \dp zabbix_server.*
    ```

???+ example "Example output"

    ```psql
    zabbix=> \dp zabbix_server.*
                                                         Access privileges
        Schema     |            Name            |   Type   |         Access privileges          | Column privileges | Policies
    ---------------+----------------------------+----------+------------------------------------+-------------------+----------
     zabbix_server | acknowledges               | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | actions                    | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | alerts                     | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | auditlog                   | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
    ```

This will display the access privileges for all tables in the `zabbix_server`
schema. Ensure that `zabbix-srv` has the required privileges.

If everything looks correct, your tables are properly created and the `zabbix-srv`
user has the appropriate ownership and permissions. If you need to adjust any
permissions, you can do so using the GRANT commands as needed.

---

## Configure firewall to allow Zabbix trapper connections

Back on your Zabbix server machine, we need to ensure that the firewall is configured
to allow incoming connections to the Zabbix server.

Your Zabbix server needs to accept incoming connections from Zabbix agents, senders,
and proxies. By default, Zabbix uses port `10051/tcp` for these connections.
To allow these connections, you need to open this port in your firewall.

!!! info "Open firewall for zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```

If the service is not recognized using `firewall-cmd --add-service`, you can
manually specify the port:

!!! info "Add port instead of the service name"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```

---

## Starting the Zabbix server

With the Zabbix server configuration updated to connect to your database, you
can now start and enable the Zabbix server service. Run the following command
to enable the Zabbix server and ensure it starts automatically on boot:

???+ note

    Before restarting the Zabbix server after modifying its configuration, it is
    considered best practice to validate the configuration to prevent potential
    issues. Running a configuration check ensures that any errors are detected
    beforehand, avoiding downtime caused by an invalid configuration. This can
    be accomplished using the following command: `zabbix-server -T`

!!! info "Enable and start zabbix-server service"

    Red Hat, SUSE and Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```

This command will start the Zabbix server service immediately and configure it
to launch on system startup. To verify that the Zabbix server is running correctly,
check the log file for any messages. You can view the latest entries in the
`Zabbix server` log file using:

!!! info "Check the log file"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```

Look for messages indicating that the server has started successfully. If there
are any issues, the log file will provide details to help with troubleshooting.

!!! example "Example output"

    ```
    12074:20250225:145333.529 Starting Zabbix Server. Zabbix 7.2.4 (revision c34078a4563).
    12074:20250225:145333.530 ****** Enabled features ******
    12074:20250225:145333.530 SNMP monitoring:           YES
    12074:20250225:145333.530 IPMI monitoring:           YES
    12074:20250225:145333.530 Web monitoring:            YES
    12074:20250225:145333.530 VMware monitoring:         YES
    12074:20250225:145333.530 SMTP authentication:       YES
    12074:20250225:145333.530 ODBC:                      YES
    12074:20250225:145333.530 SSH support:               YES
    12074:20250225:145333.530 IPv6 support:              YES
    12074:20250225:145333.530 TLS support:               YES
    12074:20250225:145333.530 ******************************
    12074:20250225:145333.530 using configuration file: /etc/zabbix/zabbix_server.conf
    12074:20250225:145333.545 current database version (mandatory/optional): 07020000/07020000
    12074:20250225:145333.545 required mandatory version: 07020000
    12075:20250225:145333.557 starting HA manager
    12075:20250225:145333.566 HA manager started in active mode
    12074:20250225:145333.567 server #0 started [main process]
    12076:20250225:145333.567 server #1 started [service manager #1]
    12077:20250225:145333.567 server #2 started [configuration syncer #1]
    12078:20250225:145333.718 server #3 started [alert manager #1]
    12079:20250225:145333.719 server #4 started [alerter #1]
    12080:20250225:145333.719 server #5 started [alerter #2]
    12081:20250225:145333.719 server #6 started [alerter #3]
    12082:20250225:145333.719 server #7 started [preprocessing manager #1]
    12083:20250225:145333.719 server #8 started [lld manager #1]
    ```

If there was an error and the server was not able to connect to the database you
would see something like this in the server log file :

!!! example "Example log with errors"

    ```
    12068:20250225:145309.018 Starting Zabbix Server. Zabbix 7.2.4 (revision c34078a4563).
    12068:20250225:145309.018 ****** Enabled features ******
    12068:20250225:145309.018 SNMP monitoring:           YES
    12068:20250225:145309.018 IPMI monitoring:           YES
    12068:20250225:145309.018 Web monitoring:            YES
    12068:20250225:145309.018 VMware monitoring:         YES
    12068:20250225:145309.018 SMTP authentication:       YES
    12068:20250225:145309.018 ODBC:                      YES
    12068:20250225:145309.018 SSH support:               YES
    12068:20250225:145309.018 IPv6 support:              YES
    12068:20250225:145309.018 TLS support:               YES
    12068:20250225:145309.018 ******************************
    12068:20250225:145309.018 using configuration file: /etc/zabbix/zabbix_server.conf
    12068:20250225:145309.027 [Z3005] query failed: [1146] Table 'zabbix.users' doesn't exist [select userid from users limit 1]
    12068:20250225:145309.027 cannot use database "zabbix": database is not a Zabbix database
    ```
If that is the case, double-check your database connection settings in the
`/etc/zabbix/zabbix_server.d/database.conf` file and ensure that the database
is properly populated as described in the previous steps. Also check firewall rules
and when using PostgreSQL make sure that `pg_hba.conf` is correctly configured 
to allow connections from the Zabbix server.

Let's check the Zabbix server service to see if it's enabled so that it survives
a reboot

!!! info "check status of zabbix-server service"

    ```bash
    sudo systemctl status zabbix-server
    ```

???+ example "Example output"
    ```shell-session
    localhost:~> sudo systemctl status zabbix-server

    ● zabbix-server.service - Zabbix Server
         Loaded: loaded (/usr/lib/systemd/system/zabbix-server.service; enabled; preset: disabled)
         Active: active (running) since Tue 2025-02-25 14:53:33 CET; 26min ago
       Main PID: 12074 (zabbix_server)
          Tasks: 77 (limit: 24744)
         Memory: 71.5M
            CPU: 18.535s
         CGroup: /system.slice/zabbix-server.service
                 ├─12074 /usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf
                 ├─12075 "/usr/sbin/zabbix_server: ha manager"
                 ├─12076 "/usr/sbin/zabbix_server: service manager #1 [processed 0 events, updated 0 event tags, deleted 0 problems, synced 0 service updates, idle 5.027667 sec during 5.042628 sec]"
                 ├─12077 "/usr/sbin/zabbix_server: configuration syncer [synced configuration in 0.051345 sec, idle 10 sec]"
                 ├─12078 "/usr/sbin/zabbix_server: alert manager #1 [sent 0, failed 0 alerts, idle 5.030391 sec during 5.031944 sec]"
                 ├─12079 "/usr/sbin/zabbix_server: alerter #1 started"
                 ├─12080 "/usr/sbin/zabbix_server: alerter #2 started"
                 ├─12081 "/usr/sbin/zabbix_server: alerter #3 started"
                 ├─12082 "/usr/sbin/zabbix_server: preprocessing manager #1 [queued 0, processed 0 values, idle 5.023818 sec during 5.024830 sec]"
                 ├─12083 "/usr/sbin/zabbix_server: lld manager #1 [processed 0 LLD rules, idle 5.017278sec during 5.017574 sec]"
                 ├─12084 "/usr/sbin/zabbix_server: lld worker #1 [processed 1 LLD rules, idle 21.031209 sec during 21.063879 sec]"
                 ├─12085 "/usr/sbin/zabbix_server: lld worker #2 [processed 1 LLD rules, idle 43.195541 sec during 43.227934 sec]"
                 ├─12086 "/usr/sbin/zabbix_server: housekeeper [startup idle for 30 minutes]"
                 ├─12087 "/usr/sbin/zabbix_server: timer #1 [updated 0 hosts, suppressed 0 events in 0.017595 sec, idle 59 sec]"
                 ├─12088 "/usr/sbin/zabbix_server: http poller #1 [got 0 values in 0.000071 sec, idle 5 sec]"
                 ├─12089 "/usr/sbin/zabbix_server: browser poller #1 [got 0 values in 0.000066 sec, idle 5 sec]"
                 ├─12090 "/usr/sbin/zabbix_server: discovery manager #1 [processing 0 rules, 0 unsaved checks]"
                 ├─12091 "/usr/sbin/zabbix_server: history syncer #1 [processed 4 values, 3 triggers in 0.027382 sec, idle 1 sec]"
                 ├─12092 "/usr/sbin/zabbix_server: history syncer #2 [processed 0 values, 0 triggers in 0.000077 sec, idle 1 sec]"
                 ├─12093 "/usr/sbin/zabbix_server: history syncer #3 [processed 0 values, 0 triggers in 0.000076 sec, idle 1 sec]"
                 ├─12094 "/usr/sbin/zabbix_server: history syncer #4 [processed 0 values, 0 triggers in 0.000020 sec, idle 1 sec]"
                 ├─12095 "/usr/sbin/zabbix_server: escalator #1 [processed 0 escalations in 0.011627 sec, idle 3 sec]"
                 ├─12096 "/usr/sbin/zabbix_server: proxy poller #1 [exchanged data with 0 proxies in 0.000081 sec, idle 5 sec]"
                 ├─12097 "/usr/sbin/zabbix_server: self-monitoring [processed data in 0.000068 sec, idle 1 sec]"
    ```

This concludes our chapter on installing and configuring the Zabbix server.
