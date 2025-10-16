---
description : | Apprendre la configuration requise pour Zabbix : OS supporté,
options de base de données, spécifications matérielles, ports de pare-feu, et
synchronisation du temps nécessaire pour une installation en douceur. tags :
[beginner]
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

???+ note

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Configuration de base du système d'exploitation

Les systèmes d'exploitation, vaste choix, chacun avec ses propres avantages et
sa base de fervants utilisateurs. Bien que Zabbix puisse être installé sur une
large gamme de plateformes, documenter le processus pour chaque système
d'exploitation disponible ne serait pas pratique. Pour que ce livre reste ciblé
et efficace, nous avons choisi de ne couvrir que les options les plus largement
utilisées : Ubuntu et Red Hat.

Comme tout le monde n'a pas accès à un abonnement Red Hat Enterprise Linux
(RHEL), même si un compte de développeur offre un accès limité, nous avons opté
pour Rocky Linux comme alternative facilement disponible. Pour ce livre, nous
utiliserons Rocky Linux 9.x et Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://ubuntu.com/>

### Pare-feu

Avant d'installer Zabbix, il est essentiel de préparer correctement le système
d'exploitation. La première étape est de s'assurer que le pare-feu est installé
et configuré.

Pour installer et activer le pare-feu, exécutez la commande suivante :

!!! info "Installer et activer le pare-feu"

    Red Hat
    ```yaml
    dnf install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```yaml
    sudo apt install ufw
    sudo ufw enable
    ```

Une fois installé, vous pouvez configurer les ports nécessaires. Pour Zabbix,
nous devons autoriser l'accès au port `10051/tcp`, qui est l'endroit où le
trappeur Zabbix écoute les données entrantes. Utilisez la commande suivante pour
ouvrir ce port dans le pare-feu :

!!! info "Autoriser l'accès au trappeur Zabbix"

    Red Hat
    ```yaml
    firewall-cmd --add-service=zabbix-server --permanent
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    ```

Si le service n'est pas reconnu, vous pouvez spécifier manuellement le port :

!!! info "Ajouter le port au lieu du nom du service"

    ```yaml
    firewall-cmd --add-port=10051/tcp --permanent
    ```

???+ note

    "Firewalld is the replacement for iptables in RHEL-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps."
    Ubuntu makes use of UFW and is merely a frontend for iptables.

Une autre approche consiste à définir des zones de pare-feu dédiées à des cas
d'utilisation spécifiques. Par exemple...

!!! info "Créer une zone dans firewalld"

    ```yaml
    firewall-cmd --new-zone=postgresql-access --permanent
    ```

Vous pouvez valider la création de la zone en exécutant la commande suivante :

!!! info "Vérifier la création de la zone"

    ```yaml
    firewall-cmd --get-zones
    ```

block dmz drop external home internal nm-shared postgresql-access public trusted
work

L'utilisation de zones dans firewalld pour configurer les règles de pare-feu
pour PostgreSQL offre plusieurs avantages en termes de sécurité, de flexibilité
et de facilité de gestion. Voici pourquoi l'utilisation des zones est vivement
conseillé :

- **Contrôle d'accès granulaire :**
  - Les zones firewalld permettent différents niveaux de confiance pour
    différentes interfaces réseau et plages IP. Vous pouvez définir quels
    systèmes sont autorisés à se connecter à PostgreSQL en fonction de leur
    niveau de confiance.
- **Gestion simplifiée des règles :**
  - Au lieu de définir manuellement des règles iptables complexes, les zones
    fournissent un moyen organisé, de regrouper et de gérer les règles de
    pare-feu en fonction des scénarios d'utilisation.
- **Sécurité renforcée :**
  - En limitant l'accès de PostgreSQL à une zone spécifique, vous empêchez les
    connexions non autorisées à partir d'autres interfaces ou réseaux.
- **Configuration dynamique :**
  - firewalld prend en charge les configurations de règles permanentes et en
    cours d'exécution, ce qui permet d'apporter des modifications sans perturber
    les connexions existantes.
- **Prise en charge de plusieurs interfaces :**
  - Si le serveur possède plusieurs interfaces réseau, les zones permettent
    d'appliquer des stratégies de sécurité différentes pour chaque interface.

Si l'on regroupe toutes les informations précédentes, on obtient ce qui suit :

!!! info "Firewalld avec configuration de zone"

    ```yaml
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Lorsque la `source IP` est la seule adresse autorisée à établir une connexion
avec la base de données.

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
    ```yaml
    dnf install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```yaml
    sudo apt install chrony
    ```

Après l'installation, vérifiez que Chrony est activé et fonctionne en contrôlant
son état à l'aide de la commande suivante :

!!! info "Vérifier le statut de Chrony"

    ```yaml
    systemctl status chronyd
    ```

???+ Note "Qu'est-ce que apt ou dnf ?"

    dnf is a package manager used in Red Hat-based systems. If you're using another
    distribution, replace `dnf` with your appropriate package manager, such as `zypper`,
    `apt`, or `yum`.

???+ Note "qu'est-ce que Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Une fois Chrony installé, l'étape suivante consiste à s'assurer que le fuseau
horaire est correct. Vous pouvez visualiser votre configuration horaire actuelle
en utilisant la commande `timedatectl`:

!!! info "vérifier la configuration de l'heure"

    ```yaml
    timedatectl
    ```

    ``` yaml
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

