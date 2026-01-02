---
description: |
    Learn Zabbix system requirements: supported OS, database options, hardware
    specs, firewall ports, and time sync needed for a smooth installation.
tags: [beginner]
---

# Prérequis système

## Prérequis

Zabbix a des prérequis matérielles et logicielles spécifiques qui doivent être
respectées, et ces prérequis peuvent changer au fil du temps. Ils dépendent
également de la taille de votre installation et des logiciels que vous utilisez.
Avant d'acheter du matériel ou d'installer une version de base de données, il
est essentiel de consulter la documentation de Zabbix pour connaître les
prérequis les plus récentes pour la version que vous prévoyez d'installer. Vous
pouvez trouver les dernières exigences
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Veillez à sélectionner la bonne version de Zabbix dans la liste.

Pour les petites installations ou les installations de test, Zabbix peut
fonctionner confortablement sur un système doté de 2 CPU et de 8 Go de RAM.
Cependant, la taille de votre installation, le nombre d'éléments que vous
monitorez, les déclencheurs que vous créez et la durée pendant laquelle vous
prévoyez de conserver les données auront un impact sur les besoins en
ressources. Dans les environnements virtualisés d'aujourd'hui, nous vous
conseillions de commencer petit et d'augmenter au fur et à mesure des besoins.

Vous pouvez installer tous les composants (serveur Zabbix, base de données,
serveur web) sur une seule machine ou les répartir sur plusieurs serveurs. Pour
plus de simplicité, notez les détails du/des serveur(s) :

| Composant                  | Adresse IP |
| -------------------------- | ---------- |
| Serveur Zabbix             |            |
| Serveur de base de données |            |
| Serveur web                |            |

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

## Configuration de base du système d'exploitation

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

### Pare-feu

Next, we need to ensure that the firewall is installed and configured. A
firewall is a crucial security component that helps protect your server from
unauthorized access and potential threats by controlling incoming and outgoing
network traffic based on predetermined security rules.

Pour installer et activer le pare-feu, exécutez la commande suivante :

!!! info "Installer et activer le pare-feu"

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

Vous pouvez valider la création de la zone en exécutant la commande suivante :

!!! example "Verify the zone creation"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Using zones in firewalld to configure firewall rules provides several advantages
in terms of security, flexibility, and ease of management. Here’s why zones are
beneficial:

- **Contrôle d'accès granulaire :**

: Firewalld zones allow different levels of trust for different network
interfaces and IP ranges. You can define which systems are allowed to connect to
PostgreSQL based on their trust level.

- **Gestion simplifiée des règles :**

: Instead of manually defining complex iptables rules, zones provide an
organized way to group and manage firewall rules based on usage scenarios.

- **Sécurité renforcée :**

: By restricting application access to a specific zone, you prevent unauthorized
connections from other interfaces or networks.

- **Configuration dynamique :**

: Firewalld supports runtime and permanent rule configurations, allowing changes
without disrupting existing connections.

- **Prise en charge de plusieurs interfaces :**

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

Lorsque la `source IP` est la seule adresse autorisée à établir une connexion
avec la base de données.

If you wish to use zones when using firewalld, ensure to adapt the instructions
in the following chapters accordingly.

---

### Serveur de temps

Une autre étape cruciale consiste à configurer le serveur de temps et à
synchroniser le serveur Zabbix à l'aide d'un client NTP. Une synchronisation
précise de l'heure est vitale pour Zabbix, à la fois pour le serveur et pour les
périphériques qu'il surveille. Si l'un des hôtes a un fuseau horaire incorrect,
cela peut entraîner des confusions, comme par exemple déterminer l'heure d'un
problème dans Zabbix qui semble s'être produit plus tôt qu'il ne l'a fait en
réalité.

Pour installer et activer chrony, notre client NTP, utilisez la commande
suivante :

!!! info "Installer Chrony le client NTP"

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

Après l'installation, vérifiez que Chrony est activé et fonctionne en contrôlant
son état à l'aide de la commande suivante :

!!! info "Vérifier le statut de Chrony"

    ```bash
    systemctl status chronyd
    ```

???+ Note "qu'est-ce que Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Une fois Chrony installé, l'étape suivante consiste à s'assurer que le fuseau
horaire est correct. Vous pouvez visualiser votre configuration horaire actuelle
en utilisant la commande `timedatectl`:

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

Assurez-vous que le service Chrony fonctionne (reportez-vous aux étapes
précédentes si nécessaire). Pour définir le bon fuseau horaire, vous pouvez tout
d'abord lister tous les fuseaux horaires disponibles à l'aide de la commande
suivante :

!!! info "List the timezones"

    ```bash
    timedatectl list-timezones
    ```

Cette commande affiche une liste des fuseaux horaires disponibles, vous
permettant de sélectionner celui qui est le plus proche de votre position. Par
exemple :

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

Une fois que vous avez identifié votre fuseau horaire, configurez-le à l'aide de
la commande suivante :

!!! info "Régler le fuseau horaire"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Pour vérifier que le fuseau horaire a été configuré correctement, utilisez à
nouveau la commande `timedatectl`:

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

#### Vérification de la synchronisation de Chrony

Pour s'assurer que Chrony se synchronise avec les bons serveurs de temps, vous
pouvez exécuter la commande suivante :

!!! info "Vérifier chrony"

    ```bash
    chronyc
    ```

Le résultat devrait ressembler à :

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

Exemple de sortie :

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

Dans cet exemple, les serveurs NTP utilisés sont situés en dehors de votre
région. Il est recommandé de passer à des serveurs de temps dans votre pays ou,
si disponible, à un serveur de temps dédié à votre entreprise. Vous pouvez
trouver des serveurs NTP locaux ici :
[www.ntppool.org](https://www.ntppool.org/).

---

#### Mise à jour des serveurs de temps

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

Exemple de la configuration actuelle :

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

Après avoir effectué cette modification, redémarrez le service Chrony pour
appliquer la nouvelle configuration :

!!! info "Restart the chrony service"

    ```bash
    systemctl restart chronyd
    ```

#### Vérification des serveurs de temps mis à jour

Vérifiez à nouveau les sources de temps pour vous assurer que les nouveaux
serveurs locaux sont utilisés :

!!! info "Vérifier les sources Chrony"

    ```
    chronyc> sources
    ```

Exemple de résultat attendu avec des serveurs locaux :

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

Ceci confirme que le système utilise maintenant des serveurs de temps locaux.

## Conclusion

As we have seen, before even considering the Zabbix packages, attention must be
paid to the environment in which it will reside. A properly configured and
up-to-date operating system, an open path through the firewall, and accurate
timekeeping are not mere suggestions, but essential building blocks. Having laid
this groundwork, we can now proceed with confidence to the Zabbix installation,
knowing that the underlying system is prepared for the task.

## Questions

- Pourquoi pensez-vous qu'une synchronisation précise du temps est si cruciale
  pour un système de surveillance comme Zabbix ?
- Maintenant que les bases sont posées, quelle sera, selon vous, la première
  étape du processus d'installation de Zabbix ?
- Alors que nous nous apprêtons à installer Zabbix, pensons à la communication
  réseau. Quels sont les ports clés que vous pensez devoir autoriser à travers
  le pare-feu pour que le serveur Zabbix et les agents puissent interagir
  efficacement ?

## URL utiles

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
