---
description: |
    Mettre en place Zabbix High Availability avec des serveurs clusterisés, une base de données partagée et Keepalived pour la bascule du VIP—assurant un monitoring sans temps d'arrêt.
tags: [expert]
---

# Configuration HA

Dans cette section, nous allons mettre en place Zabbix dans une configuration High Availability (HA). Cette fonctionnalité native, introduite avec Zabbix 6, est une amélioration cruciale qui garantit le suivi continu même si un serveur Zabbix tombe en panne. Avec HA, lorsque l'un des serveurs Zabbix tombe en panne, un autre peut prendre la relève sans interruption.

Pour ce guide, nous utiliserons deux serveurs Zabbix et une base de données, mais la configuration permet d'ajouter plus de serveurs Zabbix si nécessaire.

![Configuration-HA](./ha-setup/ch01.10-HA-setup.png)

_1.10 Configuration HA_

Il est important de noter que la mise en place de Zabbix HA est simple, offrant une redondance sans des fonctionnalités complexes comme le balanceur de charge. Seul un nœud sera actif, tous les autres seront en attente. Tous les serveurs Zabbix en attente dans le cluster HA surveilleront le nœud actif via des battements de cœur utilisant la base de données partagée. Elle ne nécessite pas d'autres logiciels de clustering ou même de ports pare-feu pour le serveur Zabbix lui-même. Cependant, pour l'interface frontale, nous utiliserons Keepalived pour fournir une IP virtuelle (VIP) dans les cas de bascule.

Comme dans notre configuration de base, nous documenterons les détails clés des serveurs dans cette configuration HA. Voici la liste des serveurs et un espace pour ajouter leurs adresses IP respectives à votre convenance :

| Serveur          | Adresse IP |
| :-------------- | :--------- |
| Zabbix Server 1 |            |
| Zabbix Server 2 |            |
| Base de données  |            |
| IP virtuelle     |            |

???+ note

    Notre base de données (DB) dans cette configuration n'est pas configurée pour HA. Puisqu'il ne s'agit pas d'un composant Zabbix, vous devrez mettre en place votre propre solution pour la haute disponibilité de la base de données, comme un SAN HA ou une configuration de cluster de base de données. Une configuration de cluster de base de données est hors du champ d'application de ce guide et n'est pas liée à Zabbix, donc elle ne sera pas couverte ici.

---

## Installation de la base de données

Reportez-vous au chapitre [_Composants Zabbix : Base de données_](database.md) pour des instructions détaillées sur l'installation de la base de données. Ce chapitre fournit une guidance étape par étape pour installer soit PostgreSQL, soit MariaDB sur un nœud dédié exécutant Ubuntu, SUSE ou Rocky Linux. Les mêmes étapes d'installation s'appliquent lors de la configuration de la base de données pour cette configuration.

---

## Installation du cluster Zabbix

La mise en place d'un cluster Zabbix implique la configuration de plusieurs serveurs Zabbix pour qu'ils fonctionnent ensemble, fournissant une haute disponibilité. Bien que le processus soit similaire à celui de l'installation d'un seul serveur Zabbix, des étapes supplémentaires de configuration sont nécessaires pour activer HA (High Availability).

Commencez par préparer les systèmes et installer le serveur Zabbix sur tous les systèmes en suivant les étapes du chapitre _Composants Zabbix_ dans les sections [_Préparation du serveur pour Zabbix_](preparation.md) et [_Installation du serveur Zabbix_](zabbix-server.md).

Prenez note que :

- vous devez sauter l'étape de population de la base de données sur tous les serveurs Zabbix, à l'exception du premier serveur Zabbix car la base de données est partagée entre tous les serveurs Zabbix.
- vous devez sauter l'étape d'activation et de démarrage du service zabbix-server sur tous les serveurs comme nous le ferons plus tard après avoir configuré HA.
- vous devez vous assurer que tous les serveurs Zabbix peuvent se connecter au serveur de base de données. Par exemple, si vous utilisez PostgreSQL, assurez-vous que le fichier `pg_hba.conf` est configuré pour permettre les connexions à partir de tous les serveurs Zabbix.
- tous les serveurs Zabbix doivent utiliser le même nom de base de données, utilisateur et mot de passe pour se connecter à la base de données.
- tous les serveurs Zabbix doivent être de la même version majeure.

