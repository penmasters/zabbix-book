---
description: |
    Learn Zabbix system requirements: supported OS, database options, hardware
    specs, firewall ports, and time sync needed for a smooth installation.
tags: [beginner]
---

# Systeemvereisten

## Vereisten

Zabbix heeft specifieke hardware- en softwarevereisten waaraan voldaan moet
worden, en deze vereisten kunnen na verloop van tijd veranderen. Ze zijn ook
afhankelijk van de grootte van je installatie en de softwarestack die je kiest.
Voordat je hardware aanschaft of een databaseversie installeert, is het
essentieel om de Zabbix documentatie te raadplegen voor de meest recente
vereisten voor de versie die je van plan bent te installeren. Je kunt de meest
recente vereisten vinden
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Zorg ervoor dat je de juiste Zabbix-versie uit de lijst selecteert.

Voor kleinere of testopstellingen kan Zabbix gemakkelijk draaien op een systeem
met 2 CPU's en 8 GB RAM. Echter, de grootte van je setup, het aantal items dat
je monitort, de triggers die je aanmaakt en hoe lang je van plan bent gegevens
te bewaren, zullen invloed hebben op de benodigde bronnen. In de
gevirtualiseerde omgevingen van vandaag is mijn advies om klein te beginnen en
zo nodig op te schalen.

Je kunt alle componenten (Zabbix server, database, webserver) op één machine
installeren of verdelen over meerdere servers. Noteer voor de eenvoud de
servergegevens:

| Component      | IP-adres |
| -------------- | -------- |
| Zabbix server  |          |
| Databaseserver |          |
| Webserver      |          |

???+ tip

    Zabbix package names often use dashes (`-`) in their names, such as `zabbix-get`
    or `zabbix-sender`, but the binaries themselves may use underscores (`_`),
    like `zabbix_sender` or `zabbix_server`. This naming discrepancy can sometimes
    be confusing, particularly if you are using packages from non-official Zabbix
    repositories.

    Always check if a binary uses a dash or an underscore when troubleshooting.

???+ warning

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Basis OS-configuratie

Operating systems, so many choices, each with its own advantages and loyal user
base. While Zabbix can be installed on a wide range of platforms, documenting
the process for every available OS would be impractical. To keep this book
focused and efficient, we have chosen to cover only the most widely used
options: Ubuntu, Red Hat and Suse based distributions.

Since not everyone has access to a Red Hat Enterprise Linux (RHEL) or a SUSE
Linux Enterprise Server (SLES) subscription even though a developer account
provides limited access we have opted for Rocky Linux respectively openSUSE Leap
as a readily available alternative. For this book, we will be using Rocky Linux
9.x, openSUSE Leap 16 and Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    OS installation steps are outside the scope of this book, but a default or even a
    minimal installation of your preferred OS should be sufficient. Please refrain from
    installing graphical user interfaces (GUIs) or desktop environments, as they are
    unnecessary for server setups and consume valuable resources.

Once you have your preferred OS installed, there are a few essential
configurations to perform before proceeding with the Zabbix installation.
Perform the following steps on **all** the servers that will host Zabbix
components (i.e., Zabbix server, database server, and web server).

---

### Update the System

Before installing the Zabbix components, or any new software, it's a best
practice to ensure your operating system is up-to-date with the latest patches
and security fixes. This will help maintain system stability and compatibility
with the software you're about to install. Even if your OS installation is
recent, it's still advisable to run an update to ensure you have the latest
packages.

To update your system, run the following command based on your OS:

!!! info "Update your system"

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
???+ note "What is apt, dnf or zypper"

    - DNF (Dandified YUM) is a package manager used in recent Red Hat-based systems (invoked as `dnf`).
    - ZYpp (Zen / YaST Packages Patches Patterns Products) is the package manager 
    used on SUSE-based systems (invoked as `zypper`) and 
    - APT (Advanced Package Tool) is the package manager used on Debian/Ubuntu-based systems (invoked as `apt`). 

    If you're using another distribution, replace `dnf`/`zypper`/`apt` with your appropriate 
    package manager, such as `yum`, `pacman`, `emerge`, `apk` or ... .

    Do note that package names may also vary from distribution to distribution.

