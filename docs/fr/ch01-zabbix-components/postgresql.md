---
description: |
    Cette section du livre The Zabbix Book intitulée "Installation d'une base de données PostgreSQL"
    vous guide à travers l'installation de PostgreSQL en tant que backend de base de données alternatif
    pour Zabbix. Elle couvre les méthodes d'installation utilisant des paquets fournis par le gestionnaire 
    d'opérateur système ou les dépôts officiels PostgreSQL, avec des commandes spécifiques pour Red Hat,
    SUSE et Ubuntu. La section comprend également les étapes pour démarrer et sécuriser le serveur
    PostgreSQL, créer la base de données Zabbix et les utilisateurs, ainsi que configurer les règles du pare-feu 
    si nécessaire.
tags: [débutant]
---

# Installation d'une base de données PostgreSQL

À la place de MariaDB/MySQL, vous pouvez choisir d'utiliser PostgreSQL comme backend de base de données pour Zabbix.
Similaire à MariaDB, PostgreSQL peut être installé en utilisant soit les paquets fournis par le gestionnaire 
d'opérateur système ou les dépôts officiels PostgreSQL.

Si vous avez déjà installé MariaDB dans la section précédente, vous pouvez sauter cette section.

À ce jour, PostgreSQL 13-18 est pris en charge par Zabbix. Vérifiez la documentation de Zabbix
pour obtenir une liste à jour des versions prises en charge pour votre version de Zabbix. Généralement,
il est une bonne idée d'utiliser la dernière version prise en charge par Zabbix.

