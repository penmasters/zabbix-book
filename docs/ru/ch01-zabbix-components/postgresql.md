---
description: |
    Этот раздел из книги "The Zabbix Book", названный "Установка базы данных PostgreSQL",
    поможет вам установить PostgreSQL в качестве альтернативного сервера базы данных для Zabbix.
    Он охватывает методы установки с использованием пакетов, предоставляемых поставщиком ОС,
    или официальных репозиториев PostgreSQL, со специфическими командами для систем Red Hat, SUSE
    и Ubuntu. В разделе также приведены шаги по запуску и защите сервера PostgreSQL,
    созданию базы данных Zabbix и пользователей, а также настройке правил брандмауэра при необходимости.
tags: [начинающий]
---

# Установка базы данных PostgreSQL

Вместо MariaDB/MySQL вы можете выбрать установку PostgreSQL в качестве сервера базы данных для Zabbix.
Аналогично MariaDB, PostgreSQL можно установить с использованием либо пакетов,
предоставляемых поставщиком ОС, либо официальных репозиториев PostgreSQL.

Если вы уже установили MariaDB в предыдущем разделе, вы можете пропустить этот раздел.

На момент написания Zabbix поддерживает PostgreSQL версий 13-18. Проверьте документацию
Zabbix для получения актуального списка поддерживаемых версий для вашей версии Zabbix.
Обычно хорошая идея установить последнюю версию, которую поддерживает Zabbix.

