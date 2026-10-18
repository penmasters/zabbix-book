---
description: |
    Cette section du livre The Zabbix Book intitulée "Installation d'une base de données MariaDB"
    vous guide à travers l'installation de MariaDB en tant que backend de base de données pour Zabbix.
    Elle couvre deux méthodes d'installation : l'utilisation des paquets fournis par le vendeur
    d'OS ou les dépôts officiels MariaDB. La section comprend les étapes pour démarrer et sécuriser
    le serveur MariaDB, créer une base de données Zabbix avec des utilisateurs appropriés,
    et configurer les règles du pare-feu si nécessaire.
tags: [beginner]
---

# Installation d'une base de données MariaDB

Dans cette section, nous allons installer les paquets server et client MariaDB. Cela vous
permettra d'exécuter et de gérer MariaDB comme backend de base de données pour Zabbix.

Si vous préférez utiliser PostgreSQL en tant que backend de base de données,
vous pouvez sauter cette section et passer à la section [_Installation de la base de données PostgreSQL_](postgresql.md).

???+ tip "MySQL/Percona"
    Si vous préférez utiliser MySQL ou Percona au lieu de MariaDB, les étapes
    d'installation et de configuration sont très similaires. Généralement, vous remplacerez
    `mariadb` par `mysql` dans les noms des paquets et commandes.

## Installation du serveur MariaDB et du client à partir de paquets fournis par le vendeur d'OS

Pour installer la version par défaut du distributeur MariaDB server et client, exécutez
la commande suivante :

!!! info "Installation de la version distribuée de Mariadb"

    Red Hat
    ```bash
    dnf install mariadb-server
    ```


    SUSE
    ``` bash
    zypper install mariadb mariadb-client
    ```


    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```


Cette commande téléchargera et installera les paquets serveur et client, vous permettant de configurer,
gérer et interagir avec votre base de données MariaDB. Une fois l'installation terminée, vous pouvez passer à la section [_Démarrage de la base de données MariaDB_](#démarrage-de-la-base-de-données-mariadb).

---

## Installation du serveur MariaDB et du client à partir des dépôts officiels MariaDB

Si vous préférez installer MariaDB à partir des dépôts officiels MariaDB au lieu
des paquets fournis par le vendeur d'OS, la première étape consiste à ajouter le dépôt MariaDB
à votre système.

---

### Ajout du dépôt MariaDB
Pour créer le fichier de dépôt MariaDB, exécutez la commande suivante dans votre terminal :

!!! info "Définition du dépôt MariaDB"

    Red Hat
    ``` bash
    vi /etc/yum.repos.d/mariadb.repo
    ```


    SUSE
    ``` bash
    sudo vi /etc/zypp/repos.d/mariadb.repo
    ```


    Ubuntu
    ``` bash
    sudo apt install apt-transport-https curl
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp'

    sudo vi /etc/apt/sources.list.d/mariadb.sources
    ```


Cela ouvrira un éditeur de texte où vous pouvez entrer les détails de configuration du dépôt.
Une fois le dépôt configuré, vous pouvez procéder à l'installation de MariaDB en utilisant votre gestionnaire de paquets.

La dernière configuration peut être trouvée ici : [https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Voici un exemple de configuration pour les dépôts MariaDB 11.4 :

!!! example "Configuration du dépôt MariaDB"

    Red Hat
    ```ini
    # MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-02-21 10:15 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/rhel/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/rhel/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```


    SUSE
    ```ini
    # MariaDB 11.4 openSUSE repository list - created 2025-12-29 14:34 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/opensuse/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```


    Ubuntu
    ```  yaml
    # MariaDB 11.4 repository list - created 2025-02-21 11:42 UTC
    # https://mariadb.org/download/
    X-Repolib-Name: MariaDB
    Types: deb
    # deb.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # URIs: https://deb.mariadb.org/11.4/ubuntu
    URIs: https://mirror.bouwhuis.network/mariadb/repo/11.4/ubuntu
    Suites: noble
    Components: main main/debug
    Signed-By: /etc/apt/keyrings/mariadb-keyring.pgp
    ```


Après avoir enregistré le fichier, assurez-vous que tout est correctement configuré et que votre version préférée de MariaDB est compatible avec la version Zabbix pour éviter les problèmes d'intégration potentiels.

---

### Installation du serveur MariaDB et du client

Avec le dépôt MariaDB configuré, vous êtes maintenant prêt à installer les paquets server et client MariaDB.
Cela fournira les composants nécessaires pour exécuter et gérer votre base de données.

Pour installer le serveur et le client MariaDB, exécutez la commande suivante :

