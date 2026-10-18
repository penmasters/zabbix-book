---
description: |
    Cette section du livre Zabbix intitulée "Installation du serveur Zabbix" 
    vous guide tout au long de l'installation et de la configuration du serveur 
    Zabbix sur diverses distributions Linux. Elle couvre l'installation du paquet 
    du serveur Zabbix, la configuration des paramètres de connexion à la base de 
    données et la mise en place du pare-feu pour autoriser les connexions entrantes 
    vers le serveur Zabbix. De plus, elle fournit des instructions pour démarrer 
    et activer le service du serveur Zabbix, valider la configuration et vérifier 
    le fichier de journal du serveur pour tout problème.
tags: [débutant]
---

# Installation du serveur Zabbix

Maintenant que nous avons ajouté le dépôt Zabbix avec les logiciels nécessaires,
nous sommes prêts à installer à la fois le serveur Zabbix et le serveur web. 
Il est important de noter que le serveur web n'a pas besoin d'être installé sur
la même machine que le serveur Zabbix ; ils peuvent être hébergés sur des systèmes
différents si nécessaire.

Pour installer les composants du serveur Zabbix, exécutez la commande suivante :

!!! info "Installez le serveur zabbix"

    Red Hat
    ``` bash
    # For MySQL/MariaDB backend:
    dnf install zabbix-server-mysql
    # For PostgreSQL backend:
    dnf install zabbix-server-pgsql
    ```


    SUSE
    ``` bash
    # For MySQL/MariaDB backend:
    zypper install zabbix-server-mysql
    # For PostgreSQL backend:
    zypper install zabbix-server-pgsql
    ``` 


    Ubuntu
    ``` bash
    # For MySQL/MariaDB backend:
    sudo apt install zabbix-server-mysql
    # For PostgreSQL backend:
    sudo apt install zabbix-server-pgsql
    ```


Après une installation réussie du paquet serveur Zabbix, nous devons configurer 
le serveur Zabbix pour qu'il se connecte à la base de données. Cela nécessite la 
modification du fichier de configuration du serveur Zabbix.

Le fichier de configuration du serveur Zabbix offre l'option d'inclure des fichiers
de configuration supplémentaires pour les paramètres personnalisés. Pour un environnement
en production, il est souvent préférable d'éviter la modification directe du fichier 
de configuration original. Au lieu de cela, vous pouvez créer et inclure des fichiers 
de configuration séparés pour tout paramètre supplémentaire ou modifié. Cette approche 
assure que votre fichier de configuration original reste inchangé, ce qui est particulièrement
utile lors des mises à niveau ou de la gestion des configurations avec des outils tels 
qu'Ansible, Puppet ou SaltStack.

