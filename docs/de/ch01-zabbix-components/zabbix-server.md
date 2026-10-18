---
description: |
    Diese Abschnitt aus dem Buch "The Zabbix Book" mit dem Titel "Installation des Zabbix-Servers"
    führt Sie durch die Installation und Konfiguration des Zabbix-Servers auf verschiedenen Linux-Distributionen.
    Es behandelt die Installation des Zabbix-Server-Pakets, die Konfiguration der Datenbankverbindungsparameter
    und die Einrichtung eines Firewalls, um eingehende Verbindungen zum Zabbix-Server zuzulassen. 
    Darüber hinaus bietet es Anweisungen zur Starteinstellung des Zabbix-Servers-Dienstes,
    zur Validierung der Konfiguration und zum Überprüfen der Serverprotokolle auf Probleme.
tags: [beginner]
---

# Installation des Zabbix-Servers

Nachdem wir den Zabbix-Repository mit dem notwendigen Software hinzugefügt haben, sind
wir bereit, sowohl den Zabbix-Server als auch den Webserver zu installieren. Beachten Sie,
dass der Webserver nicht auf demselben Computer wie der Zabbix-Server installiert werden muss;
sie können auf getrennten Systemen gehostet werden, wenn gewünscht.

Um die Komponenten des Zabbix-Servers zu installieren, führen Sie den folgenden Befehl aus:

!!! info "Installieren Sie den zabbix server"

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


Nach erfolgreicher Installation des Zabbix-Server-Pakets müssen wir den Zabbix-Server
konfigurieren, um eine Verbindung zur Datenbank herzustellen. Dies erfordert die Anpassung der
Zabbix-Server-Konfigurationsdatei.

Die Zabbix-Server-Konfigurationsdatei bietet eine Option zum Einbinden von zusätzlichen Konfigurationsdateien für benutzerdefinierte Parameter.
Für Produktionsumgebungen ist es oft am besten, die ursprüngliche Konfigurationsdatei nicht direkt zu ändern. Stattdessen
kann man separate Konfigurationsdateien für zusätzliche oder geänderte Parameter erstellen und einbinden. Dieser Ansatz sorgt dafür,
dass Ihre ursprüngliche Konfigurationsdatei unverändert bleibt, was besonders hilfreich ist bei Upgrades oder der Verwaltung von Konfigurationen
mit Tools wie Ansible, Puppet oder SaltStack.