!!! info "Installation de MariaDB depuis le dépôt officiel"

    Red Hat
    ```bash
    dnf install MariaDB-server
    ```


    SUSE
    ```bash
    sudo rpm --import https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    sudo zypper install MariaDB-server MariaDB-client
    ```



    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```


Cette commande téléchargera et installera les paquets serveur et client, vous permettant de configurer,
gérer et interagir avec votre base de données MariaDB. Une fois l'installation terminée, vous pouvez passer à la section [_Démarrage de la base de données MariaDB_](#démarrage-de-la-base-de-données-mariadb).

---

## Démarrage de la base de données MariaDB

Maintenant que MariaDB est installé, nous devons activer le service pour qu'il démarre automatiquement
au démarrage et le démarrer immédiatement. Utilisez la commande suivante pour accomplir cela :

!!! info "Activation du service MariaDB"

    ```bash
    sudo systemctl enable mariadb --now
    ```


Cette commande activera et démarrera le service MariaDB, et puisque c'est la première fois que le service est démarré,
il initialisera le répertoire de base de données. Avec le service MariaDB maintenant en cours d'exécution, vous pouvez vérifier
le succès de l'installation en consultant la version de MariaDB à l'aide de la commande suivante :

!!! info "Vérification de la version de Mariadb"

    ```bash
    mariadb -V
    ```


La sortie attendue ressemblera à ceci :

???+ example "Exemple de version MariaDB"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb from 11.4.13-MariaDB, client 15.2 for Linux (aarch64) using  EditLine wrapper
    ```


Pour vous assurer que le service MariaDB fonctionne correctement, vous pouvez vérifier son statut
avec la commande suivante :

!!! info "Vérification du statut mariadb"

    ```bash
    sudo systemctl status mariadb
    ```


Vous devriez voir une sortie similaire à celle-ci, indiquant que le service MariaDB est actif et en cours d'exécution :

???+ example "Exemple de statut du service Mariadb"

    ```shell-session
    localhost:~ $ sudo systemctl status mariadb
    ● mariadb.service - MariaDB database server
         Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: disabled)
         Active: active (running) since Wed 2025-12-03 00:16:04 CET; 5s ago
           Docs: man:mysqld(8)
                 https://mariadb.com/kb/en/library/systemd/
        Process: 11148 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper install (code=exited, status=0/SUCCESS)
        Process: 11155 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper upgrade (code=exited, status=0/SUCCESS)
       Main PID: 11162 (mysqld)
         Status: "Taking your SQL requests now..."
          Tasks: 18 (limit: 4670)
            CPU: 340ms
         CGroup: /system.slice/mariadb.service
                 └─11162 /usr/sbin/mysqld --defaults-file=/etc/my.cnf --user=mysql --socket=/run/mysql/mysql.sock

    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Plugin 'FEEDBACK' is disabled.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Server socket created on IP: '127.0.0.1', port: '3306'.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] /usr/sbin/mysqld: ready for connections.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Version: '11.4.13-MariaDB'  socket: '/run/mysql/mysql.sock'  port: 3306  MariaDB package
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Buffer pool(s) load completed at 251203  0:16:04
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Started MariaDB database server.
    ```


Cela confirme que votre serveur MariaDB est opérationnel et prêt pour une configuration supplémentaire.

---

## Sécurisation de la base de données MariaDB

Pour renforcer la sécurité de votre serveur MariaDB, il est essentiel d'éliminer les bases de données test inutiles,
les utilisateurs anonymes et de définir un mot de passe root. Cela peut être fait en utilisant le script mariadb-secure-installation,
qui fournit une procédure guidée pour sécuriser votre base de données.

Exécutez la commande suivante :

!!! info "Sécurisation de l'installation Mariadb"

    ```bash
    sudo mariadb-secure-installation
    ```


Le script mariadb-secure-installation vous guidera à travers plusieurs étapes clés :

1. Définir un mot de passe root si aucun n'est déjà défini.
2. Éliminer les utilisateurs anonymes.
3. Interdire les connexions root à distance.
4. Éliminer la base de données test.
5. Recharger les tables d'autorisations pour garantir que les modifications prennent effet.

Une fois terminé, votre instance MariaDB sera significativement plus sécurisée.

