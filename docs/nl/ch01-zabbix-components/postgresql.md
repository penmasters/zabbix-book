---
description: |
    This section from The Zabbix Book titled "Installing a PostgreSQL database"
    guides you through installing PostgreSQL as an alternative database backend
    for Zabbix. It covers installation methods using OS vendor-provided packages
    or official PostgreSQL repositories, with specific commands for Red Hat, SUSE,
    and Ubuntu systems. The section also includes steps to start and secure the
    PostgreSQL server, create the Zabbix database and users, and configure
    firewall rules if necessary.
tags: [beginner]
---

# Een PostgreSQL-database installeren

Als alternatief voor MariaDB/MySQL kun je ervoor kiezen om PostgreSQL te
gebruiken als database backend voor Zabbix. Net als MariaDB kan PostgreSQL
geïnstalleerd worden met de pakketten van de OS-leverancier of met de officiële
PostgreSQL-repositories.

Als je MariaDB al geïnstalleerd hebt in de vorige sectie, kan je deze sectie
overslaan.

Op het moment van schrijven worden PostgreSQL 13-17 ondersteund door Zabbix.
Controleer de Zabbix documentatie voor een actuele lijst van ondersteunde
versies voor jouw Zabbix versie. Meestal is het een goed idee om de laatste
versie te gebruiken die wordt ondersteund door Zabbix.

Tip: "TimescaleDB uitbreiding".

    Zabbix also supports the extension TimescaleDB but due to its advanced nature, 
    we won't cover it in this chapter. Refer to [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    for detailed instructions on that topic. 

    Do note that if you want to use TimescaleDB RPM packages provided
    by Timescale, you will need to install PostgreSQL from the official
    PostgreSQL repositories instead of the OS vendor-provided packages.
    If you choose to install PostgreSQL from the OS vendor-provided packages,
    you will need to compile and install the TimescaleDB extension from source.

---

## PostgreSQL-server en -client installeren vanuit door de leverancier van het besturingssysteem geleverde pakketten

Voer de volgende commando's uit om de standaard PostgreSQL server van de
distributie te installeren:

Info "Installeer de Postgres-server".

    Red Hat
    ``` bash
    dnf install postgresql-server postgresql-client	postgresql-contrib
    ```

    SUSE
    ``` bash
    zypper install postgresql-server postgresql postgresql-contrib
    ```

    Ubuntu
    ``` bash
    sudo apt install postgresql postgresql-client postgresql-contrib
    ```

Dit commando downloadt en installeert zowel de server- als de clientpakketten,
zodat je je PostgreSQL database kunt instellen, configureren en ermee kunt
werken.

Waarschuwing "Database-initialisatie vereist op Red Hat".

    Due to policies for Red Hat family distributions, the PostgreSQL service
    does not initialize an empty database required for PostgreSQL to function.
    So for Red Hat we need to initialize an empty database before continuing:

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```

    On SUSE and Ubuntu the OS provided SystemD service will automatically initialize
    an empty database on first startup.

Als de installatie voltooid is, kunt u verder gaan naar het gedeelte [_De
PostgreSQL Database starten_](#starting-the-postgresql-database).

---

## PostgreSQL installeren vanuit officiële PostgreSQL opslagplaatsen

Als je PostgreSQL liever installeert vanuit de officiële PostgreSQL repositories
in plaats van de door de OS-leverancier geleverde pakketten, is de eerste stap
het toevoegen van de PostgreSQL repository aan je systeem.

---

### De PostgreSQL opslagplaats toevoegen

Set up the PostgreSQL repository with the following commands:

Check
[https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/)
for more information.

!!! info "Add PostgreSQL repo"

    Red Hat
    ```bash
    # Install the repository RPM:
    dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

    # Disable the built-in PostgreSQL module:
    dnf -qy module disable postgresql
    ```

    SUSE
    ```bash
    # Import the repository signing key:
    rpm --import https://zypp.postgresql.org/keys/PGDG-RPM-GPG-KEY-SLES16

    # Install the repository RPM:
    zypper install https://download.postgresql.org/pub/repos/zypp/reporpms/SLES-16-x86_64/pgdg-suse-repo-latest.noarch.rpm

    # Update the package lists:
    zypper refresh
    ```

    !!! warning "openSUSE Leap"

        Since the official PostgreSQL packages are specifically built for use on 
        SUSE Linux Enterprise Server (SLES), you will get an error trying to install the
        repository on openSUSE Leap. We can however safely ignore this problem by
        choosing to "break the package by ignoring some of its dependencies" as
        long as you match the SLES version with your openSUSE version:

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```

    ???+ note "Suse Linux Enterprise Server"

        On SUSE Linux Enterprise Server (SLES), ensure you are subscribed to the
        "SUSE Package Hub extension" repository to access necessary dependency
        packages required for the Official PostgreSQL installation. On SLES 15
        you will also need the "Desktop Applications Module":

        ```bash
        # On SLES 16
        suseconnect -p PackageHub/16.0/x86_64

        # On SLES 15
        SUSEConnect -p sle-module-desktop-applications/15.7/x86_64
        SUSEConnect -p PackageHub/15.7/x86_64
        ```

    Ubuntu
    ```bash
    # Import the repository signing key:
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

    # Create the repository configuration file:
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    # Update the package lists:
    sudo apt update
    ```

