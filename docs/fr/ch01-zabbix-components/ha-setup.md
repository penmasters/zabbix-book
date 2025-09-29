---
description : | Ce chapitre du livre Zabbix, intitulé « HA Setup », explique
comment configurer un cluster Zabbix `High Availability` (HA) pour assurer une
surveillance continue. Il détaille une installation utilisant deux serveurs
Zabbix avec une seule base de données pour créer un système de basculement
transparent. Le guide couvre l'installation et la configuration du cluster
Zabbix, y compris l'utilisation de Keepalived pour gérer une IP virtuelle (VIP)
pour le frontend, ce qui garantit un service ininterrompu. Le chapitre fournit
des instructions étape par étape pour l'ensemble du processus, de la
configuration des serveurs à la vérification du bon fonctionnement de la
configuration HA.
---

# Configuration HA

Dans cette section, nous allons configurer Zabbix en haute disponibilité (HA).
Cette fonctionnalité, introduite dans Zabbix 6, est une amélioration cruciale
qui garantit la poursuite de la surveillance même si un serveur Zabbix tombe en
panne. Avec HA, lorsqu'un serveur Zabbix tombe en panne, un autre peut prendre
le relais de manière transparente.

Pour ce guide, nous utiliserons deux serveurs Zabbix et une base de données,
mais la configuration permet d'ajouter d'autres serveurs Zabbix si nécessaire.

![Configuration HA](./ha-setup/ch01-HA-setup.png)

_1.1 Configuration HA_

Il est important de noter que la configuration de Zabbix HA est simple,
fournissant une redondance sans fonctionnalités complexes telles que
l'équilibrage de charge.

Au même titre que dans notre configuration de base, nous allons documenter les
détails clés des serveurs dans cette configuration HA. Vous trouverez ci-dessous
la liste des serveurs et l'endroit où ajouter leurs adresses IP respectives pour
plus de commodité :

| Serveur          | Adresse IP |
| ---------------- | ---------- |
| Serveur Zabbix 1 |            |
| Serveur Zabbix 2 |            |
| Base de données  |            |
| IP virtuelle     |            |

???+ note

    Our database (DB) in this setup is not configured for HA. Since it's not a
    Zabbix component, you will need to implement your own solution for database
    HA, such as a HA SAN or a database cluster setup. A DB cluster configuration
    is out of the scope of this guide and unrelated to Zabbix, so it will not be
    covered here.

---

## Installer la base de données

Reportez-vous au chapitre [_Installation de base_](basic-installation.md) pour
obtenir des instructions détaillées sur la configuration de la base de données.
Ce chapitre fournit des conseils étape par étape sur l'installation d'une base
de données PostgreSQL ou MariaDB sur un nœud dédié fonctionnant sous Ubuntu ou
Rocky Linux.

---

## Installation du cluster Zabbix

La mise en place d'un cluster Zabbix consiste à configurer plusieurs serveurs
Zabbix pour qu'ils fonctionnent ensemble et offrent une haute disponibilité.
Bien que le processus soit similaire à la configuration d'un seul serveur
Zabbix, des étapes de configuration supplémentaires sont nécessaires pour
activer la haute disponibilité (HA).

Ajoutez les dépôts Zabbix à vos serveurs.

Tout d'abord, ajoutez le dépôt Zabbix à vos deux serveurs Zabbix :

!!! info "ajouter le dépôt zabbix"

    Redhat

    ``` yaml
    rpm -Uvh https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
    dnf clean all
    ```

    Ubuntu

    ``` yaml
    sudo wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo apt update
    ```

Une fois cela fait, nous pouvons installer les paquets du serveur zabbix.

!!! info "installer les paquets du serveur Zabbix"

    Redhat

    ``` yaml
    dnf install zabbix-server-pgsql
    ```
    or if your database is MySQL or MariaDB
    ```
    dnf install zabbix-server-mysql
    ```

    Ubuntu

    ``` yaml
    sudo apt install zabbix-server-pgsql
    ```
    or if your database is MySQL or MariaDB
    ``` yaml
    sudo apt install zabbix-server-mysql
    ```

