---
description: |
    Découvrez les prérequis système de Zabbix : systèmes d'exploitation pris en
    charge, bases de données, matériel, ports de pare-feu et synchronisation horaire.
tags: [beginner]
---

# Prérequis système

## Prérequis

Zabbix a des prérequis matériels et logiciels spécifiques qui doivent être
respectés, et ces prérequis peuvent changer au fil du temps. Ils dépendent
également de la taille de votre installation et des logiciels que vous utilisez.
Avant d'acheter du matériel ou d'installer une version de base de données, il
est essentiel de consulter la documentation de Zabbix pour connaître les
prérequis les plus récents pour la version que vous prévoyez d'installer. Vous
pouvez trouver les dernières exigences
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Veillez à sélectionner la bonne version de Zabbix dans la liste.

Pour les petites installations ou les installations de test, Zabbix peut
fonctionner confortablement sur un système doté de 2 CPU et de 8 Go de RAM.
Cependant, la taille de votre installation, le nombre d'éléments que vous
supervisez, les déclencheurs que vous créez et la durée pendant laquelle vous
prévoyez de conserver les données auront un impact sur les besoins en
ressources. Dans les environnements virtualisés actuels, nous vous conseillons
de commencer modestement et d'adapter les ressources en fonction des besoins.

Vous pouvez installer tous les composants (serveur Zabbix, base de données,
serveur web) sur une seule machine ou les répartir sur plusieurs serveurs. Pour
plus de simplicité, notez les détails du/des serveur(s) :

| Composant                  | Adresse IP |
| -------------------------- | ---------- |
| Serveur Zabbix             |            |
| Serveur de base de données |            |
| Serveur web                |            |

???+ tip

    Les noms des paquets Zabbix contiennent souvent des traits d'union (`-`),
    comme `zabbix-get` ou `zabbix-sender`, tandis que les binaires eux-mêmes
    peuvent utiliser des traits de soulignement (`_`), comme `zabbix_sender` ou
    `zabbix_server`. Cette différence peut prêter à confusion, notamment si vous
    utilisez des paquets provenant de dépôts Zabbix non officiels.

    Lors d'un dépannage, vérifiez toujours si le nom du binaire utilise un trait
    d'union ou un trait de soulignement.

???+ warning

    À partir de Zabbix 7.2, seuls MySQL (y compris ses forks) et PostgreSQL sont
    pris en charge comme bases de données back-end. Les versions antérieures de
    Zabbix prenaient également en charge Oracle Database ; cette prise en charge
    a toutefois été abandonnée avec Zabbix 7.0 LTS, dernière version LTS à prendre
    officiellement en charge Oracle DB.

---

## Configuration de base du système d'exploitation

Il existe de nombreux systèmes d'exploitation, chacun avec ses avantages et sa
communauté d'utilisateurs. Bien que Zabbix puisse être installé sur de nombreuses
plateformes, il serait irréaliste de documenter la procédure pour chaque système.
Afin que ce livre reste ciblé et efficace, nous ne couvrons que les options les
plus utilisées : Ubuntu et les distributions basées sur Red Hat et SUSE.

Tout le monde ne dispose pas d'un abonnement Red Hat Enterprise Linux (RHEL) ou
SUSE Linux Enterprise Server (SLES), même si un compte développeur offre un accès
limité. Nous avons donc choisi Rocky Linux et openSUSE Leap comme alternatives
facilement accessibles. Dans ce livre, nous utiliserons Rocky Linux 9.x,
openSUSE Leap 16 et Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    L'installation du système d'exploitation n'entre pas dans le cadre de ce livre,
    mais une installation par défaut, voire minimale, du système de votre choix
    devrait suffire. N'installez pas d'interface graphique ni d'environnement de
    bureau : ils sont inutiles sur un serveur et consomment des ressources.

Une fois le système d'exploitation installé, quelques configurations essentielles
doivent être effectuées avant l'installation de Zabbix. Réalisez les étapes
suivantes sur **tous** les serveurs qui hébergeront des composants Zabbix
(serveur Zabbix, serveur de base de données et serveur web).

---

### Mettre à jour le système

Avant d'installer les composants Zabbix ou tout autre logiciel, il est recommandé
de vérifier que le système d'exploitation dispose des derniers correctifs et mises
à jour de sécurité. Cela contribue à sa stabilité et à sa compatibilité avec les
logiciels que vous allez installer. Même après une installation récente du système,
il est conseillé d'effectuer une mise à jour afin de disposer des derniers paquets.

Pour mettre à jour le système, exécutez la commande correspondant à votre OS :

