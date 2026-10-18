---
description: |
    Dieser Abschnitt des Zabbix Book beschreibt die Vorbereitung des Systems vor
    der Installation einer Zabbix-Komponente. Dazu gehören das offizielle
    Zabbix-Repository und die Vorbereitung für Podman-Container.
tags: [beginner]
---

# System für Zabbix vorbereiten

Vor der Installation einer Zabbix-Komponente müssen die Server die im vorherigen
Abschnitt beschriebenen [Systemanforderungen](Requirements.md) erfüllen.

Wenn Datenbank, Zabbix-Server und/oder Frontend auf getrennten Maschinen laufen,
bereiten Sie jeden Server einzeln vor. Dies gilt auch für Zabbix-Proxys.

---

## SELinux unter RHEL deaktivieren

In einer Test- oder Laborumgebung auf Red-Hat-Basis können Sie SELinux
vorübergehend in den Modus permissive versetzen, damit es die Installation und
Erstkonfiguration von Zabbix nicht beeinträchtigt.

Deaktivieren Sie SELinux nicht in Produktionsumgebungen. Dort sollte es aktiviert
und im Modus enforcing bleiben. Die erforderlichen Zabbix-Richtlinien werden im
SELinux-Abschnitt des Kapitels zur erweiterten Konfiguration und Sicherheit erklärt.

Prüfen Sie den aktuellen Status mit `sestatus`.

!!! info "SELinux-Status"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   enforcing
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Das System arbeitet im Modus enforcing. Wechseln Sie vorübergehend mit
`setenforce 0` in den Modus permissive.

!!! info "SELinux vorübergehend auf permissive setzen"

    ```console
    ~# setenforce 0
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Diese Änderung gilt nicht über einen Neustart hinaus. Ersetzen Sie für eine
dauerhafte Einstellung in `/etc/selinux/config` den Wert `enforcing` durch
`permissive` oder verwenden Sie:

!!! info "SELinux dauerhaft auf permissive setzen"

    Red Hat
    ``` bash
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Danach zeigt `sestatus` sowohl für den aktuellen Modus als auch für die
Konfigurationsdatei permissive an.

!!! info "SELinux-Status erneut prüfen"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          permissive
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

---

## Zabbix-Repository installieren

