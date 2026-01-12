---
description: |
    This section from The Zabbix Book titled "Installing a MariaDB Database"
    guides you through installing MariaDB as the database backend for Zabbix.
    It covers two installation methods: using OS vendor-provided packages or the
    official MariaDB repositories. The section includes steps to start and 
    secure the MariaDB server, create a Zabbix database with appropriate users,
    and configure firewall rules if necessary. 
tags: [beginner]
---

# Installing a MariaDB Database

In this section we will install the MariaDB server and -client packages. This
will provide the necessary components to run and manage MariaDB as your Zabbix
database backend.

If you prefer to use PostgreSQL as your database backend, you can skip this
section and proceed to the [_Installing the PostgreSQL Database_](postgresql.md)
section.

???+ tip "MySQL/Percona" If you prefer to use MySQL or Percona instead of
MariaDB, the installation and configuration steps are very similar. Generally,
you would replace `mariadb` with `mysql` in the package names and commands.

## Installing MariaDB Server and Client from OS Vendor-Provided Packages

To install the distribution default MariaDB server and client, execute the
following command:

!!! info "Install distribution version of Mariadb"

    Red Hat
    ```bash
    dnf install mariadb-server
    ```

    SUSE
    ``` bash
    zypper install mariadb mariadb-client
    ```

    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```

This command will download and install both the server and client packages,
enabling you to set up, configure, and interact with your MariaDB database. Once
the installation is complete, you can proceed to the [_Starting the MariaDB
database_](#starting-the-mariadb-database) section.

---

## Installing MariaDB Server and Client from Official MariaDB Repositories

If you prefer to install MariaDB from the official MariaDB repositories instead
of the OS vendor-provided packages, the first step is to add the MariaDB
repository to your system.

---

### Adding the MariaDB Repository
To create the MariaDB repository file, execute the following command in your
terminal:

!!! info "Define the MariaDB repository"

    Red Hat
    ``` bash
    vi /etc/yum.repos.d/mariadb.repo
    ```

    SUSE
    ``` bash
    sudo vi /etc/zypp/repos.d/mariadb.repo
    ```

    Ubuntu
    ``` bash
    sudo apt install apt-transport-https curl
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp'

    sudo vi /etc/apt/sources.list.d/mariadb.sources
    ```

This will open a text editor where you can input the repository configuration
details. Once the repository is configured, you can proceed with the
installation of MariaDB using your package manager.

The latest config can be found here:
[https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Here's an example configuration for MariaDB 11.4 repositories:

!!! example "Mariadb repository configuration"

    Red Hat
    ```ini
    # MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-02-21 10:15 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/rhel/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/rhel/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```

    SUSE
    ```ini
    # MariaDB 11.4 openSUSE repository list - created 2025-12-29 14:34 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/opensuse/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```

    Ubuntu
    ```  yaml
    # MariaDB 11.4 repository list - created 2025-02-21 11:42 UTC
    # https://mariadb.org/download/
    X-Repolib-Name: MariaDB
    Types: deb
    # deb.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # URIs: https://deb.mariadb.org/11.4/ubuntu
    URIs: https://mirror.bouwhuis.network/mariadb/repo/11.4/ubuntu
    Suites: noble
    Components: main main/debug
    Signed-By: /etc/apt/keyrings/mariadb-keyring.pgp
    ```

After saving the file, ensure that everything is properly set up and that your
preferred MariaDB version is compatible with your Zabbix version to avoid
potential integration issues.

---

### Installing MariaDB Server and Client

With the MariaDB repository configured, you are now ready to install the MariaDB
server and client packages. This will provide the necessary components to run
and manage your database.

To install the MariaDB server and client, execute the following command:

!!! info "Install MariaDB from official repository"

    Red Hat
    ```bash
    dnf install MariaDB-server
    ```

    SUSE
    ```bash
    sudo rpm --import https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    sudo zypper install MariaDB-server MariaDB-client
    ```


    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```

This command will download and install both the server and client packages,
enabling you to set up, configure, and interact with your MariaDB database. Once
the installation is complete, you can proceed to the [_Starting the MariaDB
database_](#starting-the-mariadb-database) section.

---

## Starting the MariaDB Database

Now that MariaDB is installed, we need to enable the service to start
automatically upon boot and start it immediately. Use the following command to
accomplish this:

!!! info "Enable MariaDB service"

    ```bash
    sudo systemctl enable mariadb --now
    ```

This command will both enable and start the MariaDB service and since this will
be the first time the service is started, it will initialize the database
directory. With the MariaDB service now up and running, you can verify that the
installation was successful by checking the version of MariaDB using the
following command:

!!! info "Check Mariadb version"

    ```bash
    mariadb -V
    ```

The expected output should resemble this:

???+ example "MariaDB version example"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb  Ver 15.1 Distrib 10.11.14-MariaDB, for Linux (x86_64) using  EditLine wrapper
    ```

To ensure that the MariaDB service is running properly, you can check its status
with the following command:

!!! info "Get mariadb status"

    ```bash
    sudo systemctl status mariadb
    ```

You should see an output similar to this, indicating that the MariaDB service is
active and running:

