---
description: |
    Diese Abschnitt aus dem Buch "The Zabbix Book" mit dem Titel "Das Frontend installieren" bietet
    Schritt-für-Schritt-Anweisungen zur Installation des Zabbix-Frontends mit NGINX auf verschiedenen Linux-Distributionen. Es behandelt die Installation der notwendigen Pakete,
    die Konfiguration von SELinux und Systemd für PHP-FPM, sowie die Anpassung der NGINX-Konfiguration, um das Zabbix-Frontend über Port 80 zu servieren. Darüber hinaus führt es Benutzer durch die erste Einstellung des Zabbix-Frontends, einschließlich
    der Datenbankverbindungs-Einrichtung und grundlegender Einstellungen wie Instanzname,
    Zeitzone und Zeitformat.
tags: [beginner]
---

# Das Frontend installieren

Bevor Sie das Zabbix-Frontend konfigurieren, stellen Sie sicher, dass das System die Anforderungen erfüllt
und entsprechend vorbereitet ist, wie im vorherigen Kapitel beschrieben: [_Getting started_](../ch00-getting-started/Requirements.md). Dieser Server kann der gleiche sein, auf dem zuvor Zabbix-Server-Pakete installiert wurden, oder es kann sich um einen separaten
Rechner handeln.

Führen Sie alle nachfolgenden Schritte auf dem für das Frontend vorgesehenen Server aus.

---

## Das Frontend mit NGINX installieren