---

### Installing the PostgreSQL Server and Client

With the PostgreSQL repositories configured, you are now ready to install the
PostgreSQL server and client packages. This will provide the necessary
components to run and manage your database.

!!! info "Install PostgreSQL from official repositories"

    Red Hat
    ```bash
    # Install Postgres server:
    dnf install postgresql17 postgresql17-server postgresql17-contrib
    ```

    SUSE
    ```bash
    zypper install postgresql17 postgresql17-server postgresql17-contrib
    ```

    Ubuntu
    ```bash
    sudo apt install postgresql-17 postgresql-client-17
    ```

Dit commando downloadt en installeert zowel de server- als de clientpakketten,
zodat je je PostgreSQL database kunt instellen, configureren en ermee kunt
werken.

Next, before we can start the PostgreSQL server we need to initialize a new
empty database:

!!! info "Initialize empty PostgreSQL database"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```

Once the installation is complete, you can proceed to the [Starting the
PostgreSQL Database](#starting-the-postgresql-database) section.

---

## Starting the PostgreSQL Database

Now that PostgreSQL is installed, we need to enable the service to start
automatically upon boot as well as start it immediately. Use the following
command to accomplish this:

!!! info "Enable and start PostgreSQL service"

    for OS-provided packages
    ```bash
    sudo systemctl enable postgresql --now
    ```

    for official PostgreSQL packages:
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```

This command will both enable and start the PostgreSQL service. With the service
now up and running, you can verify that the installation was successful by
checking the version of PostgreSQL using the following command:

!!! info "Check PostgreSQL version"

    ```bash
    psql -V
    ```

The expected output should resemble this:

???+ example "PostgreSQL version example"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```

To ensure that the PostgreSQL service is running properly, you can check its
status with the following command:

!!! info "Get PostgreSQL status"

    for OS-provided packages
    ```bash
    sudo systemctl status postgresql
    ```

    for official PostgreSQL packages:
    ```bash
    sudo systemctl status postgresql-17
    ```

You should see an output similar to this, indicating that the PostgreSQL service
is active and running:

???+ example "PostgreSQL service status example"

    ```shell-session
    localhost:~ $ sudo systemctl status postgresql-17
    ● postgresql-17.service - PostgreSQL 17 database server
        Loaded: loaded (/usr/lib/systemd/system/postgresql-17.service; enabled; preset: disabled)
        Active: active (running) since Mon 2025-12-29 17:24:07 CET; 6s ago
    Invocation: 43ba47dfee5b415db223e3452c3cfacc
        Docs: https://www.postgresql.org/docs/17/static/
        Process: 11131 ExecStartPre=/usr/pgsql-17/bin/postgresql-17-check-db-dir ${PGDATA} (code=exited, status=0/SUCCESS)
    Main PID: 11137 (postgres)
        Tasks: 7 (limit: 4672)
            CPU: 471ms
        CGroup: /system.slice/postgresql-17.service
                ├─11137 /usr/pgsql-17/bin/postgres -D /var/lib/pgsql/17/data/
                ├─11138 "postgres: logger "
                ├─11139 "postgres: checkpointer "
                ├─11140 "postgres: background writer "
                ├─11142 "postgres: walwriter "
                ├─11143 "postgres: autovacuum launcher "
                └─11144 "postgres: logical replication launcher "

    Dec 29 17:24:07 localhost.localdomain systemd[1]: Starting PostgreSQL 17 database server...
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] LOG:  redirecting log output to logging co>
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] HINT:  Future log output will appear in di>
    Dec 29 17:24:07 localhost.localdomain systemd[1]: Started PostgreSQL 17 database server.
    ```

This confirms that your PostgreSQL server is up and running, ready for further
configuration.

---

## Securing the PostgreSQL database

PostgreSQL handles access permissions differently from MySQL and MariaDB.
PostgreSQL relies on a file called `pg_hba.conf` to manage who can access the
database, from where, and what encryption method is allowed for authentication.

???+ note "About pg_hba.conf"

    Client authentication in PostgreSQL is configured through the `pg_hba.conf`
    file, where "HBA" stands for Host-Based Authentication. This file specifies
    which users can access the database, from which hosts, and how they are authenticated.
    For further details, you can refer to the official PostgreSQL documentation."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Add the following lines, the order here is important.

!!! info "Edit the pg_hba file"

    Red Hat / SUSE
    ``` bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/pg_hba.conf

    # for official packages
    vi /var/lib/pgsql/17/data/pg_hba.conf
    ```

    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/pg_hba.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/pg_hba.conf
    ```

