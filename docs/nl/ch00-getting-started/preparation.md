---
description: |
    Dit hoofdstuk van The Zabbix Book, "Het systeem voorbereiden op Zabbix",
    beschrijft de stappen die nodig zijn voordat je Zabbix-componenten
    installeert. Je leert hoe je de officiële Zabbix repository toevoegt en
    het systeem voorbereidt om containers met Podman uit te voeren.
tags: [beginner]
---

# Het systeem voorbereiden op Zabbix

Voordat we Zabbix-componenten installeren, moeten we ervoor zorgen dat de
servers voldoen aan de configuratievereisten uit het vorige hoofdstuk:
[Systeemvereisten](Requirements.md).

Als je de Zabbix database, server en/of frontend op afzonderlijke machines
wilt installeren, moet je elke server afzonderlijk voorbereiden volgens de
instructies in dit hoofdstuk. Ook servers waarop een Zabbix proxy wordt
geïnstalleerd, moeten op dezelfde manier worden voorbereid.

---

## SELinux op RHEL in permissive mode zetten

Wanneer je een Red Hat-gebaseerd systeem gebruikt in een test- of labomgeving,
kun je SELinux tijdelijk in `permissive` mode zetten. Zo voorkom je dat
SELinux de installatie en eerste configuratie van Zabbix belemmert.

Doe dit niet op productiesystemen. Daar moet SELinux ingeschakeld blijven in
`enforcing` mode. Raadpleeg het gedeelte over SELinux in het hoofdstuk
Advanced Setup and Security voor het configureren van de vereiste policies.

Controleer de huidige SELinux-status met `sestatus`:

!!! info "SELinux-status"

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

Zoals je ziet, staat SELinux momenteel in `enforcing` mode. Met het volgende
commando schakel je tijdelijk over naar `permissive` mode: `setenforce 0`.

!!! info "SELinux tijdelijk in permissive mode zetten"

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

SELinux staat nu in `permissive` mode. Deze wijziging blijft echter niet
behouden na een herstart. Om de instelling permanent te maken, moet je het
configuratiebestand `/etc/selinux/config` aanpassen. Open het bestand en
vervang `enforcing` door `permissive`.

Je kunt dezelfde wijziging ook uitvoeren met dit commando:

!!! info "SELinux permanent in permissive mode zetten"

    Red Hat
    ```bash
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Dit commando past het configuratiebestand automatisch aan. Wanneer we
`sestatus` opnieuw uitvoeren, zien we dat zowel de huidige mode als de
instelling in het configuratiebestand op `permissive` staan.

!!! info "SELinux-status opnieuw controleren"

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

## De Zabbix repository installeren

Ga naar de [Zabbix Download-pagina](https://www.zabbix.com/download) en kies
de Zabbix-versie die je wilt installeren. In dit boek gebruiken we Zabbix
8.0 LTS. Selecteer ook de juiste Linux-distributie. Voor onze voorbeelden
zijn dat Rocky Linux 9, openSUSE Leap 16 en Ubuntu 24.04.

We installeren de Zabbix server met NGINX als webserver voor de frontend.
Zorg ervoor dat je de pakketten voor jouw configuratie selecteert.

![Zabbix Download](./getting-started/ch00.1-getting-started-zabbixdownload.png)

_0.1 Zabbix download_

---

### Opmerkingen voor Red Hat

Gebruik je een RHEL-gebaseerd systeem zoals Rocky Linux, dan moet je eerst
de Zabbix-pakketten uit de EPEL repository uitsluiten, als die repository
op je systeem aanwezig is. Bewerk hiervoor `/etc/yum.repos.d/epel.repo` en
voeg de volgende regel toe:

!!! info "Zabbix-pakketten uitsluiten"

    Red Hat
    ```ini
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ tip

    Het is doorgaans geen goed idee om de EPEL repository voortdurend
    ingeschakeld te laten. Dat kan conflicten veroorzaken doordat ongewenste
    pakketten worden geïnstalleerd of bestaande pakketten worden vervangen.
    Je kunt EPEL beter alleen inschakelen wanneer je die nodig hebt:

    ```bash
    dnf install --enablerepo=epel <package-name>
    ```

    Zo wordt EPEL alleen gebruikt wanneer je dat expliciet aangeeft.

---

### Opmerkingen voor openSUSE

Op openSUSE zijn Zabbix-pakketten ook beschikbaar in de standaardrepository
`repo-oss`. In tegenstelling tot RHEL-gebaseerde systemen biedt openSUSE
geen ingebouwde mogelijkheid om specifieke pakketten per repository uit te
sluiten. De Zabbix-pakketten in de standaardrepositories lopen doorgaans
één tot twee LTS-versies achter op de nieuwste releases. Daarom zullen ze
normaal geen problemen veroorzaken, tenzij ze al geïnstalleerd zijn.