Une fois que tous les serveurs Zabbix sont installés et configurés pour accéder à la base de données, nous pouvons passer à la configuration HA.

---

### Configuration du serveur Zabbix 1

Ajoutez un nouveau fichier de configuration pour la configuration HA sur le premier serveur Zabbix :

!!! info "Ajouter la configuration du serveur Zabbix en mode haute disponibilité"

    ``` bash
    sudo vi /etc/zabbix/zabbix_server.d/high-availability.conf
    ```


    Ajoutez la ligne suivante dans le fichier de configuration pour activer le mode HA.

    ```ini
    HANodeName=zabbix1  # or choose a name you prefer
    ```


    Spécifiez l'adresse du nœud frontal pour les scénarios de bascule :

    ```ini
    NodeAddress=<Zabbix server 1 ip>:10051
    ```


???+ warning

    Le `NodeAddress` doit correspondre à l'IP ou au nom FQDN du serveur Zabbix. Sans ce paramètre, le front-end Zabbix ne peut pas se connecter au nœud actif et ne pourra donc pas afficher l'état de la file d'attente et d'autres informations.


---

### Configuration du serveur Zabbix 2

Répétez les étapes de configuration pour le deuxième serveur Zabbix. Ajustez le `HANodeName` et `NodeAddress` comme nécessaire pour ce serveur.

???+ example "Configuration haute disponibilité du serveur Zabbix 2 high-availability.conf"

    ```ini
    HANodeName=zabbix2  # or choose a name you prefer
    NodeAddress=<Zabbix server 2 ip>:10051
    ```


Vous pouvez ajouter plus de serveurs en répétant les mêmes étapes, en vous assurant que chaque serveur a un `HANodeName` unique et le bon `NodeAddress` configuré.

---

### Démarrage du serveur Zabbix

Après avoir configuré les deux serveurs, activez et démarrez le service zabbix-server sur chacun :

!!! info "Activer et démarrer le service zabbix-server"

    ```
    sudo systemctl enable zabbix-server --now
    ```


---

### Vérification de la configuration

Vérifiez les journaux des deux serveurs pour vous assurer qu'ils ont démarré correctement et fonctionnent en mode HA respectif.

Sur le premier serveur :

!!! info "Vérifier les journaux pour les messages HA"

    ``` bash
    sudo grep HA /var/log/zabbix/zabbix_server.log
    ```


Dans les journaux du système, vous devriez observer les entrées suivantes, indiquant l'initialisation de la gestionnaire High Availability (HA) :

???+ example "Messages de journal HA sur le nœud actif"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22597:20240309:155230.353 starting HA manager
    22597:20240309:155230.362 HA manager started in active mode
    ```


Ces messages de journal confirment que le processus gestionnaire HA a démarré et a pris en charge le rôle actif. Cela signifie que l'instance Zabbix est maintenant le nœud principal dans le cluster HA, gérant toutes les opérations de suivi. En cas d'événement de bascule, un autre nœud en attente prendra la relève selon la stratégie HA configurée.

Exécutez la même commande sur le deuxième serveur (et tout autre nœud supplémentaire) :

???+ example "Messages de journal HA sur le nœud en attente"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22304:20240309:155331.163 starting HA manager
    22304:20240309:155331.174 HA manager started in standby mode
    ```


Ces messages confirment que le processus gestionnaire HA a été invoqué et lancé avec succès en mode d'attente. Cela suggère que le nœud est opérationnel mais ne joue pas actuellement le rôle de nœud HA principal, attendant des transitions d'état supplémentaires basées sur la stratégie HA configurée.

À ce stade, votre cluster Zabbix est correctement configuré pour la haute disponibilité (HA). Les journaux du système confirment que le gestionnaire HA a été initialisé et fonctionne en mode d'attente, indiquant que les mécanismes de bascule sont en place. Cette configuration garantit un suivi ininterrompu même en cas d'échec du serveur, en permettant des transitions automatiques de rôle basées sur la configuration HA.

---

## Installation de l'interface frontale

Avant de procéder à l'installation et à la configuration du serveur web, il est essentiel d'installer un certain type de logiciel de clustering ou d'utiliser un balanceur de charge devant les interfaces frontales Zabbix pour pouvoir avoir une IP virtuelle partagée (VIP).

