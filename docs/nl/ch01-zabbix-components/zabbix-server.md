---
description: |
    This section from The Zabbix Book titled "Installing the Zabbix server" 
    guides you through the installation and configuration of the Zabbix server 
    on various Linux distributions. It covers the installation of the Zabbix 
    server package, configuration of the database connection settings, and setup 
    of the firewall to allow incoming connections to the Zabbix server. 
    Additionally, it provides instructions for starting and enabling the Zabbix 
    server service, validating the configuration, and checking the server's log
    file for any issues. 
tags: [beginner]
---

# De Zabbix-server installeren

Nu we de Zabbix repository hebben toegevoegd met de benodigde software, zijn we
klaar om zowel de Zabbix server als de webserver te installeren. Houd in
gedachten dat de webserver niet op dezelfde machine hoeft te worden
geïnstalleerd als de Zabbix server; ze kunnen op aparte systemen worden gehost
indien gewenst.

Voer het volgende commando uit om de Zabbix servercomponenten te installeren:

Info "Zabbix-server installeren".

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

Na de succesvolle installatie van het Zabbix serverpakket moeten we de Zabbix
server configureren om verbinding te maken met de database. Hiervoor moet het
configuratiebestand van de Zabbix-server worden aangepast.

Het Zabbix server configuratiebestand biedt een optie om extra
configuratiebestanden voor aangepaste parameters op te nemen. Voor een
productieomgeving is het vaak het beste om het oorspronkelijke
configuratiebestand niet direct te wijzigen. In plaats daarvan kun je aparte
configuratiebestanden maken en toevoegen voor aanvullende of gewijzigde
parameters. Deze aanpak zorgt ervoor dat je originele configuratiebestand
onaangeroerd blijft, wat vooral handig is bij het uitvoeren van upgrades of het
beheren van configuraties met tools zoals Ansible, Puppet of SaltStack.

Op SUSE 16 en later is deze functie al standaard ingeschakeld en geconfigureerd.
(zie ook [SUSE
documentatie](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Op SUSE-systemen bevindt het Zabbix serverconfiguratiebestand zich daarom in
`/usr/etc/zabbix/zabbix_server.conf`, en het is zo ingesteld dat het alle
`.conf` bestanden uit de `/etc/zabbix_server/zabbix_server.d/` directory bevat.

Op andere distributies moet je het misschien handmatig inschakelen:

Om deze functie in te schakelen, moet je ervoor zorgen dat de volgende regel
bestaat en niet is becommentarieerd (met een `#` ervoor) in
`/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```

Het pad `/etc/zabbix/zabbix_server.d/` zou al aangemaakt moeten zijn door het
geïnstalleerde pakket, maar controleer of het echt bestaat.

Nu maken we een aangepast configuratiebestand `database.conf` in de
`/etc/zabbix/zabbix_server.d/` directory dat onze database
verbindingsinstellingen zal bevatten:

Info "Zabbix databaseverbindingsinstellingen toevoegen".

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

Vervang `<database-host>`, `<database-naam>`, `<database-schema>`,
`<database-user>`, `<database-paswoord>`, en `<database-port>` door de juiste
waarden voor jouw setup. Dit zorgt ervoor dat de Zabbix server kan communiceren
met je database.

Ensure that there is no `#` (comment symbol) in front of the configuration
parameters, as Zabbix will treat lines beginning with `#` as comments, ignoring
them during execution. Additionally, double-check for duplicate configuration
lines; if there are multiple lines with the same parameter, Zabbix will use the
value from the last occurrence.

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

- DBHost refers to the host where your database is running (use localhost if
  it's on the same machine).
- DBName is the name of the Zabbix database.
- DBSchema is the schema name used in PostgreSQL (only needed for PostgreSQL).
- DBUser is the database user.
- DBPassword is the password for the database user.
- DBPort is the port number on which your database server is listening (default
  for MySQL/MariaDB is 3306 and PostgreSQL is 5432).

Make sure the settings reflect your environment's database configuration.

---

## Configure firewall to allow Zabbix trapper connections

Back on your Zabbix server machine, we need to ensure that the firewall is
configured to allow incoming connections to the Zabbix server.

Your Zabbix server needs to accept incoming connections from Zabbix agents,
senders, and proxies. By default, Zabbix uses port `10051/tcp` for these
connections. To allow these connections, you need to open this port in your
firewall.

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
can now start and enable the Zabbix server service. Run the following command to
enable the Zabbix server and ensure it starts automatically on boot:

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
to launch on system startup. To verify that the Zabbix server is running
correctly, check the log file for any messages. You can view the latest entries
in the `Zabbix server` log file using:

!!! info "Check the log file"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```

Look for messages indicating that the server has started successfully. If there
are any issues, the log file will provide details to help with troubleshooting.

!!! example "Voorbeeld uitvoer"

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
`/etc/zabbix/zabbix_server.d/database.conf` file and ensure that the database is
properly populated as described in the previous steps. Also check firewall rules
and when using PostgreSQL make sure that `pg_hba.conf` is correctly configured
to allow connections from the Zabbix server.

Let's check the Zabbix server service to see if it's enabled so that it survives
a reboot

!!! info "check status of zabbix-server service"

    ```bash
    sudo systemctl status zabbix-server
    ```

???+ example "Example output" ```shell-session localhost:~> sudo systemctl
status zabbix-server

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

---

## Conclusie

With the successful installation and configuration of the Zabbix server, you
have now established the core component of your monitoring system. We've covered
the installation of the Zabbix server package, configuration of the database
connection settings, and setup of the firewall to allow incoming connections to
the Zabbix server. Additionally, we've started the Zabbix server service and
verified its operation.

Your Zabbix server is now ready to communicate with Zabbix agents, senders, and
proxies. The next step is to install and configure the Zabbix frontend, which
will provide the user interface for interacting with your monitoring system.

Let's proceed to the next chapter to set up the Zabbix frontend.

---

## Vragen

1. What version of Zabbix should I install for compatibility and stability?
2. What Zabbix logs should I check for troubleshooting common issues?

---

## Nuttige URL's

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