In de volgende stap configureren we de officiële Zabbix repositories.
Zolang je een nieuwere Zabbix-versie selecteert dan die in `repo-oss`,
installeert `zypper` automatisch de recentste versie.

???+ tip

    Heb je al Zabbix-pakketten uit de standaardrepositories geïnstalleerd?
    Dan kun je het beste een van de volgende opties kiezen:

    - Verwijder de pakketten voordat je verdergaat.
    - Upgrade ze nadat je de nieuwe Zabbix repositories hebt toegevoegd.
      Gebruik daarvoor de `zypper`-optie `--allow-vendor-change`.

???+ note "SUSE Linux Enterprise Server (SLES)"

    Op SLES zijn Zabbix-pakketten niet opgenomen in de standaardrepositories.
    Je kunt daarom de officiële Zabbix repository toevoegen zonder conflicten
    met bestaande Zabbix-pakketten uit die repositories te verwachten.

---

### De Zabbix repository toevoegen

Vervolgens voegen we de Zabbix repository toe aan ons besturingssysteem.
Daarna is het verstandig om oude cachebestanden te verwijderen en de
repositorymetadata bij te werken. Dat doen we met de volgende commando's:

!!! info "De Zabbix repository toevoegen"

    Red Hat
    ```bash
    rpm -Uvh https://repo.zabbix.com/zabbix/8.0/release/rocky/9/noarch/zabbix-release-latest-8.0.el9.noarch.rpm
    dnf clean all
    ```

    SUSE
    ```bash
    rpm -Uvh --nosignature https://repo.zabbix.com/zabbix/8.0/release/sles/16/noarch/zabbix-release-latest-8.0.sles16.noarch.rpm
    zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'

    # Set the repository to auto-refresh to ensure it's always up to date
    zypper modifyrepo --refresh 'Zabbix Official Repository'
    ```

    Ubuntu
    ```bash
    sudo wget https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo apt update
    ```

Hiermee wordt de repositorymetadata vernieuwd en is het systeem klaar om
Zabbix te installeren.

???+ note "Wat is een repository?"

    Een repository is een bron waaruit je op Linux softwarepakketten kunt
    installeren. Je kunt het vergelijken met een appwinkel waarin je software
    van een vertrouwde aanbieder vindt en downloadt. In dit geval gebruiken
    we de officiële Zabbix repository.

    Er bestaan veel repositories, maar voeg alleen bronnen toe die je
    vertrouwt. Gebruik bij voorkeur de repositories van je besturingssysteem
    en voeg andere alleen toe wanneer ze betrouwbaar en noodzakelijk zijn.

    De Zabbix repository wordt door Zabbix zelf aangeboden en is daarom de
    aangewezen bron voor onze installatie. Een andere veelgebruikte
    repository voor Red Hat-gebaseerde systemen is EPEL (Extra Packages for
    Enterprise Linux). Ook bij bekende repositories blijft het belangrijk
    om voorzichtig te zijn met het toevoegen van nieuwe pakketbronnen.

---

## Het systeem voorbereiden op containers met Podman

Als je Zabbix-componenten als containers met Podman wilt uitvoeren, moet
Podman geïnstalleerd en correct geconfigureerd zijn. Hieronder lees je hoe
je Podman op verschillende besturingssystemen installeert.

Je kunt dit gedeelte overslaan als je op dit systeem geen Zabbix-componenten
in containers wilt uitvoeren.

???+ note "Waarom Podman?"

    Podman is een populaire container engine waarmee je containers kunt
    uitvoeren en beheren zonder een daemon zoals bij Docker. Op veel moderne
    Linux-distributies is Podman de aanbevolen container engine. Het biedt
    verschillende voordelen ten opzichte van Docker.

    Ten eerste ondersteunt Podman rootless containers, zodat containers
    onder een gebruikersaccount zonder verhoogde rechten kunnen draaien.
    Ten tweede integreert Podman met SELinux, wat een nauwkeurige
    toegangscontrole mogelijk maakt. Ten derde werkt Podman rechtstreeks
    samen met systemd. Daardoor kun je de levenscyclus van containers
    beheren met systemd units en Quadlets.

### Podman installeren

Om containers met Podman uit te voeren, installeren we eerst Podman en
enkele aanvullende tools voor het beheer van containers met systemd.

!!! info "Podman en de benodigde tools installeren"

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

### Podman configureren voor containerbeheer per gebruiker

Vervolgens maken we een gebruiker `podman` aan die de containers zal
uitvoeren. Je kunt ook een andere gebruikersnaam kiezen, bijvoorbeeld
`zabbix-proxy` voor een gebruiker die uitsluitend een Zabbix proxy in een
container uitvoert.