!!! info "liste des fuseaux horaires"

    ```yaml
    timedatectl list-timezones
    ```

Cette commande affiche une liste des fuseaux horaires disponibles, vous
permettant de sélectionner celui qui est le plus proche de votre position. Par
exemple :

!!! info "Liste de tous les fuseaux horaires disponibles"

    ```yaml
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

    ```yaml
    timedatectl set-timezone Europe/Brussels
    ```

Pour vérifier que le fuseau horaire a été configuré correctement, utilisez à
nouveau la commande `timedatectl`:

!!! info "Vérifier l'heure et le fuseau horaire"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 16:13:35 CET
    Universal time: Thu 2023-11-16 15:13:35 UTC
    RTC time: Thu 2023-11-16 15:13:36
    **Time zone: Europe/Brussels (CET, +0100)**
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

### Vérification de la synchronisation de Chrony

Pour s'assurer que Chrony se synchronise avec les bons serveurs de temps, vous
pouvez exécuter la commande suivante :

!!! info "Vérifier chrony"

    ```yaml
    chronyc
    ```

Le résultat devrait ressembler à :

!!! info "Vérifiez votre sortie chrony"

    ```yaml
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Une fois dans le prompt de Chrony, tapez la commande suivante pour vérifier les
sources :

!!! info ""

    ```yaml
    chronyc> sources
    ```

Exemple de sortie :

!!! info "Vérifiez les sources de votre serveur de temps"

    ```bash
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

### Mise à jour des serveurs de temps

Pour mettre à jour les serveurs de temps, modifiez le fichier `/etc/chrony.conf`
pour les systèmes basés sur Red Hat, et si vous utilisez Ubuntu éditez
`/etc/chrony/chrony.conf`. Remplacez le serveur NTP existant par un autre plus
proche de votre emplacement.

Exemple de la configuration actuelle :

!!! info "exemple de configuration du ntp pool"

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

    Change the pools you want to a local time server:

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Après avoir effectué cette modification, redémarrez le service Chrony pour
appliquer la nouvelle configuration :

!!! info "redémarrer le service Chrony"

    ```yaml
    systemctl restart chronyd
    ```

### Vérification des serveurs de temps mis à jour

Vérifiez à nouveau les sources de temps pour vous assurer que les nouveaux
serveurs locaux sont utilisés :

!!! info "Vérifier les sources Chrony"

    ```yaml
    chronyc> sources
    ```

Exemple de résultat attendu avec des serveurs locaux :

!!! info "Exemple de sortie"

    ```yaml
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Ceci confirme que le système utilise maintenant des serveurs de temps locaux.

## Conclusion

Comme nous l'avons vu, avant même de considérer les paquets Zabbix, il faut
prêter attention à l'environnement dans lequel il fonctionnera. Un système
d'exploitation correctement configuré, un chemin ouvert à travers le pare-feu et
une gestion du temps précise ne sont pas de simples suggestions, mais des
éléments essentiels. Après avoir posé ces bases, nous pouvons maintenant
procéder en toute confiance à l'installation de Zabbix, en sachant que le
système sous-jacent est prêt pour la tâche.

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