Wählen Sie auf der Zabbix-Downloadseite
[https://www.zabbix.com/download](https://www.zabbix.com/download) die gewünschte
Version und Distribution. In diesem Buch verwenden wir Zabbix 8.0 LTS mit Rocky
Linux 9, openSUSE Leap 16 oder Ubuntu 24.04.

Wir installieren den Zabbix-Server und NGINX als Webserver für das Frontend.
Laden Sie die Pakete für die gewählte Konfiguration herunter.

![Zabbix Download](./getting-started/ch00.1-getting-started-zabbixdownload.png)

_0.1 Zabbix-Download_

---

### Hinweise zu Red Hat

Auf RHEL-basierten Systemen wie Rocky Linux schließen Sie zunächst die
Zabbix-Pakete des EPEL-Repositorys aus, sofern EPEL installiert ist. Ergänzen Sie
in `/etc/yum.repos.d/epel.repo`:

!!! info "Pakete ausschließen"

    Red Hat
    ``` ini
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ tip

    EPEL sollte nicht dauerhaft aktiviert sein, da Pakete unbeabsichtigt ersetzt
    oder installiert werden könnten. Aktivieren Sie es nur bei Bedarf mit
    `dnf install --enablerepo=epel <package-name>`.

---

### Hinweise zu openSUSE

Unter openSUSE sind Zabbix-Pakete auch im Standard-Repository `repo-oss`
verfügbar. Anders als RHEL kann openSUSE einzelne Pakete nicht für ein bestimmtes
Repository ausschließen. Die Standardpakete liegen jedoch meist ein bis zwei
LTS-Versionen zurück und stören die Installation nur, wenn sie bereits installiert sind.

Im nächsten Schritt konfigurieren wir die offiziellen Zabbix-Repositorys. Ist
deren Version neuer als die Pakete in `repo-oss`, installiert zypper automatisch
die aktuelle Version.

???+ tip

    Sind bereits Zabbix-Pakete aus Standard-Repositorys installiert:

    - entfernen Sie diese vor dem Fortfahren; oder
    - aktualisieren Sie sie nach dem Hinzufügen der neuen Repositorys mit der
      zypper-Option `--allow-vendor-change`.

???+ note "SUSE Linux Enterprise Server (SLES)"

    SLES enthält keine Zabbix-Pakete in den Standard-Repositorys. Das offizielle
    Zabbix-Repository kann daher ohne Konflikte hinzugefügt werden.

---

### Zabbix-Repository hinzufügen

Installieren Sie das Repository und bereinigen Sie anschließend den Cache, damit
alte Dateien entfernt und Metadaten aktualisiert werden:

!!! info "Zabbix-Repository hinzufügen"

    Red Hat
    ``` bash
    rpm -Uvh https://repo.zabbix.com/zabbix/8.0/release/rocky/9/noarch/zabbix-release-latest-8.0.el9.noarch.rpm
    dnf clean all
    ```

    SUSE
    ``` bash
    rpm -Uvh --nosignature https://repo.zabbix.com/zabbix/8.0/release/sles/16/noarch/zabbix-release-latest-8.0.sles16.noarch.rpm
    zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'

    # Set the repository to auto-refresh to ensure it's always up to date
    zypper modifyrepo --refresh 'Zabbix Official Repository'
    ```

    Ubuntu
    ``` bash
    sudo wget https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo apt update
    ```

Damit sind die Repository-Metadaten aktuell und das System ist für die
Zabbix-Installation vorbereitet.

???+ note "Was ist ein Repository?"

    Ein Linux-Repository stellt Softwarepakete aus einer vertrauenswürdigen
    Quelle bereit. Nutzen Sie vorzugsweise die Repositorys des Betriebssystems
    und fügen Sie nur vertrauenswürdige und notwendige Quellen hinzu.

    Das Zabbix-Repository stammt direkt vom Hersteller. EPEL (Extra Packages for
    Enterprise Linux) ist eine weitere verbreitete Quelle für Red-Hat-basierte
    Systeme. Gehen Sie beim Hinzufügen neuer Repositorys dennoch vorsichtig vor,
    um Sicherheit und Stabilität zu erhalten.

---

## System für Podman-Container vorbereiten

Wenn Zabbix-Komponenten als Podman-Container laufen sollen, muss Podman installiert
und korrekt konfiguriert sein. Andernfalls können Sie diesen Abschnitt überspringen.

???+ note "Warum Podman?"

    Podman verwaltet Container ohne einen Daemon wie Docker und ist auf vielen
    modernen Distributionen der empfohlene Container-Engine. Rootless-Container
    laufen unter nicht privilegierten Konten. Podman integriert sich in SELinux
    und systemd und unterstützt die Verwaltung über systemd-Units und Quadlets.

### Podman installieren

Installieren Sie Podman und die Werkzeuge zur Verwaltung mit systemd.

!!! info "Podman und benötigte Werkzeuge installieren"

    Red Hat
    ```bash
    dnf install podman policycoreutils-python-utils
    ```

    SUSE
    ```bash
    zypper install podman policycoreutils-python-utils
    ```

    Ubuntu
    ```bash
    sudo apt install podman
    ```

### Podman für benutzerbasierte Containerverwaltung konfigurieren

Erstellen Sie einen Benutzer `podman`, der die Container ausführt. Sie können
auch einen anderen Namen verwenden, etwa `zabbix-proxy` für einen Benutzer, der
nur einen Zabbix-Proxy im Container startet.

!!! info "Podman-Benutzer erstellen und initialisieren"

    ```bash
    sudo useradd --comment "User for running container workloads" podman
    sudo -i -u podman
    mkdir -p ~/.local/share/containers
    mkdir -p ~/.config/containers/systemd/
    exit
    ```

Führen Sie bei aktiviertem SELinux den folgenden Befehl als `root` aus.

!!! info "SELinux: Dateikontext-Zuordnung definieren"

    ```bash
    semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
    ```

Der Befehl erstellt eine SELinux-Äquivalenz (`-e`) zwischen dem standardmäßigen
Container-Speicher `/var/lib/containers` und dem Benutzerspeicher
`/home/podman/.local/share/containers`. SELinux wendet dadurch dieselben
Richtlinien und Zugriffsrechte an.

!!! info "SELinux: Dateikontext-Zuordnung anwenden"

    ```bash
    restorecon -R -v /home/podman/.local/share/containers
    ```

Dieser Befehl wendet die korrekten Sicherheitskontexte rekursiv (`-R`) an. Mit
`-v` werden die Änderungen ausführlich angezeigt.

!!! info "Fortbestehen von Benutzerprozessen aktivieren"

    ```bash
    loginctl enable-linger podman
    ```

„Linger“ lässt Benutzerdienste wie systemd-verwaltete Container ohne aktive
Anmeldung weiterlaufen, auch nach Abmeldung oder Systemneustart.

Teilen Sie systemd abschließend mit, wo die benutzerspezifischen Laufzeitdateien
liegen:

!!! info "XDG_RUNTIME_DIR für den Podman-Benutzer setzen"

    ```bash
    sudo -u podman -i
    echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile && \
        source ~/.bash_profile
    ```

`XDG_RUNTIME_DIR` verweist auf benutzerspezifische Laufzeitdateien einschließlich
des systemd-Benutzerbusses. Die Variable wird für die aktuelle und folgende
Sitzungen geladen und ermöglicht `systemctl --user` für Podman-Container.

Das System ist nun für Zabbix-Komponenten in Podman-Containern vorbereitet.

???+ warning "Bekanntes Problem beim Warten auf network-online.target"

    Dauert der Containerstart etwa 90 Sekunden und schlägt anschließend fehl,
    können im Systemprotokoll (`journalctl`) folgende Meldungen erscheinen:

    ```
    systemd[1601]: Starting Wait for system level network-online.target as user....
    sh[3128]: inactive
    sh[3130]: inactive
    sh[3132]: inactive
    sh[3134]: inactive
    sh[3136]: inactive
    ...
    ...
    sh[3604]: inactive
    sh[3606]: inactive
    systemd[1601]: podman-user-wait-network-online.service: start operation timed out. Terminating.
    systemd[1601]: podman-user-wait-network-online.service: Main process exited, code=killed, status=15/TERM
    systemd[1601]: podman-user-wait-network-online.service: Failed with result 'timeout'.
    systemd[1601]: Failed to start Wait for system level network-online.target as user..
    ```

    Dies ist ein bekanntes Quadlet-Problem:
    [https://github.com/containers/podman/issues/24796](https://github.com/containers/podman/issues/24796).

    Der von systemd erzeugte Quadlet-Dienst hängt von `network-online.target` ab.
    In bestimmten Distributionen oder Netzwerkkonfigurationen melden die
    Netzwerkkomponenten den Zustand „online“ nicht korrekt. Das Target wird nicht
    aktiviert und Podman wartet bis zum Timeout.

    Erstellen Sie als Workaround einen Dummy-Dienst, der
    `network-online.target` aktiviert:

    ```bash
    vi /etc/systemd/system/podman-network-online-dummy.service
    ```
    ```ini
    [Unit]
    Description=This is a dummy service to activate network-online.target
    After=network-online.target
    Wants=network-online.target

    [Service]
    ExecStart=/usr/bin/echo Activating network-online.target

    [Install]
    WantedBy=multi-user.target
    ```
    ```bash
    systemctl daemon-reload
    systemctl enable --now podman-network-online-dummy.service
    ```

---

## Fazit

Das System ist für die Installation von Zabbix vorbereitet. Das offizielle
Repository wurde hinzugefügt und die Voraussetzungen für Zabbix-Server,
Datenbank und Frontend sind erfüllt. Bei Bedarf können außerdem Podman-Container
ausgeführt werden.

Im nächsten Kapitel installieren und konfigurieren wir die Zabbix-Komponenten.

---

## Fragen

- Warum sollte das offizielle Zabbix-Repository statt der Pakete Ihrer
  Linux-Distribution verwendet werden?
- Warum sollte SELinux in Produktionsumgebungen aktiviert bleiben und welche
  Folgen hat der Modus permissive?

---

## Nützliche URLs

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
