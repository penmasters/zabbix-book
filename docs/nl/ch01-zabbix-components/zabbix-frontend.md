---
description: |
    This section from The Zabbix Book titled "Installing the frontend" provides
    step-by-step instructions for installing the Zabbix frontend with NGINX on
    various Linux distributions. It covers the installation of necessary packages,
    configuration of SELinux and SystemD for PHP-FPM, and modification of the
    NGINX configuration to serve the Zabbix frontend on port 80. Additionally, 
    it guides users through the initial setup of the Zabbix frontend, including
    database connection configuration and basic settings such as instance name,
    timezone, and time format.
tags: [beginner]
---

# Frontend installeren

Voordat je de Zabbix frontend configureert, moet je ervoor zorgen dat het
systeem voldoet aan de vereisten en is voorbereid zoals beschreven in het vorige
hoofdstuk: [_Aan de slag_](../ch00-getting-started/Requirements.md). Deze server
kan dezelfde zijn waarop eerder de Zabbix serverpakketten zijn geïnstalleerd, of
het kan een aparte machine zijn.

Voer alle volgende stappen uit op de server die is aangewezen voor de frontend.

---

## Frontend installeren met NGINX

info "frontend pakketten installeren".

    Red Hat
    ```bash
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

        On SUSE Linux Enterprise Server (SLES), ensure you are subscribed to the
        "SUSE Linux Enterprise Module Web and Scripting" repository to access
        the necessary PHP 8 packages required for the Zabbix frontend installation:
        (on SLES versions < 16, the command is "`SUSEConnect`" instead of "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```
        The actual URL for web scripting module may be different depending on particular service pack. Use the following command to determine the right one.
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

Dit commando installeert de front-end pakketten samen met de benodigde
afhankelijkheden voor Nginx.

Vanaf SUSE 16 is SELinux nu de standaard beveiligingsmodule in plaats van
AppArmor. Standaard mag PHP-FPM van SELinux op SUSE niet
- map exec memory nodig voor PHP JIT compilatie,
- verbinding maken met Zabbix-server of
- verbinding maken met de databaseserver via TCP. We moeten SELinux vertellen
  dit allemaal toe te staan:

!!! info "SELinux: PHP-FPM toestaan exec geheugen in kaart te brengen"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```
???+ tip

    To troubleshoot SELinux issues, it is recommended to install the `setroubleshoot`
    package which will log any SELinux denials in the system log and provide
    suggestions on how to resolve them.

Afhankelijk van de standaardinstellingen van je Linux-distributie, kan PHP-FPM
standaard geen toestemming krijgen van SystemD om te schrijven naar de
`/etc/zabbix/web` directory die nodig is voor de Zabbix frontend setup. Om dit
in te schakelen moeten we een drop-in bestand maken om dit toe te staan:

!!! info "SystemD: Allow PHP-FPM to write to /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```

    This will open an editor to create a drop-in file `/etc/systemd/system/php-fpm.service.d/override.conf`
    which will override or extend the existing service file.

    Add the following lines to the file:

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```

    Then exit the editor and reload the SystemD configuration:

    ```bash
    systemctl daemon-reload
    ```

???+ note "How is SystemD preventing PHP-FPM from writing to /etc/zabbix/web?"

    On many modern Linux distributions, SystemD employs a security feature known as
    sandboxing to restrict the capabilities of services. This is done to enhance
    security by limiting the access of services to only the resources they need to function.
    By default, PHP-FPM may be restricted from writing to certain directories,
    including `/etc/zabbix/web`, to prevent potential security vulnerabilities.
    This is enforced through SystemD's `ProtectSystem` and `ReadWritePaths` directives, which
    control the file system access of services.

???+ tip

    Normally write access to `/etc/zabbix/web` is only needed during the initial setup
    of the Zabbix frontend. After the setup is complete you can remove the drop-in
    file again to further harden the security of your system.

First thing we have to do is alter the Nginx configuration file so that we don't
use the standard config and serve the Zabbix frontend on port 80.

!!! info "Edit nginx config for Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

In this configuration file look for the following block that starts with `server
{`:

!!! example "Original config"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```
    ???+ tip

        This block may be different depending on your distribution and Nginx version.


Then, comment out the any `listen` and `server_name` directives to disable the
default http server configuration. You can do this by adding a `#` at the
beginning of each line, like in the example below:

!!! example "Config after edit"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```

The Zabbix configuration file must now be modified to take over the default
service on port 80 we just disabled. Open the following file for editing:

!!! info "Edit Zabbix config for nginx"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```

And alter the following lines:

!!! example "Original config"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```

Verwijder de `#` voor de eerste 2 regels en pas ze aan met de juiste poort en
domein voor je front-end.

???+ tip

    In case you don't have a domain you can replace `servername` with `_` 
    like in the example below:

!!! example "Config after the edit"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```

The web server and PHP-FPM service are now ready for activation and persistent
startup. Execute the following commands to enable and start them immediately:

!!! info "Restart the front-end services"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```

    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```

Let's verify if the service is properly started and enabled so that it survives
our reboot next time.

!!! info "Check if the service is running"

    ```bash
    sudo systemctl status nginx
    ```
???+ example "Example output"

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

With the service operational and configured for automatic startup, the final
preparatory step involves adjusting the firewall to permit inbound HTTP traffic.
Execute the following commands:

!!! info "Configure the firewall"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```

Open your browser and go to the url or ip of your front-end :

!!! info "Front-end configuration"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```

If all goes well you should be greeted with a Zabbix welcome page. In case you
have an error check the configuration again or have a look at the nginx log file
`/var/log/nginx/error.log` or run the following command :

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```

This should help you in locating the errors you made.

Upon accessing the appropriate URL, a page resembling the one illustrated below
should appear:

![overview](ch01-basic-installation-setup.png){ align=left }

_1.4 Zabbix welcome_

The Zabbix frontend presents a limited array of available localizations, as
shown.

![overview language](ch01-basic-installation-setuplanguage.png){ align=left }

_!.5 Zabbix welcome language choice_

What if we want to install Chinese as language or another language from the
list? Run the next command to get a list of all locales available for your OS.

!!! info "Install language packs"

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

Users on Ubuntu will probably notice following error `"Locale for language
"en_US" is not found on the web server."``

!!! info "This can be solved easy with the following commands."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```

This will give you a list like:

???+ example "Example output"

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

Let's search for our Chinese locale to see if it is available. As you can see
the code starts with zh.

!!! info "search for language pack"

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

On RedHat and Ubuntu, the command outputs two lines; however, given the
identified language code, 'zh_CN,' only the first package requires installation.
on SUSE either only locales `C.UTF-8` and `en_US.UTF-8` are install or all
available locales are installed, depending on whether the package `glibc-locale`
is installed or not.

!!! info "Install the locale package"

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

When we return now to our front-end we are able to select the Chinese language,
after a reload of our browser.

![select language](ch01-basic-installation-selectlanguage.png){ align=left }

_1.6 Zabbix select language_

???+ note

    If your preferred language is not available in the Zabbix front-end, don't
    worry, it simply means that the translation is either incomplete or not yet
    available. Zabbix is an open-source project that relies on community contributions
    for translations, so you can help improve it by contributing your own translations.

Visit the translation page at
[https://translate.zabbix.com/](https://translate.zabbix.com/) to assist with
the translation efforts. Once your translation is complete and reviewed, it will
be included in the next minor patch version of Zabbix. Your contributions help
make Zabbix more accessible and improve the overall user experience for
everyone.

When you're satisfied with the available translations, click `Next`. You will
then be taken to a screen to verify that all prerequisites are satisfied. If any
prerequisites are not fulfilled, address those issues first. However, if
everything is in order, you should be able to proceed by clicking `Next`.

![pre-requisites](ch01-basic-installation-prerequisites.png){ align=left }

_1.7 Zabbix pre-requisites_

On the next page, you'll configure the database connection parameters:

1. `Select the Database Type`: Choose either MySQL or PostgreSQL depending on
   your setup.
2. `Enter the Database Host`: Provide the IP address or DNS name of your
   database server. Use port 3306 for MariaDB/MySQL or 5432 for PostgreSQL.
3. `Enter the Database Name`: Specify the name of your database. In our case, it
   is zabbix. If you are using PostgreSQL, you will also need to provide the
   schema name, which is zabbix_server in our case.
4. `Enther the Database Schema`: Only for PostgreSQL users, enter the schema
   name created for Zabbix server, which is `zabbix_server` in our case.
4. `Enter the Database User`: Input the database user created for the web
   front-end, remember in our basic installation guide we created 2 users
   `zabbix-web` and `zabbix-srv`. One for the frontend and the other one for our
   zabbix server so here we will use the user `zabbix-web`. Enter the
   corresponding password for this user.

Ensure that the `Database TLS encryption` option is not selected, and then click
`Next step` to proceed.

![dbconnection](ch01-basic-installation-dbconnection.png){ align=left }

_1.8 Zabbix connections_

You're almost finished with the setup! The final steps involve:

1. `Assigning an Instance Name`: Choose a descriptive name for your Zabbix
   instance.
2. `Selecting the Timezone`: Choose the timezone that matches your location or
   your preferred time zone for the Zabbix interface.
3. `Setting the Default Time Format`: Select the default time format you prefer
   to use.
4. **Encrypt connections from Web interface**: I marked this box but you should
   not. This box is to encrypt communications between Zabbix frontend and your
   browser. We will cover this later. Once these settings are configured, you
   can complete the setup and proceed with any final configuration steps as
   needed.

???+ note

    It's a good practice to set your Zabbix server to the UTC timezone, especially
    when managing systems across multiple timezones. Using UTC helps ensure consistency
    in time-sensitive actions and events, as the server’s timezone is often used for
    calculating and displaying time-related information.

![settings](ch01-basic-installation-settings.png){ align=left }

_1.9 Zabbix summary_

After clicking `Next step` again, you'll be taken to a page confirming that the
configuration was successful. Click `Finish` to complete the setup process.

![settings](ch01-basic-installation-final.png){ align=left }

_1.10 Zabbix install_

We are now ready to login :

![settings](ch01-basic-installation-login.png)

_1.11 Zabbix login_

- Login : Admin
- Password : zabbix

This concludes our topic on setting up the Zabbix server. If you're interested
in securing your front-end, I recommend checking out the topic Securing Zabbix
for additional guidance and best practices.

???+ tip

    If you are not able to save your configuration at the end, make sure you
    executed the SELinux related instructions or have SELinux disabled.
    Also check if the `/etc/zabbix/web` directory is writable by the webservice
    user (usually `wwwrun` or `www`)

---

## Conclusie

With the installation and configuration of the Zabbix frontend now complete, you
have successfully set up the user interface for your Zabbix monitoring system.
This process included installing the necessary packages, configuring a web
server and PHP engine, setting up the database connection, and customizing the
frontend settings.

At this stage, your Zabbix instance is operational, providing the foundation for
advanced monitoring and alerting. In the upcoming chapters, we will delve into
fine-tuning Zabbix, optimizing performance, and exploring key features that
transform it into a powerful observability platform.

Now that your Zabbix environment is up and running, let’s take it to the next
level.

---

## Vragen

---

## Nuttige URL's

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