!!! warning "Location of pg_hba file"

    If you don't find the `pg_hba.conf` and `postgres.conf` files in the above 
    mentioned location you can ask PostgreSQL itself for the location using
    this command (provided that PostgreSQL is currently running):

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```

The resulting pg_hba file should look like :

!!! example "Pg_hba example"

    ```
    # "local" is for Unix domain socket connections only
    local    zabbix     zabbix-srv                                 scram-sha-256
    local    all        all                                        peer
    # IPv4 local connections
    host     zabbix         zabbix-srv      <ip from zabbix server/24>     scram-sha-256
    host     zabbix         zabbix-web      <ip from zabbix server/24>     scram-sha-256
    host     all            all             127.0.0.1/32                   scram-sha-256
    # IPv6 local connections:
    host    zabbix          zabbix-srv      ::1/128                 scram-sha-256
    host    zabbix          zabbix-web      ::1/128                 scram-sha-256
    host    all             all             ::1/128                 ident
    ```

!!! warning "Ensure to keep the order of the entries"

    The order of the entries in the `pg_hba.conf` file is crucial, as PostgreSQL
    processes these rules sequentially. Ensure that the specific rules for the
    `zabbix-srv` and `zabbix-web` users are placed before any broader rules like
    the default `all` user rules that could potentially override them.

After we changed the `pg_hba.conf` file don't forget to restart postgres
otherwise the settings will not be applied. But before we restart, let us also
edit the file `postgresql.conf` and allow our database to listen on our network
interface for incoming connections from the Zabbix server. PostgreSQL will by
default only allow connections from a unix socket.

!!! info "Edit postgresql.conf file"

    Red Hat / SUSE
    ```bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/postgresql.conf

    # for official packages
    vi /var/lib/pgsql/17/data/postgresql.conf
    ```

    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/postgresql.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/postgresql.conf
    ```

Locate the following line:

!!! info ""

    ```ini
    #listen_addresses = 'localhost'
    ```

and replace it with:

!!! info ""

    ```ini
    listen_addresses = '*'
    ```

???+ note

    This will enable PostgreSQL to accept connections from any network interface,
    not just the local machine. In production it's probably a good idea to limit
    who can connect to the DB.

After making this change, restart the PostgreSQL service to apply the new
settings:

!!! info "Restart the DB server"

    for OS-provided packages
    ``` bash
    sudo systemctl restart postgresql
    ```

    for official packages
    ```bash
    sudo systemctl restart postgresql-17
    ```

???+ tip

    If the service fails to restart, review the `pg_hba.conf` file for any syntax errors,
    as incorrect entries here may prevent PostgreSQL from starting.

---

## Creating the Zabbix database instance

With the necessary packages installed, you are now ready to create the Zabbix
database and users for both the server and frontend.

The PostgreSQL packages automatically create a default `postgres` linux-user
during installation which has administrative privileges on the PostgreSQL
instance. To administer the database, you will need to execute commands as the
`postgres` user.

First, create the Zabbix server database user (also referred to as a "role" in
PostgreSQL):

!!! info "Create server users"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```

Next, create the Zabbix frontend user, which will be used to connect to the
database:

!!! info "Create front-end user"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```

Now with the users created, the next step is to create the Zabbix database.
Execute the following command to create the database `zabbix` with the owner set
to `zabbix-srv` and the character encoding set to `Unicode` as required by
Zabbix:

!!! info "Create DB"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```

???+ note "What is this 'template0'?"

    In PostgreSQL, `template0` is a default database template that serves as a pristine
    copy of the database system. When creating a new database using `template0`,
    it ensures that the new database starts with a clean slate, without any
    pre-existing objects or configurations that might be present in other templates.
    This is particularly useful when you want to create a database with specific
    settings or extensions without inheriting any unwanted elements from other templates.

Once the database is created, you should verify the connection and ensure that
the correct user session is active. To do this, log into the zabbix database
using the `zabbix-srv` user:

!!! info "Login as user zabbix-srv"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```

After logging in, run the following SQL query to confirm that both the
`session_user` and `current_user` are set to `zabbix-srv`:

!!! info ""

    ```psql
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```

