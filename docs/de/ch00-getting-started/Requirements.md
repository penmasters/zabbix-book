---
description: |
    Lernen Sie die Systemanforderungen von Zabbix kennen: unterstützte
    Betriebssysteme, Datenbanken, Hardware, Firewall-Ports und Zeitsynchronisation.
tags: [beginner]
---

# System Requirements

## Requirements

Zabbix stellt bestimmte Anforderungen an Hardware und Software, die sich im
Laufe der Zeit ändern können. Sie hängen außerdem von der Größe der Umgebung und
dem gewählten Software-Stack ab. Prüfen Sie vor dem Kauf von Hardware oder der
Installation einer Datenbankversion die aktuellen Anforderungen für die
vorgesehene Zabbix-Version in der Dokumentation:
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Wählen Sie in der Liste die richtige Zabbix-Version aus.

Für kleine oder Testumgebungen genügen meist 2 CPUs und 8 GB RAM. Die benötigten
Ressourcen hängen jedoch von der Größe der Umgebung, der Anzahl überwachter Items
und Trigger sowie der Aufbewahrungsdauer der Daten ab. Beginnen Sie in virtuellen
Umgebungen klein und erweitern Sie die Ressourcen bei Bedarf.

Sie können alle Komponenten (Zabbix-Server, Datenbank und Webserver) auf einem
System installieren oder auf mehrere Server verteilen. Notieren Sie die Daten:

| Component       | IP Address |
| --------------- | ---------- |
| Zabbix Server   |            |
| Database Server |            |
| Web Server      |            |

???+ tip

    Paketnamen von Zabbix verwenden häufig Bindestriche (`-`), etwa `zabbix-get`
    oder `zabbix-sender`. Die Binärdateien können dagegen Unterstriche (`_`)
    verwenden, etwa `zabbix_sender` oder `zabbix_server`. Dieser Unterschied kann
    besonders bei Paketen aus inoffiziellen Zabbix-Repositorys verwirrend sein.

    Prüfen Sie bei der Fehlersuche immer die Schreibweise des Binärnamens.

???+ warning

    Ab Zabbix 7.2 werden nur MySQL einschließlich seiner Forks und PostgreSQL als
    Backend-Datenbanken unterstützt. Oracle Database wurde zuletzt von Zabbix
    7.0 LTS offiziell unterstützt.

---

## Basic OS Configuration

Es gibt viele Betriebssysteme mit eigenen Vorteilen. Zabbix lässt sich auf
zahlreichen Plattformen installieren, doch eine Beschreibung für jedes System
wäre unpraktisch. Dieses Buch behandelt daher Ubuntu sowie Distributionen auf
Basis von Red Hat und SUSE.

Da nicht jeder über ein Abonnement für Red Hat Enterprise Linux (RHEL) oder SUSE
Linux Enterprise Server (SLES) verfügt, verwenden wir Rocky Linux beziehungsweise
openSUSE Leap als frei verfügbare Alternativen. Zum Einsatz kommen Rocky Linux
9.x, openSUSE Leap 16 und Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    Die Installation des Betriebssystems ist nicht Bestandteil dieses Buches.
    Eine Standard- oder Minimalinstallation genügt. Installieren Sie keine
    grafische Oberfläche oder Desktop-Umgebung, da diese auf Servern unnötig ist
    und Ressourcen verbraucht.

Nach der Installation sind einige grundlegende Einstellungen erforderlich.
Führen Sie die folgenden Schritte auf **allen** Servern aus, die Zabbix-Komponenten
hosten: Zabbix-Server, Datenbankserver und Webserver.

---

### System aktualisieren

Aktualisieren Sie das Betriebssystem vor der Installation von Zabbix oder anderer
Software. Aktuelle Patches und Sicherheitskorrekturen verbessern Stabilität und
Kompatibilität. Dies gilt auch für eine kürzlich installierte Umgebung.

Verwenden Sie den Befehl für Ihr Betriebssystem:

!!! info "System aktualisieren"

    Red Hat
    ```bash
    dnf update
    ```

    SUSE
    ```bash
    zypper refresh
    zypper update
    ```

    Ubuntu
    ```bash
    sudo apt update
    sudo apt upgrade
    ```
???+ note "Was sind apt, dnf und zypper?"

    - DNF ist der Paketmanager aktueller Red-Hat-basierter Systeme (`dnf`).
    - ZYpp ist der Paketmanager SUSE-basierter Systeme (`zypper`).
    - APT ist der Paketmanager Debian-/Ubuntu-basierter Systeme (`apt`).

    Verwenden Sie bei anderen Distributionen den passenden Paketmanager, etwa
    `yum`, `pacman`, `emerge` oder `apk`.

    Auch Paketnamen können je nach Distribution abweichen.

???+ tip

    Regelmäßige Updates sind für Sicherheit und Leistung wichtig. Richten Sie
    automatische Updates oder regelmäßige Wartungsfenster ein.