!!! info "Installiere Frontend-Pakete"

    Red Hat
    ```bash
    # List all available php modules and active php-8.2
    dnf module list php -y
    dnf module enable php:8.2
    # When using MySQL/MariaDB
    dnf install zabbix-nginx-conf zabbix-web-mysql
    # or when using PostgreSQL
    dnf install zabbix-nginx-conf zabbix-web-pgsql
    ```

    SUSE
    ```bash
    # When using MySQL/MariaDB
    zypper install zabbix-nginx-conf zabbix-web-mysql php8-openssl php8-xmlreader php8-xmlwriter
    # or when using PostgreSQL
    zypper install zabbix-nginx-conf zabbix-web-pgsql php8-openssl php8-xmlreader php8-xmlwriter
    ```

    ???+ note "Suse Linux Enterprise Server"

        Auf SUSE Linux Enterprise Server (SLES) stellen Sie sicher, dass Sie abonniert sind für den
        "SUSE Linux Enterprise Module Web and Scripting" Repository, um auf die notwendigen PHP 8-Pakete zuzugreifen,
        die für die Installation des Zabbix-Frontends erforderlich sind:
        (für SLES-Versionen < 16 lautet der Befehl "`SUSEConnect`" anstelle von "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```

        Die tatsächliche URL für das Web-Scripting-Modul kann je nach spezifischem Service-Paket unterschiedlich sein. Verwenden Sie den folgenden Befehl, um die richtige zu bestimmen.
        ```bash
        suseconnect --list-extensions
        ```


    Ubuntu
    ```bash
    # When using MySQL/MariaDB
    sudo apt install zabbix-frontend-php php8.3-mysql zabbix-nginx-conf
    # or when using PostgreSQL
    sudo apt install zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```


Dieser Befehl installiert die Frontend-Pakete sowie die erforderlichen Abhängigkeiten für NGINX.

Ab SUSE 16 ist SELinux nun das Standard-Sicherheitsmodul anstelle von AppArmor.
Standardmäßig erlaubt SELinux auf SUSE PHP-FPM nicht,
- Ausführungs-Memorystecker zu mappen, die für die JIT-Kompilierung von PHP erforderlich sind,
- eine Verbindung zum Zabbix-Server herzustellen oder
- eine Verbindung zur Datenbank über TCP.
Wir müssen SELinux dazu auffordern, dies zuzulassen:

!!! info "SELinux: Erlaube PHP-FPM, Ausführungs-Memorystecker zu mappen"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```

???+ tip

    Um Probleme mit SELinux zu beheben, wird empfohlen, das Paket `setroubleshoot` zu installieren,
    welches jede SELinux-Absage im System-Protokoll protokolliert und Vorschläge zur Behebung liefert.

Abhängig von den Standard-Einstellungen Ihrer Linux-Distribution ist PHP-FPM möglicherweise standardmäßig nicht
erlaubt, durch Systemd in das Verzeichnis zu schreiben `/etc/zabbix/web`, welches für die Einrichtung des Zabbix-Frontends erforderlich ist. Um dies zuzulassen, müssen wir eine Drop-In-Datei erstellen:

!!! info "Systemd: Erlaube PHP-FPM das Schreiben in /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```


    Dies öffnet einen Editor zur Erstellung einer Drop-In-Datei `/etc/systemd/system/php-fpm.service.d/override.conf`
    die die bestehende Dienstdatei überschreibt oder erweitert.

    Fügen Sie die folgenden Zeilen in die Datei ein:

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```


    Schließen Sie dann den Editor und laden Sie das Systemd-Konfiguration neu:

    ```bash
    systemctl daemon-reload
    ```


???+ note "Wie hält Systemd PHP-FPM vom Schreiben in /etc/zabbix/web ab?"

    Auf vielen modernen Linux-Distributionen verwendet Systemd eine Sicherheitsfunktion namens
    Sandboxing, um die Fähigkeiten von Diensten zu begrenzen. Dies geschieht, um durch Einschränkung der Zugriffsmöglichkeiten auf nur notwendige Ressourcen die Sicherheit zu erhöhen.
    Standardmäßig kann PHP-FPM möglicherweise von Systemd verhindert werden, in bestimmten Verzeichnissen
    zu schreiben, einschließlich `/etc/zabbix/web`, um potenzielle Sicherheitslücken zu vermeiden.
    Dies wird durch die Systemd-Direktiven `ProtectSystem` und `ReadWritePaths` kontrolliert,
    welche den Dateisystemzugriff von Diensten steuern.

???+ tip

    Normalerweise ist der Schreibzugriff auf `/etc/zabbix/web` nur während der ersten Einrichtung
    des Zabbix-Frontends erforderlich. Nach Abschluss der Einrichtung können Sie die Drop-In-Datei wieder entfernen, um die Sicherheit Ihres Systems weiter zu erhöhen.

Als Erstes müssen wir die NGINX-Konfigurationsdatei anpassen, damit wir nicht
die Standardkonfiguration verwenden und das Zabbix-Frontend über Port 80 servieren können.

!!! info "Bearbeite nginx-Config für Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

Wenn Sie auf Ubuntu sind, müssen Sie `nginx.conf` nicht bearbeiten, führen Sie stattdessen `sudo unlink /etc/nginx/sites-enabled/default` aus

In dieser Konfigurationsdatei suchen Sie nach dem folgenden Block, der mit `server {` beginnt:

!!! example "Original-Config"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```

    ???+ tip

        Dieser Block kann je nach Ihrer Distribution und NGINX-Version unterschiedlich sein.


Dann kommentieren Sie die `listen` und `server_name`-Direktiven aus, um die Standardkonfiguration
des HTTP-Servers zu deaktivieren. Dies können Sie tun, indem Sie am Anfang jeder Zeile ein `#` hinzufügen,
wie im folgenden Beispiel gezeigt:

!!! example "Config nach der Bearbeitung"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```


Die Zabbix-Konfigurationsdatei muss nun angepasst werden, um die Standarddienste auf Port 80 zu übernehmen
wir haben gerade deaktiviert.
Öffnen Sie die folgende Datei zur Bearbeitung:

!!! info "Bearbeite Zabbix-Config für nginx"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```


Und ändern Sie die folgenden Zeilen:

!!! example "Original-Config"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```


Entfernen Sie das `#` vor den ersten beiden Zeilen und passen Sie sie an, um die korrekten
Port und Domain für Ihr Frontend zu verwenden.

???+ tip

    Falls Sie keine Domain haben können Sie `servername` mit `_` ersetzen
    wie im folgenden Beispiel gezeigt:

!!! example "Config nach der Bearbeitung"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```


Der Webserver und der PHP-FPM-Dienst sind nun bereit für die Aktivierung und den automatischen Start.
Führen Sie die folgenden Befehle aus, um sie zu aktivieren und sofort zu starten:

!!! info "Starte Frontend-Dienste neu"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```


    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```


Lassen Sie uns überprüfen, ob der Dienst ordnungsgemäß gestartet und für den automatischen Start konfiguriert ist,
damit er nach dem nächsten Neustart weiterläuft.

!!! info "Überprüfe, ob der Dienst läuft"

    ```bash
    sudo systemctl status nginx
    ```

???+ example "Beispielausgabe"

    ```shell-session
    localhost:~> sudo systemctl status nginx
    ● nginx.service - The nginx HTTP and reverse proxy server
          Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: disabled)
         Drop-In: /usr/lib/systemd/system/nginx.service.d
                  └─php-fpm.conf
          Active: active (running) since Mon 2023-11-20 11:42:18 CET; 30min ago
        Main PID: 1206 (nginx)
           Tasks: 2 (limit: 12344)
          Memory: 4.8M
             CPU: 38ms
          CGroup: /system.slice/nginx.service
                  ├─1206 "nginx: master process /usr/sbin/nginx"
                  └─1207 "nginx: worker process"

    Nov 20 11:42:18 zabbix-srv systemd[1]: Starting The nginx HTTP and reverse proxy server...
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: configuration file /etc/nginx/nginx.conf test is successful
    Nov 20 11:42:18 zabbix-srv systemd[1]: Started The nginx HTTP and reverse proxy server.
    ```


Mit einem ordnungsgemäß laufenden und für den automatischen Start konfigurierten Dienst ist der letzte vorbereitende Schritt die Anpassung des Firewalls, um eingehenden HTTP-Traffic zuzulassen. Führen Sie
die folgenden Befehle aus:

!!! info "Konfiguriere die Firewall"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```


Öffnen Sie Ihren Browser und gehen Sie zur URL oder IP-Adresse Ihres Frontends:

!!! info "Frontend-Konfiguration"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```


Wenn alles gut läuft, sollten Sie mit einer Zabbix-Willkommenseite begrüßt werden. Falls ein Fehler auftritt,
prüfen Sie die Konfiguration erneut oder schauen Sie sich den NGINX-Protokollen `/var/log/nginx/error.log` an oder führen Sie den folgenden Befehl aus:

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```


Dies sollte Ihnen helfen, die Fehler zu lokalisieren.

Beim Zugriff auf die entsprechende URL sollte eine Seite erscheinen, wie im Folgenden dargestellt:

![Übersicht](ch01.2-basic-installation-setup.png){ align=left }

_1.2 Zabbix
Willkommenseite_

!!! tip "Wähle das passende Englische Locale"

    Das `en_US`-locale verwendet amerikanisches Datumsformat und eine 12-Stunden-Uhr, während
    `en_GB` internationales Datumsformat und eine 24-Stunden-Uhr verwendet.

Das Zabbix-Frontend bietet eine begrenzte Auswahl an verfügbaren Lokalisierungen, wie im Folgenden dargestellt.

![Übersicht Sprachauswahl](ch01.3-basic-installation-setuplanguage.png){ align=left }

_1.3 Zabbix Sprachauswahl_

Was tun wir, wenn wir Chinesisch als Sprache installieren oder eine andere Sprache aus der Liste?
Führen Sie den folgenden Befehl aus, um eine Liste aller verfügbaren Lokalisierungen für Ihr Betriebssystem zu erhalten.

!!! info "Installiere Sprachpakete"

    Red Hat
    ```bash
    dnf list glibc-langpack-*
    ```


    SUSE
    ```bash
    localectl list-locales
    ```


    Ubuntu
    ```bash
    apt-cache search language-pack
    ```


Benutzer auf Ubuntu werden wahrscheinlich den Fehler `"Locale for language "en_US"
is not found on the web server."``" bemerken.

!!! info "Dies kann einfach mit folgenden Befehlen gelöst werden."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```


Dies gibt Ihnen eine Liste wie folgt:

???+ example "Beispielausgabe"

    Red Hat
    ```
    Installed Packages
    glibc-langpack-en.x86_64
    Available Packages
    glibc-langpack-aa.x86_64
    ---
    glibc-langpack-zu.x86_64
    ```


    SUSE
    ```
    C.UTF-8
    aa_DJ.UTF-8
    af_ZA.UTF-8
    an_ES.UTF-8
    ---
    zh_SG.UTF-8
    zh_TW.UTF-8
    zu_ZA.UTF-8
    ```


    Ubuntu
    ```
    language-pack-kab - translation updates for language Kabyle
    language-pack-kab-base - translations for language Kabyle
    language-pack-kn - translation updates for language Kannada
    language-pack-kn-base - translations for language Kannada
    ---
    language-pack-ko - translation updates for language Korean
    language-pack-ko-base - translations for language Korean
    language-pack-ku - translation updates for language Kurdish
    language-pack-ku-base - translations for language Kurdish
    language-pack-lt - translation updates for language Lithuanian
    ```


Suchen Sie nun nach Ihrer chinesischen Lokalisierung, um zu überprüfen, ob sie verfügbar ist. Wie Sie sehen können,
beginnt der Code mit zh.

!!! info "Suche nach Sprachpaket"

    Red Hat
    ```shell-session
    ~# dnf list glibc-langpack-* | grep zh
    glibc-langpack-zh.x86_64
    glibc-langpack-lzh.x86_64
    ```


    SUSE
    ```shell-session
    ~> localectl list-locales | grep zh
    zh_CN.UTF-8
    zh_HK.UTF-8
    zh_SG.UTF-8
    zh_TW.UTF-8
    ```


    Ubuntu
    ```bash
    sudo apt-cache search language-pack | grep -i zh
    ```


Auf RedHat und Ubuntu gibt der Befehl zwei Zeilen aus; jedoch, gegeben dem identifizierten Sprachcode,
'zh_CN', muss nur das erste Paket installiert werden.
auf SUSE entweder nur die Locale `C.UTF-8` und `en_US.UTF-8` sind zu installieren oder alle
verfügbaren Lokalisierungen, abhängig davon, ob das Paket `glibc-locale`
installiert ist oder nicht.

!!! info "Installiere die Locale-Pakete"

    Red Hat
    ```bash
    dnf install glibc-langpack-zh.x86_64
    sudo systemctl restart nginx php-fpm
    ```


    SUSE
    ```bash
    zypper install glibc-locale
    sudo systemctl restart nginx php-fpm
    ```


    Ubuntu
    ```bash
    sudo apt install language-pack-zh-hans
    sudo systemctl restart nginx php8.3-fpm
    ```


Wenn wir jetzt zurückkehren zu unserem Frontend, können wir die Chinesische Sprache auswählen,
nach einem Neuladen des Browsers.

![Sprache wählen](ch01.4-basic-installation-selectlanguage.png){ align=left }

_1.4 Zabbix Sprache
auswählen_

???+ note

    Wenn Ihre bevorzugte Sprache nicht im Zabbix-Frontend verfügbar ist, brauchen Sie sich keine Sorgen zu machen,
    dies bedeutet nur, dass die Übersetzung entweder unvollständig oder noch nicht verfügbar ist. Zabbix ist ein Open-Source-Projekt, das auf Gemeinschaftsbeiträge für Übersetzungen angewiesen ist.
    Sie können helfen, es zu verbessern, indem Sie Ihre eigenen Übersetzungen beisteuern.

Besuchen Sie die Übersetzungssite unter [https://translate.zabbix.com/](https://translate.zabbix.com/)
um bei den Übersetzungsefforts mitzuwirken. Sobald Ihre Übersetzung abgeschlossen und überprüft wurde,
wird sie in der nächsten Minor-Patch-Version von Zabbix enthalten sein.
Ihre Beiträge helfen, Zabbix für mehr Menschen zugänglicher zu machen und verbessern die allgemeine
Benutzererfahrung.Wenn Sie mit den verfügbaren Übersetzungen zufrieden sind, klicken Sie auf `Next`. Sie werden dann zu einer Seite weitergeleitet, um zu überprüfen, ob alle Voraussetzungen erfüllt sind. Wenn nicht alle Voraussetzungen erfüllt sind, beheben Sie diese Probleme zunächst. Bei Erfüllung aller Voraussetzungen können Sie fortfahren, indem Sie auf `Next` klicken.

![pre-requisites](ch01.5-basic-installation-prerequisites.png){ align=left }

_1.5 Zabbix
Voraussetzungen_

Auf der nächsten Seite konfigurieren Sie die Datenbankverbindungsparameter:

1. `Select the Database Type`: Wählen Sie entweder MySQL oder PostgreSQL, abhängig von Ihrer
   Umgebung.
2. `Enter the Database Host`: Geben Sie die IP-Adresse oder den DNS-Namen Ihres Datenbankservers an. Verwenden Sie Port 3306 für MariaDB/MySQL oder Port 5432 für PostgreSQL.
3. `Enter the Database Name`: Geben Sie den Namen Ihrer Datenbank an. In unserem Fall lautet dieser Name zabbix. Wenn Sie PostgreSQL verwenden, müssen Sie auch den Schemanamen angeben, der in unserem Fall zabbix_server ist.
4. `Enther the Database Schema`: Nur für Benutzer von PostgreSQL - Geben Sie den Schemanamen an,
   der für den Zabbix-Server erstellt wurde, der in unserem Fall `zabbix_server` lautet.
4. `Enter the Database User`: Geben Sie den Datenbankbenutzer ein, der für das Webfrontend
   erstellt wurde. Denken Sie daran, dass wir im einfachen Installationsleitfaden zwei Benutzer `zabbix-web` und `zabbix-srv` erstellt haben.
   Einen für das Frontend und einen anderen für unseren Zabbix-Server. Hier verwenden wir den Benutzer `zabbix-web`. Geben Sie das zugehörige Passwort für diesen Benutzer ein.

Stellen Sie sicher, dass die Option `Database TLS encryption` nicht ausgewählt ist, und klicken Sie dann auf
`Next step`, um fortzufahren.

![dbconnection](ch01.6-basic-installation-dbconnection.png){ align=left }

_1.6 Zabbix
Verbindungen_

Sie sind fast mit der Einrichtung fertig! Die letzten Schritte beinhalten:

1. `Assigning an Instance Name`: Geben Sie einen beschreibenden Namen für Ihre Zabbix-Instanz an.
2. `Selecting the Timezone`: Wählen Sie die Zeitzone, die Ihrer Standort oder
   Ihrer bevorzugten Zeitzone für das Zabbix-Interface entspricht.
3. `Setting the Default Time Format`: Wählen Sie den Standardzeitformat, das Sie bevorzugen.
4. **Verschlüsselte Verbindungen vom Webinterface**: Ich habe dieses Kästchen markiert, aber Sie sollten es nicht tun. Dieses Kästchen dient zur Verschlüsselung der Kommunikation zwischen Zabbix-Frontend und Ihrem Browser. Wir werden dies später behandeln.
   Sobald diese Einstellungen konfiguriert sind, können Sie die Einrichtung abschließen und gegebenenfalls weitere Konfigurationsanweisungen ausführen.

???+ note

    Es ist eine gute Praxis, Ihren Zabbix-Server auf die UTC-Zeitzone einzustellen, insbesondere
    wenn Sie Systeme in mehreren Zeitzonen verwalten. Die Verwendung von UTC hilft dabei, Konsistenz
    bei zeitabhängigen Aktionen und Ereignissen zu gewährleisten, da die Zeitzone des Servers oft für
    das Berechnen und Anzeigen von zeitbezogenen Informationen verwendet wird.

![settings](ch01.7-basic-installation-settings.png){ align=left }

_1.7 Zabbix
Übersicht_

Nachdem Sie auf `Next step` geklickt haben, werden Sie zu einer Seite weitergeleitet, die bestätigt, dass die
Konfiguration erfolgreich war. Klicken Sie auf `Finish`, um den Einrichtungsprozess abzuschließen.

![settings](ch01.8-basic-installation-final.png){ align=left }

_1.8 Zabbix
Installieren_

Wir sind nun bereit, uns anzumelden:

![settings](ch01.9-basic-installation-login.png)

_1.9 Zabbix
Anmelden_

- Anmeldung: Admin
- Passwort: zabbix

Dies schließt unser Thema zur Einrichtung des Zabbix-Servers ab. Wenn Sie sich für die Sicherung Ihres Frontends interessieren, empfehle ich Ihnen das Thema "Sicherung von Zabbix" zu lesen,
um weitere Richtlinien und Best Practices kennenzulernen.

???+ tip

    Wenn Sie Ihre Konfiguration nicht speichern können, stellen Sie sicher, dass Sie
    die Anweisungen für SELinux ausgeführt haben oder SELinux deaktiviert ist.
    Überprüfen Sie auch, ob das Verzeichnis `/etc/zabbix/web` schreibbar vom Webservice-Benutzer ist (normalerweise `wwwrun` oder `www`)

---

## Schlussfolgerung

Mit der Installation und Konfiguration des Zabbix-Frontends abgeschlossen,
haben Sie erfolgreich die Benutzeroberfläche für Ihr Zabbix-Monitoring-System eingerichtet.
Dieser Prozess umfasste das Installieren der notwendigen Pakete, die Konfiguration eines Web-Servers und
eines PHP-Engines, die Einrichtung der Datenbankverbindung und die Anpassung von Frontend-Einstellungen.

In diesem Stadium ist Ihre Zabbix-Instanz einsatzbereit und bietet eine Grundlage für
fortgeschrittene Überwachung und Warnungen. In den kommenden Kapiteln werden wir uns mit
der Feinabstimmung von Zabbix, der Optimierung der Leistung und der Erforschung von Schlüsselmerkmalen beschäftigen,
die es zu einem mächtigen Observabilitäts-Plattform machen.

Nun, da Ihr Zabbix-Umfeld läuft, lass uns auf die nächste Stufe gehen.

---

## Fragen

- Warum ist es notwendig, den Standardlisten 80 Block in der nginx.conf auszukommentieren
vor dem Bearbeiten von zabbix.conf?
- Welche Webserver und PHP-Prozessmanager-Dienste müssen aktiviert und
gestartet werden nachdem die Konfigurationen angepasst wurden?
- Warum sollten Sie während des Frontend-Datenbank-Einrichtungswizards den Zabbix-web Datenbankbenutzer eingeben anstatt zabbix-srv?
- Wenn Sie eine PostgreSQL-Datenbank in der Zabbix-Einrichtungsanleitung verbinden, welches
weitere Parameter müssen im Vergleich zu MySQL/MariaDB bereitgestellt werden?

---

## Nützliche URLs

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)