???+ tip

    Regularly updating your system is crucial for security and performance.
    Consider setting up automatic updates or scheduling regular maintenance windows
    to keep your systems current.

---

### Sudo

By default the Zabbix processes like the Zabbix server and agent run under their
own unprivileged user accounts (e.g., `zabbix`). However, there are scenarios
where elevated privileges are required, such as executing custom scripts or
commands that need root access. Also throughout this book, we will perform
certain administrative tasks that require `sudo` on the system.

Usually, `sudo` is already present on most systems, but when you performed a
minimal installation of your OS, it might be missing. Therefore we need to
ensure it's installed.

This will also allow the Zabbix user to execute specific configured commands
with elevated privileges without needing to switch to the root user entirely.

!!! info "What is sudo"

    `sudo` (short for "superuser do") is a command-line utility that allows
    permitted users to execute commands with the security privileges of another
    user, typically the superuser (root). It is commonly used in Unix-like
    operating systems to perform administrative tasks without needing to log in
    as the root user.

To install `sudo`, run the following command based on your OS:

!!! info "Install sudo"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    On Ubuntu, `sudo` is normally installed by default. Root access is managed
    through `sudo` for the initial user created during installation.

If `sudo` is already installed, these commands will inform you that the latest
version is already present and no further action is needed. If not, the package
manager will proceed to install it.

---

### Firewall

Next, we need to ensure that the firewall is installed and configured. A
firewall is a crucial security component that helps protect your server from
unauthorized access and potential threats by controlling incoming and outgoing
network traffic based on predetermined security rules.

Voer het volgende commando uit om de firewall te installeren en in te schakelen:

!!! info "Installeer en schakel de firewall in"

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
???+ note "What is firewalld / ufw"

    Firewalld is the replacement for iptables in RHEL- and SUSE-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps.
    Ubuntu makes use of UFW which is merely a frontend for iptables.

During the Zabbix installation in the next chapters, we will need to open
specific ports in the firewall to allow communication between Zabbix components.

Alternatively to just opening ports, as we will do in the next chapters, you can
also choose to define dedicated firewall zones for specific use cases. This
approach enhances security by isolating services and restricting access based on
trust levels. For example...

!!! example "Create a firewalld zone for database access"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Je kunt het aanmaken van de zone bevestigen door het volgende commando uit te
voeren:

!!! example "Verify the zone creation"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Using zones in firewalld to configure firewall rules provides several advantages
in terms of security, flexibility, and ease of management. Here’s why zones are
beneficial:

- **Granulaire toegangscontrole :**

: Firewalld zones allow different levels of trust for different network
interfaces and IP ranges. You can define which systems are allowed to connect to
PostgreSQL based on their trust level.

- **Vereenvoudigd regelbeheer:**

: Instead of manually defining complex iptables rules, zones provide an
organized way to group and manage firewall rules based on usage scenarios.

- **Verbeterde beveiliging:**

: By restricting application access to a specific zone, you prevent unauthorized
connections from other interfaces or networks.

- **Dynamische configuratie:**

: Firewalld supports runtime and permanent rule configurations, allowing changes
without disrupting existing connections.

- **Ondersteuning voor meerdere interfaces:**

: If the server has multiple network interfaces, zones allow different security
policies for each interface.

Bringing everything together to add a zone for, in this example, PostgreSQL it
would look like this:

!!! example "Firewalld with zone config for PostgreSQL database access"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Waarbij het `bron IP` het enige adres is dat een verbinding met de database tot
stand mag brengen.

If you wish to use zones when using firewalld, ensure to adapt the instructions
in the following chapters accordingly.

---

### Tijdserver

Een andere cruciale stap is het configureren van de tijdserver en het
synchroniseren van de Zabbix server met behulp van een NTP client. Nauwkeurige
tijdsynchronisatie is van vitaal belang voor Zabbix, zowel voor de server als
voor de apparaten die het bewaakt. Als een van de hosts een onjuiste tijdzone
heeft, kan dat tot verwarring leiden, zoals het onderzoeken van een probleem in
Zabbix dat uren eerder lijkt te zijn gebeurd dan in werkelijkheid het geval was.

Gebruik het volgende commando om chrony, onze NTP-cliënt, te installeren en in
te schakelen:

!!! info "NTP-cliënt installeren"

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

Controleer na de installatie of Chrony is ingeschakeld en draait door de status
te controleren met het volgende commando:

!!! info "Controleer status chronyd"

    ```bash
    systemctl status chronyd
    ```

???+ note "Wat is Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Zodra Chrony geïnstalleerd is, is de volgende stap ervoor te zorgen dat de
juiste tijdzone ingesteld is. U kan uw huidige tijdsconfiguratie bekijken met
het commando `timedatectl`:

!!! example "Check the time config"

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

Zorg ervoor dat de Chrony service actief is (raadpleeg indien nodig de vorige
stappen). Om de juiste tijdzone in te stellen, kunt u eerst alle beschikbare
tijdzones oplijsten met het volgende commando:

!!! info "List the timezones"

    ```bash
    timedatectl list-timezones
    ```

Deze opdracht toont een lijst met beschikbare tijdzones, zodat je de tijdzone
kunt selecteren die het dichtst bij je locatie ligt. Bijvoorbeeld:

!!! example "List of all the timezones available"

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

Zodra je je tijdzone hebt geïdentificeerd, configureer je deze met het volgende
commando:

!!! info "Tijdzone instellen"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Gebruik het commando `timedatectl` opnieuw om te controleren of de tijdzone
juist is ingesteld:

!!! example "Check the time and zone"

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

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

#### Chrony-synchronisatie controleren

Om ervoor te zorgen dat Chrony met de juiste tijdservers synchroniseert, kunt u
het volgende commando uitvoeren:

!!! info "chrony verifiëren"

    ```bash
    chronyc
    ```

De uitvoer moet lijken op:

!!! example "Verify your chrony output"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Once inside the Chrony prompt, type the `sources` command to check the used time
sources:

Voorbeelduitvoer:

!!! example "Check your time server sources"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In dit voorbeeld bevinden de gebruikte NTP-servers zich buiten je lokale regio.
Het wordt aanbevolen om over te schakelen naar tijdservers in je eigen land of,
indien beschikbaar, naar een speciale bedrijfstijdserver. U kunt lokale
NTP-servers hier vinden: [www.ntppool.org](https://www.ntppool.org/).

---

#### Tijdservers bijwerken

To update the time servers, modify the Chrony configuration file:

!!! info "Edit chrony config file"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    On SUSE, the pool configuration is located in a separate file. You can
    edit that file directly or add a new configuration file in the same directory.
    In the latter case, ensure to disable or remove the existing pool configuration
    to avoid conflicts.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Replace the existing NTP server pool with one closer to your location.

Voorbeeld van de huidige configuratie:

!!! example "Example ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Change the pools you want to a local time server:

!!! info "Change ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Herstart de Chrony service na deze wijziging om de nieuwe configuratie toe te
passen:

!!! info "Restart the chrony service"

    ```bash
    systemctl restart chronyd
    ```

#### Bijgewerkte tijdservers controleren

Controleer de tijdbronnen opnieuw om er zeker van te zijn dat de nieuwe lokale
servers in gebruik zijn:

!!! info "Controleer chrony bronnen"

    ```
    chronyc> sources
    ```

Voorbeeld van verwachte uitvoer met lokale servers:

!!! example "Example output"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Dit bevestigt dat het systeem nu lokale tijdservers gebruikt.

## Conclusie

As we have seen, before even considering the Zabbix packages, attention must be
paid to the environment in which it will reside. A properly configured and
up-to-date operating system, an open path through the firewall, and accurate
timekeeping are not mere suggestions, but essential building blocks. Having laid
this groundwork, we can now proceed with confidence to the Zabbix installation,
knowing that the underlying system is prepared for the task.

## Vragen

- Waarom denk je dat nauwkeurige tijdsynchronisatie zo cruciaal is voor een
  monitoringsysteem als Zabbix?
- Nu de basis is gelegd, wat is volgens jullie de eerste stap in het
  daadwerkelijke Zabbix installatieproces?
- Als we Zabbix gaan installeren, laten we dan eens nadenken over
  netwerkcommunicatie. Welke belangrijke poorten moet je door de firewall
  toestaan zodat de Zabbix server en agents effectief met elkaar kunnen
  communiceren?

## Nuttige URL's

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
