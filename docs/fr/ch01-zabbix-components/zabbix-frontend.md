---
description: |
    Cette section du livre The Zabbix Book intitulée "Installation de l'interface utilisateur" fournit des instructions étape par étape pour installer l'interface utilisateur Zabbix avec NGINX sur diverses distributions Linux. Elle couvre l'installation des paquets nécessaires, la configuration d'SELinux et Systemd pour PHP-FPM, ainsi que la modification de la configuration NGINX afin de servir l'interface utilisateur Zabbix sur le port 80. De plus, elle guide les utilisateurs à travers la première configuration de l'interface utilisateur Zabbix, y compris la configuration de la connexion à la base de données et des paramètres de base tels que le nom d'instance, le fuseau horaire et le format de temps.
tags: [débutant]
---

# Installation de l'interface utilisateur

Avant de configurer l'interface utilisateur Zabbix, assurez-vous que le système répond aux exigences et est prêt comme indiqué dans le chapitre précédent : [_Débuter_](../ch00-getting-started/Requirements.md). Ce serveur peut être le même où les paquets du serveur Zabbix ont été précédemment installés, ou il peut s'agir d'une machine distincte.

Effectuez toutes les étapes suivantes sur le serveur désigné pour l'interface utilisateur.

---

## Installation de l'interface utilisateur avec NGINX

!!! info "installer les paquets de l'interface utilisateur"

    Red Hat
    ```bash
    # List all available php modules and active php-8.2
    dnf module list php -y
    dnf module enable php:8.2
    # When using MySQL/MariaDB
    dnf install zabbix-nginx-conf zabbix-web-mysql
    # or when using PostgreSQL
    dnf install zabbix-nginx-conf zabbix-web-pgsql
    ```

    SUSE
    ```bash
    # When using MySQL/MariaDB
    zypper install zabbix-nginx-conf zabbix-web-mysql php8-openssl php8-xmlreader php8-xmlwriter
    # or when using PostgreSQL
    zypper install zabbix-nginx-conf zabbix-web-pgsql php8-openssl php8-xmlreader php8-xmlwriter
    ```

    ???+ note "Suse Linux Enterprise Server"

        Sur SUSE Linux Enterprise Server (SLES), assurez-vous d'être abonné au dépôt "SUSE Linux Enterprise Module Web and Scripting" pour accéder aux paquets PHP 8 nécessaires à l'installation de l'interface utilisateur Zabbix : (sur les versions SLES < 16, la commande est "`SUSEConnect`" au lieu de "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```

        L'URL réelle pour le module web scripting peut varier en fonction du service pack particulier. Utilisez la commande suivante pour déterminer celle qui convient.

        ```bash
        suseconnect --list-extensions
        ```


    Ubuntu
    ```bash
    # When using MySQL/MariaDB
    sudo apt install zabbix-frontend-php php8.3-mysql zabbix-nginx-conf
    # or when using PostgreSQL
    sudo apt install zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```


Cette commande installera les paquets de l'interface utilisateur ainsi que les dépendances requises pour NGINX. 

À partir de SUSE 16, SELinux est le module de sécurité par défaut au lieu d'AppArmor.
Par défaut, PHP-FPM n'est pas autorisé par SELinux sur SUSE à :
- mapper la mémoire exécutable nécessaire à la compilation JIT PHP,
- se connecter au serveur Zabbix ou
- se connecter au serveur de base de données via TCP.
Nous devons informer SELinux d'autoriser tout cela :

