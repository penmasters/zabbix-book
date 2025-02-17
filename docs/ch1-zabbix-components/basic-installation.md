# Basic installation

In this chapter, we will walk through the process of installing the Zabbix server.
There are many different ways to setup a Zabbix server. We will cover the most
common setups with MariaDB and PostgreSQL on Ubuntu and on Rocky Linux.

Before beginning the installation, it is important to understand the architecture
of Zabbix.
The Zabbix server is structured in a modular fashion, composed of three main components,
which we will discuss in detail.

* The Zabbix server
* The Zabbix web server
* The Zabbix database

![overview](./basic-installation/zabbix-server.png){ align=left }

All of these components can either be installed on a single server or distributed
across three separate servers. The core of the system is the Zabbix server, often
referred to as the "brain." This component is responsible for processing trigger
calculations and sending alerts. The database serves as the storage for the Zabbix
server’s configuration and all the data it collects. The web server provides the
user interface (front-end) for interacting with the system. It is important to note
that the Zabbix API is part of the front-end component, not the Zabbix server itself.

These components must function together seamlessly, as illustrated in the diagram
above. The Zabbix server must read configurations and store monitoring data in the
database, while the front-end needs access to read and write configuration data.
Furthermore, the front-end must be able to check the status of the Zabbix server
and retrieve additional necessary information to ensure smooth operation.

For our setup, we will be using two virtual machines (VMs): one VM will host both
the Zabbix server and the Zabbix web front-end, while the second VM will host the
Zabbix database.

???+ note

    It's perfect possible to install all components on 1 single VM or every component
    on a separate VM.
    Reason we split the DB as an example is because the database will probably be the
    first component giving you performance headaches. It's also the component that
    needs some extra attention when we split it so for this reason we have chosen
    in this example to split the database from the rest of the setup.

We will cover the following topics:

Install our Database based on MariaDB.
Install our Database based on PostgreSQL.
Installing the Zabbix.
Install the frontend.

## Installing the MariaDB database

To begin the installation process for the MariaDB server, the first step involves
manually creating a repository configuration file. This file, mariadb.repo on Rocky,
must be placed in the /etc/yum.repos.d/ directory. The repository file will allow
your package manager to locate and install the necessary MariaDB components.

To create the MariaDB repository file, execute the following command in your terminal:

```bash
RedHat
# vi /etc/yum.repos.d/mariadb.repo

Ubuntu
```

This will open a text editor where you can input the repository configuration details.
Once the repository is configured, you can proceed with the installation of MariaDB
using your package manager.

Here’s the configuration you need to add into the file:

```bash
RedHat

# MariaDB 10.11 RedHatEnterpriseLinux repository list - created 2023-11-01 14:20 UTC
# https://mariadb.org/download/
[mariadb]
name = MariaDB
# rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
# baseurl = https://rpm.mariadb.org/10.11/rhel/$releasever/$basearch
baseurl = https://mirror.23m.com/mariadb/yum/10.11/rhel/$releasever/$basearch
# gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
gpgkey = https://mirror.23m.com/mariadb/yum/RPM-GPG-KEY-MariaDB
gpgcheck = 1

Ubuntu
```

After saving the file, ensure that everything is properly set up and that your
MariaDB version is compatible with your Zabbix version to avoid potential
integration issues.

Before proceeding with the MariaDB installation, it’s a best practice to ensure
your operating system is up-to-date with the latest patches and security fixes.
This will help maintain system stability and compatibility with the software you're
about to install.

To update your OS, run the following command:

```bash
RedHat
# dnf update -yum

Ubuntu
```

This command will automatically fetch and install the latest updates available for
your system, applying security patches, performance improvements, and bug fixes.
Once the update process is complete, you can move forward with the MariaDB installation.

### Install the MariaDB database¶

With the operating system updated and the MariaDB repository configured, you are
now ready to install the MariaDB server and client packages. This will provide the
necessary components to run and manage your database.

