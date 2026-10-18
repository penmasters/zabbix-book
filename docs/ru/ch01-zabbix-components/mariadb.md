---
description: |
    Этот раздел из книги "The Zabbix Book", названный "Установка базы данных MariaDB",
    ведет вас через установку MariaDB как базового уровня данных для Zabbix.
    Он охватывает два метода установки: использование пакетов, предоставляемых поставщиком ОС,
    или официальных репозиториев MariaDB. В разделе приводятся шаги для запуска и
    защиты сервера MariaDB, создания базы данных Zabbix с соответствующими пользователями,
    а также настройки правил брандмауэра при необходимости.
tags: [beginner]
---

# Установка базы данных MariaDB

В этом разделе мы установим пакеты сервера и клиента MariaDB. Это предоставит вам
необходимые компоненты для запуска и управления базой данных MariaDB как базовым уровнем данных для Zabbix.

Если вы предпочитаете использовать PostgreSQL в качестве базового уровня данных,
вы можете пропустить этот раздел и перейти к разделу [_Установка базы данных PostgreSQL_](postgresql.md).

???+ tip "MySQL/Percona"
    Если вам нужно использовать MySQL или Percona вместо MariaDB, шаги установки
    и настройки очень похожи. Обычно вы замените `mariadb` на `mysql` в названиях пакетов и командах.

## Установка сервера и клиента MariaDB из пакетов, предоставляемых поставщиком ОС

Чтобы установить распределенный по умолчанию сервер и клиент MariaDB, выполните
следующую команду:

!!! info "Установка версии дистрибутива MariaDB"

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


