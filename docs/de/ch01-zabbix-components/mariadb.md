---
description: |
    Diese Abschnitt aus dem Buch "The Zabbix Book" mit dem Titel "Ein MariaDB-Datenbank-Backend installieren"
    führt Sie durch die Installation von MariaDB als Datenbankspeicher für Zabbix.
    Es behandelt zwei Installationsmethoden: das Verwenden der vom Betriebssystem bereitgestellten Pakete oder
    der offiziellen MariaDB-Repositorien. Der Abschnitt enthält Schritte zur Startung und Sicherung des MariaDB-Servers,
    zur Erstellung einer Zabbix-Datenbank mit angemessenen Benutzern sowie zur Konfiguration von Feuerwaldrules, falls erforderlich.
tags: [beginner]
---

# Ein MariaDB-Datenbanksystem installieren

In diesem Abschnitt werden wir die Pakete für den MariaDB-Server und -Client installieren. Dies stellt die notwendigen Komponenten bereit,
um MariaDB als Datenbankbackend für Zabbix zu betreiben.

Wenn Sie PostgreSQL als Datenbankbackend bevorzugen, können Sie diesen Abschnitt überspringen und mit dem
[_PostgreSQL-Datenbanksystem installieren_](postgresql.md) Abschnitt fortfahren.

???+ tip "MySQL/Percona"
    Wenn Sie MySQL oder Percona anstelle von MariaDB bevorzugen, sind die Installations- und Konfigurationsanweisungen sehr ähnlich.
    Allgemein ersetzen Sie `mariadb` durch `mysql` in den Paketnamen und Befehlen.

## MariaDB Server und Client aus Betriebssystem-Paketen installieren

Um das vom Betriebssystem bereitgestellte Standard-MariaDB-Datenbanksystem zu installieren, führen Sie den folgenden Befehl aus:

!!! info "Installiere die von der Distribution bereitgestellte Version von Mariadb"

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