!!! info "Mettre à jour le système"

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
???+ note "Que sont apt, dnf et zypper ?"

    - DNF (Dandified YUM) est le gestionnaire de paquets des systèmes récents
      basés sur Red Hat ; il s'utilise avec la commande `dnf`.
    - ZYpp (Zen / YaST Packages Patches Patterns Products) est le gestionnaire
      de paquets des systèmes basés sur SUSE ; il s'utilise avec `zypper`.
    - APT (Advanced Package Tool) est le gestionnaire de paquets des systèmes
      basés sur Debian et Ubuntu ; il s'utilise avec `apt`.

    Si vous utilisez une autre distribution, remplacez `dnf`/`zypper`/`apt` par
    le gestionnaire approprié, par exemple `yum`, `pacman`, `emerge` ou `apk`.

    Le nom des paquets peut également varier d'une distribution à l'autre.

???+ tip

    La mise à jour régulière du système est essentielle pour sa sécurité et ses
    performances. Envisagez des mises à jour automatiques ou des fenêtres de
    maintenance périodiques afin de maintenir vos systèmes à jour.

---

### Sudo

Par défaut, les processus Zabbix, comme le serveur et l'agent Zabbix, s'exécutent
sous leurs propres comptes utilisateur non privilégiés (par exemple `zabbix`).
Certaines situations exigent toutefois des privilèges élevés, notamment pour
exécuter des scripts personnalisés ou des commandes nécessitant un accès root.
Dans ce livre, nous effectuerons également des tâches administratives qui
requièrent `sudo` sur le système.

`sudo` est généralement déjà présent sur la plupart des systèmes, mais il peut
manquer après une installation minimale. Nous devons donc vérifier qu'il est
installé.

Cela permettra aussi à l'utilisateur Zabbix d'exécuter certaines commandes
configurées avec des privilèges élevés sans devoir passer entièrement sous root.

!!! info "Qu'est-ce que sudo ?"

    `sudo` (abréviation de « superuser do ») est un utilitaire en ligne de commande
    qui permet aux utilisateurs autorisés d'exécuter des commandes avec les
    privilèges d'un autre utilisateur, généralement le superutilisateur (root).
    Il est couramment utilisé sur les systèmes de type Unix pour effectuer des
    tâches administratives sans ouvrir de session en tant que root.

Pour installer `sudo`, exécutez la commande correspondant à votre OS :

!!! info "Installer sudo"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    Sur Ubuntu, `sudo` est normalement installé par défaut. L'accès root de
    l'utilisateur initial créé pendant l'installation est géré par `sudo`.

Si `sudo` est déjà installé, ces commandes indiquent que la dernière version est
présente et qu'aucune autre action n'est nécessaire. Dans le cas contraire, le
gestionnaire de paquets l'installera.

---

### Pare-feu