---

### Configuration du serveur Zabbix 1

Modifiez le fichier de configuration du serveur Zabbix,

!!! info "éditer le fichier de configuration du serveur"

    ``` yaml
    sudo vi /etc/zabbix/zabbix_server.conf
    ```

Mettez à jour les lignes suivantes pour vous connecter à la base de données :

!!! info ""

    ``` yaml
    DBHost=<zabbix db ip>
    DBName=<name of the zabbix DB>
    DBUser=<name of the db user>
    DBSchema=<db schema for the PostgreSQL DB>
    DBPassword=<your secret password>
    ```

Configurer les paramètres HA pour ce serveur :

!!! info ""

    ```yaml
    HANodeName=zabbix1 (or choose a name you prefer)
    ```

Spécifier l'adresse du serveur frontend pour les scénarios de basculement :

!!! info ""

    ``` yaml
    NodeAddress=<Zabbix server 1 ip>:10051
    ```

---

### Configuration de Zabbix Server 2

Répétez les étapes de configuration pour le deuxième serveur Zabbix. Ajustez les
champs `HANodeName` et `NodeAddress` si nécessaire pour ce serveur.

---

### Démarrage du serveur Zabbix

Après avoir configuré les deux serveurs, activez et démarrez le service
zabbix-server sur chacun d'eux :

!!! info "redémarrer le service zabbix-server"

    ```
    sudo systemctl enable zabbix-server --now
    ```

???+ note

    The `NodeAddress` must match the IP or FQDN name of the Zabbix server node.
    Without this parameter the Zabbix front-end is unable to connect to the active
    node. The result will be that the frontend is unable to display the status
    the queue and other information.

---

### Vérification de la configuration

Vérifiez les fichiers journaux des deux serveurs pour vous assurer qu'ils ont
démarré correctement et qu'ils fonctionnent dans leurs modes HA respectifs.

Sur le premier serveur :

!!! info "vérifier les journaux pour les messages HA"

    ``` yaml
    sudo grep HA /var/log/zabbix/zabbix_server.log
    ```

Dans les journaux du système, vous devriez observer les entrées suivantes,
indiquant l'initialisation du gestionnaire de haute disponibilité (HA) :

!!! info ""

    ``` yaml
    22597:20240309:155230.353 starting HA manager
    22597:20240309:155230.362 HA manager started in active mode
    ```

Ces messages confirment que le processus HA manager a démarré et a assumé le
rôle actif. Cela signifie que l'instance Zabbix est maintenant le nœud principal
dans le cluster HA, gérant toutes les opérations de surveillance. Si un
événement de basculement se produit, un autre nœud en attente prendra le relais
en fonction de la stratégie HA configurée.

Sur le deuxième serveur (et tout autre nœud supplémentaire) :

!!! info ""

    ``` yaml
    grep HA /var/log/zabbix/zabbix_server.log
    ```

Dans les journaux du système, les entrées suivantes indiquent l'initialisation
du gestionnaire de haute disponibilité (HA) :

!!! info ""

    ```yaml
    22304:20240309:155331.163 starting HA manager
    22304:20240309:155331.174 HA manager started in standby mode
    ```

Ces messages confirment que le processus du gestionnaire HA a été lancé avec
succès en mode veille. Cela suggère que le nœud est opérationnel mais qu'il
n'agit pas actuellement en tant qu'instance HA active, en attendant d'autres
transitions d'état basées sur la stratégie HA configurée.

À ce stade, votre cluster Zabbix est configuré correctement pour la haute
disponibilité (HA). Les journaux du système confirment que le gestionnaire HA a
été initialisé et qu'il fonctionne en mode veille, ce qui indique que les
mécanismes de basculement sont en place. Cette configuration garantit une
surveillance ininterrompue, même en cas de défaillance d'un serveur, en
permettant des transitions de rôle automatiques basées sur la configuration HA.