Эта команда загрузит и установит пакеты сервера и клиента, позволяя вам настроить,
управлять и взаимодействовать с вашей базой данных MariaDB. После завершения
установки вы можете перейти к разделу [_Запуск базы данных MariaDB_](#запуск-базы-данных-mariadb).

---

## Установка сервера и клиента MariaDB из официальных репозиториев MariaDB

Если вам нужно установить MariaDB из официальных репозиториев MariaDB вместо пакетов,
предоставляемых поставщиком ОС, первым шагом будет добавление репозитория MariaDB
в вашу систему.

---

### Добавление репозитория MariaDB

Чтобы создать файл репозитория MariaDB, выполните следующую команду в терминале:

!!! info "Определение репозитория MariaDB"

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


Это откроет текстовый редактор, где вы сможете ввести детали конфигурации репозитория.
После настройки репозитория вы можете приступить к установке MariaDB
с помощью менеджера пакетов.

Последняя конфигурация доступна здесь: [https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Вот пример конфигурации для репозиториев MariaDB 11.4:

!!! example "Конфигурация репозитория MariaDB"

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


После сохранения файла убедитесь, что все настроено правильно и ваша предпочтительная версия MariaDB совместима с вашей версией Zabbix для избежания возможных проблем интеграции.

---

### Установка сервера и клиента MariaDB

С репозиторием MariaDB настроенным, вы готовы установить пакеты сервера и клиента MariaDB.
Это предоставит вам необходимые компоненты для запуска и управления вашей базой данных.

Чтобы установить сервер и клиент MariaDB, выполните следующую команду:

!!! info "Установка MariaDB из официального репозитория"

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


Эта команда загрузит и установит пакеты сервера и клиента, позволяя вам настроить,
управлять и взаимодействовать с вашей базой данных MariaDB. После завершения
установки вы можете перейти к разделу [_Запуск базы данных MariaDB_](#запуск-базы-данных-mariadb).

---

## Запуск базы данных MariaDB

Теперь, когда установлена MariaDB, нам нужно включить службу для автоматического запуска
при загрузке системы и немедленного старта. Используйте следующую команду для этого:

!!! info "Включение службы MariaDB"

    ```bash
    sudo systemctl enable mariadb --now
    ```


Эта команда включит и запустит службу MariaDB, а также создаст директорию базы данных,
так как это первый раз, когда служба запускается. Служба MariaDB теперь работает,
и вы можете проверить успешность установки, проверив версию MariaDB с помощью следующей команды:

!!! info "Проверка версии MariaDB"

    ```bash
    mariadb -V
    ```


Ожидаемый вывод будет похож на этот:

???+ example "Пример версии MariaDB"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb from 11.4.13-MariaDB, client 15.2 for Linux (aarch64) using  EditLine wrapper
    ```


Чтобы убедиться, что служба MariaDB работает правильно, вы можете проверить ее статус
следующей командой:

!!! info "Получение статуса mariadb"

    ```bash
    sudo systemctl status mariadb
    ```


Вы должны увидеть вывод, похожий на этот, указывающий, что служба MariaDB активна и работает:

???+ example "Пример статуса службы Mariadb"

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


Это подтверждает, что ваш сервер MariaDB запущен и готов к дальнейшей настройке.

---

## Усиление безопасности базы данных MariaDB

Для повышения безопасности вашего сервера MariaDB необходимо удалить ненужные тестовые базы данных,
анонимных пользователей и установить пароль для root. Это можно сделать с помощью
скрипта mariadb-secure-installation, который предоставляет пошаговое руководство по усилению безопасности вашей базы данных.

Выполните следующую команду:

!!! info "Усиление настроек MariaDB"

    ```bash
    sudo mariadb-secure-installation
    ```


Скрипт mariadb-secure-installation проведет вас через несколько ключевых шагов:

1. Установка пароля для root, если он еще не установлен.
2. Удаление анонимных пользователей.
3. Запрет входа root из удаленного доступа.
4. Удаление тестовой базы данных.
5. Перезагрузка таблиц привилегий для применения изменений.

После завершения ваш экземпляр MariaDB будет значительно более безопасен.

!!! example "Пример вывода mariadb-secure-installation"

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


Теперь вы готовы к настройке базы данных для Zabbix.

---

## Создание экземпляра базы данных Zabbix

С установкой и усилением безопасности MariaDB мы можем приступить к созданию базы данных
для Zabbix. Эта база данных будет хранить всю необходимую информацию, связанную с вашим сервером Zabbix,
включая конфигурационные данные и данные мониторинга.

Следуйте этим шагам для создания базы данных Zabbix:

Войдите в оболочку MariaDB как пользователь root:
Вы будете prompted ввести пароль root, установленный во время процесса mariadb-secure-installation.

!!! info "Вход в Mariadb как пользователь root"

    ```bash
    mariadb -uroot -p
    ```


После входа в оболочку MariaDB выполните следующую команду для создания базы данных Zabbix:

!!! info "Создание базы данных"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```


???+ note "Что такое utf8mb4"

     utf8mb4 — это правильная реализация UTF-8 в MySQL/MariaDB, поддерживающая все
     символы Unicode, включая эмодзи. Старый набор символов utf8 в MySQL/MariaDB поддерживает только до трех байтов на символ и не является истинной реализацией UTF-8,
     поэтому рекомендуется использовать utf8mb4.

Эта команда создает новую базу данных с именем `zabbix` со набором символов UTF-8, который требуется для Zabbix.

Создайте пользователя для Zabbix и предоставьте необходимые привилегии: Далее вам нужно
создать пользователя, которого будет использовать Zabbix для доступа к базе данных. Замените `<password>`
сильным паролем по вашему выбору.

!!! info "Создание пользователей и предоставление привилегий"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```


    - Замените `<zabbix server ip>` на фактический IP-адрес вашего сервера,
      где будет установлен Zabbix server.
    - Замените `<zabbix frontend ip>` на фактический IP-адрес вашего сервера,
      где будет установлен Zabbix frontend.

    Если оба компонента установлены на одном и том же сервере, используйте одинаковый IP-адрес.

    ???+ tip

        Если ваш Zabbix server, frontend и база данных находятся на одной машине, вы можете заменить
        `<zabbix server ip>` и `<zabbix frontend ip>` на `localhost` или `127.0.0.1`.

Это создает новых пользователей `zabbix-web` и `zabbix-srv`, предоставляет им доступ к базе данных Zabbix,
и гарантирует, что привилегии применяются сразу же.

На этом ваша база данных Zabbix готова, но до того как она будет использоваться Zabbix,
нам нужно заполнить базу данных необходимыми таблицами и начальными данными,
что будет описано в следующем разделе при установке сервера Zabbix.

Если вы планируете установить Zabbix server на другом компьютере, чем тот, который хостит
базу данных, вам нужно открыть брандмауэр хоста для входящих подключений к серверу базы данных.
По умолчанию MariaDB слушает порт 3306.

!!! info "Добавление правил брандмауэра"

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

## Заполнение базы данных Zabbix

Во время установки программного обеспечения для базы данных ранее мы создали необходимых пользователей и базу данных для Zabbix,
однако, Zabbix ожидает определенных таблиц, схем, изображений и других элементов в базе данных.
Чтобы правильно настроить базу данных, нам нужно заполнить ее требуемой схемой.

Сначала нам нужно установить SQL-скрипты Zabbix, содержащие необходимые
скрипты импорта для базы данных.

!!! info "Установка SQL-скриптов"

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

    При использовании недавней версии MySQL или MariaDB в качестве базового уровня данных для Zabbix,
    вы можете столкнуться с проблемами, связанными с созданием триггеров во время
    процесса импорта схемы. Это особенно актуально, если на вашем сервере базы данных включено бинарное логирование.
    (Бинарное логирование часто включается по умолчанию)
    Чтобы решить эту проблему, вам нужно установить опцию `log_bin_trust_function_creators` на `1`
    в файле конфигурации MySQL/MariaDB или временно во время выполнения.
    Это позволяет пользователям без прав root создавать хранимые функции и триггеры без необходимости обладания
    `SUPER` привилегиями, которые ограничены при включенном бинарном логировании.

    Обычно мы не будем нуждаться в этом настройке после завершения первоначального импорта схемы Zabbix,
    поэтому мы отключим его снова после завершения импорта.

    !!! info "Временно активируйте расширенные привилегии для пользователей, не являющихся root"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```


Теперь загрузим данные из zabbix (структура базы данных, изображения, пользователи и т.д.)
для этого мы используем пользователя `zabbix-srv` и загружаем всё в нашу базу данных `zabbix`.

!!! info "Заполните базу данных"

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```


!!! warning

    В зависимости от скорости вашего оборудования или виртуальной машины, процесс может
    занять от нескольких секунд до нескольких минут без какого-либо визуального обратного отклика
    после ввода пароля root.

    Пожалуйста, будьте терпеливы и не прерывайте операцию; просто дождитесь появления linux
    командной строки.

???+ note

    Zabbix любит менять местоположения скриптов для заполнения базы данных
    каждую версию или даже между версиями. Если вы столкнулись с ошибкой, обратитесь к документации Zabbix,
    есть большая вероятность, что какое-то местоположение было изменено.

После завершения импорта схемы Zabbix вам больше не потребуется глобальный параметр
`log_bin_trust_function_creators`. Это хорошая практика для безопасности его удалить.

Чтобы откатить глобальный параметр обратно к 0, используйте следующую команду в
MySQL/MariaDB оболочке:

!!! info "Отключите функцию log_bin_trust снова"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```


Эта команда отключит настройку, обеспечивая, что позиция безопасности сервера остаётся прочной.

Это завершает установку MariaDB. Вы можете приступить к [Подготовке сервера Zabbix](preparation.md).

---

## Заключение

С успешной установкой и настройкой MariaDB в качестве базы данных
для Zabbix у вас теперь есть прочная основа для вашего решения мониторинга.
Мы рассмотрели установку MariaDB из предоставляемых поставщиком пакетов и официальных репозиториев,
обеспечение безопасности базы данных, создание необходимой базы данных Zabbix и пользователей,
а также заполнение базы данных требуемой схемой и начальными данными.

Ваша среда Zabbix теперь готова для следующих этапов настройки и конфигурации.

---

## Вопросы

1. Какую версию MariaDB мне следует установить для совместимости и стабильности?
2. На каком порту работает моя база данных?
3. Какие пользователи базы данных я создал и почему?

---

## Полезные ссылки

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)