!!! example "Exemple de sortie du script mariadb-secure-installation"

    ```shell-session
    localhost:~ $ sudo mariadb-secure-installation
    NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
          SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!

    In order to log into MariaDB to secure it, we'll need the current
    password for the root user. If you've just installed MariaDB, and
    haven't set the root password yet, you should just press enter here.

    Enter current password for root (enter for none):
    OK, successfully used password, moving on...

    Setting the root password or using the unix_socket ensures that nobody
    can log into the MariaDB root user without the proper authorisation.

    You already have your root account protected, so you can safely answer 'n'.

    Switch to unix_socket authentication [Y/n] n
     ... skipping.

    You already have your root account protected, so you can safely answer 'n'.

    Change the root password? [Y/n] y
    New password:
    Re-enter new password:
    Password updated successfully!
    Reloading privilege tables..
     ... Success!


    By default, a MariaDB installation has an anonymous user, allowing anyone
    to log into MariaDB without having to have a user account created for
    them.  This is intended only for testing, and to make the installation
    go a bit smoother.  You should remove them before moving into a
    production environment.

    Remove anonymous users? [Y/n] y
     ... Success!

    Normally, root should only be allowed to connect from 'localhost'.  This
    ensures that someone cannot guess at the root password from the network.

    Disallow root login remotely? [Y/n] y
     ... Success!

    By default, MariaDB comes with a database named 'test' that anyone can
    access.  This is also intended only for testing, and should be removed
    before moving into a production environment.

    Remove test database and access to it? [Y/n] y
     - Dropping test database...
     ... Success!
     - Removing privileges on test database...
     ... Success!

    Reloading the privilege tables will ensure that all changes made so far
    will take effect immediately.

    Reload privilege tables now? [Y/n] y
     ... Success!

    Cleaning up...

    All done!  If you've completed all of the above steps, your MariaDB
    installation should now be secure.

    Thanks for using MariaDB!
    ```


Vous êtes maintenant prêt à configurer la base de données pour Zabbix.

---

## Création de l'instance de base de données Zabbix

Avec MariaDB maintenant configurée et sécurisée, nous pouvons passer à la création de la base de données
pour Zabbix. Cette base de données stockera toutes les informations nécessaires liées au serveur Zabbix,
y compris des informations de configuration et des données de supervision.

Suivez ces étapes pour créer la base de données Zabbix :

Connectez-vous à l'interface shell MariaDB en tant qu'utilisateur root :
Vous serez invité à entrer le mot de passe root que vous avez défini lors du processus mariadb-secure-installation.

!!! info "Connexion à Mariadb en tant qu'utilisateur root"

    ```bash
    mariadb -uroot -p
    ```


Une fois connecté à l'interface shell MariaDB, exécutez la commande suivante pour créer une
base de données Zabbix :

!!! info "Création de la base de données"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```


???+ note "Qu'est-ce que utf8mb4"

     utf8mb4 est une mise en œuvre correcte de UTF-8 dans MySQL/MariaDB, supportant tous
     les caractères Unicode, y compris les emojis. L'ancien jeu de caractères utf8 dans MySQL/MariaDB
     ne prend en charge que jusqu'à trois octets par caractère et n'est pas une véritable mise en œuvre UTF-8,
     c'est pourquoi utf8mb4 est recommandé.

Cette commande crée une nouvelle base de données nommée `zabbix` avec le jeu de caractères UTF-8,
ce qui est requis pour Zabbix.

Créez un utilisateur dédié pour Zabbix et accordez les privilèges nécessaires : Ensuite, vous devez créer
un utilisateur que Zabbix utilisera pour accéder à la base de données. Remplacez `<password>` par un mot de passe fort de votre choix.

!!! info "Création des utilisateurs et attribution des privilèges"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```


    - Remplacez `<zabbix server ip>` par l'adresse IP réelle du serveur
      où le serveur Zabbix sera installé.
    - Remplacez `<zabbix frontend ip>` par l'adresse IP réelle du serveur
      où la partie frontale de Zabbix sera installée.

    Si les deux composants sont installés sur le même serveur, utilisez la même adresse IP.

    ???+ tip

        Si votre serveur Zabbix, frontend et base de données sont sur la même machine,
        vous pouvez remplacer `<zabbix server ip>` et `<zabbix frontend ip>` par `localhost` ou `127.0.0.1`.

Cela crée de nouveaux utilisateurs `zabbix-web` et `zabbix-srv`, leur accorde l'accès à la
base de données Zabbix et garantit que les privilèges sont appliqués immédiatement.

À ce stade, votre base de données Zabbix est prête, mais avant qu'elle ne puisse être réellement utilisée par
Zabbix, nous devons encore remplir la base de données avec les tables et les données initiales nécessaires,
mais cela sera couvert dans la section suivante lors de l'installation du serveur Zabbix.