Sur SUSE 16 et versions ultérieures, cette fonctionnalité est déjà activée et configurée 
par défaut. (voir aussi [https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Par conséquent, sur les systèmes SUSE, le fichier de configuration du serveur Zabbix se
trouve à `/usr/etc/zabbix/zabbix_server.conf` et est configuré pour inclure tous les fichiers 
`.conf` du répertoire `/etc/zabbix_server/zabbix_server.d/`.

Sur d'autres distributions, vous devrez peut-être l'activer manuellement :

Pour activer cette fonctionnalité, assurez-vous que la ligne suivante existe et n'est pas
commentée (avec un `#` devant) dans `/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```


Le chemin `/etc/zabbix/zabbix_server.d/` devrait déjà avoir été créé par le
paquet installé, mais assurez-vous qu'il existe réellement.

Nous allons maintenant créer un fichier de configuration personnalisé `database.conf` dans 
le répertoire `/etc/zabbix/zabbix_server.d/` qui contiendra nos paramètres de connexion à la base de données :

!!! info "Ajoutez les paramètres de connexion à la base de données Zabbix"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```


    Ajoutez les lignes suivantes dans le fichier de configuration pour correspondre 
    à votre configuration de base de données :

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```


Remplacez `<database-host>`, `<database-name>`, `<database-schema>`, 
`<database-user>`, `<database-password>` et `<database-port>` par les valeurs appropriées pour votre
configuration. Cela garantit que le serveur Zabbix peut communiquer avec votre base de données.

Assurez-vous qu'il n'y a pas de `#` (symbole de commentaire) devant les paramètres 
de configuration, car Zabbix traitera les lignes commençant par `#` comme des commentaires,
les ignorant lors de l'exécution. De plus, vérifiez attentivement pour éviter toute duplication
des lignes de configuration ; si plusieurs lignes ont le même paramètre, Zabbix utilisera la valeur 
de la dernière occurrence.

Pour notre configuration, la configuration ressemblera à ceci :

!!! example "Exemple de fichier database.conf"

    MariaDB/MySQL:
    ```ini
    # MariaDB database configuration
    DBHost=<ip or dns of your MariaDB server>
    DBName=zabbix
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=3306
    ```


    PostgreSQL:
    ```ini
    # PostgreSQL database configuration
    DBHost=<ip or dns of your PostgreSQL server>
    DBName=zabbix
    DBSchema=zabbix_server
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=5432
    ```


!!! note "Pour PostgreSQL en haute disponibilité (HA)"

    Avec Zabbix 8.0, il est maintenant possible d'ajouter plus d'un IP pour DBHost. De cette 
    manière, il est possible de configurer un ensemble de base de données en haute disponibilité
    avec PostgreSQL sans avoir besoin d'utiliser un équilibreur de charge. Zabbix détectera la 
    base de données active lui-même. Exemple :
    DBHost=192.168.10.2:5432,192.168.10.3:5432

Dans cet exemple :

- `DBHost` fait référence à l'hôte où votre base de données est en cours d'exécution (utilisez 
  localhost si elle se trouve sur la même machine).
- `DBName` est le nom de la base de données Zabbix.
- `DBSchema` est le nom du schéma utilisé dans PostgreSQL (nécessaire uniquement pour PostgreSQL).
- `DBUser` est l'utilisateur de la base de données.
- `DBPassword` est le mot de passe pour l'utilisateur de la base de données.
- `DBPort` est le numéro de port sur lequel votre serveur de base de données écoute (par défaut 
  pour MySQL/MariaDB c'est 3306 et PostgreSQL c'est 5432).

Assurez-vous que les paramètres reflètent la configuration de votre environnement de base de données.

---

## Configurer le pare-feu pour autoriser les connexions Zabbix trapper

Sur votre machine serveur Zabbix, nous devons nous assurer que le pare-feu est configuré
pour autoriser les connexions entrantes vers le serveur Zabbix.

Votre serveur Zabbix doit accepter des connexions entrantes à partir des agents, 
des envois et des proxys Zabbix. Par défaut, Zabbix utilise le port `10051/tcp` pour ces 
connexions. Pour autoriser ces connexions, vous devez ouvrir ce port dans votre pare-feu.

!!! info "Ouvrez le pare-feu pour zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```


Si le service n'est pas reconnu en utilisant `firewall-cmd --add-service`, vous pouvez 
spécifier manuellement le port :

!!! info "Ajoutez le port au lieu du nom de service"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```


---

## Démarrer le serveur Zabbix

Avec la configuration mise à jour du serveur Zabbix pour se connecter à votre base 
de données, vous pouvez maintenant démarrer et activer le service du serveur Zabbix. 
Exécutez la commande suivante pour activer le service du serveur Zabbix et configurer
son lancement automatique au démarrage :

???+ note

    Avant de redémarrer le serveur Zabbix après avoir modifié sa configuration, il est
    considéré comme une bonne pratique de valider la configuration pour éviter les problèmes 
    potentiels. Lancer un contrôle de configuration permet de détecter tout problème avant,
    évitant ainsi toute interruption causée par une configuration invalide. Cela peut être 
    accompli en utilisant la commande suivante : `zabbix-server -T`

!!! info "Activez et démarrez le service zabbix-server"

    Red Hat, SUSE et Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```


Cette commande démarrera immédiatement le service du serveur Zabbix et le configurera 
pour qu'il se lance au démarrage du système. Pour vérifier que le serveur Zabbix fonctionne correctement,
consultez le fichier de journal pour tout message. Vous pouvez afficher les dernières entrées dans
le fichier de journal `Zabbix server` en utilisant :

!!! info "Vérifiez le fichier de journal"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```


Recherchez des messages indiquant que le serveur a démarré avec succès. Si des problèmes 
existent, le fichier de journal fournira des détails pour aider à la résolution des problèmes.

!!! example "Exemple d'output"

    ```
    12074:20250225:145333.529 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
    12074:20250225:145333.530 ****** Enabled features ******
    12074:20250225:145333.530 SNMP monitoring:           YES
    12074:20250225:145333.530 IPMI monitoring:           YES
    12074:20250225:145333.530 Web monitoring:            YES
    12074:20250225:145333.530 VMware monitoring:         YES
    12074:20250225:145333.530 SMTP authentication:       YES
    12074:20250225:145333.530 ODBC:                      YES
    12074:20250225:145333.530 SSH support:               YES
    12074:20250225:145333.530 IPv6 support:              YES
    12074:20250225:145333.530 TLS support:               YES
    12074:20250225:145333.530 ******************************
    12074:20250225:145333.530 using configuration file: /etc/zabbix/zabbix_server.conf
    12074:20250225:145333.545 current database version (mandatory/optional): 08000000/08000000
    12074:20250225:145333.545 required mandatory version: 08000000
    12075:20250225:145333.557 starting HA manager
    12075:20250225:145333.566 HA manager started in active mode
    12074:20250225:145333.567 server #0 started [main process]
    12076:20250225:145333.567 server #1 started [service manager #1]
    12077:20250225:145333.567 server #2 started [configuration syncer #1]
    12078:20250225:145333.718 server #3 started [alert manager #1]
    12079:20250225:145333.719 server #4 started [alerter #1]
    12080:20250225:145333.719 server #5 started [alerter #2]
    12081:20250225:145333.719 server #6 started [alerter #3]
    12082:20250225:145333.719 server #7 started [preprocessing manager #1]
    12083:20250225:145333.719 server #8 started [lld manager #1]
    ```


Si une erreur est survenue et que le serveur n'a pas pu se connecter à la base de données, vous verrez quelque chose comme ceci dans le fichier de journal du serveur :

!!! example "Exemple de log avec des erreurs"

    ```
    12068:20250225:145309.018 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
    12068:20250225:145309.018 ****** Enabled features ******
    12068:20250225:145309.018 SNMP monitoring:           YES
    12068:20250225:145309.018 IPMI monitoring:           YES
    12068:20250225:145309.018 Web monitoring:            YES
    12068:20250225:145309.018 VMware monitoring:         YES
    12068:20250225:145309.018 SMTP authentication:       YES
    12068:20250225:145309.018 ODBC:                      YES
    12068:20250225:145309.018 SSH support:               YES
    12068:20250225:145309.018 IPv6 support:              YES
    12068:20250225:145309.018 TLS support:               YES
    12068:20250225:145309.018 ******************************
    12068:20250225:145309.018 using configuration file: /etc/zabbix/zabbix_server.conf
    12068:20250225:145309.027 [Z3005] query failed: [1146] Table 'zabbix.users' doesn't exist [select userid from users limit 1]
    12068:20250225:145309.027 cannot use database "zabbix": database is not a Zabbix database
    ```


Dans ce cas, vérifiez vos paramètres de connexion à la base de données dans le fichier
`/etc/zabbix/zabbix_server.d/database.conf` et assurez-vous que la base de données est correctement peuplée comme décrit 
dans les étapes précédentes. Vérifiez également les règles du pare-feu et, lorsque vous utilisez PostgreSQL,
assurez-vous que `pg_hba.conf` est configuré correctement pour autoriser les connexions
du serveur Zabbix.

Vérifions l'état du service zabbix-server pour nous assurer qu'il est activé afin de survivre à un redémarrage

!!! info "Vérifiez l'état du service zabbix-server"

    ```bash
    sudo systemctl status zabbix-server
    ```


???+ example "Exemple d'output"
    ```shell-session
    localhost:~> sudo systemctl status zabbix-server

    ● zabbix-server.service - Zabbix Server
         Loaded: loaded (/usr/lib/systemd/system/zabbix-server.service; enabled; preset: disabled)
         Active: active (running) since Tue 2025-02-25 14:53:33 CET; 26min ago
       Main PID: 12074 (zabbix_server)
          Tasks: 77 (limit: 24744)
         Memory: 71.5M
            CPU: 18.535s
         CGroup: /system.slice/zabbix-server.service
                 ├─12074 /usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf
                 ├─12075 "/usr/sbin/zabbix_server: ha manager"
                 ├─12076 "/usr/sbin/zabbix_server: service manager #1 [processed 0 events, updated 0 event tags, deleted 0 problems, synced 0 service updates, idle 5.027667 sec during 5.042628 sec]"
                 ├─12077 "/usr/sbin/zabbix_server: configuration syncer [synced configuration in 0.051345 sec, idle 10 sec]"
                 ├─12078 "/usr/sbin/zabbix_server: alert manager #1 [sent 0, failed 0 alerts, idle 5.030391 sec during 5.031944 sec]"
                 ├─12079 "/usr/sbin/zabbix_server: alerter #1 started"
                 ├─12080 "/usr/sbin/zabbix_server: alerter #2 started"
                 ├─12081 "/usr/sbin/zabbix_server: alerter #3 started"
                 ├─12082 "/usr/sbin/zabbix_server: preprocessing manager #1 [queued 0, processed 0 values, idle 5.023818 sec during 5.024830 sec]"
                 ├─12083 "/usr/sbin/zabbix_server: lld manager #1 [processed 0 LLD rules, idle 5.017278sec during 5.017574 sec]"
                 ├─12084 "/usr/sbin/zabbix_server: lld worker #1 [processed 1 LLD rules, idle 21.031209 sec during 21.063879 sec]"
                 ├─12085 "/usr/sbin/zabbix_server: lld worker #2 [processed 1 LLD rules, idle 43.195541 sec during 43.227934 sec]"
                 ├─12086 "/usr/sbin/zabbix_server: housekeeper [startup idle for 30 minutes]"
                 ├─12087 "/usr/sbin/zabbix_server: timer #1 [updated 0 hosts, suppressed 0 events in 0.017595 sec, idle 59 sec]"
                 ├─12088 "/usr/sbin/zabbix_server: http poller #1 [got 0 values in 0.000071 sec, idle 5 sec]"
                 ├─12089 "/usr/sbin/zabbix_server: browser poller #1 [got 0 values in 0.000066 sec, idle 5 sec]"
                 ├─12090 "/usr/sbin/zabbix_server: discovery manager #1 [processing 0 rules, 0 unsaved checks]"
                 ├─12091 "/usr/sbin/zabbix_server: history syncer #1 [processed 4 values, 3 triggers in 0.027382 sec, idle 1 sec]"
                 ├─12092 "/usr/sbin/zabbix_server: history syncer #2 [processed 0 values, 0 triggers in 0.000077 sec, idle 1 sec]"
                 ├─12093 "/usr/sbin/zabbix_server: history syncer #3 [processed 0 values, 0 triggers in 0.000076 sec, idle 1 sec]"
                 ├─12094 "/usr/sbin/zabbix_server: history syncer #4 [processed 0 values, 0 triggers in 0.000020 sec, idle 1 sec]"
                 ├─12095 "/usr/sbin/zabbix_server: escalator #1 [processed 0 escalations in 0.011627 sec, idle 3 sec]"
                 ├─12096 "/usr/sbin/zabbix_server: proxy poller #1 [exchanged data with 0 proxies in 0.000081 sec, idle 5 sec]"
                 ├─12097 "/usr/sbin/zabbix_server: self-monitoring [processed data in 0.000068 sec, idle 1 sec]"
    ```


Cela conclut notre chapitre sur l'installation et la configuration du serveur Zabbix.

---

## Conclusion

Avec une installation et une configuration réussies du serveur Zabbix, vous avez maintenant
établi le composant central de votre système de surveillance. Nous avons couvert l'installation 
du paquet du serveur Zabbix, la configuration des paramètres de connexion à la base de données 
et la mise en place du pare-feu pour autoriser les connexions entrantes vers le serveur Zabbix.
De plus, nous avons démarré et vérifié le service du serveur Zabbix.

Votre serveur Zabbix est maintenant prêt à communiquer avec les agents, les envois et les proxys 
Zabbix. Le prochain pas consiste à installer et configurer l'interface web Zabbix qui fournira
l'interface utilisateur pour interagir avec votre système de surveillance.

Passons au chapitre suivant pour mettre en place l'interface web Zabbix.

---

## Questions

1. Quelle version de Zabbix dois-je installer pour la compatibilité et la stabilité ?
2. Quels journaux Zabbix dois-je vérifier pour résoudre les problèmes courants ?

---

## Liens utiles

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)