!!! info "De podman-gebruiker aanmaken en initialiseren"

    ```bash
    sudo useradd --comment "User for running container workloads" podman
    sudo -i -u podman
    mkdir -p ~/.local/share/containers
    mkdir -p ~/.config/containers/systemd/
    exit
    ```

Als SELinux op je systeem is ingeschakeld, voer dan het volgende commando
uit als `root`.

!!! info "SELinux: file context mapping instellen"

    ```bash
    semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
    ```

Dit commando voegt een SELinux file context mapping toe door een equivalentie
(`-e`) te definiëren tussen de standaardopslaglocatie voor containers,
`/var/lib/containers`, en de opslaglocatie van de gebruiker `podman`,
`/home/podman/.local/share/containers`. Hierdoor behandelt SELinux de
bestanden in de gebruikersmap op dezelfde manier als bestanden in de
standaardopslaglocatie, met de bijbehorende toegangsrechten.

!!! info "SELinux: file context mapping toepassen"

    ```bash
    restorecon -R -v /home/podman/.local/share/containers
    ```

Na het definiëren van de nieuwe SELinux-contexten past dit commando de
juiste security contexts recursief (`-R`) toe op de bestanden in de
opgegeven map. De optie `-v` toont welke wijzigingen worden uitgevoerd.
Zo krijgen alle bestanden de SELinux-labels die overeenkomen met de eerder
gedefinieerde mapping.

!!! info "Lingering voor gebruikersprocessen inschakelen"

    ```bash
    loginctl enable-linger podman
    ```

Dit commando schakelt `linger` in voor de gebruiker `podman`. Daardoor
blijven gebruikersservices, zoals containers die door systemd worden
beheerd, actief wanneer de gebruiker niet is aangemeld. Dit is handig
voor containers die op de achtergrond moeten blijven draaien, ook na
uitloggen of een herstart van het systeem.

Als laatste stap vertellen we systemd waar de gebruikersspecifieke
runtimebestanden worden opgeslagen:

!!! info "XDG_RUNTIME_DIR instellen voor de podman-gebruiker"

    ```bash
    sudo -u podman -i
    echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile && \
        source ~/.bash_profile
    ```

Deze regel zorgt ervoor dat de omgevingsvariabele `XDG_RUNTIME_DIR` correct
wordt ingesteld voor de gebruiker `podman`, zowel in de huidige sessie als
in toekomstige sessies. De variabele verwijst naar de locatie van
gebruikersspecifieke runtimebestanden, waaronder de systemd user session
bus. Deze instelling is nodig om `systemctl --user` correct te laten
werken met containers die door Podman worden beheerd.

Je systeem is nu voorbereid om Zabbix-componenten als containers met
Podman uit te voeren.

???+ warning "Bekend probleem bij wachten op network-online.target"

    Als het starten van je containers ongeveer 90 seconden duurt en daarna
    mislukt, controleer dan de systeemlogs met `journalctl`. Mogelijk zie
    je meldingen zoals deze:

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

    Dan heb je mogelijk te maken met een
    [bekend probleem met Podman Quadlets](https://github.com/containers/podman/issues/24796).

    Dit probleem ontstaat doordat de door systemd gegenereerde Quadlet
    service afhankelijk is van het systeembrede target
    `network-online.target`. Normaal geeft dit target aan dat het netwerk
    volledig beschikbaar is. Op sommige Linux-distributies of bij bepaalde
    netwerkconfiguraties melden netwerkcomponenten echter niet correct aan
    systemd dat het netwerk online is. Daardoor wordt
    `network-online.target` niet geactiveerd en blijft Podman wachten
    totdat de timeout wordt bereikt.

    Als workaround kun je een eenvoudige systemd service aanmaken die
    `network-online.target` activeert:

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

## Conclusie

Nu de voorbereiding is afgerond, is je systeem klaar voor de installatie
van Zabbix-componenten. We hebben de officiële Zabbix repository toegevoegd
en het systeem voorbereid op de installatie van de Zabbix server, database
en frontend. Waar nodig hebben we ook Podman geconfigureerd om
Zabbix-componenten in containers uit te voeren.

In het volgende hoofdstuk gaan we verder met de installatie van de
Zabbix-componenten. Daarbij behandelen we stap voor stap de installatie
van de Zabbix server, database en frontend.

---

## Vragen

- Waarom is het belangrijk om de officiële Zabbix repository te gebruiken
  in plaats van de pakketten die je Linux-distributie aanbiedt?

- Waarom moet SELinux ingeschakeld blijven in productieomgevingen, en
  wat zijn de gevolgen van het overschakelen naar permissive mode?

---

## Nuttige URL's

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)

