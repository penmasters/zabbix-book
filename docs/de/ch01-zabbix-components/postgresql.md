---
description: |
    Diese Abschnitt aus dem Buch "The Zabbix Book" mit dem Titel "PostgreSQL-Datenbank installieren"
    führt Sie durch den Prozess der Installation von PostgreSQL als alternative Datenbankspeicher für Zabbix.
    Es behandelt die Installationsmethoden über OS-Vendor-Provided-Pakete oder offizielle PostgreSQL-Repositorien,
    mit spezifischen Befehlen für Red Hat, SUSE und Ubuntu Systeme. Der Abschnitt enthält auch Schritte zur
    Startung und Sicherstellung des PostgreSQL-Servers, Erstellen der Zabbix-Datenbank und Benutzer sowie Konfigurieren
    von Feuerwaldrules falls erforderlich.
tags: [beginner]
---

# PostgreSQL-Datenbank installieren

Als Alternative zu MariaDB/MySQL können Sie die Wahl treffen, PostgreSQL als Datenbankspeicher für Zabbix zu verwenden.
Ähnlich wie bei MariaDB kann PostgreSQL über OS-Vendor-Provided-Pakete oder offizielle PostgreSQL-Repositorien installiert werden.

Wenn Sie bereits in einem früheren Abschnitt MariaDB installiert haben, können Sie diesen Abschnitt überspringen.

Bis zum Zeitpunkt der Schreibweise unterstützt Zabbix PostgreSQL 13-18. Überprüfen Sie die Zabbix-Dokumentation
für eine aktuelle Liste unterstützter Versionen für Ihre Zabbix-Version. Normalerweise ist es eine gute Idee, die neueste unterstützte Version von Zabbix zu verwenden.