---

## Installation du frontend

Avant de procéder à l'installation et à la configuration du serveur web, il est
essentiel d'installer Keepalived. Keepalived permet l'utilisation d'une IP
virtuelle (VIP) pour les services frontaux, assurant un basculement transparent
et la continuité du service. Il fournit un cadre robuste pour l'équilibrage de
la charge et la haute disponibilité, ce qui en fait un composant essentiel dans
le maintien d'une infrastructure résiliente.

---

### Mise en place de keepalived

Commençons donc. Sur nos deux serveurs, nous devons installer keepalived.

!!! info "Installation de keepalived"

    Redhat
    ``` yaml
    dnf install keepalived
    ```

    Ubuntu
    ``` yaml
    sudo apt install keepalived
    ```

Next, we need to modify the Keepalived configuration on both servers. While the
configurations will be similar, each server requires slight adjustments. We will
begin with Server 1. To edit the Keepalived configuration file, use the
following command:

!!! info "edit the keepalived config"

    RedHat and Ubuntu
    ``` yaml
    sudo vi /etc/keepalived/keepalived.conf
    ```

If the file contains any existing content, it should be cleared and replaced
with the following lines :

!!! info ""

    ```yaml
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

    Replace `enp0s1` with the interface name of your machine and replace the `password`
    with something secure. For the virtual_ipaddress use a free IP from your network.
    This will be used as our VIP.

We can now do the same modification on our `second` Zabbix server. Delete
everything again in the same file like we did before and replace it with the
following lines:

!!!info ""

    ``` yaml
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

Just as with our 1st Zabbix server, replace `enp0s1` with the interface name of
your machine and replace the `password` with your password and fill in the
virtual_ipaddress as used before.

This ends the configuration of keepalived. We can now continue adapting the
frontend.

---

### Install and configure the frontend

On both servers we can run the following commands to install our web server and
the zabbix frontend packages:

!!! info "install web server and config"

    RedHat
    ```yaml
    dnf install nginx zabbix-web-pgsql zabbix-nginx-conf
    ```

    Ubuntu
    ```yaml
    sudo apt install nginx zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```

Additionally, it is crucial to configure the firewall. Proper firewall rules
ensure seamless communication between the servers and prevent unexpected
failures. Before proceeding, verify that the necessary ports are open and apply
the required firewall rules accordingly.

!!! info "configure the firewall"

    RedHat
    ```yaml
    firewall-cmd --add-service=http --permanent
    firewall-cmd --add-service=zabbix-server --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    sudo ufw allow 80/tcp
    ```

With the configuration in place and the firewall properly configured, we can now
start the Keepalived service. Additionally, we should enable it to ensure it
automatically starts on reboot. Use the following commands to achieve this:

!!! info "start and enable keepalived"

    RedHat and Ubuntu
    ```yaml
    sudo systemctl enable keepalived nginx --now
    ```

---

### Configure the web server