If the output matches, you are successfully connected to the database with the
correct user.

PostgreSQL differs significantly from MySQL or MariaDB in several aspects, and
one of the key features that sets it apart is its use of schemas. Unlike MySQL,
where databases are more standalone, PostgreSQL's schema system provides a
structured, multi-user environment within a single database.

Schemas act as logical containers within a database, enabling multiple users or
applications to access and manage data independently without conflicts. This
feature is especially valuable in environments where several users or
applications need to interact with the same database server concurrently. Each
user or application can have its own schema, preventing accidental interference
with each other's data.

???+ note

    PostgreSQL comes with a default schema, typically called `public`, but in
    general, it's a best practice to create custom schemas to better organize and separate
    database objects, especially in complex or multi-user environments.

    For more in-depth information, I recommend checking out the detailed guide at
    this URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    which explains the benefits and use cases for schemas in PostgreSQL.

To finalize the initial database setup for Zabbix, we need to configure schema
permissions for both the `zabbix-srv` and `zabbix-web` users.

First, we create a custom schema named `zabbix_server` and assign ownership to
the `zabbix-srv` user:

!!! info "Create the db schema"

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```

Next, we set the `search path` to `zabbix_server` schema so that it's the
default for the current session:

!!! info "Set search path"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```

???+ tip

    If you prefer not to set the search path manually each time you log in as the
    `zabbix-srv` user, you can configure PostgreSQL to automatically use the desired
    search path. Run the following SQL command to set the default search path for
    the `zabbix-srv` role:

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```

    This command ensures that every time the `zabbix-srv` user connects to the
    database, the `search_path` is automatically set to `zabbix_server`.


To confirm the schema setup, you can list the existing schemas:

!!! example "Verify schema access"

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```

At this point, the `zabbix-srv` user has full access to the schema, but the
`zabbix-web` user still needs appropriate permissions to connect and interact
with the database. First, we grant `USAGE` privileges on the schema to allow
`zabbix-web` to connect:

!!! info "Grant access to schema for user zabbix-web"

    ```psql
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```

Now, the `zabbix-web` user has appropriate access to interact with the schema
while maintaining security by limiting permissions to essential operations.

If you are ready you can exit the database and return to your linux shell.

!!! info "Exit the database shell"

    ```psql
    zabbix=> \q
    ```

At this point, your Zabbix database is ready, but before it can actually be used
by Zabbix, we still need to populate the database with the necessary tables and
initial data, but that will be covered in the next section when we install the
Zabbix server.

If you intent to install Zabbix server on a different machine than the one
hosting the database you will need to open the host firewall to allow incoming
connections to the database server. By default, PostgreSQL listens on port 5432.

!!! info "Add firewall rules"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=postgresql --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 5432/tcp
    ```
---

## Populate the Zabbix database

During the installation of the database software earlier, we created the
necessary users, database and schema for Zabbix, however, Zabbix expects certain
tables, schemas, images, and other elements to be present in the database. To
set up the database correctly, we need to populate it with the required schema.

First we need to install the Zabbix SQL scripts that contain the required import
scripts for the database.

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

Next you need to prepare the database schema: unzip the necessary schema files
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

Now we will execute the SQL file to populate the database. Open a `psql` shell:

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

Upload the DB schema to the database using the following commands:

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
should be successfully populated with all the required tables, schemas, images,
and other elements needed for Zabbix.

However, `zabbix-web` still cannot perform any operations on the tables or
sequences. To allow basic data interaction without giving too many privileges,
grant the following permissions:

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
permissions, you can verify the table list and their ownership using the `psql`
command:

- List the Tables: Use the following command to list all tables in the
  `zabbix_server` schema:

!!! info "List tables"

    ```psql
    zabbix=# \dt
    ```

You should see a list of tables with their schema, name, type, and owner. For
example:

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

If everything looks correct, your tables are properly created and the
`zabbix-srv` user has the appropriate ownership and permissions. If you need to
adjust any permissions, you can do so using the GRANT commands as needed.

This concludes our installation of the PostgreSQL database.

---

## Conclusie

With the installation and configuration of PostgreSQL as the database backend
for Zabbix complete, you now have a powerful and efficient database system ready
for your monitoring needs. We've covered the installation of PostgreSQL from
both vendor-provided packages and official repositories, securing the database,
creating the necessary Zabbix database and users, and populating the database
with the required schema and initial data.

Your Zabbix environment is now ready for the next stages of setup and
configuration.

---

## Vragen

1. What version of PostgreSQL should I install for compatibility and stability?
2. What port does my DB use ?
3. Which database users did I create and why?

---

## Nuttige URL's

- [https://yum.postgresql.org](ttps://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)