???+ tip "Extension TimescaleDB"

    Zabbix prend également en charge l'extension TimescaleDB mais, en raison de sa nature avancée, 
    nous ne couvrirons pas ce sujet dans ce chapitre. Consultez [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    pour des instructions détaillées sur ce sujet.

    Notez que si vous souhaitez utiliser les paquets RPM de TimescaleDB fournis
    par Timescale, vous devrez installer PostgreSQL à partir des dépôts officiels
    PostgreSQL au lieu des paquets fournis par le gestionnaire d'opérateur système.
    Si vous choisissez d'installer PostgreSQL à partir des paquets fournis par le gestionnaire 
    d'opérateur système, vous devrez compiler et installer l'extension TimescaleDB à partir de sources.

    Note supplémentaire : TimescaleDB ne fournit pas de paquets pour SUSE Linux Enterprise
    Server (SLES) ou openSUSE Leap. Au lieu de cela, Suse fournit l'extension TimescaleDB 
    dans leurs propres dépôts. Mais pour que cela fonctionne, vous devrez installer PostgreSQL à partir des
    paquets fournis par le gestionnaire d'opérateur système au lieu des dépôts officiels
    PostgreSQL.

---

## Installation du serveur et du client PostgreSQL à partir de paquets fournis par le gestionnaire d'opérateur système

Pour installer le serveur PostgreSQL par défaut de la distribution, exécutez les 
commandes suivantes :

!!! info "Installation du serveur Postgres"

    Red Hat
    ``` bash
    dnf install postgresql-server postgresql-client	postgresql-contrib
    ```


    SUSE
    ``` bash
    zypper install postgresql-server postgresql postgresql-contrib
    ```


    Ubuntu
    ``` bash
    sudo apt install postgresql postgresql-client postgresql-contrib
    ```


Cette commande téléchargera et installera à la fois les paquets serveur et client, vous permettant de configurer,
configurer et interagir avec votre base de données PostgreSQL.

!!! warning "Initialisation de la base de données requise sur Red Hat"

    En raison des politiques pour les distributions familiales Red Hat, le service
    PostgreSQL ne initialise pas une base de données vide nécessaire au bon fonctionnement de PostgreSQL.
    Donc pour Red Hat, nous devons initialiser une base de données vide avant de continuer :

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```


    Sur SUSE et Ubuntu, le service Systemd fourni par l'OS initiera automatiquement 
    une base de données vide lors du premier démarrage.

Une fois l'installation terminée, vous pouvez passer à la section [_Démarrer la base de données PostgreSQL_](#starting-the-postgresql-database).

---

## Installation de PostgreSQL à partir des dépôts officiels PostgreSQL

Si vous préférez installer PostgreSQL à partir des dépôts officiels PostgreSQL au lieu
des paquets fournis par le gestionnaire d'opérateur système, la première étape est d'ajouter 
le dépôt PostgreSQL à votre système.

---

### Ajout du dépôt PostgreSQL

Configurez le dépôt PostgreSQL avec les commandes suivantes :

Consultez [https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/)
pour plus d'informations.

!!! info "Ajouter le dépôt PostgreSQL"

    Red Hat
    ```bash
    # Install the repository RPM:
    dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

    # Disable the built-in PostgreSQL module:
    dnf -qy module disable postgresql
    ```


    SUSE
    ```bash
    # Import the repository signing key:
    rpm --import https://zypp.postgresql.org/keys/PGDG-RPM-GPG-KEY-SLES16

    # Install the repository RPM:
    zypper install https://download.postgresql.org/pub/repos/zypp/reporpms/SLES-16-x86_64/pgdg-suse-repo-latest.noarch.rpm

    # Update the package lists:
    zypper refresh
    ```


    !!! warning "openSUSE Leap"
    
        Comme les paquets officiels de PostgreSQL sont spécifiquement construits pour être utilisés sur 
        SUSE Linux Enterprise Server (SLES), vous obtiendrez une erreur en essayant d'installer le
        dépôt sur openSUSE Leap. Nous pouvons néanmoins ignorer ce problème en choisissant de "briser le paquet en ignorant certaines de ses dépendances" 
        tant que vous correspondez à la version SLES avec votre version openSUSE :

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```


    ???+ note "Suse Linux Enterprise Server"

        Sur SUSE Linux Enterprise Server (SLES), assurez-vous d'être abonné au
        dépôt "SUSE Package Hub extension" pour accéder aux paquets dépendances nécessaires à l'installation officielle de PostgreSQL. 
        Sur SLES 15 vous aurez également besoin du module "Desktop Applications":

        ```bash
        # On SLES 16
        suseconnect -p PackageHub/16.0/x86_64

        # On SLES 15
        SUSEConnect -p sle-module-desktop-applications/15.7/x86_64
        SUSEConnect -p PackageHub/15.7/x86_64
        ```


    Ubuntu
    ```bash
    # Import the repository signing key:
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

    # Create the repository configuration file:
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    # Update the package lists:
    sudo apt update
    ```


---

### Installation du serveur et du client PostgreSQL

Avec les dépôts PostgreSQL configurés, vous êtes maintenant prêt à installer le serveur 
et les paquets clients PostgreSQL. Cela fournira les composants nécessaires pour exécuter
et gérer votre base de données.

!!! info "Installation de PostgreSQL depuis les dépôts officiels"

    Red Hat
    ```bash
    # Install Postgres server:
    dnf install postgresql17 postgresql17-server postgresql17-contrib
    ```


    SUSE
    ```bash
    zypper install postgresql17 postgresql17-server postgresql17-contrib
    ```


    Ubuntu
    ```bash
    sudo apt install postgresql-17 postgresql-client-17
    ```


Cette commande téléchargera et installera à la fois les paquets serveur et client, vous permettant de configurer,
configurer et interagir avec votre base de données PostgreSQL.

Ensuite, avant que nous puissions démarrer le serveur PostgreSQL, nous devons initialiser une nouvelle
base de données vide :

!!! info "Initialisation d'une base de données PostgreSQL vide"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```


Une fois l'installation terminée, vous pouvez passer à la section [Démarrage de la base de données PostgreSQL](#starting-the-postgresql-database).

---

## Démarrage de la base de données PostgreSQL

Maintenant que PostgreSQL est installé, nous devons activer le service pour qu'il démarre automatiquement
au démarrage du système ainsi que lancer immédiatement. Utilisez la commande suivante pour accomplir cela :

!!! info "Activation et démarrage du service PostgreSQL"

    Pour les paquets fournis par le gestionnaire d'opérateur système
    ```bash
    sudo systemctl enable postgresql --now
    ```


    Pour les paquets officiels de PostgreSQL :
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```


Cette commande activera et démarrera le service PostgreSQL.
Avec le service maintenant en cours d'exécution, vous pouvez vérifier que l'installation
a été réussie en vérifiant la version de PostgreSQL à l'aide de la commande suivante :

!!! info "Vérification de la version de PostgreSQL"

    ```bash
    psql -V
    ```


La sortie attendue ressemblera à ceci :

???+ example "Exemple de version PostgreSQL"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```


Pour vous assurer que le service PostgreSQL fonctionne correctement, vous pouvez vérifier son statut
avec la commande suivante :

!!! info "Obtention du statut du service PostgreSQL"

    Pour les paquets fournis par le gestionnaire d'opérateur système
    ```bash
    sudo systemctl status postgresql
    ```


    Pour les paquets officiels de PostgreSQL :
    ```bash
    sudo systemctl status postgresql-17
    ```


Vous devriez voir une sortie similaire à celle-ci, indiquant que le service PostgreSQL est actif et en cours d'exécution :

???+ example "Exemple du statut du service PostgreSQL"

    ```shell-session
    localhost:~ $ sudo systemctl status postgresql-17
    ● postgresql-17.service - PostgreSQL 17 database server
        Loaded: loaded (/usr/lib/systemd/system/postgresql-17.service; enabled; preset: disabled)
        Active: active (running) since Mon 2025-12-29 17:24:07 CET; 6s ago
    Invocation: 43ba47dfee5b415db223e3452c3cfacc
        Docs: https://www.postgresql.org/docs/17/static/
        Process: 11131 ExecStartPre=/usr/pgsql-17/bin/postgresql-17-check-db-dir ${PGDATA} (code=exited, status=0/SUCCESS)
    Main PID: 11137 (postgres)
        Tasks: 7 (limit: 4672)
            CPU: 471ms
        CGroup: /system.slice/postgresql-17.service
                ├─11137 /usr/pgsql-17/bin/postgres -D /var/lib/pgsql/17/data/
                ├─11138 "postgres: logger "
                ├─11139 "postgres: checkpointer "
                ├─11140 "postgres: background writer "
                ├─11142 "postgres: walwriter "
                ├─11143 "postgres: autovacuum launcher "
                └─11144 "postgres: logical replication launcher "

    Dec 29 17:24:07 localhost.localdomain systemd[1]: Starting PostgreSQL 17 database server...
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] LOG:  redirecting log output to logging co>
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] HINT:  Future log output will appear in di>
    Dec 29 17:24:07 localhost.localdomain systemd[1]: Started PostgreSQL 17 database server.
    ```


Cela confirme que votre serveur PostgreSQL est opérationnel et prêt pour une configuration supplémentaire.

---

## Sécurisation de la base de données PostgreSQL

PostgreSQL gère les permissions d'accès différemment des MySQL et MariaDB.
PostgreSQL se fie à un fichier appelé `pg_hba.conf` pour gérer qui peut accéder à la base de données,
d'où, et quelle méthode de chiffrement est autorisée pour l'authentification.

???+ note "À propos du fichier pg_hba.conf"

    L'authentification des clients dans PostgreSQL est configurée via le fichier `pg_hba.conf`
    où "HBA" signifie Host-Based Authentication. Ce fichier spécifie qui peut accéder à la base de données,
    d'où, et comment ils sont authentifiés.
    Pour plus de détails, vous pouvez consulter la documentation officielle PostgreSQL."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Ajoutez les lignes suivantes, l'ordre ici est important.

!!! info "Modification du fichier pg_hba"

    Red Hat / SUSE
    ``` bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/pg_hba.conf

    # for official packages
    vi /var/lib/pgsql/17/data/pg_hba.conf
    ```


    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/pg_hba.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/pg_hba.conf
    ```