---

### Sudo

Zabbix-Prozesse wie Server und Agent laufen standardmäßig unter eigenen,
nicht privilegierten Konten, etwa `zabbix`. Für benutzerdefinierte Skripte oder
administrative Aufgaben können jedoch erhöhte Rechte erforderlich sein.

`sudo` ist meist vorhanden, kann bei einer Minimalinstallation jedoch fehlen.

Damit kann der Zabbix-Benutzer gezielt konfigurierte Befehle mit erhöhten Rechten
ausführen, ohne vollständig zum Benutzer root zu wechseln.

!!! info "Was ist sudo?"

    `sudo` erlaubt autorisierten Benutzern, Befehle mit den Rechten eines anderen
    Benutzers, üblicherweise root, auszuführen. So lassen sich administrative
    Aufgaben ohne direkte root-Anmeldung erledigen.

Installieren Sie `sudo` mit dem passenden Befehl:

!!! info "sudo installieren"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    Unter Ubuntu ist `sudo` normalerweise vorinstalliert. Der während der
    Installation angelegte Benutzer erhält darüber root-Rechte.

Ist `sudo` bereits aktuell, meldet der Paketmanager dies; andernfalls wird es installiert.

---

### Firewall

Stellen Sie als Nächstes sicher, dass die Firewall installiert und konfiguriert
ist. Sie schützt den Server anhand festgelegter Regeln vor unbefugtem Zugriff und
kontrolliert ein- und ausgehenden Netzwerkverkehr.

Installieren und aktivieren Sie die Firewall wie folgt:

!!! info "Firewall installieren und aktivieren"

    Red Hat
    ```bash
    dnf install firewalld
    systemctl enable firewalld --now
    ```
    SUSE
    ```bash
    zypper install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```bash
    sudo apt install ufw
    sudo ufw enable
    ```
???+ note "Was sind firewalld und ufw?"

    Firewalld ersetzt iptables auf RHEL- und SUSE-basierten Systemen. Änderungen
    werden ohne Neustart wirksam. Nutzt Ihre Distribution
    [https://www.firewalld.org](https://www.firewalld.org) nicht, beachten Sie
    deren Dokumentation. Ubuntu verwendet UFW als Oberfläche für iptables.

In den nächsten Kapiteln öffnen wir bestimmte Ports für die Kommunikation der
Zabbix-Komponenten.

Alternativ können Sie eigene Firewall-Zonen für bestimmte Anwendungsfälle
definieren. Dies isoliert Dienste und beschränkt den Zugriff nach Vertrauensstufe.

!!! example "Firewalld-Zone für den Datenbankzugriff erstellen"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Prüfen Sie die erstellte Zone:

!!! example "Erstellung der Zone prüfen"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Firewalld-Zonen erhöhen Sicherheit und Flexibilität und vereinfachen die Verwaltung:

- **Granular Access Control :**

:   Schnittstellen und IP-Bereiche können unterschiedliche Vertrauensstufen
    erhalten. So legen Sie fest, welche Systeme PostgreSQL erreichen dürfen.

- **Simplified Rule management:**

:   Zonen gruppieren Regeln übersichtlich nach Anwendungsfall und ersetzen
    komplexe manuelle iptables-Regeln.

- **Enhanced security:**

:   Eine Anwendung kann auf eine Zone beschränkt werden, um unbefugte
    Verbindungen aus anderen Netzen zu verhindern.

- **Dynamische Konfiguration:**

:   Firewalld unterstützt Laufzeit- und permanente Regeln, ohne bestehende
    Verbindungen zu unterbrechen.

- **Multi-Interface support:**

:   Für mehrere Netzwerkschnittstellen können unterschiedliche Richtlinien gelten.

Eine vollständige Zone für PostgreSQL sieht beispielsweise so aus:

!!! example "Firewalld-Zone für PostgreSQL-Datenbankzugriff"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Die `Quell-IP` ist dabei die einzige Adresse mit Datenbankzugriff.

Passen Sie bei Verwendung von Zonen die Anweisungen der folgenden Kapitel an.

---

### Time Server

Ein weiterer wichtiger Schritt ist die Zeitsynchronisation des Zabbix-Servers
über einen NTP-Client. Eine korrekte Uhrzeit ist für Server und überwachte Geräte
entscheidend. Falsche Zeitzonen erschweren die zeitliche Einordnung von Problemen.

Installieren und aktivieren Sie Chrony als NTP-Client:

!!! info "NTP-Client installieren"

    Red Hat
    ```bash
    dnf install chrony
    systemctl enable chronyd --now
    ```

    SUSE
    ```bash
    zypper install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```bash
    sudo apt install chrony
    ```

Prüfen Sie anschließend den Status von Chrony:

!!! info "Status von chronyd prüfen"

    ```bash
    systemctl status chronyd
    ```

???+ note "what is Chrony"

    Chrony ist ein moderner Ersatz für `ntpd` und synchronisiert schneller und
    genauer. Unterstützt Ihre OS
    [https://chrony-project.org/](https://chrony-project.org/) nicht, verwenden
    Sie stattdessen `ntpd`.

Stellen Sie danach die richtige Zeitzone ein. Die aktuelle Konfiguration zeigt
`timedatectl` an:

!!! example "Zeitkonfiguration prüfen"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 15:09:14 UTC
               Universal time: Thu 2023-11-16 15:09:14 UTC
                     RTC time: Thu 2023-11-16 15:09:15
                    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

Vergewissern Sie sich, dass Chrony aktiv ist. Listen Sie die verfügbaren
Zeitzonen auf:

!!! info "Zeitzonen auflisten"

    ```bash
    timedatectl list-timezones
    ```

Wählen Sie aus der Liste die passende Zeitzone, zum Beispiel:

!!! example "Verfügbare Zeitzonen"

    ```shell-session
    localhost:~ # timedatectl list-timezones
    Africa/Abidjan
    Africa/Accra
    ...
    Pacific/Tongatapu
    Pacific/Wake
    Pacific/Wallis
    UTC
    ```

Konfigurieren Sie die gewählte Zeitzone:

!!! info "Zeitzone einstellen"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Prüfen Sie die Einstellung erneut mit `timedatectl`:

!!! example "Uhrzeit und Zeitzone prüfen"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 16:13:35 CET
               Universal time: Thu 2023-11-16 15:13:35 UTC
                     RTC time: Thu 2023-11-16 15:13:36
                    Time zone: Europe/Brussels (CET, +0100)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

???+ note

    Manche Administratoren betreiben alle Server in UTC, damit Protokolle einer
    globalen Umgebung synchron bleiben. Zabbix unterstützt benutzerspezifische
    Zeitzonen: Der Server bleibt in UTC, während Benutzer ihre Zeitzone in der
    Oberfläche einstellen.

---

#### Verifying Chrony Synchronization

Prüfen Sie die Synchronisation mit den richtigen Zeitservern:

!!! info "Chrony prüfen"

    ```bash
    chronyc
    ```

Die Ausgabe sollte wie folgt aussehen:

!!! example "Chrony-Ausgabe prüfen"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Geben Sie in der Chrony-Eingabeaufforderung `sources` ein:

Beispielausgabe:

!!! example "Zeitquellen prüfen"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In diesem Beispiel liegen die NTP-Server außerhalb der Region. Verwenden Sie
möglichst Server in Ihrem Land oder einen unternehmenseigenen Zeitserver. Lokale
NTP-Server finden Sie hier:
[https://www.ntppool.org/](https://www.ntppool.org/).

---

#### Updating Time Servers

Ändern Sie für neue Zeitserver die Chrony-Konfiguration:

!!! info "Chrony-Konfiguration bearbeiten"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    Unter SUSE liegt die Pool-Konfiguration in einer separaten Datei. Bearbeiten
    Sie diese oder legen Sie im selben Verzeichnis eine neue Datei an. Deaktivieren
    oder entfernen Sie dann die vorhandene Pool-Konfiguration, um Konflikte zu vermeiden.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Ersetzen Sie den vorhandenen NTP-Pool durch einen näher gelegenen.

Beispiel der aktuellen Konfiguration:

!!! example "Beispiel einer NTP-Pool-Konfiguration"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Ändern Sie den Pool auf einen lokalen Zeitserver:

!!! info "NTP-Pool-Konfiguration ändern"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Starten Sie Chrony neu, um die Änderung anzuwenden:

!!! info "Chrony neu starten"

    ```bash
    systemctl restart chronyd
    ```

#### Verifying Updated Time Servers

Prüfen Sie erneut, ob die lokalen Server verwendet werden:

!!! info "Chrony-Quellen prüfen"

    ```
    chronyc> sources
    ```

Beispielausgabe mit lokalen Servern:

!!! example "Beispielausgabe"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Damit verwendet das System nun lokale Zeitserver.

## Conclusion

Noch vor der Installation der Zabbix-Pakete muss die Umgebung vorbereitet sein.
Ein aktuelles Betriebssystem, die erforderlichen Firewall-Freigaben und eine
genaue Zeitsynchronisation bilden die Grundlage. Damit können wir mit der
Installation von Zabbix fortfahren.

## Questions

- Warum ist eine genaue Zeitsynchronisation für ein Monitoring-System wie
  Zabbix so wichtig?
- Welcher Schritt folgt als Erstes bei der eigentlichen Zabbix-Installation?
- Welche Ports müssen in der Firewall freigegeben werden, damit Zabbix-Server
  und Agents miteinander kommunizieren können?

## Useful URLs

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