!!! info "SELinux : Autoriser PHP-FPM à mapper la mémoire exécutable"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```

???+ tip

    Pour dépanner les problèmes de SELinux, il est recommandé d'installer le paquet `setroubleshoot` qui enregistrera toute dénégation SELinux dans le journal système et fournira des suggestions sur la façon de résoudre ces problèmes.

Selon les paramètres par défaut de votre distribution Linux, PHP-FPM peut ne pas être autorisé par Systemd à écrire dans le répertoire `/etc/zabbix/web` requis pour la configuration de l'interface utilisateur Zabbix. Pour activer cela, nous devons créer un fichier drop-in :

!!! info "Systemd : Autoriser PHP-FPM à écrire dans /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```

    
    Ceci ouvrira un éditeur pour créer le fichier drop-in `/etc/systemd/system/php-fpm.service.d/override.conf` qui surchargera ou étendra le fichier de service existant.

    Ajoutez les lignes suivantes au fichier :

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```


    Puis quittez l'éditeur et rechargez la configuration Systemd :

    ```bash
    systemctl daemon-reload
    ```


???+ note "Comment Systemd empêche PHP-FPM d'écrire dans /etc/zabbix/web ?"

    Sur de nombreuses distributions Linux modernes, Systemd utilise une fonctionnalité de sécurité appelée sandboxing pour restreindre les capacités des services. Cela est fait pour améliorer la sécurité en limitant l'accès des services à seulement les ressources dont ils ont besoin pour fonctionner.
    Par défaut, PHP-FPM peut être restreint d'écrire dans certains répertoires, y compris `/etc/zabbix/web`, afin de prévenir les vulnérabilités potentielles en matière de sécurité. Cela est imposé par les directives Systemd `ProtectSystem` et `ReadWritePaths` qui contrôlent l'accès au système de fichiers des services.

???+ tip

    Généralement, l'accès en écriture à `/etc/zabbix/web` est nécessaire uniquement lors de la configuration initiale de l'interface utilisateur Zabbix. Une fois cette configuration terminée, vous pouvez supprimer le fichier drop-in pour renforcer davantage la sécurité de votre système.

La première chose que nous devons faire est d'ajuster le fichier de configuration NGINX afin qu'il ne utilise pas la configuration standard et serve l'interface utilisateur Zabbix sur le port 80.

!!! info "Modifier la configuration nginx pour Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

Si vous êtes sous Ubuntu, il n'est pas nécessaire d'éditer `nginx.conf` ; exécutez simplement `sudo unlink /etc/nginx/sites-enabled/default`

Dans ce fichier de configuration, recherchez le bloc suivant qui commence par `server {` :

!!! example "Configuration originale"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```

    ???+ tip

        Ce bloc peut varier en fonction de votre distribution et de la version NGINX.

Ensuite, commentez les directives `listen` et `server_name` pour désactiver la configuration par défaut du serveur HTTP. Vous pouvez le faire en ajoutant un `#` au début de chaque ligne, comme dans l'exemple ci-dessous :

!!! example "Configuration après modification"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```


Le fichier de configuration Zabbix doit maintenant être modifié pour prendre en charge le service par défaut sur le port 80 que nous venons de désactiver.
Ouvrez le fichier suivant pour l'édition :

!!! info "Modifier la configuration Zabbix pour NGINX"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```


Et modifiez les lignes suivantes :

!!! example "Configuration originale"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```


Supprimez le `#` devant les deux premières lignes et modifiez-les avec le port et le domaine corrects pour votre interface utilisateur.

???+ tip 

    Si vous n'avez pas de domaine, vous pouvez remplacer `servername` par `_` comme dans l'exemple ci-dessous :

!!! example "Configuration après modification"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```


Le serveur web et le service PHP-FPM sont maintenant prêts pour la mise en route et le démarrage persistant. Exécutez les commandes suivantes pour activer et démarrer immédiatement ces services :

!!! info "Redémarrer les services de l'interface utilisateur"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```


    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```


Vérifions maintenant si le service est correctement démarré et configuré pour un démarrage automatique lors du prochain redémarrage.

!!! info "Vérifier que le service fonctionne"

    ```bash
    sudo systemctl status nginx
    ```

???+ example "Sortie d'exemple"

    ```shell-session
    localhost:~> sudo systemctl status nginx
    ● nginx.service - The nginx HTTP and reverse proxy server
          Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: disabled)
         Drop-In: /usr/lib/systemd/system/nginx.service.d
                  └─php-fpm.conf
          Active: active (running) since Mon 2023-11-20 11:42:18 CET; 30min ago
        Main PID: 1206 (nginx)
           Tasks: 2 (limit: 12344)
          Memory: 4.8M
             CPU: 38ms
          CGroup: /system.slice/nginx.service
                  ├─1206 "nginx: master process /usr/sbin/nginx"
                  └─1207 "nginx: worker process"

    Nov 20 11:42:18 zabbix-srv systemd[1]: Starting The nginx HTTP and reverse proxy server...
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: configuration file /etc/nginx/nginx.conf test is successful
    Nov 20 11:42:18 zabbix-srv systemd[1]: Started The nginx HTTP and reverse proxy server.
    ```


Avec le service opérationnel et configuré pour un démarrage automatique, l'étape préparatoire finale consiste à ajuster le pare-feu afin de permettre les connexions entrantes HTTP. Exécutez les commandes suivantes :

!!! info "Configurer le pare-feu"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```