To install the MariaDB server and client, execute the following command:

```bash
RedHat
# dnf install MariaDB-server MariaDB-client

Ubuntu
```

This command will download and install both the server and client packages, enabling
you to set up, configure, and interact with your MariaDB database. Once the
installation is complete, you can proceed to start and configure the MariaDB service.

Now that MariaDB is installed, we need to enable the service to start automatically
upon boot and start it immediately. Use the following command to accomplish this:

```bash
RedHat
# systemctl enable mariadb --now

Ubuntu
```

This command will both enable and start the MariaDB service. Once the service is
running, you can verify that the installation was successful by checking the
version of MariaDB using the following command:

```bash
RedHat and Ubuntu
# mysql -V
```

The expected output should resemble this:

```
mysql  Ver 15.1 Distrib 10.11.6-MariaDB, for Linux (x86_64) using EditLine wrapper
```

To ensure that the MariaDB service is running properly, you can check its status
with the following command:

```bash
# systemctl status MariaDB
```

You should see an output similar to this, indicating that the MariaDB service
is active and running:

```bash
mariadb.service - MariaDB 10.11.6 database server
     Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: disabled)
    Drop-In: /etc/systemd/system/mariadb.service.d
             └─migrated-from-my.cnf-settings.conf
     Active: active (running) since Sat 2023-11-18 19:19:36 CET; 2min 13s ago
       Docs: man:mariadbd(8)
             https://mariadb.com/kb/en/library/systemd/
    Process: 41986 ExecStartPre=/bin/sh -c systemctl unset-environment _WSREP_START_POSITION (code=exited, status=0/SUCCESS)
    Process: 41987 ExecStartPre=/bin/sh -c [ ! -e /usr/bin/galera_recovery ] && VAR= ||   VAR=`cd /usr/bin/..; /usr/bin/galera_recovery`; [ $? -eq 0 ]   && systemctl set-environment _WSREP_START>
    Process: 42006 ExecStartPost=/bin/sh -c systemctl unset-environment _WSREP_START_POSITION (code=exited, status=0/SUCCESS)
   Main PID: 41995 (mariadbd)
     Status: "Taking your SQL requests now..."
      Tasks: 9 (limit: 12344)
     Memory: 206.8M
        CPU: 187ms
```

This confirms that your MariaDB server is up and running, ready for further configuration.

### Securing the MariaDB Database

To enhance the security of your MariaDB server, it's essential to remove unnecessary
test databases, anonymous users, and set a root password. This can be done using the
mariadb-secure-installation script, which provides a step-by-step guide to securing
your database.

Run the following command:

```bash
RedHat
# mariadb-secure-installation
```

```
NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
      SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!

In order to log into MariaDB to secure it, we'll need the current
password for the root user. If you've just installed MariaDB, and
haven't set the root password yet, you should just press enter here.

Enter current password for root (enter for none):
OK, successfully used password, moving on...

Setting the root password or using the unix_socket ensures that nobody
can log into the MariaDB root user without the proper authorisation.

You already have your root account protected, so you can safely answer 'n'.

Switch to unix_socket authentication [Y/n] n
 ... skipping.

You already have your root account protected, so you can safely answer 'n'.

Change the root password? [Y/n] y
New password:
Re-enter new password:
Password updated successfully!
Reloading privilege tables..
 ... Success!


By default, a MariaDB installation has an anonymous user, allowing anyone
to log into MariaDB without having to have a user account created for
them.  This is intended only for testing, and to make the installation
go a bit smoother.  You should remove them before moving into a
production environment.

Remove anonymous users? [Y/n] y
 ... Success!

Normally, root should only be allowed to connect from 'localhost'.  This
ensures that someone cannot guess at the root password from the network.

Disallow root login remotely? [Y/n] y
 ... Success!

By default, MariaDB comes with a database named 'test' that anyone can
access.  This is also intended only for testing, and should be removed
before moving into a production environment.

Remove test database and access to it? [Y/n] y
 - Dropping test database...
 ... Success!
 - Removing privileges on test database...
 ... Success!

Reloading the privilege tables will ensure that all changes made so far
will take effect immediately.

Reload privilege tables now? [Y/n] y
 ... Success!

Cleaning up...

All done!  If you've completed all of the above steps, your MariaDB
installation should now be secure.

Thanks for using MariaDB!
```