The setup process for the frontend follows the same steps outlined in the `Basic
Installation` section under [Installing the
Frontend](basic-installation.md/#installing-the-frontend). By adhering to these
established procedures, we ensure consistency and reliability in the deployment.

???+ warning

    Ubuntu users need to use the VIP in the setup of Nginx, together with the local
    IP in the listen directive of the config.

???+ note

    Don't forget to configure both front-ends. Also this is a new setup. Keep in
    mind that with an existing setup we need to comment out the lines  `$ZBX_SERVER`
    and `$ZBX_SERVER_PORT`. Our frontend will check what node is active by reading
    the node table in the database.

!!! info ""

    ```yaml
    select * from ha_node;
    ```
    ```sql
    zabbix=# select * from ha_node;
             ha_nodeid         |  name   |   address       | port  | lastaccess | status |       ha_sessionid
    ---------------------------+---------+-----------------+-------+------------+--------+---------------------------
     cm8agwr2b0001h6kzzsv19ng6 | zabbix1 | xxx.xxx.xxx.xxx | 10051 | 1742133911 |      0 | cm8apvb0c0000jkkzx1ojuhst
     cm8agyv830001ell0m2nq5o6n | zabbix2 | localhost       | 10051 | 1742133911 |      3 | cm8ap7b8u0000jil0845p0w51
    (2 rows)
    ```

In this instance, the node `zabbix2` is identified as the active node, as
indicated by its status value of `3`, which designates an active state. The
possible status values are as follows:

- `0` – Multiple nodes can remain in standby mode.
- `1` – A previously detected node has been shut down.
- `2` – A node was previously detected but became unavailable without a proper
  shutdown.
- `3` – The node is currently active.

This classification allows for effective monitoring and state management within
the cluster.

---

### Verify the correct working

To verify that the setup is functioning correctly, access your `Zabbix server`
using the Virtual IP (VIP). Navigate to Reports → System Information in the
menu. At the bottom of the page, you should see a list of servers, with at least
one marked as active. The number of servers displayed will depend on the total
configured in your HA setup.

![1st active frontend](ha-setup/ch01-HA-check1.png)

_1.2 verify HA_

Shut down or reboot the active frontend server and observe that the `Zabbix
frontend` remains accessible. Upon reloading the page, you will notice that the
other `frontend server` has taken over as the active instance, ensuring an
almost seamless failover and high availability.

![2st active frontend](ha-setup/ch01-HA-check2.png)

_1.3 verify HA_

In addition to monitoring the status of HA nodes, Zabbix provides several
runtime commands that allow administrators to manage failover settings and
remove inactive nodes dynamically.

One such command is:

!!! info ""

    ```yaml
    zabbix_server -R ha_set_failover_delay=10m
    ```

This command adjusts the failover delay, which defines how long Zabbix waits
before promoting a standby node to active status. The delay can be set within a
range of **10 seconds** to **15 minutes**.

To remove a node that is either **stopped** or **unreachable**, the following
runtime command must be used:

!!! info ""

    ```yaml
    zabbix_server -R ha_remove_node=`zabbix1`
    ```

Executing this command removes the node from the HA cluster. Upon successful
removal, the output confirms the action:

!!! info ""

    ```yaml
    Removed node "zabbix1" with ID "cm8agwr2b0001h6kzzsv19ng6"
    ```

If the removed node becomes available again, it can be added back automatically
when it reconnects to the cluster. These runtime commands provide flexibility
for managing high availability in Zabbix without requiring a full restart of the
`zabbix_server` process.

---

## Conclusion

In this chapter, we have successfully set up a high-availability (HA) Zabbix
environment by configuring both the Zabbix server and frontend for redundancy.
We first established HA for the Zabbix server, ensuring that monitoring services
remain available even in the event of a failure. Next, we focused on the
frontend, implementing a Virtual IP (VIP) with Keepalived to provide seamless
failover and continuous accessibility.

Additionally, we configured the firewall to allow Keepalived traffic and ensured
that the service starts automatically after a reboot. With this setup, the
Zabbix frontend can dynamically switch between servers, minimizing downtime and
improving reliability.

While database HA is an important consideration, it falls outside the scope of
this setup. However, this foundation provides a robust starting point for
building a resilient monitoring infrastructure that can be further enhanced as
needed.

---

## Questions

1. What is Zabbix High Availability (HA), and why is it important?
2. How does Zabbix determine which node is active in an HA setup?
3. Can multiple Zabbix nodes be active simultaneously in an HA cluster? Why or
   why not?
4. What configuration file(s) are required to enable HA in Zabbix?

---

## URL utiles

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
- <https://www.zabbix.com/documentation/7.2/en/manual/concepts/server/ha>