???+ tip "TimescaleDB-Erweiterung"

    Zabbix unterstützt auch die Erweiterung TimescaleDB, aber aufgrund ihrer fortgeschrittenen Natur,
    behandeln wir sie in diesem Kapitel nicht. Siehe [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    für detaillierte Anweisungen zu diesem Thema.

    Beachten Sie, dass wenn Sie die von Timescale bereitgestellten TimescaleDB RPM-Pakete verwenden möchten,
    müssen Sie PostgreSQL aus den offiziellen PostgreSQL-Repositorien installieren anstatt über OS-Vendor-Provided-Pakete.
    Wenn Sie sich für die Installation von PostgreSQL über OS-Vendor-Provided-Pakete entscheiden,
    müssen Sie das TimescaleDB-Erweiterungspaket aus der Quelle kompilieren und installieren.

    Extra Hinweis: TimescaleDB bietet keine Pakete für SUSE Linux Enterprise Server (SLES) oder openSUSE Leap.
    Stattdessen stellt Suse die TimescaleDB-Erweiterung in ihren eigenen Repositories zur Verfügung. Aber dafür müssen Sie
    PostgreSQL aus den OS-Vendor-Provided-Paketen installieren anstatt von den offiziellen PostgreSQL-Repositorien.

---

## PostgreSQL Server und Client über OS-Vendor-Provided-Pakete installieren

Um den Standard-Distributionen-PostgreSQL-Server zu installieren, führen Sie die folgenden Befehle aus:

!!! info "Installieren des Postgres-Servers"

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


Dieser Befehl lädt und installiert sowohl die Server- als auch die Client-Pakete, sodass Sie Ihre PostgreSQL-Datenbank einrichten,
konfigurieren und interagieren können.

!!! warning "Datenbankinitialisierung auf Red Hat erforderlich"

    Aufgrund von Richtlinien für Red-Hat-Familie-Verteilungen initialisiert der PostgreSQL-Service
    keine leere Datenbank, die für den Betrieb von PostgreSQL erforderlich ist.
    Daher müssen wir bei Red Hat eine leere Datenbank vor dem Fortfahren initialisieren:

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```


    Auf SUSE und Ubuntu wird durch das OS bereitgestellte Systemd-Service automatisch eine leere Datenbank beim ersten Start initialisieren.

Nach der Installation können Sie mit der [_PostgreSQL-Datenbank starten_](#starting-the-postgresql-database) Abschnitt fortfahren.

---

## PostgreSQL aus offiziellen PostgreSQL-Repositorien installieren

Wenn Sie lieber PostgreSQL aus den offiziellen PostgreSQL-Repositorien als von OS-Vendor-Provided-Paketen installieren möchten,
ist der erste Schritt, das PostgreSQL-Repositorium Ihrem System hinzuzufügen.

---

### PostgreSQL-Repositorium hinzufügen

Setzen Sie das PostgreSQL-Repositorium mit folgenden Befehlen ein:

Weitere Informationen finden Sie unter [https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/).

!!! info "PostgreSQL-Repositorium hinzufügen"

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
    
        Da die offiziellen PostgreSQL-Pakete speziell für den Einsatz auf 
        SUSE Linux Enterprise Server (SLES) erstellt wurden, erhalten Sie einen Fehler,
        wenn Sie versuchen, das Repository auf openSUSE Leap zu installieren. Wir können
        dieses Problem jedoch sicher ignorieren, indem wir "das Paket durch Ignorieren einiger seiner Abhängigkeiten brechen" wählen,
        solange Ihre openSUSE-Version mit der SLES-Version übereinstimmt:

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```


    ???+ note "Suse Linux Enterprise Server"

        Auf SUSE Linux Enterprise Server (SLES) stellen Sie sicher, dass Sie abonniert sind für das
        "SUSE Package Hub extension" Repository, um notwendige Abhängigkeits-Pakete zu erhalten,
        die für die offizielle PostgreSQL-Installation erforderlich sind. Auf SLES 15
        benötigen Sie auch das "Desktop Applications Module":

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

### PostgreSQL Server und Client installieren

Mit den konfigurierten PostgreSQL-Repositorien sind Sie nun bereit, die PostgreSQL-Server- und -Client-Pakete zu installieren.
Dies bietet Ihnen die notwendigen Komponenten zum Betrieb und Verwalten Ihrer Datenbank.

!!! info "PostgreSQL aus offiziellen Repositories installieren"

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


Dieser Befehl lädt und installiert sowohl die Server- als auch die Client-Pakete, sodass Sie Ihre PostgreSQL-Datenbank einrichten,
konfigurieren und interagieren können.

Bevor wir den PostgreSQL-Server starten können, müssen wir eine neue leere Datenbank initialisieren:

!!! info "Leere PostgreSQL-Datenbank initialisieren"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```


Nach der Installation können Sie mit dem [PostgreSQL-Datenbank starten](#starting-the-postgresql-database) Abschnitt fortfahren.

---

## PostgreSQL-Datenbank starten

Nun, da PostgreSQL installiert ist, müssen wir den Dienst so konfigurieren, dass er beim Systemstart automatisch gestartet wird.
Verwenden Sie folgenden Befehl, um dies zu erreichen:

!!! info "PostgreSQL-Dienst aktivieren und starten"

    für OS-Vendor-Provided-Pakete
    ```bash
    sudo systemctl enable postgresql --now
    ```


    für offizielle PostgreSQL-Pakete:
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```


Dieser Befehl aktiviert und startet den PostgreSQL-Dienst.
Mit dem Dienst nun laufend können Sie die erfolgreiche Installation überprüfen, indem Sie die Version von PostgreSQL mit folgendem Befehl abfragen:

!!! info "PostgreSQL-Version prüfen"

    ```bash
    psql -V
    ```


Die erwartete Ausgabe sollte wie folgt aussehen:

???+ example "Beispiel für PostgreSQL-Version"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```


Um sicherzustellen, dass der PostgreSQL-Dienst ordnungsgemäß läuft, können Sie seine Status mit dem folgenden Befehl prüfen:

!!! info "PostgreSQL-Status abfragen"

    für OS-Vendor-Provided-Pakete
    ```bash
    sudo systemctl status postgresql
    ```


    für offizielle PostgreSQL-Pakete:
    ```bash
    sudo systemctl status postgresql-17
    ```


Sie sollten eine Ausgabe ähnlich wie folgende sehen, die darauf hinweist, dass der PostgreSQL-Dienst aktiv und läuft:

???+ example "Beispiel für PostgreSQL-Dienst-Status"

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


Dies bestätigt, dass Ihr PostgreSQL-Server bereit ist für weitere Konfiguration.

---

## PostgreSQL-Datenbank sichern

PostgreSQL behandelt Zugriffsberechtigungen anders als MySQL und MariaDB.
PostgreSQL verlässt sich auf eine Datei namens `pg_hba.conf`, um zu bestimmen, wer die Datenbank
zugreifen kann, von welchen Hosts aus und welche Verschlüsselungsmethode für die Authentifizierung erlaubt ist.

???+ note "Über pg_hba.conf"

    Die Client-Authentifizierung in PostgreSQL wird durch die `pg_hba.conf`
    Datei konfiguriert, wobei "HBA" für Host-Based Authentication steht. Diese Datei bestimmt,
    welche Benutzer die Datenbank zugreifen können, von welchen Hosts aus und wie sie authentifiziert werden.
    Für weitere Details können Sie sich das offizielle PostgreSQL-Dokumentation ansehen."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Fügen Sie die folgenden Zeilen hinzu, die Reihenfolge hier ist wichtig.

!!! info "Die pg_hba-Datei bearbeiten"

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


!!! warning "Standort der pg_hba-Datei"

    Wenn Sie die `pg_hba.conf` und `postgres.conf` Dateien nicht im oben erwähnten
    Standort finden, können Sie PostgreSQL selbst nach dem Standort fragen, indem Sie diesen Befehl verwenden (vorausgesetzt,
    dass PostgreSQL aktuell läuft):

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```


Die resultierende pg_hba-Datei sollte wie folgt aussehen:

!!! example "Beispiel für pg_hba"

    ```
    # "local" is for Unix domain socket connections only
    local    zabbix     zabbix-srv                                 scram-sha-256
    local    all        all                                        peer
    # IPv4 local connections
    host     zabbix         zabbix-srv      <ip from zabbix server/24>     scram-sha-256
    host     zabbix         zabbix-web      <ip from zabbix frontend/24>   scram-sha-256
    host     all            all             127.0.0.1/32                   scram-sha-256
    # IPv6 local connections:
    host    zabbix          zabbix-srv      ::1/128                 scram-sha-256
    host    zabbix          zabbix-web      ::1/128                 scram-sha-256
    host    all             all             ::1/128                 ident
    ```


!!! warning "Bewahren Sie die Reihenfolge der Einträge bei"

    Die Reihenfolge der Einträge in der `pg_hba.conf` Datei ist entscheidend, da PostgreSQL
    diese Regeln sequentiell verarbeitet. Stellen Sie sicher, dass die spezifischen Regeln für die
    `zabbix-srv` und `zabbix-web` Benutzer vor allgemeineren Regeln wie der Standard-`all`-Benutzer-Regel platzen,
    die diese potenziell überschreiben könnten.

Nachdem Sie die `pg_hba.conf` Datei geändert haben, vergessen Sie nicht den PostgreSQL-Dienst zu neustarten, damit die neuen Einstellungen angewendet werden.
Bevor wir den Dienst neustarten, bearbeiten wir auch die Datei `postgresql.conf`
und erlauben unserer Datenbank, auf unserem Netzwerkinterface eingehende Verbindungen vom Zabbix-Server anzunehmen.
PostgreSQL akzeptiert standardmäßig nur Verbindungen über einen Unix-Socket.

!!! info "Die postgresql.conf-Datei bearbeiten"

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


Suchen Sie nach der folgenden Zeile:

!!! info ""

    ```ini
    #listen_addresses = 'localhost'
    ```


und ersetzen Sie sie durch:

!!! info ""

    ```ini
    listen_addresses = '*'
    ```


???+ note

    Dies ermöglicht PostgreSQL, Verbindungen von jedem Netzwerkinterface anzunehmen,
    nicht nur vom lokalen Computer. In der Produktion ist es wahrscheinlich eine gute Idee, diejenigen zu begrenzen,
    die auf die DB zugreifen können.

Nachdem Sie diese Änderung vorgenommen haben, starten Sie den PostgreSQL-Dienst neu, um die neuen Einstellungen anzuwenden:

!!! info "Den DB-Server neustarten"

    für OS-Vendor-Provided-Pakete
    ``` bash
    sudo systemctl restart postgresql
    ```


    für offizielle Pakete
    ```bash
    sudo systemctl restart postgresql-17
    ```


???+ tip

    Wenn der Dienst beim Neustart fehlschlägt, überprüfen Sie die `pg_hba.conf` Datei auf Syntaxfehler,
    da inkorrekte Einträge hier PostgreSQL davon abhalten könnten zu starten.

---

## Erstellen der Zabbix-Datenbank-Instanz

Mit den notwendigen Paketen installiert, sind Sie nun bereit, die Zabbix-Datenbank und Benutzer für Server und Frontend zu erstellen.Die PostgreSQL-Pakete erstellen automatisch einen Standardbenutzer `postgres` während der Installation, der Administratorrechte auf dem PostgreSQL-Instanz hat.
Um die Datenbank zu verwalten, müssen Sie Befehle als Benutzer `postgres` ausführen.

Erstelle zunächst den Zabbix-Server-Datenbankbenutzer (auch als "Rolle" in PostgreSQL bezeichnet):

!!! info "Server-Benutzer erstellen"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```


Im Anschluss daran erstellst du den Frontend-Benutzer, der zum Verbinden mit der Datenbank verwendet wird:

!!! info "Frontend-Benutzer erstellen"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```


Nachdem die Benutzer erstellt wurden, ist das nächste Schritt die Erstellung der Zabbix-Datenbank.
Führe den folgenden Befehl aus, um die Datenbank `zabbix` zu erstellen und den Besitzer auf
`zabbix-srv` einzurichten sowie das Zeichensatz-Encoding auf `Unicode` einzustellen, wie von Zabbix erforderlich:

!!! info "Datenbank erstellen"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```


???+ note "Was ist diese 'template0'?"

    In PostgreSQL ist `template0` eine Standard-Datenbank-Vorlage, die als saubere Kopie des
    Datenbanksystems dient. Wenn eine neue Datenbank mit `template0` erstellt wird,
    stellt sie sicher, dass die neue Datenbank ohne vorhandene Objekte oder Konfigurationen beginnt.
    Dies ist besonders nützlich, wenn man eine Datenbank mit spezifischen Einstellungen oder Erweiterungen
    erstellen möchte, ohne unerwünschte Elemente von anderen Vorlagen zu erben.

Nachdem die Datenbank erstellt wurde, solltest du die Verbindung überprüfen und sicherstellen,
dass der korrekte Benutzer angemeldet ist. Dazu logge dich in die zabbix-Datenbank mit
dem `zabbix-srv`-Benutzer ein:

!!! info "Als Benutzer zabbix-srv anmelden"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```


Nach der Anmeldung führe den folgenden SQL-Abfrage aus, um zu bestätigen, dass sowohl die `session_user`
als auch die `current_user` auf `zabbix-srv` eingestellt sind:

!!! info ""

    ```psql
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```


Wenn das Ergebnis übereinstimmt, bist du erfolgreich mit dem korrekten Benutzer in der Datenbank verbunden.

PostgreSQL unterscheidet sich von MySQL oder MariaDB in mehreren Aspekten,
und einer der Schlüsselmerkmale ist die Verwendung von Schemata. Im Gegensatz zu MySQL,
wo Datenbanken eher autonom sind, bietet das Schema-System von PostgreSQL eine strukturierte,
mehrzweckige Umgebung innerhalb einer einzelnen Datenbank.

Schemata dienen als logische Container innerhalb einer Datenbank und ermöglichen es mehreren Benutzern oder
Anwendungen, Daten unabhängig voneinander zu verwalten ohne Konflikte. Diese Funktion ist besonders wertvoll in Umgebungen,
wo mehrere Benutzer oder Anwendungen gleichzeitig mit der gleichen Datenbankserver interagieren müssen.
Jeder Benutzer oder jede Anwendung kann sein eigenes Schema haben, was eine unabsichtliche Beeinflussung durch andere verhindert.

???+ note

    PostgreSQL kommt mit einem Standard-Schema, normalerweise als `public` bezeichnet, aber im Allgemeinen
    ist es eine gute Praxis, benutzerdefinierte Schemata zu erstellen, um Datenbankobjekte besser zu organisieren und zu trennen,
    insbesondere in komplexen oder mehrbenutzerspezifischen Umgebungen.

    Für detailliertere Informationen empfehle ich die Durchsicht der ausführlichen Anleitung unter
    dieser URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    welche die Vorteile und Einsatzmöglichkeiten für Schemata in PostgreSQL erklärt.

Um den Initialen Datenbankaufbau für Zabbix abzuschließen, müssen wir Schema-Berechtigungen
für sowohl den `zabbix-srv` als auch den `zabbix-web`-Benutzer konfigurieren.

Erstelle zunächst ein benutzerdefiniertes Schema mit dem Namen `zabbix_server` und weise Besitz dem
`zabbix-srv`-Benutzer zu:

!!! info "Schema erstellen"

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```


Im Anschluss daran setze den `search path` auf `zabbix_server` Schema, damit es das Standard-Schema für die aktuelle Sitzung ist:

!!! info "Suchpfad setzen"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


???+ tip

    Wenn du nicht möchtest, dass der Suchpfad manuell jedes Mal beim Anmelden als
    `zabbix-srv`-Benutzer gesetzt wird, kannst du PostgreSQL so konfigurieren, dass es automatisch den gewünschten
    Suchpfad verwendet. Führe den folgenden SQL-Befehl aus, um den Standard-Suchpfad für
    das `zabbix-srv`-Rolle zu setzen:

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```


    Dieser Befehl stellt sicher, dass jedes Mal, wenn der `zabbix-srv`-Benutzer sich mit der
    Datenbank verbindet, der `search_path` automatisch auf `zabbix_server` gesetzt wird.


Um die Schema-Einstellungen zu bestätigen, kannst du die vorhandenen Schemata auflisten:

!!! example "Schemazeugang überprüfen"

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```


In diesem Punkt hat der `zabbix-srv`-Benutzer vollständigen Zugriff auf das Schema, aber der `zabbix-web`
Benutzer benötigt noch angemessene Berechtigungen, um sich anzumelden und mit der Datenbank zu interagieren.
Erstelle zunächst die Berechtigung `USAGE` auf das Schema, damit `zabbix-web` sich anmelden kann:

!!! info "Berechtigungen für den Benutzer zabbix-web erteilen"

    ```psql
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```


Nun hat der `zabbix-web`-Benutzer angemessenen Zugriff auf das Schema, während die Sicherheit durch
die Begrenzung der Berechtigungen auf wesentliche Operationen gewährleistet wird.

Wenn du bereit bist, kannst du die Datenbank verlassen und in dein Linux-Shell zurückkehren.

!!! info "Datenbankschale beenden"

    ```psql
    zabbix=> \q
    ```


An diesem Punkt ist deine Zabbix-Datenbank bereit, aber bevor sie tatsächlich von
Zabbix verwendet werden kann, müssen wir die Datenbank mit den notwendigen Tabellen und Initialdaten füllen,
was im nächsten Abschnitt behandelt wird, wenn wir den Zabbix-Server installieren.

Wenn du beabsichtigst, den Zabbix-Server auf einem anderen Computer als dem zu installieren, der die
Datenbank hostet, musst du das Host-Firewall für eingehende Verbindungen zur Datenbankschicht öffnen. PostgreSQL hört standardmäßig auf Port 5432.

!!! info "Firewallregeln hinzufügen"

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

## Fülle die Zabbix-Datenbank

Während der Installation der Datenbankschicht haben wir die notwendigen Benutzer, Datenbank und Schema für Zabbix erstellt,
allerdings erwartet Zabbix bestimmte Tabellen, Schemata, Bilder und andere Elemente in der Datenbank.
Um die Datenbank korrekt einzurichten, müssen wir sie mit den erforderlichen Schemen füllen.

Zuerst musst du die Zabbix SQL-Skripte installieren, welche die notwendigen Import-Skripte für die Datenbank enthalten.

!!! info "SQL-Skripte installieren"

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


Im Anschluss daran musst du das Datenbankschema vorbereiten: Entpacke die notwendigen Schema-Dateien mit dem folgenden Befehl:

!!! info "Entpacke DB-Patch"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


???+ note

    Zabbix scheint die Orte der Skripte, welche die DB füllen, in jeder Version zu ändern oder sogar innerhalb von Versionen. Wenn du einen Fehler erhältst, schau dir die
    Zabbix-Dokumentation an, es besteht eine gute Chance, dass einige Orte geändert wurden.

Dies wird das Datenbankschema extrahieren, welches für den Zabbix-Server erforderlich ist.

Nun werden wir den SQL-Datei ausführen, um die Datenbank zu füllen. Öffne ein `psql` Shell:

!!! info "Öffne psql-Schale"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```


???+ warning "Stelle sicher, dass der korrekte Suchpfad gesetzt ist"

    Stelle sicher, dass du die vorherigen Schritte wie in [Erstellen des Zabbix-Datenbank-Instanz mit PostgreSQL](postgresql.md#creating-the-zabbix-database-instance)
    sorgfältig durchgeführt hast, um den korrekten `search_path` zu setzen.

    Wenn du keinen Standard-`search_path` für den `zabbix-srv`-Benutzer gesetzt hast,
    stelle es manuell in der aktuellen Sitzung vor dem Fortfahren sicher:
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


Lade das DB-Schema in die Datenbank mit folgenden Befehlen hoch:

!!! info "DB-Schema im Schema zabbix hochladen"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```


???+ warning

    Abhängig von deinem Hardware- oder VM-Leistung, kann dieser Prozess einige Sekunden bis zu mehreren Minuten dauern. Bitte sei geduldig und vermeide das Beenden der Operation.

Beobachte den Fortschritt während die Skript läuft. Du wirst eine Ausgabe ähnlich wie folgt sehen:

!!! example "Ausgabebispiel"

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


Wenn das Skript abgeschlossen ist und du wieder zum `zabbix=>`-Prompt zurückkehrst, sollte die Datenbank
mit allen erforderlichen Tabellen, Schemata, Bildern und anderen Elementen erfolgreich gefüllt sein.

Allerdings kann `zabbix-web` noch keine Operationen auf den Tabellen oder Sequenzen durchführen.
Um grundlegende Dateneingriffe ohne zu viele Berechtigungen zu gewähren, erteile die folgenden Rechte:

- Für Tabellen: SELECT, INSERT, UPDATE und DELETE.
- Für Sequenzen: SELECT und UPDATE.

!!! info "Berechtigungen auf das Schema für den Benutzer zabbix-web erteilen"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```


Überprüfe ob die Rechte korrekt auf dem Schema sind:

!!! example "Beispiel-Schemarechte"

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

    Wenn du während des SQL-Imports den folgenden Fehler erhältst:
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: kein
        Schema wurde ausgewählt, um in zu erstellen` It indicates that the `Suchpfad` Einstellung
    könnte nicht korrekt angewendet worden sein. Diese Einstellung ist wichtig, da sie das Schema bestimmt,
    wo Tabellen und andere Objekte erstellt werden sollen. Durch die korrekten Setzung des Suchpfads,
    stellst du sicher, dass der SQL-Skript Tabellen und andere Objekte im gewünschten Schema erstellt.

Um zu sichern, dass die Zabbix-Tabellen erfolgreich erstellt wurden und die richtigen Berechtigungen haben,
kannst du die Tabellistung und deren Besitz überprüfen mit dem `psql`-Befehl:

- Liste der Tabellen: Verwende den folgenden Befehl, um alle Tabellen im `zabbix_server`-Schema aufzulisten:

!!! info "Tabellen auflisten"

    ```psql
    zabbix=# \dt
    ```


Du solltest eine Liste von Tabellen mit ihrem Schema, Namen, Typ und Besitzer sehen.
Beispiel:

???+ example "Liste der Tabellen mit Beziehungen"

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


- Überprüfe Berechtigungen: Bestätige, dass der zabbix-srv-Benutzer die Tabellen besitzt und die notwendigen Berechtigungen hat. Du kannst Berechtigungen für spezifische Tabellen mit dem \dp-Befehl überprüfen:

!!! info "Überprüfe Tabellberechtigungen"

    ```psql
    zabbix=> \dp zabbix_server.*
    ```


???+ example "Beispiel-Ausgabe"

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


Dies wird die Zugriffsberechtigungen für alle Tabellen im `zabbix_server`
Schema anzeigen. Stelle sicher, dass `zabbix-srv` die erforderlichen Berechtigungen hat.Wenn alles korrekt aussieht und die Tabellen ordnungsgemäß erstellt wurden, sowie der `zabbix-srv`
Benutzer die entsprechenden Berechtigungen hat, können Sie ggf. mit den GRANT-Befehlen notwendige Berechtigungen anpassen.

Dies schließt unsere Installation der PostgreSQL-Datenbank ab.

---

## Fazit

Mit der Installation und Konfiguration von PostgreSQL als Datenbanksystem für Zabbix haben Sie nun ein leistungsstarkes und effizientes Datenbanksystem, das bereitsteht für Ihre Überwachungsaufgaben. Wir haben die Installation von PostgreSQL sowohl aus vendedienstlich bereitgestellten Paketen als auch aus offiziellen Repositorien behandelt, die Sicherheit der Datenbank, die Erstellung der notwendigen Zabbix-Datenbank und Benutzer sowie das Füllen der Datenbank mit den erforderlichen Schemata und Initialdaten.

Ihr Zabbix-Umfeld ist nun bereit für die nächsten Schritte in Richtung Einrichtung und Konfiguration.

---

## Fragen

1. Welche Version von PostgreSQL sollte ich installieren, um Kompatibilität und Stabilität zu gewährleisten?
2. Auf welchem Port verwendet meine DB eine Verbindung?
3. Welche Datenbankbenutzer habe ich erstellt und warum?

---

## Nützliche URLs

- [https://yum.postgresql.org](ttps://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)