Si vous prévoyez d'installer le serveur Zabbix sur une machine différente que celle hébergeant
la base de données, vous devrez ouvrir le pare-feu hôte pour permettre les connexions entrantes à la
machine serveur de base de données. Par défaut, MariaDB écoute sur le port 3306.

!!! info "Ajout des règles du pare-feu"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=mysql --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 3306/tcp
    ```


---

## Remplissage de la base de données Zabbix

Au cours de l'installation des logiciels de base de données précédemment, nous avons créé les
utilisateurs et la base de données nécessaires pour Zabbix, cependant, Zabbix attend certaines tables,
schémas, images et autres éléments dans la base de données.
Pour configurer correctement la base de données, il faut la remplir avec le schéma requis.

Tout d'abord, nous devons installer les scripts SQL Zabbix qui contiennent les scripts d'import nécessaires pour la base de données.

!!! info "Installation des scripts SQL"

    Red Hat
    ``` bash
    dnf install zabbix-sql-scripts
    ```


    SUSE
    ``` bash
    zypper install zabbix-sql-scripts
    ```


    Ubuntu
    ``` bash
    sudo apt install zabbix-sql-scripts
    ```


???+ warning

    Lors de l'utilisation d'une version récente de MySQL ou MariaDB en tant que backend de base de données pour
    Zabbix, vous pouvez rencontrer des problèmes liés à la création de déclencheurs lors du processus
    d'importation du schéma. Cela est particulièrement pertinent si le journalisation binaire est activée sur votre serveur de base de données.
    (La journalisation binaire est souvent activée par défaut)
    Pour résoudre ce problème, vous devez définir l'option `log_bin_trust_function_creators` à `1`
    dans le fichier de configuration MySQL/MariaDB ou temporairement en temps réel.
    Cela permet aux utilisateurs non root de créer des fonctions stockées et des déclencheurs sans nécessiter
    les privilèges `SUPER`, qui sont restreints lorsque la journalisation binaire est activée.

    Généralement, nous n'aurons pas besoin de ce paramètre après l'import initial du schéma Zabbix,
    donc nous le désactiverons à nouveau une fois l'importation terminée.

    !!! info "Activer temporairement des privilèges supplémentaires pour les utilisateurs non root"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```


Maintenant, chargeons les données de zabbix (structure de la base de données,
images, utilisateur, etc.) dans notre base de données. Pour cela, nous utilisons
l'utilisateur `zabbix-srv` et nous l'importons tout dans notre DB
`zabbix`.

!!! info "Populer la base de données"

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```


!!! warning

    Selon les performances de votre matériel ou de votre machine virtuelle, le
    processus peut prendre quelques secondes à plusieurs minutes sans aucun retour
    visuel après l'entrée du mot de passe root.

    Veuillez être patient et évitez d'annuler l'opération ; attendez simplement que
    la ligne de commande Linux réapparaisse.

???+ note

    Zabbix semble aimer changer les emplacements des scripts pour populer la base
    de données à chaque version ou même entre versions. Si vous rencontrez une
    erreur, consultez la documentation Zabbix ; il y a de fortes chances que
    certains emplacements aient été modifiés.

Une fois l'importation du schéma Zabbix terminée, vous n'aurez plus besoin du
paramètre global `log_bin_trust_function_creators`. Il est une bonne pratique de le supprimer
pour des raisons de sécurité.

Pour rétablir le paramètre global à 0, utilisez la commande suivante dans l'invite
de commandes MySQL/MariaDB :

!!! info "Désactiver la fonction log_bin_trust à nouveau"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```


Cette commande désactive cette configuration, assurant que le positionnement de
sécurité des serveurs reste robuste.

Cela conclut notre installation de MariaDB. Vous pouvez maintenant passer à la
préparation du serveur Zabbix [Préparation du serveur Zabbix](preparation.md).

---

## Conclusion

Avec l'installation et la configuration réussies de MariaDB en tant que backend
de base de données pour Zabbix, vous disposez maintenant d'une fondation solide
pour votre solution de supervision. Nous avons couvert l'installation de MariaDB
à partir des paquets fournis par le fournisseur et des dépôts officiels, la
sécurisation de la base de données, la création des bases de données et utilisateurs
nécessaires Zabbix, ainsi que la population de la base de données avec le schéma
et les données initiales requis.

Votre environnement Zabbix est maintenant prêt pour les prochaines étapes de
configuration et d'installation.

---

## Questions

1. Quelle version de MariaDB dois-je installer pour la compatibilité et la stabilité ?
2. Sur quel port ma base de données fonctionne-t-elle ?
3. Quels utilisateurs de base de données ai-je créés et pourquoi ?

---

## Liens utiles

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)