Ouvrez votre navigateur et accédez à l'URL ou à l'adresse IP de votre interface utilisateur :

!!! info "Configuration de l'interface utilisateur"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```


Si tout se passe bien, vous devriez être accueilli par une page d'accueil Zabbix. En cas d'erreur, vérifiez la configuration à nouveau ou consultez le fichier journal NGINX `/var/log/nginx/error.log` ou exécutez la commande suivante :

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```


Cela devrait vous aider à localiser les erreurs que vous avez commises.

À l'ouverture de l'URL appropriée, une page ressemblant à celle illustrée ci-dessous doit apparaître :

![aperçu](ch01.2-basic-installation-setup.png){ align=left }

_1.2 Zabbix
accueil_

!!! tip "Choisissez la localisation anglaise appropriée"

    La localisation `en_US` utilise une notation de date américaine et un horloge à 12 heures, tandis que `en_GB` utilise une notation de date internationale et une horloge à 24 heures.

L'interface utilisateur Zabbix présente un ensemble limité de localisations disponibles, comme illustré ci-dessous.

![aperçu langue](ch01.3-basic-installation-setuplanguage.png){ align=left }

_1.3 Choix de la langue
d'accueil Zabbix_

Que se passe-t-il si nous voulons installer le chinois ou une autre langue de cette liste ?
Exécutez la commande suivante pour obtenir la liste des localisations disponibles pour votre système d'exploitation.

!!! info "Installer les paquets linguistiques"

    Red Hat
    ```bash
    dnf list glibc-langpack-*
    ```


    SUSE
    ```bash
    localectl list-locales
    ```


    Ubuntu
    ```bash
    apt-cache search language-pack
    ```


Les utilisateurs d'Ubuntu remarqueront probablement l'erreur suivante : `"Locale for language "en_US" is not found on the web server."```