!!! warning "Emplacement du fichier pg_hba"

    Si vous ne trouvez pas les fichiers `pg_hba.conf` et `postgres.conf` à l'emplacement mentionné ci-dessus,
    vous pouvez demander à PostgreSQL lui-même de fournir l'emplacement en utilisant
    la commande suivante (à condition que PostgreSQL soit actuellement en cours d'exécution) :

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```


Le fichier pg_hba résultant devrait ressembler à ceci :

!!! example "Exemple de pg_hba"

    ```
    # "local" is for Unix domain socket connections only
    local    zabbix     zabbix-srv                                 scram-sha-256
    local    all        all                                        peer
    # IPv4 local connections
    host     zabbix         zabbix-srv      <ip from zabbix server/24>     scram-sha-256
    host     zabbix         zabbix-web      <ip from zabbix frontend/24>   scram-sha-256
    host     all            all             127.0.0.1/32                   scram-sha-256
    # IPv6 local connections:
    host    zabbix          zabbix-srv      ::1/128                 scram-sha-256
    host    zabbix          zabbix-web      ::1/128                 scram-sha-256
    host    all             all             ::1/128                 ident
    ```


!!! warning "Assurez-vous de conserver l'ordre des entrées"

    L'ordre des entrées dans le fichier `pg_hba.conf` est crucial, car PostgreSQL
    traite ces règles séquentiellement. Assurez-vous que les règles spécifiques pour les utilisateurs 
    `zabbix-srv` et `zabbix-web` sont placées avant toute règle plus large comme la règle par défaut
    `all` qui pourrait potentiellement les annuler.

Après avoir modifié le fichier `pg_hba.conf`, n'oubliez pas de redémarrer PostgreSQL sinon les paramètres ne seront pas appliqués. Mais avant de redémarrer,
modifions également le fichier `postgresql.conf` et permettons à notre base de données d'écouter sur l'interface réseau pour accepter des connexions
du serveur Zabbix. PostgreSQL ne permet par défaut que les connexions depuis un socket Unix.

!!! info "Modification du fichier postgresql.conf"

    Red Hat / SUSE
    ```bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/postgresql.conf

    # for official packages
    vi /var/lib/pgsql/17/data/postgresql.conf
    ```


    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/postgresql.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/postgresql.conf
    ```


Localisez la ligne suivante :

!!! info ""

    ```ini
    #listen_addresses = 'localhost'
    ```


et remplacez-la par :

!!! info ""

    ```ini
    listen_addresses = '*'
    ```


???+ note

    Cela permettra à PostgreSQL d'accepter des connexions depuis n'importe quelle interface réseau,
    pas seulement la machine locale. En production, il est probablement une bonne idée de limiter
    qui peut se connecter à la base de données.

Après avoir effectué ce changement, redémarrez le service PostgreSQL pour appliquer les nouvelles configurations :

!!! info "Redémarrage du serveur de base de données"

    Pour les paquets fournis par le gestionnaire d'opérateur système
    ``` bash
    sudo systemctl restart postgresql
    ```


    Pour les paquets officiels
    ```bash
    sudo systemctl restart postgresql-17
    ```


???+ tip

    Si le service ne redémarre pas, vérifiez le fichier `pg_hba.conf` pour toute erreur de syntaxe,
    car des entrées incorrectes ici peuvent empêcher PostgreSQL de démarrer.

---

## Création de l'instance de base de données Zabbix

Avec les paquets nécessaires installés, vous êtes maintenant prêt à créer la base de données 
et les utilisateurs pour le serveur et l'interface frontale Zabbix.Les packages PostgreSQL créent automatiquement un utilisateur par défaut `postgres` lors de l'installation, qui dispose des privilèges administratifs sur l'instance PostgreSQL. Pour administrer la base de données, vous devrez exécuter les commandes en tant que l'utilisateur `postgres`.

Tout d'abord, créez l'utilisateur du serveur Zabbix (aussi appelé "rôle" dans PostgreSQL) :

!!! info "Créer les utilisateurs du serveur"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```


Ensuite, créez l'utilisateur de la console frontale qui sera utilisé pour se connecter à la base de données :

!!! info "Créer l'utilisateur de la console frontale"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```


Maintenant que les utilisateurs ont été créés, le prochain pas est de créer la base de données Zabbix. Exécutez la commande suivante pour créer la base de données `zabbix` avec le propriétaire défini sur
`zabbix-srv` et l'encodage des caractères défini sur `Unicode` comme requis par Zabbix :

!!! info "Créer la base de données"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```


???+ note "Qu'est-ce que ce 'template0'?"

    Dans PostgreSQL, `template0` est un modèle de base de données par défaut qui sert de copie vierge du système de base de données. Lors de la création d'une nouvelle base de données en utilisant `template0`,
    cela garantit que la nouvelle base de données commence avec une feuille blanche, sans aucun
    objet ou configuration préexistants qui pourraient être présents dans d'autres modèles.
    Cela est particulièrement utile lorsque vous souhaitez créer une base de données avec des paramètres spécifiques ou des extensions sans hériter d'éléments indésirables provenant d'autres modèles.

Une fois la base de données créée, vous devriez vérifier la connexion et vous assurer que
la session utilisateur correcte est active. Pour cela, connectez-vous à la base de données zabbix en utilisant l'utilisateur `zabbix-srv` :

!!! info "Se connecter en tant qu'utilisateur zabbix-srv"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```


Après la connexion, exécutez la requête SQL suivante pour confirmer que les paramètres `session_user`
et `current_user` sont définis sur `zabbix-srv` :

!!! info ""

    ```psql
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```


Si la sortie correspond, vous êtes connecté à la base de données avec l'utilisateur correct.

PostgreSQL diffère considérablement de MySQL ou MariaDB dans plusieurs aspects,
et l'un des principaux éléments qui le distingue est son utilisation des schémas. Contrairement à MySQL,
où les bases de données sont plus autonomes, le système de schémas de PostgreSQL fournit un environnement structuré et multi-utilisateurs au sein d'une seule base de données.

Les schémas agissent comme des conteneurs logiques au sein d'une base de données, permettant à plusieurs utilisateurs ou
applications d'accéder et de gérer les données indépendamment sans conflits. Cette fonctionnalité est particulièrement précieuse dans les environnements où plusieurs utilisateurs ou applications doivent interagir avec le même serveur de base de données simultanément. Chaque utilisateur ou application peut avoir son propre schéma, prévenant toute interférence accidentelle entre leurs données.

???+ note

    PostgreSQL vient avec un schéma par défaut, généralement appelé `public`, mais en
    général, il est une bonne pratique de créer des schémas personnalisés pour mieux organiser et séparer les objets de la base de données, surtout dans des environnements complexes ou multi-utilisateurs.

    Pour plus d'informations détaillées, je recommande de consulter le guide approfondi à cette URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    qui explique les avantages et les cas d'utilisation des schémas dans PostgreSQL.

Pour finaliser la configuration initiale de la base de données pour Zabbix, nous devons configurer les permissions du schéma pour les utilisateurs `zabbix-srv` et `zabbix-web`.

Tout d'abord, nous créons un schéma personnalisé nommé `zabbix_server` et attribuons la propriété à
l'utilisateur `zabbix-srv` :

!!! info "Créer le schéma de la base de données"

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```


Ensuite, nous définissons le `search path` sur `zabbix_server` pour qu'il soit par défaut
pour la session actuelle :

!!! info "Définir le chemin de recherche"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


???+ tip

    Si vous préférez ne pas définir manuellement le chemin de recherche chaque fois que vous vous connectez en tant qu'utilisateur `zabbix-srv`,
    vous pouvez configurer PostgreSQL pour utiliser automatiquement le chemin de recherche souhaité. Exécutez la commande SQL suivante pour définir le chemin de recherche par défaut pour
    le rôle `zabbix-srv` :

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```


    Cette commande garantit que chaque fois que l'utilisateur `zabbix-srv` se connecte à la base de données,
    le `search_path` est automatiquement défini sur `zabbix_server`.

Pour confirmer la configuration du schéma, vous pouvez lister les schémas existants :

!!! example "Vérifier l'accès au schéma"

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```


À ce stade, l'utilisateur `zabbix-srv` a un accès complet au schéma, mais l'utilisateur `zabbix-web`
a toujours besoin de permissions appropriées pour se connecter et interagir avec la base de données. Tout d'abord, nous accordons des privilèges `USAGE` sur le schéma afin que l'utilisateur `zabbix-web` puisse se connecter :

!!! info "Accorder un accès au schéma pour l'utilisateur zabbix-web"

    ```psql
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```


Maintenant, l'utilisateur `zabbix-web` a les permissions appropriées pour interagir avec le schéma
tout en maintenant la sécurité en limitant les permissions aux opérations essentielles.

Si vous êtes prêt, vous pouvez quitter la base de données et revenir à votre shell Linux.

!!! info "Quitter l'invite de commande de la base de données"

    ```psql
    zabbix=> \q
    ```


À ce stade, votre base de données Zabbix est prête, mais avant qu'elle ne puisse être utilisée par
Zabbix, nous devons encore la remplir avec les tables et les données initiales nécessaires, mais cela sera couvert dans la section suivante lors de l'installation du serveur Zabbix.

Si vous prévoyez d'installer le serveur Zabbix sur une machine différente que celle hébergeant
la base de données, vous devrez ouvrir le pare-feu hôte pour permettre les connexions entrantes à
le serveur de la base de données. Par défaut, PostgreSQL écoute sur le port 5432.

!!! info "Ajouter des règles au pare-feu"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=postgresql --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 5432/tcp
    ```

---

## Remplir la base de données Zabbix

Au cours de l'installation du logiciel de base de données précédemment, nous avons créé les 
utilisateurs nécessaires, la base de données et le schéma pour Zabbix, cependant, Zabbix attend certaines tables,
schémas, images et autres éléments présents dans la base de données.
Pour configurer correctement la base de données, nous devons la remplir avec les schémas requis.

Tout d'abord, nous avons besoin d'installer les scripts SQL Zabbix qui contiennent les scripts d'import nécessaires pour la base de données.

!!! info "Installer les scripts SQL"

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


Ensuite, vous devez préparer le schéma de la base de données : décompressez les fichiers de schéma nécessaires en exécutant la commande suivante :

!!! info "Décompresser le correctif DB"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


???+ note

    Zabbix semble aimer changer les emplacements des scripts pour remplir la base de données
    à chaque version ou même entre versions. Si vous rencontrez une erreur, consultez la documentation Zabbix,
    il y a de fortes chances que certains emplacements aient été modifiés.

Cela extrait le schéma de base de données requis pour le serveur Zabbix.

Maintenant, nous allons exécuter le fichier SQL pour remplir la base de données. Ouvrez une `psql` shell :

!!! info "Ouvrir l'invite psql"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```


???+ warning "Assurez-vous que le chemin de recherche correct est défini"

    Assurez-vous d'avoir suivi les étapes précédentes comme indiqué dans [Créer une instance Zabbix avec PostgreSQL](postgresql.md#creating-the-zabbix-database-instance)
    soigneusement pour avoir défini le chemin de recherche correct `search_path`.

    Si vous n'avez pas défini le chemin de recherche par défaut `search_path` pour l'utilisateur `zabbix-srv`,
    assurez-vous de le définir manuellement dans la session actuelle avant de continuer :
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


Chargez le schéma de base de données dans la base de données en utilisant les commandes suivantes :

!!! info "Charger le schéma de base de données dans db zabbix"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```


???+ warning

    Selon votre matériel ou la performance de votre machine virtuelle, ce processus peut prendre entre quelques secondes et plusieurs minutes. Veuillez être patient et évitez d'annuler
    l'opération.

Surveillez le progrès pendant que le script s'exécute. Vous verrez un affichage similaire à :

!!! example "Exemple de sortie"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    ...
    ...
    ...
    INSERT 0 10444
    DELETE 90352
    COMMIT
    ```


Une fois que le script est terminé et que vous revenez au `zabbix=>` prompt, la base de données
devrait être remplie avec toutes les tables, schémas,
images et autres éléments nécessaires pour Zabbix.

Cependant, `zabbix-web` ne peut toujours pas effectuer d'opérations sur les tables ou les séquences.
Pour permettre une interaction de base avec les données sans donner trop de privilèges, accordez les
privilèges suivants :

- Pour les tables : SELECT, INSERT, UPDATE et DELETE.
- Pour les séquences : SELECT et UPDATE.

!!! info "Accorder des droits sur le schéma à l'utilisateur zabbix-web"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```


Vérifiez si les droits sont corrects sur le schéma :

!!! example "Exemple de droits du schéma"

    ```psql
    zabbix=> \dn+
                                               List of schemas
         Name      |       Owner       |           Access privileges            |      Description
    ---------------+-------------------+----------------------------------------+------------------------
     public        | pg_database_owner | pg_database_owner=UC/pg_database_owner+| standard public schema
                   |                   | =U/pg_database_owner                   |
     zabbix_server | zabbix-srv        | "zabbix-srv"=UC/"zabbix-srv"          +|
                   |                   | "zabbix-web"=U/"zabbix-srv"            |
    ```


???+ note

    Si vous rencontrez l'erreur suivante lors de l'importation SQL :
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: no
        schéma a été sélectionné pour la création dans` It indicates that the `chemin de recherche` peut ne pas avoir été correctement appliqué. Ce paramètre est crucial car il spécifie le schéma où les tables et autres objets doivent être créés. En définissant correctement le chemin de recherche, vous assurez que le script SQL créera des tables
    et d'autres objets dans le schéma prévu.

Pour vous assurer que les tables Zabbix ont été créées avec succès et disposent des permissions correctes, vous pouvez vérifier la liste des tables et leur propriétaire en utilisant la commande `psql` :

- Liste des Tables : Utilisez la commande suivante pour lister toutes les tables dans le schéma `zabbix_server` :

!!! info "Liste des tables"

    ```psql
    zabbix=# \dt
    ```


Vous devriez voir une liste de tables avec leur schéma, nom, type et propriétaire.
Par exemple :

???+ example "Liste des tables avec relations"

    ```psql
    zabbix=> \dt
                            List of relations
        Schema     |            Name            | Type  |   Owner
    ---------------+----------------------------+-------+------------
     zabbix_server | acknowledges               | table | zabbix-srv
     zabbix_server | actions                    | table | zabbix-srv
     zabbix_server | alerts                     | table | zabbix-srv
     zabbix_server | auditlog                   | table | zabbix-srv
     zabbix_server | autoreg_host               | table | zabbix-srv
     zabbix_server | changelog                  | table | zabbix-srv
     zabbix_server | conditions                 | table | zabbix-srv
    ...
    ...
    ...
     zabbix_server | valuemap                   | table | zabbix-srv
     zabbix_server | valuemap_mapping           | table | zabbix-srv
     zabbix_server | widget                     | table | zabbix-srv
     zabbix_server | widget_field               | table | zabbix-srv
    (203 rows)
    ```


- Vérifier les Permissions : Confirmez que l'utilisateur zabbix-srv possède les tables et dispose des permissions nécessaires. Vous pouvez vérifier les permissions pour des tables spécifiques en utilisant la commande \dp :

!!! info "Vérifier les permissions de table"

    ```psql
    zabbix=> \dp zabbix_server.*
    ```


???+ example "Exemple d'affichage"

    ```psql
    zabbix=> \dp zabbix_server.*
                                                         Access privileges
        Schema     |            Name            |   Type   |         Access privileges          | Column privileges | Policies
    ---------------+----------------------------+----------+------------------------------------+-------------------+----------
     zabbix_server | acknowledges               | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | actions                    | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | alerts                     | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | auditlog                   | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
    ```


Cela affichera les privilèges d'accès pour toutes les tables dans le schéma `zabbix_server`.
Assurez-vous que `zabbix-srv` dispose des privilèges requis.Si tout semble correct, vos tables sont créées correctement et l'utilisateur `zabbix-srv` a les droits d'ownership et de permissions appropriés. Si vous devez ajuster des permissions, vous pouvez le faire en utilisant les commandes GRANT selon vos besoins.

Cela conclut notre installation de la base de données PostgreSQL.

---

## Conclusion

Avec l'installation et la configuration de PostgreSQL comme système de gestion de base de données pour Zabbix, vous disposez maintenant d'un système puissant et efficace prêt à répondre à vos besoins en matière de supervision. Nous avons couvert l'installation de PostgreSQL à partir des paquets fournis par le fournisseur et des dépôts officiels, la sécurisation de la base de données, la création de la base de données Zabbix et des utilisateurs nécessaires, ainsi que la population de la base de données avec le schéma et les données initiales requis.

Votre environnement Zabbix est maintenant prêt pour les prochaines étapes d'installation et de configuration.

---

## Questions

1. Quelle version de PostgreSQL dois-je installer pour la compatibilité et la stabilité ?
2. Sur quel port ma base de données utilise-t-elle ?
3. Quels utilisateurs de base de données ai-je créés et pourquoi ?

---

## Liens utiles

- [https://yum.postgresql.org](ttps://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)