Dieser Befehl lädt und installiert sowohl den Server- als auch den Client-Paket, sodass Sie das MariaDB-Datenbanksystem einrichten,
konfigurieren und nutzen können. Sobald die Installation abgeschlossen ist, können Sie mit dem
[_Starten des MariaDB-Datenbanksystems_](#starting-the-mariadb-database) Abschnitt fortfahren.

---

## MariaDB Server und Client aus den offiziellen MariaDB-Repositorien installieren

Wenn Sie die Installation von MariaDB aus den offiziellen MariaDB-Repositorien bevorzugen, müssen Sie zunächst das MariaDB-Repositorium
zu Ihrem System hinzufügen.

---

### Das MariaDB-Repositorium hinzufügen
Um die Datei für das MariaDB-Repositorium zu erstellen, führen Sie im Terminal folgenden Befehl aus:

!!! info "Definiere das MariaDB-Repositorium"

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


Dies öffnet einen Texteditor, in dem Sie die Konfigurationsdetails für das Repository eingeben können.
Sobald das Repository konfiguriert ist, können Sie mit der Installation von MariaDB fortsetzen,
indem Sie Ihren Paket-Manager verwenden.

Die neueste Konfiguration kann hier gefunden werden: [https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Hier ist ein Beispiel für die Konfiguration der MariaDB 11.4-Repositorien:

!!! example "MariaDB-Repository-Konfiguration"

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


Nachdem Sie die Datei gespeichert haben, stellen Sie sicher, dass alles korrekt eingerichtet ist und dass Ihre bevorzugte MariaDB-Version
mit Ihrer Zabbix-Version kompatibel ist, um potenzielle Integrationsprobleme zu vermeiden.

---

### MariaDB Server und Client installieren

Mit dem konfigurierten MariaDB-Repositorium sind Sie nun bereit, die Pakete für den MariaDB-Server und -Client zu installieren.
Dies stellt die notwendigen Komponenten zur Verfügung, um das Datenbanksystem zu betreiben und zu verwalten.

Um den MariaDB-Server und -Client zu installieren, führen Sie folgenden Befehl aus:

!!! info "Installiere MariaDB aus dem offiziellen Repository"

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


Dieser Befehl lädt und installiert sowohl den Server- als auch den Client-Paket, sodass Sie das MariaDB-Datenbanksystem einrichten,
konfigurieren und nutzen können. Sobald die Installation abgeschlossen ist, können Sie mit dem
[_Starten des MariaDB-Datenbanksystems_](#starting-the-mariadb-database) Abschnitt fortfahren.

---

## Starten des MariaDB-Datenbanksystems

Nun, da MariaDB installiert ist, müssen wir den Dienst so einrichten, dass er beim Systemstart automatisch gestartet wird und sofort
gestartet werden kann. Verwenden Sie folgenden Befehl, um dies zu erreichen:

!!! info "Aktiviere MariaDB-Dienst"

    ```bash
    sudo systemctl enable mariadb --now
    ```


Dieser Befehl aktiviert den MariaDB-Dienst und startet ihn sofort. Da es sich hierbei um die erste Startung handelt,
wird das Datenbankverzeichnis initialisiert.
Mit dem laufenden MariaDB-Dienst können Sie nun überprüfen, ob die Installation erfolgreich war, indem Sie die Version von MariaDB
mit folgendem Befehl prüfen:

!!! info "Überprüfe Mariadb-Version"

    ```bash
    mariadb -V
    ```


Die erwartete Ausgabe sollte wie folgt aussehen:

???+ example "Beispiel für MariaDB-Version"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb from 11.4.13-MariaDB, client 15.2 for Linux (aarch64) using  EditLine wrapper
    ```


Um sicherzustellen, dass der MariaDB-Dienst ordnungsgemäß läuft, können Sie mit dem folgenden Befehl den Status prüfen:

!!! info "Überprüfe mariadb-Status"

    ```bash
    sudo systemctl status mariadb
    ```


Sie sollten eine Ausgabe ähnlich wie diese sehen, was bedeutet, dass der MariaDB-Dienst aktiv und läuft:

???+ example "Beispiel für den Status des Mariadb-Diensts"

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
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Version: '11.4.13-MariaDB'  socket: '/run/mysql/mysql.sock'  port: 3306  MariaDB package
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Buffer pool(s) load completed at 251203  0:16:04
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Started MariaDB database server.
    ```


Dies bestätigt, dass Ihr MariaDB-Server bereit ist, weitere Konfigurationen durchzuführen.

---

## Sicherung des MariaDB-Datenbanksystems

Um die Sicherheit Ihres MariaDB-Servers zu erhöhen, sollten Sie unnötige Testdatenbanken entfernen, anonyme Benutzer löschen und ein Passwort für den Root-Benutzer festlegen.
Dies kann mit dem Skript `mariadb-secure-installation` durchgeführt werden, das eine Schritt-für-Schritt-Anleitung zur Sicherung Ihrer Datenbank bietet.

Führen Sie folgenden Befehl aus:

!!! info "Sichere MariaDB-Einrichtung"

    ```bash
    sudo mariadb-secure-installation
    ```


Das Skript `mariadb-secure-installation` führt Sie durch mehrere wichtige Schritte:

1. Setzen eines Root-Passworts, falls noch keines gesetzt ist.
2. Entfernen anonymer Benutzer.
3. Verhindern von Fernwartungen für den Root-Benutzer.
4. Entfernen der Testdatenbank.
5. Aktualisieren der Berechtigungslisten, um die Änderungen wirksam zu machen.

Nach Abschluss ist Ihr MariaDB-System erheblich sicherer.

!!! example "Beispiel für das Ausführen von mariadb-secure-installation"

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


Sie sind nun bereit, die Datenbank für Zabbix einzurichten.

---

## Erstellen der Zabbix-Datenbankinstanz

Mit MariaDB jetzt eingerichtet und gesichert können wir fortfahren mit dem Erstellen der Datenbank für Zabbix.
Diese Datenbank speichert alle notwendigen Informationen zum Zabbix-Server, einschließlich Konfigurationsdaten und Überwachungsdaten.

Führen Sie die folgenden Schritte aus, um die Zabbix-Datenbank zu erstellen:

Melden Sie sich als root-Benutzer im MariaDB-Skript an:
Sie werden aufgefordert, das Passwort für den root-Benutzer einzugeben, das Sie während des Prozesses `mariadb-secure-installation` gesetzt haben.

!!! info "Loggen Sie sich in Mariadb als Benutzer root ein"

    ```bash
    mariadb -uroot -p
    ```


Sobald Sie im MariaDB-Skript angemeldet sind, führen Sie den folgenden Befehl aus, um eine Datenbank für Zabbix zu erstellen:

!!! info "Erstellen der Datenbank"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```


???+ note "Was ist utf8mb4"

     utf8mb4 ist eine korrekte Implementierung von UTF-8 in MySQL/MariaDB, die alle Unicode-Zeichen unterstützt,
     einschließlich Emojis. Der ältere utf8-Zeichensatz in MySQL/MariaDB unterstützt nur bis zu drei Bytes pro Zeichen
     und ist keine echte UTF-8-Implementierung, deshalb wird utf8mb4 empfohlen.

Dieser Befehl erstellt eine neue Datenbank mit dem Namen `zabbix` unter Verwendung des UTF-8-Zeichensatzes,
der für Zabbix erforderlich ist.

Erstellen Sie einen dedizierten Benutzer für Zabbix und gewähren Sie die notwendigen Berechtigungen: Als Nächstes müssen Sie
einen Benutzer erstellen, den Zabbix zum Zugriff auf die Datenbank verwenden wird. Ersetzen Sie `<password>` durch ein starkes Passwort Ihrer Wahl.

!!! info "Erstellen von Benutzern und Gewähren der Berechtigungen"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```


    - Ersetzen Sie `<zabbix server ip>` durch die tatsächliche IP-Adresse Ihres Servers,
      auf dem der Zabbix-Server installiert wird.
    - Ersetzen Sie `<zabbix frontend ip>` durch die tatsächliche IP-Adresse Ihres Servers,
      auf dem das Zabbix-Frontend installiert wird.

    Wenn beide Komponenten auf demselben Server installiert sind, verwenden Sie dieselbe IP-Adresse.

    ???+ tip

        Wenn Ihr Zabbix-Server, Frontend und Datenbank auf demselben Rechner installiert sind, können Sie
        `<zabbix server ip>` und `<zabbix frontend ip>` durch `localhost` oder `127.0.0.1` ersetzen.

Dies erstellt neue Benutzer `zabbix-web` und `zabbix-srv`, gewährt ihnen Zugriff auf die Zabbix-Datenbank
und stellt sicher, dass die Berechtigungen sofort wirksam werden.

Bis zu diesem Punkt ist Ihre Zabbix-Datenbank bereit, aber bevor sie tatsächlich von Zabbix verwendet werden kann,
müssen Sie die Datenbank mit den notwendigen Tabellen und Initialdaten füllen. Dies wird im nächsten Abschnitt behandelt,
wenn wir den Zabbix-Server installieren.

Wenn Sie beabsichtigen, den Zabbix-Server auf einem anderen Rechner als dem zu installieren, der das Datenbanksystem hostet,
müssen Sie die Hostfeuerwaldrules so einstellen, dass eingehende Verbindungen zum Datenbankserver erlaubt sind.
Standardmäßig hört MariaDB auf Port 3306.

!!! info "Fügen Sie Feuerwaldrules hinzu"

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

## Füllen der Zabbix-Datenbank

Während der Installation des Datenbanksystems zuvor haben wir die notwendigen Benutzer und Datenbank für Zabbix erstellt,
allerdings erwartet Zabbix bestimmte Tabellen, Schemata, Bilder und andere Elemente in der Datenbank.
Um die Datenbank korrekt einzurichten, müssen Sie sie mit dem erforderlichen Schema füllen.

Zuerst müssen wir das Zabbix-SQL-Script installieren, das die notwendigen Import-Scripts für die Datenbank enthält.

!!! info "Installiere SQL-Scripts"

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

    Wenn Sie eine aktuelle Version von MySQL oder MariaDB als Datenbankbackend für Zabbix verwenden,
    können Sie Probleme mit der Erstellung von Triggern während des Schemaimports erleben.
    Dies ist besonders relevant, wenn das Binärprotokollierung auf Ihrem Datenbanksystem aktiviert ist (Binärprotokollierung wird oft standardmäßig aktiviert).
    Um dies zu beheben, müssen Sie die `log_bin_trust_function_creators` Option auf `1` in der MySQL/MariaDB-Konfigurationsdatei oder temporär beim Laufzeitbetrieb setzen.
    Dies ermöglicht es nicht-root-Benutzern, gespeicherte Funktionen und Triggern zu erstellen, ohne die
    `SUPER` Berechtigungen zu benötigen, die eingeschränkt sind, wenn Binärprotokollierung aktiviert ist.

    Normalerweise werden wir diese Einstellung nach dem ersten Import des Zabbix-Schemas nicht mehr benötigen,
    so dass wir sie danach wieder deaktivieren.    !!! info "Aktivieren Sie temporär zusätzliche Berechtigungen für nicht root-Benutzer"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```


Nun laden wir die Daten von zabbix (Datenbankstruktur, Bilder, Benutzer usw.)
in unsere DB hoch. Hierfür verwenden wir den Benutzer `zabbix-srv` und
laden alles in unsere DB `zabbix`.

!!! info "Füllen Sie die Datenbank"

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```


!!! warning

    Abhängig von der Geschwindigkeit Ihrer Hardware oder des virtuellen 
    Computers kann der Prozess einige Sekunden bis zu mehreren Minuten dauern, 
    ohne visuelle Rückmeldung nach Eingabe des root-Passworts.

    Bitte haben Sie Geduld und vermeiden Sie es, die Operation abzubrechen; 
    warten Sie einfach darauf, dass das Linux-Prompt wieder erscheint.

???+ note

    Zabbix scheint es zu mögen, die Positionen der Skripte zur Füllung der DB
    in jeder Version oder sogar innerhalb von Versionen zu ändern. Wenn Sie einen 
    Fehler erhalten, schauen Sie sich die Zabbix-Dokumentation an; es besteht eine 
    gute Chance, dass einige Positionen geändert wurden.

Nachdem das Importieren des Zabbix-Schemas abgeschlossen ist, sollten Sie den
`log_bin_trust_function_creators` globalen Parameter nicht mehr benötigen. Es ist eine gute 
Praxis, ihn aus Sicherheitsgründen zu entfernen.

Um den globalen Parameter wieder auf 0 zurückzusetzen, verwenden Sie den folgenden 
Befehl im MySQL/MariaDB-Shell:

!!! info "Deaktivieren Sie die Funktion log_bin_trust erneut"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```


Dieser Befehl deaktiviert die Einstellung und sorgt dafür, dass sich das 
Sicherheitsniveau der Server robust hält.

Mit dieser Installation von MariaDB ist unsere Arbeit abgeschlossen. Sie können
jetzt mit [Vorbereitung des Zabbix-Servers](preparation.md) fortfahren.

---

## Schlussfolgerung

Mit erfolgreicher Installation und Konfiguration von MariaDB als Datenbank-
Backend für Zabbix haben Sie eine robuste Grundlage für Ihre Überwachungs-Lösung.
Wir haben die Installation von MariaDB aus bereitgestellten Paketen der 
Anbieter sowie offiziellen Repositories abgedeckt, die Sicherheit der Datenbank,
die Erstellung der notwendigen Zabbix-Datenbank und Benutzer sowie das Füllen
der Datenbank mit den erforderlichen Schema und Initialdaten.

Ihr Zabbix-Umfeld ist nun bereit für die nächsten Stufen der Einrichtung und 
Konfiguration.

---

## Fragen

1. Welche Version von MariaDB sollte ich installieren, um Kompatibilität und 
Stabilität zu gewährleisten?
2. Welcher Port verwendet meine DB?
3. Welche Datenbank-Benutzer habe ich erstellt und warum?

---

## Nützliche URLs

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)