Auf SUSE 16 und neuer ist diese Funktion bereits standardmäßig aktiviert und konfiguriert.
(Weitere Informationen unter [https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Daher befindet sich auf Systemen mit SUSE die Zabbix-Server-Konfigurationsdatei an folgendem Ort:
`/usr/etc/zabbix/zabbix_server.conf`, und es ist so konfiguriert, dass alle `.conf` Dateien aus dem
`/etc/zabbix_server/zabbix_server.d/` Verzeichnis eingebunden werden.

Auf anderen Distributionen müssen Sie dies möglicherweise manuell aktivieren:

Um diese Funktion zu aktivieren, stellen Sie sicher, dass die nächste Zeile vorhanden und nicht mit einem `#`
kommentiert ist in der `/etc/zabbix/zabbix_server.conf` Datei.

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```


Der Pfad `/etc/zabbix/zabbix_server.d/` sollte bereits durch das installierte Paket erstellt worden sein, stellen Sie aber sicher,
dass er tatsächlich existiert.

Jetzt werden wir eine benutzerdefinierte Konfigurationsdatei `database.conf` im `/etc/zabbix/zabbix_server.d/`
Verzeichnis erstellen, die unsere Datenbankverbindungsparameter enthält:

!!! info "Fügen Sie Zabbix-Datenbankverbindungseinstellungen hinzu"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```


    Fügen Sie die folgenden Zeilen in der Konfigurationsdatei ein, um sie auf Ihre Datenbanksystemanordnung abzustimmen:

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```


Ersetzen Sie `<database-host>`, `<database-name>`, `<database-schema>`, `<database-user>`,
`<database-password>` und `<database-port>` durch die entsprechenden Werte für Ihre
Umgebung. Dies sorgt dafür, dass der Zabbix-Server eine Kommunikation mit Ihrer Datenbank aufbauen kann.

Stellen Sie sicher, dass es keinen `#` (Kommentarzeichen) vor den Konfigurationsparametern gibt,
da Zabbix Zeilen als Kommentare behandelt und ignoriert, die mit `#` beginnen.
Außerdem überprüfen Sie auf doppelte Konfigurationszeilen; wenn es mehrere Zeilen mit dem gleichen Parameter gibt,
wird Zabbix den Wert aus der letzten Erscheinung verwenden.

Für unsere Umgebung wird die Konfiguration wie folgt aussehen:

!!! example "Beispiel für database.conf"

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


!!! note "Für PostgreSQL in HA"

    Ab Zabbix 8.0 ist es jetzt möglich, mehr als eine IP für DBHost hinzuzufügen. Dies ermöglicht
    die Einrichtung einer HA-DB-Umgebung mit PostgreSQL ohne den Einsatz eines Loadbalancers.
    Zabbix erkennt den aktiven DB selbst aus. Beispiel:
    DBHost=192.168.10.2:5432,192.168.10.3:5432

In diesem Beispiel:

- `DBHost` bezieht sich auf den Host, auf dem Ihre Datenbank läuft (verwenden Sie localhost,
  wenn sie auf demselben Computer ist).
- `DBName` ist der Name des Zabbix-Datenbanks.
- `DBSchema` ist das Schemaname, das in PostgreSQL verwendet wird (nur für PostgreSQL erforderlich).
- `DBUser` ist der Datenbankbenutzer.
- `DBPassword` ist das Passwort für den Datenbankbenutzer.
- `DBPort` ist die Portnummer, auf der Ihre Datenbanksystem lauscht (Standard für
  MySQL/MariaDB ist 3306 und PostgreSQL ist 5432).

Stellen Sie sicher, dass die Einstellungen Ihrer Umgebung entsprechen.

---

## Konfigurieren des Firewalls, um Zabbix-Trapper-Verbindungen zuzulassen

Auf Ihrem Zabbix-Server-Rechner müssen wir sicherstellen, dass der Firewall so konfiguriert ist,
dass eingehende Verbindungen zum Zabbix-Server zugelassen werden.

Ihr Zabbix-Server muss eingehende Verbindungen von Zabbix-Agents, -Sendern und -Proxys akzeptieren.
Standardmäßig verwendet Zabbix den Port `10051/tcp` für diese Verbindungen.
Um diese Verbindungen zuzulassen, müssen Sie diesen Port im Firewall öffnen.

!!! info "Öffnen Sie den Firewall für zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```


Wenn der Dienst nicht mit `firewall-cmd --add-service` erkannt wird, können Sie
manuell den Port angeben:

!!! info "Port hinzufügen anstatt des Dienstnamens"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```


---

## Starten des Zabbix-Servers

Mit der aktualisierten Konfiguration des Zabbix-Servers, um eine Verbindung zur Datenbank herzustellen,
können Sie den Zabbix-Server-Dienst jetzt starten und aktivieren. Führen Sie den folgenden Befehl aus,
um den Zabbix-Server zu aktivieren und sicherzustellen, dass er bei jedem Systemstart gestartet wird:

???+ note

    Vor dem Neustarten des Zabbix-Servers nach Änderungen an seiner Konfiguration gilt es als beste Praxis,
    die Konfiguration zu validieren, um potenzielle Probleme zu verhindern. Durch das Ausführen einer
    Konfigurationsprüfung werden Fehler vorab erkannt und eine Downtime aufgrund einer ungültigen Konfiguration
    vermieden. Dies kann mit dem folgenden Befehl erreicht werden: `zabbix-server -T`

!!! info "Aktivieren und starten des zabbix-server-Dienstes"

    Red Hat, SUSE und Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```


Dieser Befehl startet den Zabbix-Server-Dienst sofort und konfiguriert ihn,
um bei jedem Systemstart gestartet zu werden. Um sicherzustellen, dass der Zabbix-Server korrekt läuft,
prüfen Sie das Protokoll auf Nachrichten. Sie können die neuesten Einträge im
`Zabbix server` Protokolldatei mit folgendem Befehl anzeigen:

!!! info "Überprüfen der Protokolldatei"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```


Suchen Sie nach Nachrichten, die darauf hinweisen, dass der Server erfolgreich gestartet wurde.
Wenn es Probleme gibt, wird das Protokoll Details bereitstellen, um mit der Fehlerbehebung zu helfen.

!!! example "Beispielausgabe"

    ```
    12074:20250225:145333.529 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
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
    12074:20250225:145333.545 current database version (mandatory/optional): 08000000/08000000
    12074:20250225:145333.545 required mandatory version: 08000000
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


Wenn ein Fehler aufgetreten ist und der Server nicht in der Lage war, eine Verbindung zur Datenbank herzustellen,
würden Sie im Protokoll des Servers etwas wie folgt sehen:

!!! example "Beispielnachricht mit Fehlern"

    ```
    12068:20250225:145309.018 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
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

Wenn dies der Fall ist, überprüfen Sie Ihre Datenbankverbindungsparameter in der
`/etc/zabbix/zabbix_server.d/database.conf` Datei und stellen Sie sicher, dass die Datenbank
richtig befüllt wurde, wie in den vorherigen Schritten beschrieben. Überprüfen Sie auch Firewall-Regeln
und wenn PostgreSQL verwendet wird, stellen Sie sicher, dass `pg_hba.conf` korrekt konfiguriert ist,
um Verbindungen vom Zabbix-Server aus zuzulassen.

Lassen Sie uns den Status des Zabbix-Server-Dienstes überprüfen, um zu sehen, ob er aktiviert ist
und nach einem Neustart überlebt.

!!! info "Überprüfung des Status des zabbix-server-Dienstes"

    ```bash
    sudo systemctl status zabbix-server
    ```


???+ example "Beispielausgabe"
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


Dies schließt unseren Abschnitt zur Installation und Konfiguration des Zabbix-Servers ab.

---

## Schlussfolgerung

Mit der erfolgreichen Installation und Konfiguration des Zabbix-Servers haben Sie
jetzt den Kernkomponenten Ihres Monitoring-Systems eingerichtet. Wir haben die Installation des Zabbix-Server-Pakets,
die Konfiguration der Datenbankverbindungsparameter und die Einrichtung eines Firewalls behandelt, um eingehende Verbindungen zum Zabbix-Server zuzulassen.
Darüber hinaus haben wir den Zabbix-Server-Dienst gestartet und seine Funktionalität überprüft.

Ihr Zabbix-Server ist jetzt bereit, mit Zabbix-Agents, -Sendern und -Proxys zu kommunizieren. Der nächste Schritt besteht darin,
den Zabbix-Frontend zu installieren und einzurichten, das die Benutzeroberfläche für die Interaktion mit Ihrem Monitoring-System bereitstellt.

Lassen Sie uns zum nächsten Kapitel übergehen, um den Zabbix-Frontend einzurichten.

---

## Fragen

1. Welche Version von Zabbix sollte ich installieren, um Kompatibilität und Stabilität zu gewährleisten?
2. Welche Zabbix-Protokolle sollten ich für die Fehlerbehebung bei gängigen Problemen überprüfen?

---

## Nützliche URLs

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)