???+ tip "Расширение TimescaleDB"

    Zabbix также поддерживает расширение TimescaleDB, но из-за его продвинутого характера,
    мы не будем рассматривать его в этом разделе. Обратитесь к [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    для получения подробных инструкций по этой теме.

    Учтите, что если вы хотите использовать пакеты TimescaleDB RPM, предоставленные
    Timescale, вам потребуется установить PostgreSQL из официальных репозиториев PostgreSQL,
    а не из пакетов, предоставляемых поставщиком ОС. Если вы выберете установку PostgreSQL
    из пакетов, предоставляемых поставщиком ОС, вам потребуется скомпилировать и установить
    расширение TimescaleDB из исходного кода.

    Дополнительная информация: TimescaleDB не предоставляет пакеты для SUSE Linux Enterprise
    Server (SLES) или openSUSE Leap. Вместо этого Suse предоставляет расширение TimescaleDB
    в своих собственных репозиториях. Но для этого вам потребуется установить PostgreSQL из
    пакетов, предоставляемых поставщиком ОС, а не из официальных репозиториев PostgreSQL.

---

## Установка сервера и клиента PostgreSQL из пакетов, предоставляемых поставщиком ОС

Чтобы установить стандартный для дистрибутива PostgreSQL сервер, выполните следующие команды:

!!! info "Установка сервера Postgres"

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


Эта команда загрузит и установит пакеты сервера и клиента, что позволит вам настроить,
конфигурировать и взаимодействовать с вашей базой данных PostgreSQL.

!!! warning "Необходимо инициализировать базу данных на Red Hat"

    Из-за политик для дистрибутивов семейства Red Hat, служба PostgreSQL не инициализирует
    пустую базу данных, необходимую для работы PostgreSQL. Поэтому на Red Hat нам нужно
    инициализировать пустую базу данных перед продолжением:

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```


    На SUSE и Ubuntu служба Systemd, предоставляемая ОС, автоматически инициализирует
    пустую базу данных при первом запуске.

После завершения установки вы можете перейти к разделу [_Запуск базы данных PostgreSQL_](#starting-the-postgresql-database).

---

## Установка PostgreSQL из официальных репозиториев PostgreSQL

Если вы предпочитаете установить PostgreSQL из официальных репозиториев PostgreSQL вместо
пакетов, предоставляемых поставщиком ОС, первым шагом будет добавление репозитория PostgreSQL
в вашу систему.

---

### Добавление репозитория PostgreSQL

Настройте репозиторий PostgreSQL с помощью следующих команд:

Проверьте [https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/)
для получения дополнительной информации.

!!! info "Добавление репозитория PostgreSQL"

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
    
        Поскольку официальные пакеты PostgreSQL специально созданы для использования на 
        SUSE Linux Enterprise Server (SLES), вы получите ошибку при попытке установить репозиторий
        на openSUSE Leap. Однако мы можем безопасно игнорировать эту проблему, выбрав "разрушение пакета,
        игнорируя некоторые из его зависимостей", если ваша версия openSUSE соответствует версии SLES:

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```


    ???+ note "Suse Linux Enterprise Server"

        На SUSE Linux Enterprise Server (SLES) убедитесь, что вы подписаны на репозиторий
        "SUSE Package Hub extension", чтобы получить необходимые пакеты зависимостей для установки
        официального PostgreSQL. В SLES 15 вам также потребуется модуль "Desktop Applications":

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

### Установка сервера и клиента PostgreSQL

С настроенным репозиторием PostgreSQL вы готовы установить пакеты сервера и клиента PostgreSQL.
Это предоставит вам необходимые компоненты для запуска и управления вашей базой данных.

!!! info "Установка PostgreSQL из официальных репозиториев"

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


Эта команда загрузит и установит пакеты сервера и клиента, что позволит вам настроить,
конфигурировать и взаимодействовать с вашей базой данных PostgreSQL.

Далее перед тем как запустить службу PostgreSQL нам нужно инициализировать новую
пустую базу данных:

!!! info "Инициализация пустой базы данных PostgreSQL"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```


После завершения установки вы можете перейти к разделу [Запуск базы данных PostgreSQL](#starting-the-postgresql-database).

---

## Запуск базы данных PostgreSQL

Теперь, когда PostgreSQL установлен, нам нужно включить службу для автоматического запуска
при загрузке системы и немедленного старта. Используйте следующую команду для этого:

!!! info "Включение и запуск службы PostgreSQL"

    для пакетов, предоставляемых поставщиком ОС:
    ```bash
    sudo systemctl enable postgresql --now
    ```


    для официальных пакетов PostgreSQL:
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```


Эта команда включит и запустит службу PostgreSQL.
Теперь, когда служба работает, вы можете проверить успешность установки,
проверив версию PostgreSQL с помощью следующей команды:

!!! info "Проверка версии PostgreSQL"

    ```bash
    psql -V
    ```


Ожидаемый вывод должен быть похож на этот:

???+ example "Пример версии PostgreSQL"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```


Чтобы убедиться, что служба PostgreSQL работает правильно, вы можете проверить ее статус
с помощью следующей команды:

!!! info "Проверка статуса службы PostgreSQL"

    для пакетов, предоставляемых поставщиком ОС:
    ```bash
    sudo systemctl status postgresql
    ```


    для официальных пакетов PostgreSQL:
    ```bash
    sudo systemctl status postgresql-17
    ```


Вы должны увидеть вывод, подобный этому, что указывает на то, что служба PostgreSQL
активна и работает:

???+ example "Пример статуса службы PostgreSQL"

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


Это подтверждает, что ваш сервер PostgreSQL запущен и готов к дальнейшей конфигурации.

---

## Защита базы данных PostgreSQL

PostgreSQL обрабатывает права доступа по-другому по сравнению с MySQL и MariaDB.
PostgreSQL полагается на файл `pg_hba.conf` для управления тем, кто может получить доступ к базе данных,
откуда и каким методом шифрования разрешена аутентификация.

???+ note "О pg_hba.conf"

    Аутентификация клиентов в PostgreSQL настраивается через файл `pg_hba.conf`, где "HBA" означает
    Хост-базированную аутентификацию. Этот файл указывает, какие пользователи могут получить доступ к базе данных,
    от каких хостов и как они аутентифицируются.
    Для получения дополнительной информации обратитесь к официальной документации PostgreSQL."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Добавьте следующие строки, порядок здесь важен.

!!! info "Редактирование файла pg_hba"

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


!!! warning "Локация файла pg_hba"

    Если вы не найдете файлы `pg_hba.conf` и `postgres.conf` в указанном выше месте,
    вы можете запросить PostgreSQL саму о локации этих файлов, используя следующую команду
    (предполагая, что PostgreSQL запущена):

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```


Результативный файл pg_hba должен выглядеть так:

!!! example "Пример файла pg_hba"

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


!!! warning "Убедитесь, что порядок записей сохранен"

    Порядок записей в файле `pg_hba.conf` важен, так как PostgreSQL обрабатывает эти правила
    последовательно. Убедитесь, что конкретные правила для пользователей `zabbix-srv` и `zabbix-web`
    расположены перед более широкими правилами, такими как стандартное правило пользователя `all`,
    которые могут перекрыть их.

После изменения файла `pg_hba.conf` не забудьте перезапустить postgres, иначе настройки
не будут применены. Но перед тем как перезапустить, также редактируем файл `postgresql.conf`
и разрешаем нашей базе данных принимать входящие соединения с нашего сетевого интерфейса от сервера Zabbix.
PostgreSQL по умолчанию позволяет подключения только через unix-сокет.

!!! info "Редактирование файла postgresql.conf"

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


Найдите следующую строку:

!!! info ""

    ```ini
    #listen_addresses = 'localhost'
    ```


и замените ее на:

!!! info ""

    ```ini
    listen_addresses = '*'
    ```


???+ note

    Это позволит PostgreSQL принимать соединения с любого сетевого интерфейса,
    а не только с локальной машины. В производственной среде, возможно, будет лучше
    ограничить доступ к базе данных.

После внесения изменений перезапустите службу PostgreSQL для применения новых настроек:

!!! info "Перезапуск сервера БД"

    для пакетов, предоставляемых поставщиком ОС:
    ``` bash
    sudo systemctl restart postgresql
    ```


    для официальных пакетов:
    ```bash
    sudo systemctl restart postgresql-17
    ```


???+ tip

    Если служба не может быть перезапущена, проверьте файл `pg_hba.conf` на наличие синтаксических ошибок,
    так как некорректные записи здесь могут помешать запуску PostgreSQL.

---

## Создание экземпляра базы данных Zabbix

С установленными необходимыми пакетами вы готовы создать базу данных Zabbix и пользователей
для сервера и фронтенда.The PostgreSQL пакеты автоматически создают по умолчанию `postgres` linux-user 
во время установки, который имеет административные привилегии на экземпляре PostgreSQL.
Для управления базой данных вам потребуется выполнять команды от имени пользователя `postgres`.

Во-первых, создайте пользователя сервера Zabbix (также известного как "роль" в PostgreSQL):

!!! info "Создание пользователей сервера"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```


Затем создайте пользователя для интерфейса Zabbix, который будет использоваться для подключения к базе данных:

!!! info "Создание пользователя для фронтенда"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```


Теперь, с учетными записями пользователями созданы, следующим шагом является создание базы данных Zabbix.
Выполните следующую команду для создания базы данных `zabbix` с владельцем, установленным на 
`zabbix-srv` и кодировкой символов, установленной на `Unicode` в соответствии с требованиями Zabbix:

!!! info "Создание базы данных"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```


???+ note "Что такое 'template0'?"

    В PostgreSQL, `template0` является шаблоном базы данных по умолчанию,
    который служит чистой копией системы базы данных. При создании новой базы данных с помощью `template0`,
    это гарантирует, что новая база данных начинается с чистого листа бумаги без каких-либо
    предварительно существующих объектов или конфигураций, которые могут присутствовать в других шаблонах.
    Это особенно полезно при создании базы данных с определенными настройками или расширениями без унаследования каких-либо нежелательных элементов из других шаблонов.

После создания базы данных вам следует проверить подключение и убедиться, что
правильная пользовательская сессия активна. Для этого войдите в базу данных zabbix с помощью
пользователя `zabbix-srv`:

!!! info "Вход как пользователь zabbix-srv"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```


После входа выполните следующий SQL-запрос, чтобы подтвердить, что оба `session_user`
и `current_user` установлены на `zabbix-srv`:

!!! info ""

    ```psql
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```


Если вывод соответствует, вы успешно подключены к базе данных с правильным
пользователем.

PostgreSQL значительно отличается от MySQL или MariaDB по нескольким аспектам,
и одним из ключевых признаков является использование схем. В отличие от MySQL,
где базы данных более автономны, система схем PostgreSQL предоставляет структурированную,
многоуровневую среду для нескольких пользователей внутри одной базы данных.

Схемы действуют как логические контейнеры внутри базы данных, позволяя нескольким пользователям или
приложениям независимо обращаться и управлять данными без конфликтов. Эта функция
особенно ценна в средах, где несколько пользователей или приложений взаимодействуют с одной и той же базой данных сервера одновременно. Каждый пользователь или приложение может иметь свою собственную схему, предотвращая случайное нарушение другого данных.

???+ note

    PostgreSQL поставляется с шаблоном схемы по умолчанию, обычно называемой `public`,
    но в общем случае рекомендуется создавать пользовательские схемы для лучшей организации и разделения
    объектов базы данных, особенно в сложных или многопользовательских средах.

    Для более подробной информации я рекомендую ознакомиться со справочным руководством по этому URI,
    [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    которое объясняет преимущества и случаи использования схем в PostgreSQL.

Чтобы завершить начальную настройку базы данных для Zabbix, нам нужно настроить разрешения схемы
для обоих пользователей `zabbix-srv` и `zabbix-web`.

Во-первых, создадим пользовательскую схему под названием `zabbix_server` и назначим владение
пользователю `zabbix-srv`:

!!! info "Создание схемы базы данных"

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```


Затем установите `search path` на `zabbix_server` схему, чтобы она была по умолчанию
для текущей сессии:

!!! info "Установка пути поиска"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


???+ tip

    Если вы предпочитаете не устанавливать путь поиска вручную каждый раз, когда входите как
    пользователь `zabbix-srv`, можно настроить PostgreSQL для автоматического использования желаемого
    пути поиска. Выполните следующую команду SQL для установки стандартного пути поиска для
    роли `zabbix-srv`:

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```


    Эта команда гарантирует, что каждый раз, когда пользователь `zabbix-srv` подключается к базе данных,
    `search_path` автоматически устанавливается на `zabbix_server`.

Чтобы подтвердить настройку схемы, вы можете перечислить существующие схемы:

!!! example "Проверка доступа к схеме"

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```


На данном этапе пользователь `zabbix-srv` имеет полный доступ к схеме, но пользователю `zabbix-web`
все еще требуются соответствующие разрешения для подключения и взаимодействия с базой данных.
Сначала мы предоставляем `USAGE` привилегии на схему, чтобы позволить `zabbix-web` подключаться:

!!! info "Предоставление доступа к схеме для пользователя zabbix-web"

    ```psql
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```


Теперь пользователь `zabbix-web` имеет соответствующий доступ для взаимодействия со схемой
при сохранении безопасности путем ограничения разрешений на необходимые операции.

Если вы готовы, можно выйти из базы данных и вернуться к своей оболочке Linux.

!!! info "Выход из оболочки базы данных"

    ```psql
    zabbix=> \q
    ```


На данном этапе ваша база данных Zabbix готова, но до того как она может быть использована
Zabbix, нам все еще нужно заполнить базу данных необходимыми таблицами и начальными данными,
но это будет рассмотрено в следующем разделе при установке сервера Zabbix.

Если вы планируете установку сервера Zabbix на другой машине, чем та, которая хостит
базу данных, вам потребуется открыть хостовский брандмауэр для разрешения входящих подключений к серверу базы данных. По умолчанию PostgreSQL слушает порт 5432.

!!! info "Добавление правил брандмауэра"

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

## Заполнение базы данных Zabbix

Во время установки программного обеспечения для базы данных ранее мы создали 
необходимых пользователей, базу данных и схему для Zabbix, однако, Zabbix ожидает определенных таблиц,
схем, изображений и других элементов в базе данных.
Чтобы правильно настроить базу данных, нам нужно заполнить ее необходимой схемой.

Во-первых, нам необходимо установить SQL-скрипты Zabbix, которые содержат требуемые
скрипты для импорта базы данных.

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


Затем вам нужно подготовить схему базы данных: распакуйте необходимые файлы схемы,
выполнив следующую команду:

!!! info "Распаковка патча базы данных"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


???+ note

    Zabbix, кажется, любит менять местоположения скриптов для заполнения базы данных
    каждый раз или даже между версиями. Если вы столкнулись с ошибкой, обратитесь к документации Zabbix,
    где есть большая вероятность того, что какое-то место было изменено.

Это извлечет необходимую схему базы данных для сервера Zabbix.

Теперь мы выполним SQL-файл для заполнения базы данных. Откройте оболочку `psql`:

!!! info "Открытие оболочки psql"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```


???+ warning "Убедитесь, что правильный search_path установлен"

    Убедитесь, что вы выполнили предыдущие шаги, как указано в [Создание экземпляра базы данных Zabbix с PostgreSQL](postgresql.md#creating-the-zabbix-database-instance),
    чтобы установить правильный `search_path`.

    Если вы не установили стандартный `search_path` для пользователя `zabbix-srv`,
    убедитесь, что вы установите его вручную в текущей сессии перед продолжением:
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


Загрузите схему базы данных в базу данных с помощью следующих команд:

!!! info "Загрузка схемы базы данных в db zabbix"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```


???+ warning

    В зависимости от производительности вашего оборудования или виртуальной машины, этот процесс может занять
    от нескольких секунд до нескольких минут. Пожалуйста, будьте терпеливы и избегайте прерывания операции.

Следите за прогрессом, пока скрипт выполняется. Вы увидите вывод похожий на:

!!! example "Пример вывода"

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


Как только скрипт завершит выполнение и вы вернетесь к `zabbix=>` промпту, база данных
должна быть успешно заполнена всеми необходимыми таблицами, схемами,
изображениями и другими элементами для Zabbix.

Однако `zabbix-web` все еще не может выполнять никакие операции над таблицами или последовательностями.
Чтобы позволить базовую работу с данными без предоставления слишком многих привилегий, предоставьте следующие права:

- Для таблиц: SELECT, INSERT, UPDATE и DELETE.
- Для последовательностей: SELECT и UPDATE.

!!! info "Предоставление прав на схему для пользователя zabbix-web"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```


Подтвердите, что права установлены правильно на схеме :

!!! example "Пример прав схемы"

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

    Если вы столкнулись со следующей ошибкой во время импорта SQL:
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: no
        schema has been selected to create in` It indicates that the `search_path` настройка
    может не быть правильно применена. Эта настройка важна, так как она указывает,
    схему, где должны создаваться таблицы и другие объекты. Правильное установление пути поиска гарантирует,
    что SQL-скрипт будет создавать таблицы и другие объекты в намеченной схеме.

Чтобы убедиться, что таблицы Zabbix были успешно созданы и имеют правильные
права доступа, вы можете проверить список таблиц и их владельцев с помощью команды `psql`:

- Список таблиц: Используйте следующую команду для получения списка всех таблиц в схеме `zabbix_server`:

!!! info "Список таблиц"

    ```psql
    zabbix=# \dt
    ```


Вы должны увидеть список таблиц со своими схемами, именами, типами и владельцами.
Например:

???+ example "Список таблиц с отношениями"

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


- Проверка прав доступа: Подтвердите, что пользователь zabbix-srv владеет таблицами и имеет
  необходимые права. Вы можете проверить права для конкретных таблиц с помощью команды \dp:

!!! info "Проверка прав доступа к таблицам"

    ```psql
    zabbix=> \dp zabbix_server.*
    ```


???+ example "Пример вывода"

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


Это покажет права доступа для всех таблиц в схеме `zabbix_server`.
Убедитесь, что `zabbix-srv` имеет необходимые привилегии.Если всё выглядит правильно и таблицы созданы корректно, а пользователь `zabbix-srv` имеет соответствующие права собственности и разрешения, то можно приступать к настройке прав доступа при необходимости с помощью команд GRANT.

Это завершает установку базы данных PostgreSQL.

---

## Заключение

С установкой и конфигурацией PostgreSQL в качестве базовой системы для Zabbix вы теперь имеете мощную и эффективную систему, готовую к использованию для мониторинга. Мы рассмотрели установку PostgreSQL как из предоставляемых поставщиками пакетов, так и из официальных репозиториев, обеспечение безопасности базы данных, создание необходимой базы данных Zabbix и пользователей, а также заполнение базы данных требуемыми схемами и начальными данными.

Ваша среда Zabbix готова к следующим этапам настройки и конфигурации.

---

## Вопросы

1. Какую версию PostgreSQL следует установить для совместимости и стабильности?
2. На каком порту работает моя база данных?
3. Какие пользователи базы данных я создал и почему?

---

## Полезные ссылки

- [https://yum.postgresql.org](ttps://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)