The mariadb-secure-installation script will guide you through several key steps:

1. Set a root password if one isn't already set.
2. Remove anonymous users.
3. Disallow remote root logins.
4. Remove the test database.
5. Reload the privilege tables to ensure the changes take effect.

Once complete, your MariaDB instance will be significantly more secure. You are
now ready to configure the database for Zabbix.

### Create the Zabbix database

With MariaDB now set up and secured, we can move on to creating the database for
Zabbix. This database will store all the necessary data related to your Zabbix server,
including configuration information and monitoring data.

Follow these steps to create the Zabbix database:

Log in to the MariaDB shell as the root user:
You'll be prompted to enter the root password that you set during the mariadb-secure-installation
process.

```bash
# mysql -uroot -p
```

Once you're logged into the MariaDB shell, run the following command to create a
database for Zabbix:

```bash
MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
```

???+ note
    utf8mb4 is a proper implementation of UTF-8 in MySQL/MariaDB, supporting all
    Unicode characters, including emojis. The older utf8 charset in MySQL/MariaDB
    only supports up to three bytes per character and is not a true UTF-8 implementation,
    which is why utf8mb4 is recommended.

This command creates a new database named zabbix with the UTF-8 character set,
which is required for Zabbix.

Create a dedicated user for Zabbix and grant the necessary privileges: Next, you
need to create a user that Zabbix will use to access the database. Replace password
with a strong password of your choice.

```sql
MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix server ip>' IDENTIFIED BY '<password>';
MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
MariaDB [(none)]> FLUSH PRIVILEGES;
```

This creates new users for zabbix-web and zabbix-srv, grants them access to the
zabbix database, and ensures that the privileges are applied immediately.

In some cases, especially when setting up Zabbix with MariaDB, you might encounter
issues related to stored functions and triggers if binary logging is enabled.
To address this, you need to set the log_bin_trust_function_creators option to 1
in the MariaDB configuration file. This allows non-root users to create stored
functions and triggers without requiring SUPER privileges, which are restricted
when binary logging is enabled.

```sql
MariaDB [(none)]> SET GLOBAL log_bin_trust_function_creators = 1;
MariaDB [(none)]> QUIT
```

At this point, your Zabbix database is ready, and you can proceed with configuring
the Zabbix server to connect to the database.

???+ warning
    In the Zabbix documentation, it is explicitly stated that deterministic
    triggers need to be created during the schema import. On MySQL and MariaDB
    systems, this requires setting GLOBAL log_bin_trust_function_creators = 1
    if binary logging is enabled, and you lack superuser privileges.

    If the log_bin_trust_function_creators option is not set in the MySQL
    configuration file, it will block the creation of these triggers during
    schema import. This is essential because, without superuser access,
    non-root users cannot create triggers or stored functions unless this setting is applied.

    To summarize:

    - Binary logging enabled: If binary logging is enabled and the user does not
      have superuser privileges, the creation of necessary Zabbix triggers will
      fail unless log_bin_trust_function_creators = 1 is set.

    - Solution: Add log_bin_trust_function_creators = 1 to the [mysqld] section
      in your MySQL/MariaDB configuration file or temporarily set it at runtime
      with SET GLOBAL log_bin_trust_function_creators = 1 if you have sufficient
      permissions.

    This ensures that Zabbix can successfully create the required triggers during
    schema import without encountering privilege-related errors.

## Installing the PostgreSQL database

## Installing the Zabbix server

## Installing the frontend