!!! info "Cela peut être résolu facilement avec les commandes suivantes."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```


Cela vous donnera une liste comme celle-ci :

???+ example "Sortie d'exemple"

    Red Hat
    ```
    Installed Packages
    glibc-langpack-en.x86_64
    Available Packages
    glibc-langpack-aa.x86_64
    ---
    glibc-langpack-zu.x86_64
    ```


    SUSE
    ```
    C.UTF-8
    aa_DJ.UTF-8
    af_ZA.UTF-8
    an_ES.UTF-8
    ---
    zh_SG.UTF-8
    zh_TW.UTF-8
    zu_ZA.UTF-8
    ```


    Ubuntu
    ```
    language-pack-kab - translation updates for language Kabyle
    language-pack-kab-base - translations for language Kabyle
    language-pack-kn - translation updates for language Kannada
    language-pack-kn-base - translations for language Kannada
    ---
    language-pack-ko - translation updates for language Korean
    language-pack-ko-base - translations for language Korean
    language-pack-ku - translation updates for language Kurdish
    language-pack-ku-base - translations for language Kurdish
    language-pack-lt - translation updates for language Lithuanian
    ```


Recherchons maintenant notre localisation chinoise pour voir si elle est disponible. Comme vous pouvez le voir, le code commence par zh.

!!! info "recherche de paquet linguistique"

    Red Hat
    ```shell-session
    ~# dnf list glibc-langpack-* | grep zh
    glibc-langpack-zh.x86_64
    glibc-langpack-lzh.x86_64
    ```


    SUSE
    ```shell-session
    ~> localectl list-locales | grep zh
    zh_CN.UTF-8
    zh_HK.UTF-8
    zh_SG.UTF-8
    zh_TW.UTF-8
    ```


    Ubuntu
    ```bash
    sudo apt-cache search language-pack | grep -i zh
    ```


Sur RedHat et Ubuntu, la commande retourne deux lignes ; cependant, étant donné le code de langue identifié, 'zh_CN', seul le premier paquet nécessite l'installation.
sur SUSE, soit seuls les locaux `C.UTF-8` et `en_US.UTF-8` sont installés ou tous les locaux disponibles sont installés, en fonction de la présence du paquet `glibc-locale`.

!!! info "Installer le paquet local"

    Red Hat
    ```bash
    dnf install glibc-langpack-zh.x86_64
    sudo systemctl restart nginx php-fpm
    ```


    SUSE
    ```bash
    zypper install glibc-locale
    sudo systemctl restart nginx php-fpm
    ```


    Ubuntu
    ```bash
    sudo apt install language-pack-zh-hans
    sudo systemctl restart nginx php8.3-fpm
    ```


Lorsque nous revenons maintenant à notre interface utilisateur, nous sommes en mesure de sélectionner la langue chinoise après un rechargement du navigateur.

![sélection de langue](ch01.4-basic-installation-selectlanguage.png){ align=left }

_1.4 Zabbix sélection
de langue_

???+ note

    Si votre langue préférée n'est pas disponible dans l'interface utilisateur Zabbix, ne vous inquiétez pas, cela signifie simplement que la traduction est soit incomplète, soit non encore disponible. Zabbix est un projet open-source qui repose sur les contributions de la communauté pour les traductions, donc vous pouvez aider à améliorer en contribuant vos propres traductions.

Visitez la page de traduction à [https://translate.zabbix.com/](https://translate.zabbix.com/)
pour participer aux efforts de traduction. Une fois votre traduction terminée et revue, elle sera incluse dans le prochain correctif mineur de Zabbix.
Vos contributions aident à rendre Zabbix plus accessible et améliorent l'expérience utilisateur globale pour tous.Quand vous êtes satisfait des traductions disponibles, cliquez sur `Next`. Vous serez alors dirigé vers une page pour vérifier que tous les prérequis sont satisfaits. Si certains prérequis ne sont pas remplis, résolvez ces problèmes en premier lieu. Cependant, si tout est en ordre, vous devriez pouvoir continuer en cliquant sur `Next`.

![pré-requis](ch01.5-basic-installation-prerequisites.png){ align=left }

_1.5 Pré-requis Zabbix_

Sur la page suivante, vous configurerez les paramètres de connexion à la base de données :

1. `Select the Database Type` : Choisissez soit MySQL ou PostgreSQL selon votre configuration.
2. `Enter the Database Host` : Fournissez l'adresse IP ou le nom DNS du serveur de base de données. Utilisez le port 3306 pour MariaDB/MySQL ou 5432 pour PostgreSQL.
3. `Enter the Database Name` : Spécifiez le nom de votre base de données. Dans notre cas, c'est zabbix. Si vous utilisez PostgreSQL, vous devrez également fournir le nom du schéma qui est zabbix_server dans notre cas.
4. `Enther the Database Schema` : Seulement pour les utilisateurs de PostgreSQL, entrez le nom du schéma créé pour le serveur Zabbix, qui est `zabbix_server` dans notre cas.
4. `Enter the Database User` : Entrez l'utilisateur de la base de données créé pour l'interface web front-end, rappelez-vous que dans notre guide d’installation de base nous avons créé 2 utilisateurs `zabbix-web` et `zabbix-srv`. Un pour le frontend et l'autre pour notre serveur Zabbix donc ici nous utiliserons l'utilisateur `zabbix-web`. Entrez le mot de passe correspondant à cet utilisateur.

Assurez-vous que l'option `Database TLS encryption` n'est pas sélectionnée, puis cliquez sur `Next step` pour continuer.

![connexionbase](ch01.6-basic-installation-dbconnection.png){ align=left }

_1.6 Connexions Zabbix_

Vous êtes presque terminé avec la configuration ! Les étapes finales impliquent :

1. `Assigning an Instance Name` : Choisissez un nom descriptif pour votre instance Zabbix.
2. `Selecting the Timezone` : Choisissez le fuseau horaire qui correspond à votre localisation ou au fuseau horaire préféré pour l'interface Zabbix.
3. `Setting the Default Time Format` : Sélectionnez le format de temps par défaut que vous préférez utiliser.
4. **Chiffrer les connexions depuis l’interface web** : J'ai coché cette case mais vous ne devriez pas. Cette case est pour chiffrer la communication entre Zabbix frontend et votre navigateur. Nous aborderons cela plus tard.
   Une fois ces paramètres configurés, vous pouvez finaliser la configuration et poursuivre avec les étapes de configuration finales si nécessaire.

???+ note

    Il est une bonne pratique de définir le serveur Zabbix sur le fuseau horaire UTC, surtout lorsque vous gérez des systèmes dans plusieurs fuseaux horaires. L'utilisation du UTC aide à garantir la cohérence pour les actions et événements sensibles au temps, car le fuseau horaire du serveur est souvent utilisé pour calculer et afficher l'information liée au temps.

![paramètres](ch01.7-basic-installation-settings.png){ align=left }

_1.7 Résumé Zabbix_

Après avoir cliqué à nouveau sur `Next step`, vous serez dirigé vers une page confirmant que la configuration a été réussie. Cliquez sur `Finish` pour finaliser le processus de configuration.

![paramètres](ch01.8-basic-installation-final.png){ align=left }

_1.8 Installation Zabbix_

Nous sommes maintenant prêts à nous connecter :

![paramètres](ch01.9-basic-installation-login.png)

_1.9 Connexion Zabbix_

- Identifiant : Admin
- Mot de passe : zabbix

Cela conclut notre sujet sur la configuration du serveur Zabbix. Si vous êtes intéressé par la sécurisation de votre front-end, je recommande de consulter le sujet Securing Zabbix pour obtenir des conseils et les meilleures pratiques supplémentaires.

???+ conseil

    Si vous ne pouvez pas sauvegarder votre configuration à la fin, assurez-vous d'avoir exécuté les instructions liées à SELinux ou d'avoir désactivé SELinux. Vérifiez également si le répertoire `/etc/zabbix/web` est accessible en écriture par l'utilisateur du service web (généralement `wwwrun` ou `www`)

---

## Conclusion

Avec l'installation et la configuration de l’interface frontale Zabbix maintenant terminées, vous avez réussi à mettre en place l'interface utilisateur pour votre système de surveillance Zabbix. Ce processus a inclus l'installation des paquets nécessaires, la configuration d'un serveur web et un moteur PHP, la mise en place de la connexion à la base de données et la personnalisation des paramètres frontaux.

À ce stade, votre instance Zabbix est opérationnelle, fournissant une base pour la surveillance avancée et l'alerte. Dans les chapitres suivants, nous allons explorer le fine-tuning de Zabbix, l’optimisation des performances et les fonctionnalités clés qui transforment cela en un puissant outil d'observabilité.

Maintenant que votre environnement Zabbix est opérationnel, passons à la prochaine étape.

---

## Questions

- Pourquoi est-il nécessaire de commenter le bloc par défaut listen 80 dans nginx.conf avant d’éditer zabbix.conf ?
- Quels services serveur web et gestionnaire PHP doivent être activés et démarrés après avoir ajusté les configurations ?
- Lors de la configuration du front-end de base de données, pourquoi devez-vous entrer l'utilisateur de la base de données zabbix-web au lieu de zabbix-srv ?
- Au moment de connecter une base de données PostgreSQL dans le wizard de configuration Zabbix, quel paramètre supplémentaire doit être fourni par rapport à MySQL/MariaDB ?

---

## Liens utiles

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)