Nous devons ensuite vérifier que le pare-feu est installé et configuré. Le
pare-feu est un composant de sécurité essentiel : il protège le serveur contre
les accès non autorisés et les menaces potentielles en contrôlant le trafic
réseau entrant et sortant selon des règles prédéfinies.

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
???+ note "Que sont firewalld et ufw ?"

    Firewalld remplace iptables sur les systèmes basés sur RHEL et SUSE. Les
    modifications prennent effet immédiatement, sans redémarrer le service.
    Si votre distribution n'utilise pas
    [https://www.firewalld.org](https://www.firewalld.org), consultez la
    documentation de votre OS pour connaître la configuration appropriée du
    pare-feu. Ubuntu utilise UFW, qui est une interface pour iptables.

Lors de l'installation de Zabbix dans les chapitres suivants, nous devrons ouvrir
certains ports du pare-feu pour permettre la communication entre les composants
Zabbix.

Au lieu d'ouvrir simplement des ports, comme nous le ferons dans les chapitres
suivants, vous pouvez définir des zones de pare-feu dédiées à des cas d'utilisation
précis. Cette approche renforce la sécurité en isolant les services et en limitant
l'accès selon le niveau de confiance. Par exemple :

!!! example "Créer une zone firewalld pour l'accès à la base de données"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Vous pouvez valider la création de la zone en exécutant la commande suivante :

!!! example "Vérifier la création de la zone"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

L'utilisation de zones firewalld pour configurer les règles de pare-feu offre
plusieurs avantages en matière de sécurité, de flexibilité et de facilité de
gestion :

- **Contrôle d'accès granulaire :**

:   Les zones firewalld permettent d'attribuer différents niveaux de confiance
    aux interfaces réseau et aux plages IP. Vous pouvez définir les systèmes
    autorisés à se connecter à PostgreSQL selon leur niveau de confiance.

- **Gestion simplifiée des règles :**

:   Au lieu de définir manuellement des règles iptables complexes, les zones
    permettent de regrouper et de gérer les règles de pare-feu de manière
    structurée selon les scénarios d'utilisation.

- **Sécurité renforcée :**

:   En limitant l'accès à une application à une zone précise, vous empêchez les
    connexions non autorisées provenant d'autres interfaces ou réseaux.

- **Configuration dynamique :**

:   Firewalld prend en charge les règles temporaires et permanentes, ce qui permet
    d'appliquer des modifications sans interrompre les connexions existantes.

- **Prise en charge de plusieurs interfaces :**

:   Si le serveur possède plusieurs interfaces réseau, les zones permettent
    d'appliquer une politique de sécurité différente à chaque interface.

Dans cet exemple, la configuration complète d'une zone pour PostgreSQL ressemble
à ceci :

!!! example "Zone firewalld pour l'accès à une base de données PostgreSQL"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

L'`IP source` est ici la seule adresse autorisée à établir une connexion avec
la base de données.

Si vous souhaitez utiliser les zones firewalld, adaptez en conséquence les
instructions des chapitres suivants.

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

!!! info "Vérifier le statut de Chronyd"

    ```bash
    systemctl status chronyd
    ```

???+ note "Qu'est-ce que Chrony ?"

    Chrony remplace avantageusement `ntpd` et offre une synchronisation horaire
    plus rapide et plus précise. Si votre OS ne prend pas en charge
    [https://chrony-project.org/](https://chrony-project.org/), envisagez
    d'utiliser `ntpd` à la place.

Une fois Chrony installé, l'étape suivante consiste à s'assurer que le fuseau
horaire est correct. Vous pouvez visualiser votre configuration horaire actuelle
en utilisant la commande `timedatectl` :

!!! example "Vérifier la configuration horaire"

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

!!! info "Lister les fuseaux horaires"

    ```bash
    timedatectl list-timezones
    ```

Cette commande affiche une liste des fuseaux horaires disponibles, vous
permettant de sélectionner celui qui est le plus proche de votre position. Par
exemple :

!!! example "Liste des fuseaux horaires disponibles"

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
nouveau la commande `timedatectl` :

!!! example "Vérifier l'heure et le fuseau horaire"

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

    Certains administrateurs préfèrent configurer tous les serveurs dans le
    fuseau UTC afin de synchroniser les journaux d'une infrastructure mondiale.
    Zabbix permet de définir le fuseau horaire par utilisateur : le serveur peut
    rester en UTC tandis que chaque utilisateur adapte son fuseau dans l'interface.

---

#### Vérification de la synchronisation de Chrony

Pour s'assurer que Chrony se synchronise avec les bons serveurs de temps, vous
pouvez exécuter la commande suivante :

!!! info "Vérifier chrony"

    ```bash
    chronyc
    ```

Le résultat devrait ressembler à :

!!! example "Vérifier la sortie de Chrony"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Dans l'invite Chrony, saisissez la commande `sources` pour vérifier les sources
de temps utilisées :

Exemple de sortie :

!!! example "Vérifier les sources des serveurs de temps"

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
[https://www.ntppool.org/](https://www.ntppool.org/).

---

#### Mise à jour des serveurs de temps

Pour mettre à jour les serveurs de temps, modifiez le fichier de configuration
de Chrony :

!!! info "Modifier le fichier de configuration de Chrony"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    Sur SUSE, la configuration du pool se trouve dans un fichier distinct. Vous
    pouvez modifier directement ce fichier ou ajouter un nouveau fichier de
    configuration dans le même répertoire. Dans ce dernier cas, désactivez ou
    supprimez la configuration existante afin d'éviter les conflits.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Remplacez le pool de serveurs NTP existant par un pool plus proche de votre
emplacement.

Exemple de la configuration actuelle :

!!! example "Exemple de configuration d'un pool NTP"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Remplacez les pools souhaités par un serveur de temps local :

!!! info "Modifier la configuration du pool NTP"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Après avoir effectué cette modification, redémarrez le service Chrony pour
appliquer la nouvelle configuration :

!!! info "Redémarrer le service Chrony"

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

!!! example "Exemple de sortie"

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

Comme nous l'avons vu, avant même d'envisager l'installation des paquets Zabbix,
il faut prêter attention à l'environnement qui les accueillera. Un système
d'exploitation correctement configuré et à jour, un passage ouvert dans le
pare-feu et une mesure précise du temps ne sont pas de simples recommandations,
mais des fondations indispensables. Ces bases étant posées, nous pouvons aborder
l'installation de Zabbix en sachant que le système sous-jacent est prêt.

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
