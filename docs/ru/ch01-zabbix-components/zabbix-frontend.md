---
description: |
    Этот раздел из книги "The Zabbix Book", названный "Установка интерфейса",
    предоставляет пошаговые инструкции для установки интерфейса Zabbix с NGINX на различных дистрибутивах Linux. Он охватывает установку необходимых пакетов, конфигурацию SELinux и Systemd для PHP-FPM, а также изменение конфигурации NGINX для обслуживания интерфейса Zabbix на порту 80. Кроме того, он руководит пользователями через начальную настройку интерфейса Zabbix, включая настройку подключения к базе данных и базовых параметров, таких как имя экземпляра, часовой пояс и формат времени.
tags: [начинающий]
---

# Установка интерфейса

Перед настройкой интерфейса Zabbix убедитесь, что система соответствует требованиям
и подготовлена в соответствии с предыдущей главой: [_Начало работы_](../ch00-getting-started/Requirements.md). Этот сервер может быть тем же самым, где ранее были установлены пакеты Zabbix-сервера,
или это может быть отдельная машина.

Выполните все последующие шаги на сервере, предназначенном для интерфейса.

---

## Установка интерфейса с NGINX

!!! info "установить пакеты интерфейса"

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

        На SUSE Linux Enterprise Server (SLES) убедитесь, что вы подписаны на репозиторий
        "SUSE Linux Enterprise Module Web and Scripting", чтобы получить доступ к необходимым пакетам PHP 8,
        требуемым для установки интерфейса Zabbix: (в версиях SLES < 16 команда "`SUSEConnect`" вместо "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```

        Актуальный URL для модуля веб-скриптинга может отличаться в зависимости от конкретного пакета обновления. Используйте следующую команду, чтобы определить правильный.

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


Эта команда установит пакеты интерфейса вместе с необходимыми зависимостями для NGINX. 

С версии SUSE 16 SELinux является по умолчанию модулем безопасности вместо AppArmor.
По умолчанию PHP-FPM не разрешен SELinux на SUSE для
- отображения памяти выполнения, необходимой для JIT компиляции PHP,
- подключения к серверу Zabbix или
- подключения к серверу базы данных через TCP.
Мы должны сообщить SELinux о том, чтобы позволить все это:

!!! info "SELinux: Разрешить PHP-FPM отображать память выполнения"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```

???+ tip

    Для устранения неполадок с SELinux рекомендуется установить пакет `setroubleshoot`,
    который будет записывать любые отказы SELinux в системный журнал и предоставлять
    предложения по их решению.

В зависимости от настроек Linux по умолчанию, PHP-FPM может быть не разрешен Systemd для записи в директорию `/etc/zabbix/web`,
необходимую для установки интерфейса Zabbix. Чтобы это разрешить нам нужно создать файл drop-in:

!!! info "Systemd: Разрешить PHP-FPM записывать в /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```

    
    Это откроет редактор для создания файла drop-in `/etc/systemd/system/php-fpm.service.d/override.conf`
    который будет переопределять или расширять существующий файл службы.

    Добавьте следующие строки в файл:

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```


    Затем выйдите из редактора и перезагрузите конфигурацию Systemd:

    ```bash
    systemctl daemon-reload
    ```


???+ note "Как Systemd препятствует записи PHP-FPM в /etc/zabbix/web?"

    На многих современных дистрибутивах Linux, Systemd использует функцию безопасности,
    известную как песочница, чтобы ограничить возможности служб. Это делается для повышения
    безопасности путем ограничения доступа служб только к тем ресурсам, которые им нужны для работы.
    По умолчанию PHP-FPM может быть ограничен от записи в определенные директории,
    включая `/etc/zabbix/web`, чтобы предотвратить потенциальные уязвимости безопасности.
    Это контролируется директивами Systemd `ProtectSystem` и `ReadWritePaths`,
    которые регулируют доступ к файловой системе служб.

???+ tip

    Обычно запись в `/etc/zabbix/web` требуется только при начальной настройке
    интерфейса Zabbix. После завершения настройки вы можете удалить файл drop-in снова,
    чтобы еще больше усилить безопасность вашей системы.

Первым делом нам нужно изменить конфигурационный файл NGINX, чтобы мы не использовали стандартную конфигурацию и обслуживали интерфейс Zabbix на порту 80.

!!! info "Измените конфигурацию nginx для Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

Если вы используете Ubuntu, не нужно редактировать `nginx.conf` просто выполните `sudo unlink /etc/nginx/sites-enabled/default`

В этом файле конфигурации найдите следующий блок, который начинается с `server {`:

!!! example "Оригинальная конфигурация"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```

    ???+ tip

        Этот блок может отличаться в зависимости от вашей дистрибутивы и версии NGINX.

Затем закомментируйте любые `listen` и `server_name` директивы, чтобы отключить стандартную
конфигурацию HTTP-сервера. Вы можете сделать это, добавив `#` в начало каждой строки,
как показано ниже:

!!! example "Конфигурация после редактирования"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```


Файл конфигурации Zabbix теперь должен быть изменен, чтобы взять на себя стандартный
сервис на порту 80, который мы только что отключили.
Откройте следующий файл для редактирования:

!!! info "Измените конфигурацию Zabbix для nginx"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```


И измените следующие строки:

!!! example "Оригинальная конфигурация"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```


Удалите `#` перед первыми двумя строками и измените их с правильным
портом и доменом для вашего интерфейса.

???+ tip 

    Если у вас нет домена, вы можете заменить `servername` на `_` 
    как показано ниже:

!!! example "Конфигурация после редактирования"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```


Веб-сервер и служба PHP-FPM теперь готовы к активации и запуску при перезагрузке.
Выполните следующие команды, чтобы включить их и немедленно запустить:

!!! info "Перезапустите службы интерфейса"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```


    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```


Давайте проверим, работает ли служба правильно и настроена ли она для автоматического запуска при следующей перезагрузке.

!!! info "Проверьте работу службы"

    ```bash
    sudo systemctl status nginx
    ```

???+ example "Пример вывода"

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


Со службой, работающей и настроенной для автоматического запуска, последний подготовительный шаг включает изменение брандмауэра для разрешения входящего трафика HTTP. Выполните следующие команды:

!!! info "Настройте брандмауэр"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```


Откройте ваш браузер и перейдите по URL или IP вашего интерфейса:

!!! info "Настройка интерфейса"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```


Если все в порядке, вы должны увидеть страницу приветствия Zabbix. В случае ошибки проверьте конфигурацию снова или посмотрите файл журнала NGINX `/var/log/nginx/error.log` или выполните следующую команду:

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```


Это поможет вам найти ошибки, которые вы сделали.

При доступе к соответствующему URL должна появиться страница, подобная той, что показана ниже:

![общий обзор](ch01.2-basic-installation-setup.png){ align=left }

_1.2 Приветствие Zabbix_

!!! tip "Выберите подходящую локализацию"

    Локализация `en_US` использует американский формат даты и 12-часовой часовой пояс, в то время как
    `en_GB` использует международный формат даты и 24-часовой часовой пояс.

Интерфейс Zabbix предлагает ограниченное количество доступных локализаций, как показано.

![общий обзор выбора языка](ch01.3-basic-installation-setuplanguage.png){ align=left }

_1.3 Выбор языка приветствия Zabbix_

Что если мы хотим установить китайский язык или другой из списка?
Выполните следующую команду, чтобы получить список всех доступных локализаций для вашей ОС.

!!! info "Установите пакеты языка"

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


Пользователи на Ubuntu, вероятно, заметят следующую ошибку `"Локализация для языка "en_US" не найдена на веб-сервере."``

!!! info "Это можно легко исправить с помощью следующих команд."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```


Это даст вам список, например:

???+ example "Пример вывода"

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


Давайте поищем нашу локализацию на китайском языке, чтобы увидеть доступна ли она.
Как вы можете видеть код начинается с zh.

!!! info "Поиск пакета языка"

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


На RedHat и Ubuntu команда выводит две строки; однако, учитывая определенный код языка,
'zh_CN', требуется установить только первый пакет.
на SUSE либо только локализации `C.UTF-8` и `en_US.UTF-8` устанавливаются или все
доступные локализации устанавливаются, в зависимости от того, установлен ли пакет `glibc-locale`
или нет.

!!! info "Установите пакет локализации"

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


Когда мы вернемся теперь к нашему интерфейсу, мы сможем выбрать язык на китайском,
после перезагрузки нашего браузера.

![выбор языка](ch01.4-basic-installation-selectlanguage.png){ align=left }

_1.4 Выбор языка Zabbix_

???+ note

    Если ваш предпочтительный язык недоступен в интерфейсе Zabbix, не волнуйтесь,
    это просто означает, что перевод либо неполон, либо еще не доступен.
    Zabbix - это проект с открытым исходным кодом, который зависит от вкладов сообщества
    для перевода. Вы можете помочь улучшить его, сделав собственный перевод.

Посетите страницу перевода по адресу [https://translate.zabbix.com/](https://translate.zabbix.com/)
для помощи в усилиях по переводам. Как только ваш перевод будет завершен и проверен,
он будет включен в следующую версию патча Zabbix.
Ваши вклады помогают сделать Zabbix более доступным и улучшают общее
пользовательский опыт для всех.Когда вы удовлетворены доступными переводами, нажмите `Next`. Вы перейдете на экран для проверки выполнения всех предварительных условий. Если какие-либо из них не выполнены, сначала устраните эти проблемы. Однако если все в порядке, вы сможете продолжить, нажав `Next`.

![pre-requisites](ch01.5-basic-installation-prerequisites.png){ align=left }

_1.5 Предварительные условия Zabbix_

На следующей странице вам нужно будет настроить параметры подключения к базе данных:

1. `Select the Database Type`: Выберите MySQL или PostgreSQL в зависимости от вашей установки.
2. `Enter the Database Host`: Укажите IP-адрес или имя DNS вашего сервера базы данных. Используйте порт 3306 для MariaDB/MySQL или 5432 для PostgreSQL.
3. `Enter the Database Name`: Укажите имя вашей базы данных. В нашем случае это zabbix. Если вы используете PostgreSQL, вам также нужно будет указать имя схемы, которое в нашем случае является zabbix_server.
4. `Enther the Database Schema`: Только для пользователей PostgreSQL, укажите имя схемы, созданной для сервера Zabbix, которое в нашем случае является `zabbix_server`.
4. `Enter the Database User`: Введите пользователя базы данных, созданный для веб-интерфейса. Помните, что в нашей базовой инструкции по установке мы создали 2 пользователей `zabbix-web` и `zabbix-srv`.
   Один для веб-интерфейса и другой для нашего сервера Zabbix, поэтому здесь мы будем использовать пользователя `zabbix-web`. Введите соответствующий пароль для этого пользователя.

Убедитесь, что опция `Database TLS encryption` не выбрана, а затем нажмите
`Next step` для продолжения.

![dbconnection](ch01.6-basic-installation-dbconnection.png){ align=left }

_1.6 Подключения Zabbix_

Вы почти закончили установку! Последние шаги включают:

1. `Assigning an Instance Name`: Выберите описательное имя для вашего экземпляра Zabbix.
2. `Selecting the Timezone`: Выберите часовой пояс, соответствующий вашему местоположению или
   предпочитаемому часовому поясу для интерфейса Zabbix.
3. `Setting the Default Time Format`: Выберите предпочтительный формат времени.

???+ note

    Хорошей практикой является установка сервера Zabbix в часовой пояс UTC, особенно
    при управлении системами в нескольких часовых поясах. Использование UTC помогает обеспечить согласованность
    во временных действиях и событиях, так как часовой пояс сервера часто используется для расчета и отображения информации о времени.

![settings](ch01.7-basic-installation-settings.png){ align=left }

_1.7 Итоги Zabbix_

После повторного нажатия `Next step` вы перейдете на страницу, подтверждающую успешную
конфигурацию. Нажмите `Finish` для завершения процесса установки.

![settings](ch01.8-basic-installation-final.png){ align=left }

_1.8 Установка Zabbix_

Теперь мы готовы войти:

![settings](ch01.9-basic-installation-login.png)

_1.9 Вход в Zabbix_

- Имя пользователя: Admin
- Пароль: zabbix

Это завершает нашу тему по установке сервера Zabbix. Если вас интересует защита вашего веб-интерфейса, рекомендую ознакомиться с темой "Защита Zabbix" для получения дополнительных советов и лучших практик.

???+ tip

    Если вы не можете сохранить свою конфигурацию в конце, убедитесь, что вы выполнили инструкции по SELinux или отключили SELinux.
    Также проверьте, доступен ли каталог `/etc/zabbix/web` для записи пользователем веб-сервиса (обычно `wwwrun` или `www`)

---

## Заключение

С завершением установки и настройки веб-интерфейса Zabbix вы успешно создали пользовательский интерфейс для системы мониторинга Zabbix. Этот процесс включал установку необходимых пакетов, настройку веб-сервера и движка PHP, настройку подключения к базе данных и настройку параметров веб-интерфейса.

На данном этапе ваш экземпляр Zabbix функционирует, предоставляя основу для продвинутого мониторинга и оповещений. В следующих главах мы углубимся в настройку Zabbix, оптимизацию производительности и изучение ключевых функций, которые превращают его в мощную платформу наблюдения.

Теперь что ваша среда Zabbix запущена, давайте поднимем ее на следующий уровень.

---

## Вопросы

- Почему необходимо закомментировать стандартный блок listen 80 в nginx.conf перед редактированием zabbix.conf?
- Какие службы веб-сервера и процессов PHP нужно активировать и запустить после изменения конфигураций?
- Во время мастера настройки базы данных для веб-интерфейса, почему следует указать пользователя zabbix-web вместо zabbix-srv?
- При подключении к PostgreSQL в мастер-настройке Zabbix, какое дополнительное параметр необходимо предоставить по сравнению с MySQL/MariaDB?

---

## Полезные ссылки

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)