???+ note
    Il existe plusieurs options disponibles pour le logiciel de clustering et les balanceurs de charge, y compris Pacemaker, Corosync, HAProxy, F5 Big-Ip, Citrix NetScaler et diverses balises de charge cloud. Chacune de ces solutions offre une gamme de fonctionnalités et de capacités au-delà du simple partage d'une IP pour la bascule. Mais dans le cadre de ce guide, nous nous concentrerons sur une approche minimaliste pour assurer la haute disponibilité des interfaces frontales Zabbix en utilisant Keepalived.

Keepalived est comme un assistant qui s'assure qu'un ordinateur prend le relais si l'autre cesse de fonctionner. Il leur donne une IP magique partagée afin que les utilisateurs ne remarquent pas quand un serveur tombe en panne. Si le principal tombe, la sauvegarde saute immédiatement en prenant le contrôle de l'IP.

Keepalived est un type minimaliste de logiciel de clustering qui permet d'utiliser une (VIP) pour les services frontaux, assurant une bascule fluide et la continuité du service.

!!! warning "Haute disponibilité sur SUSE Linux Enterprise Server (SLES)"

    Sur SUSE Linux Enterprise Server (SLES), Keepalived n'est pas inclus dans l'abonnement par défaut donc non disponible dans les dépôts par défaut.

    Pour pouvoir installer et utiliser Keepalived de manière supportée sur SLES, vous devrez obtenir le supplémentaire 'SUSE Linux Enterprise High Availability Extension' (SLE HA). Cet abonnement donne accès aux paquets et mises à jour nécessaires pour Keepalived et d'autres composants haute disponibilité.
    Après avoir obtenu l'abonnement, vous pouvez activer les dépôts appropriés et procéder à l'installation de Keepalived comme indiqué dans ce guide :

    ```bash
    SUSEConnect -p sle-ha/16/x86_64 -r ADDITIONAL_REGCODE
    ```

    Où `ADDITIONAL_REGCODE` est le code d'enregistrement fourni avec votre abonnement 'SUSE Linux Enterprise High Availability Extension'.

---

### Configuration de keepalived

Sur tous les serveurs qui hébergeront l'interface frontale Zabbix, nous devons installer Keepalived. Comme mentionné précédemment, cela peut être fait sur des serveurs séparés pour diviser le rôle du serveur et de la frontale, mais dans ce guide, nous installerons Keepalived sur les deux serveurs Zabbix pour assurer une haute disponibilité à la fois de l'interface frontale et du serveur.

!!! info "Installer keepalived"

    Red Hat
    ```bash
    dnf install keepalived
    ```


    SUSE
    ```bash
    zypper install keepalived
    ```


    Ubuntu
    ```bash
    sudo apt install keepalived
    ```


Ensuite, nous devons modifier la configuration Keepalived sur tous les serveurs. Bien que les configurations soient similaires, chaque serveur nécessite des ajustements mineurs. Nous commencerons par le Serveur 1. Pour éditer le fichier de configuration Keepalived, utilisez la commande suivante :

!!! info "Éditer la configuration keepalived"

    ```bash
    sudo vi /etc/keepalived/keepalived.conf
    ```


Si le fichier contient du contenu existant, il doit être effacé et remplacé par les lignes suivantes :

!!! info ""

    ```
    vrrp_track_process track_nginx {
        process nginx
        weight 10
    }

    vrrp_instance VI_1 {
        state MASTER
        interface enp0s1
        virtual_router_id 51
        priority 244
        advert_int 1
        authentication {
            auth_type PASS
            auth_pass 12345
        }
        virtual_ipaddress {
            xxx.xxx.xxx.xxx
        }
        track_process {
             track_nginx
          }
    }
    ```


???+ warning

    Remplacez `enp0s1` par le nom de l'interface de votre machine et remplacez le `password` par quelque chose de sécurisé. Pour le `virtual_ipaddress` utilisez une IP libre de votre réseau. Cela sera utilisé comme notre VIP.Nous pouvons maintenant effectuer la même modification sur notre deuxième serveur Zabbix ou sur tout autre serveur ultérieur.