???+ example "Mariadb service status example"

    ```shell-session
    localhost:~ $ sudo systemctl status mariadb
    ● mariadb.service - MariaDB database server
         Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: disabled)
         Active: active (running) since Wed 2025-12-03 00:16:04 CET; 5s ago
           Docs: man:mysqld(8)
                 https://mariadb.com/kb/en/library/systemd/
        Process: 11148 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper install (code=exited, status=0/SUCCESS)
        Process: 11155 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper upgrade (code=exited, status=0/SUCCESS)
       Main PID: 11162 (mysqld)
         Status: "Taking your SQL requests now..."
          Tasks: 18 (limit: 4670)
            CPU: 340ms
         CGroup: /system.slice/mariadb.service
                 └─11162 /usr/sbin/mysqld --defaults-file=/etc/my.cnf --user=mysql --socket=/run/mysql/mysql.sock

    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Plugin 'FEEDBACK' is disabled.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Server socket created on IP: '127.0.0.1', port: '3306'.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] /usr/sbin/mysqld: ready for connections.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Version: '10.11.14-MariaDB'  socket: '/run/mysql/mysql.sock'  port: 3306  MariaDB package
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Buffer pool(s) load completed at 251203  0:16:04
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Started MariaDB database server.
    ```

This confirms that your MariaDB server is up and running, ready for further
configuration.

---

## Securing the MariaDB Database

To enhance the security of your MariaDB server, it's essential to remove
unnecessary test databases, anonymous users, and set a root password. This can
be done using the mariadb-secure-installation script, which provides a
step-by-step guide to securing your database.

Run the following command:

!!! info "Secure Mariadb setup"

    ```bash
    sudo mariadb-secure-installation
    ```

The mariadb-secure-installation script will guide you through several key steps:

1. Set a root password if one isn't already set.
2. Remove anonymous users.
3. Disallow remote root logins.
4. Remove the test database.
5. Reload the privilege tables to ensure the changes take effect.

Once complete, your MariaDB instance will be significantly more secure.

!!! example "mariadb-secure-installation example output"

    ```shell-session
    localhost:~ $ sudo mariadb-secure-installation
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

You are now ready to configure the database for Zabbix.

---

## Creating the Zabbix database instance

With MariaDB now set up and secured, we can move on to creating the database for
Zabbix. This database will store all the necessary data related to your Zabbix
server, including configuration information and monitoring data.

Follow these steps to create the Zabbix database:

Log in to the MariaDB shell as the root user: You'll be prompted to enter the
root password that you set during the mariadb-secure-installation process.

!!! info "Enter Mariadb as user root"

    ```bash
    mariadb -uroot -p
    ```

Once you're logged into the MariaDB shell, run the following command to create a
database for Zabbix:

!!! info "Create the database"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```

???+ note "What is utf8mb4"

     utf8mb4 is a proper implementation of UTF-8 in MySQL/MariaDB, supporting all
     Unicode characters, including emojis. The older utf8 charset in MySQL/MariaDB
     only supports up to three bytes per character and is not a true UTF-8 implementation,
     which is why utf8mb4 is recommended.

This command creates a new database named `zabbix` with the UTF-8 character set,
which is required for Zabbix.

Create a dedicated user for Zabbix and grant the necessary privileges: Next, you
need to create a user that Zabbix will use to access the database. Replace
`<password>` with a strong password of your choice.

!!! info "Create users and grant privileges"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```

    - Replace `<zabbix server ip>` with the actual IP address of your server
      where the Zabbix server  will be installed.
    - Replace `<zabbix frontend ip>` with the actual IP address of your server
      where the Zabbix frontend will be installed.

    If both components are installed on the same server, use the same IP address.

    ???+ tip

        If your Zabbix server, frontend and database are on the same machine, you can replace
        `<zabbix server ip>` and `<zabbix frontend ip>` with `localhost` or `127.0.0.1`.

This creates new users `zabbix-web` and `zabbix-srv`, grants them access to the
Zabbix database, and ensures that the privileges are applied immediately.

At this point, your Zabbix database is ready, but before it can actually be used
by Zabbix, we still need to populate the database with the necessary tables and
initial data, but that will be covered in the next section when we install the
Zabbix server.

If you intent to install Zabbix server on a different machine than the one
hosting the database you will need to open the host firewall to allow incoming
connections to the database server. By default, MariaDB listens on port 3306.

!!! info "Add firewall rules"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=mysql --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 3306/tcp
    ```

---

## Populate the Zabbix database

During the installation of the database software earlier, we created the
necessary users and database for Zabbix, however, Zabbix expects certain tables,
schemas, images, and other elements to be present in the database. To set up the
database correctly, we need to populate it with the required schema.

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

Now lets upload the data from zabbix (db structure, images, user, ... ) for this
we make use of the user `zabbix-srv` and we upload it all in our DB `zabbix`.

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
`log_bin_trust_function_creators` global parameter. It is a good practice to
remove it for security reasons.

To revert the global parameter back to 0, use the following command in the
MySQL/MariaDB shell:

!!! info "Disable function log_bin_trust again"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```

This command will disable the setting, ensuring that the servers security
posture remains robust.

This concludes our installation of the MariaDB. You can now proceed to
[Preparing the Zabbix server](preparation.md).

---

## Conclusion

With the successful installation and configuration of MariaDB as the database
backend for Zabbix, you now have a robust foundation for your monitoring
solution. We've covered the installation of MariaDB from both vendor-provided
packages and official repositories, securing the database, creating the
necessary Zabbix database and users, and populating the database with the
required schema and initial data.

Your Zabbix environment is now ready for the next stages of setup and
configuration.

---

## Questions

1. What version of MariaDB should I install for compatibility and stability?
2. What port does my DB use ?
3. Which database users did I create and why?

---

## Useful URLs

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)