Supprimez à nouveau tout le contenu du fichier `/etc/keepalived/keepalived.conf` comme nous l'avons fait auparavant et remplacez-le par les lignes suivantes :

!!!info ""

    ```
    vrrp_track_process track_nginx {
          process nginx
          weight 10
    }

    vrrp_instance VI_1 {
        state BACKUP
        interface enp0s1
        virtual_router_id 51
        priority 243
        advert_int 1
        authentication {
            auth_type PASS
            auth_pass 12345
        }
        virtual_ipaddress {
           xxx.xxx.xxx.xxx
        }
        track_process {
             track_nginx
          }
    }
    ```


De même que pour notre premier serveur Zabbix, remplacez `enp0s1` par le nom de l'interface de votre machine et remplacez `password` par votre mot de passe. Remplissez également `virtual_ipaddress` comme précédemment.

Vérifiez que le pare-feu autorise le trafic Keepalived sur tous les serveurs. Le protocole VRRP est différent du protocole IP standard et utilise l'adresse multicast `224.0.0.18`. Par conséquent, nous devons explicitement autoriser ce trafic à travers le pare-feu. Exécutez les commandes suivantes sur tous les serveurs :

!!! info "Autorisez le trafic Keepalived à travers le pare-feu"

    Red Hat / SUSE
    ```yaml
    firewall-cmd --add-rich-rule='rule protocol value="vrrp" accept' --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```yaml
    sudo ufw allow to 224.0.0.18 comment ‘keepalived multicast’
    ```


Cela termine la configuration de Keepalived. Nous pouvons maintenant continuer l'adaptation du frontend.

---

### Installer et configurer le frontend

Installez le frontend Zabbix sur tous les serveurs Zabbix faisant partie du cluster en suivant les étapes décrites dans la section [_Installing the frontend_](zabbix-frontend.md).

???+ warning

    Les utilisateurs d'Ubuntu doivent utiliser l'adresse IP virtuelle (VIP) lors de la configuration de Nginx, avec l'adresse IP locale dans la directive listen du fichier de configuration.

???+ note

    Ne vous oubliez pas de configurer les deux front-ends. C'est une nouvelle installation. Gardez à l'esprit que pour une installation existante, nous devons commenter les lignes `$ZBX_SERVER` et `$ZBX_SERVER_PORT` dans `/etc/zabbix/web/zabbix.conf.php`. Notre frontend vérifiera quel nœud est actif en lisant la table des nœuds dans la base de données.

Vous pouvez vérifier le nœud actif en interrogeant la table `ha_node` dans la base de données Zabbix. Cette table contient des informations sur tous les nœuds du cluster HA, y compris leur statut. Pour vérifier l'état des nœuds, vous pouvez exécuter la requête SQL suivante :

!!! info ""

    ```sql
    select * from ha_node;

    ```


???+ example "Vérifiez la table ha_node dans une base de données PostgreSQL"

    ```psql
    zabbix=> select * from ha_node;
             ha_nodeid         |  name   |   address       | port  | lastaccess | status |       ha_sessionid
    ---------------------------+---------+-----------------+-------+------------+--------+---------------------------
     cm8agwr2b0001h6kzzsv19ng6 | zabbix1 | xxx.xxx.xxx.xxx | 10051 | 1742133911 |      0 | cm8apvb0c0000jkkzx1ojuhst
     cm8agyv830001ell0m2nq5o6n | zabbix2 | localhost       | 10051 | 1742133911 |      3 | cm8ap7b8u0000jil0845p0w51
    (2 rows)
    ```


Dans cet exemple, le nœud `zabbix2` est identifié comme étant actif, en fonction de sa valeur d'état `3` qui désigne un état actif. Les valeurs possibles pour l'état sont les suivantes :

- `0` – Plusieurs nœuds peuvent rester en mode veille.
- `1` – Un nœud détecté précédemment a été éteint.
- `2` – Un nœud a été détecté mais est devenu indisponible sans une extinction correcte.
- `3` – Le nœud est actuellement actif.

Cette classification permet un suivi efficace et la gestion des états au sein du cluster.

Une fois le frontend installé sur tous les serveurs, nous devons démarrer et activer le service Keepalived pour s'assurer qu'il démarre automatiquement à chaque redémarrage et commence à gérer l'adresse IP virtuelle (VIP) :

!!! info "Démarrer et activer keepalived"

    ```yaml
    sudo systemctl enable keepalived nginx --now
    ```



---

### Vérifier le bon fonctionnement

Pour vérifier que la configuration est correctement mise en place, accédez à votre serveur Zabbix en utilisant l'adresse IP virtuelle (VIP). Accédez à `Reports` | `System Information` dans le menu. En bas de la page, vous devriez voir une liste des serveurs, avec au moins un marqué comme actif. Le nombre de serveurs affichés dépendra du total configuré dans votre configuration HA.

![1er frontend actif](ha-setup/ch01.11-HA-check1.png)

_1.11 vérifier
HA_

Éteignez ou redémarrez le serveur frontend actif et observez que l'interface Zabbix reste accessible. En rechargeant la page, vous verrez que le deuxième serveur frontend a pris en charge comme instance active, assurant un basculement presque transparent et une haute disponibilité.

![2ème frontend actif](ha-setup/ch01.12-HA-check2.png)

_1.12 vérifier
HA_

En plus de surveiller l'état des nœuds HA, Zabbix fournit plusieurs commandes en temps réel qui permettent aux administrateurs de gérer les paramètres de basculement et d'effacer dynamiquement les nœuds inactifs.

Une telle commande est :

!!! info ""

    ```bash
    zabbix_server -R ha_set_failover_delay=10m
    ```


Cette commande ajuste le délai de basculement, qui définit combien de temps Zabbix attend avant de promouvoir un nœud en attente à l'état actif. Le délai peut être défini dans une plage allant de **10 secondes** à **15 minutes**.

Pour supprimer un nœud qui est soit **arrêté** soit **inatteignable**, la commande suivante doit être utilisée :

!!! info ""

    ```bash
    sudo zabbix_server -R ha_remove_node=`zabbix1`
    ```


L'exécution de cette commande retire le nœud du cluster HA. À l'issue d'une suppression réussie, la sortie confirme l'action :

!!! example "Suppression d'un nœud"

    ```shell-session
    localhost:~ # zabbix_server -R ha_remove_node=`zabbix1`
    Removed node "zabbix1" with ID "cm8agwr2b0001h6kzzsv19ng6"
    ```


Si le nœud supprimé devient à nouveau disponible, il peut être réintroduit automatiquement lorsqu'il se reconnecte au cluster. Ces commandes en temps réel offrent une flexibilité pour gérer la haute disponibilité dans Zabbix sans nécessiter un redémarrage complet du processus `zabbix_server`.

---

## Conclusion

Dans ce chapitre, nous avons mis en place avec succès un environnement Zabbix à haute disponibilité (HA) en configurant le serveur et le frontend Zabbix pour la redondance. Nous avons d'abord établi une HA pour le serveur Zabbix, assurant que les services de supervision restent disponibles même en cas d'échec. Ensuite, nous nous sommes concentrés sur le frontend, mettant en place une adresse IP virtuelle (VIP) avec Keepalived pour fournir un basculement transparent et une accessibilité continue.

De plus, nous avons configuré le pare-feu pour autoriser le trafic Keepalived et nous avons assuré que le service démarre automatiquement après un redémarrage. Avec cette configuration, l'interface Zabbix peut dynamiquement passer d'un serveur à l'autre, minimisant les temps d'inactivité et améliorant la fiabilité.

Bien que la haute disponibilité de la base de données soit une considération importante, elle est en dehors du cadre de cette configuration. Cependant, cette base fournit un point de départ robuste pour construire une infrastructure de supervision résiliente qui peut être améliorée au besoin.

---

## Questions

1. Qu'est-ce que la haute disponibilité (HA) Zabbix et pourquoi est-elle importante ?
2. Comment Zabbix détermine-t-il quel nœud est actif dans une configuration HA ?
3. Peuvent plusieurs nœuds Zabbix être actifs simultanément dans un cluster HA ? Pourquoi ou pourquoi pas ?
4. Quels fichiers de configuration sont nécessaires pour activer la haute disponibilité (HA) dans Zabbix ?

---

## Liens utiles

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
- <https://www.zabbix.com/documentation/current/en/manual/concepts/server/ha>