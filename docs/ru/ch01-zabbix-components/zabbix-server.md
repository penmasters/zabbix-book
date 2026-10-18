---
description: |
    Этот раздел из книги "The Zabbix Book", посвященный установке сервера Zabbix,
    поможет вам пройти через процесс установки и настройки сервера Zabbix на различных дистрибутивах Linux.
    Он охватывает установку пакета сервера Zabbix, настройку параметров подключения к базе данных
    и настройку брандмауэра для разрешения входящих соединений с сервером Zabbix.
    Кроме того, он предоставляет инструкции по запуску и включению службы сервера Zabbix,
    проверке конфигурации и проверке файла журнала сервера на наличие проблем.
tags: [beginner]
---

# Установка сервера Zabbix

Теперь, когда мы добавили репозиторий Zabbix с необходимым программным обеспечением,
мы готовы установить как сам сервер Zabbix, так и веб-сервер. Помните, что
веб-сервер не обязательно должен быть установлен на том же компьютере, что и сервер Zabbix;
они могут находиться на отдельных системах по желанию.

Чтобы установить компоненты сервера Zabbix, выполните следующую команду:

!!! info "Установка zabbix-server"

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


После успешной установки пакета сервера Zabbix нам нужно настроить сервер Zabbix для подключения к базе данных.
Это требует изменения файла конфигурации сервера Zabbix.

Файл конфигурации сервера Zabbix предлагает опцию включения дополнительных файлов конфигурации
для пользовательских параметров. В производственной среде обычно лучше избегать прямого изменения
оригинального файла конфигурации. Вместо этого вы можете создавать и включать отдельные файлы конфигурации для любых дополнительных или измененных параметров.
Этот подход гарантирует, что ваш оригинальный файл конфигурации остается нетронутым,
что особенно полезно при выполнении обновлений или управлении конфигурациями с помощью инструментов
таких как Ansible, Puppet или SaltStack.

На SUSE 16 и более поздних версиях эта функция уже включена и настроена по умолчанию.
(см. также [https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Поэтому на системах SUSE файл конфигурации сервера Zabbix находится по адресу
`/usr/etc/zabbix/zabbix_server.conf`, и он настроен для включения всех `.conf` файлов из директории
`/etc/zabbix_server/zabbix_server.d/`.

На других дистрибутивах вам может потребоваться включить эту функцию вручную:

Чтобы включить эту функцию, убедитесь, что следующая строка существует и не закомментирована
(с `#` перед ней) в `/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```


Путь `/etc/zabbix/zabbix_server.d/` уже должен быть создан установленным пакетом, но убедитесь,
что он действительно существует.

Теперь мы создадим пользовательский файл конфигурации `database.conf` в директории `/etc/zabbix/zabbix_server.d/`
для хранения наших параметров подключения к базе данных:

!!! info "Добавление параметров подключения к базе данных Zabbix"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```


    Добавьте следующие строки в файл конфигурации, чтобы соответствовать вашей настройке базы данных:

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```


Замените `<database-host>`, `<database-name>`, `<database-schema>`, `<database-user>`,
`<database-password>` и `<database-port>` соответствующими значениями для вашей
настройки. Это гарантирует, что сервер Zabbix сможет общаться с вашей базой данных.

Убедитесь, что перед параметрами конфигурации нет `#` (символ комментария),
так как Zabbix будет игнорировать строки, начинающиеся с `#` во время выполнения.
Кроме того, внимательно проверьте наличие дублирующихся строк конфигурации; если есть несколько
строк с одним и тем же параметром, Zabbix будет использовать значение из последнего вхождения.

Для нашей настройки конфигурация будет выглядеть следующим образом:

!!! example "Пример файла database.conf"

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


!!! note "Для PostgreSQL в режиме HA"

    С Zabbix 8.0 теперь возможно добавить более одного IP для DBHost. Таким образом,
    можно настроить высокодоступное базовое решение с PostgreSQL без необходимости использования балансировщика нагрузки.
    Zabbix сам определит активную базу данных. Пример:
    DBHost=192.168.10.2:5432,192.168.10.3:5432

В этом примере:

- `DBHost` относится к хосту, где находится ваша база данных (используйте localhost,
  если она на том же компьютере).
- `DBName` — это имя базы данных Zabbix.
- `DBSchema` — это имя схемы, используемое в PostgreSQL (только для PostgreSQL).
- `DBUser` — это пользователь базы данных.
- `DBPassword` — это пароль пользователя базы данных.
- `DBPort` — номер порта, на котором слушает ваш сервер базы данных (по умолчанию для
  MySQL/MariaDB 3306 и PostgreSQL 5432).

Убедитесь, что параметры отражают конфигурацию вашей базы данных.

---

## Настройка брандмауэра для разрешения соединений Zabbix trapper

На вашем компьютере с сервером Zabbix нам нужно убедиться, что брандмауэр настроен
на разрешение входящих соединений к серверу Zabbix.

Ваш сервер Zabbix должен принимать входящие соединения от агентов, отправителей и прокси-серверов Zabbix.
По умолчанию Zabbix использует порт `10051/tcp` для этих соединений.
Чтобы разрешить эти соединения, вам нужно открыть этот порт в вашем брандмауэре.

!!! info "Открытие брандмауэра для zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```


Если служба не распознается с помощью `firewall-cmd --add-service`, вы можете
указать порт вручную:

!!! info "Добавление порта вместо имени службы"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```


---

## Запуск сервера Zabbix

С обновленной конфигурацией сервера Zabbix для подключения к вашей базе данных,
вы теперь можете запустить и включить службу сервера Zabbix. Выполните следующую команду
для включения службы сервера Zabbix и настройки автоматического запуска при загрузке системы:

???+ note

    Перед перезапуском сервера Zabbix после изменения его конфигурации рекомендуется проверить
    конфигурацию, чтобы предотвратить возможные проблемы. Проверка конфигурации позволяет обнаружить ошибки заранее,
    избегая простоя системы из-за некорректной конфигурации. Это можно сделать с помощью следующей команды: `zabbix-server -T`

!!! info "Включение и запуск службы zabbix-server"

    Red Hat, SUSE и Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```


Эта команда запустит службу сервера Zabbix немедленно и настроит ее для автоматического запуска при загрузке системы.
Чтобы убедиться, что сервер Zabbix работает правильно, проверьте файл журнала на наличие сообщений. Вы можете просмотреть
последние записи в файле `Zabbix server` с помощью следующей команды:

!!! info "Проверка файла журнала"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```


Ищите сообщения, указывающие на успешный запуск сервера. Если есть какие-либо проблемы,
файл журнала предоставит детали для устранения неполадок.

!!! example "Пример вывода"

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


Если произошла ошибка и сервер не смог подключиться к базе данных, вы увидите что-то вроде этого
в файле журнала сервера:

!!! example "Пример файла журнала с ошибками"

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


В этом случае проверьте параметры подключения к базе данных в файле `/etc/zabbix/zabbix_server.d/database.conf` и убедитесь,
что база данных правильно настроена, как описано в предыдущих шагах. Также проверьте правила брандмауэра
и при использовании PostgreSQL убедитесь, что `pg_hba.conf` правильно настроен для разрешения соединений с сервером Zabbix.

Давайте проверим службу zabbix-server, чтобы узнать, включена ли она и будет ли работать после перезагрузки

!!! info "Проверка статуса службы zabbix-server"

    ```bash
    sudo systemctl status zabbix-server
    ```


???+ example "Пример вывода"
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


Это завершает нашу главу по установке и настройке сервера Zabbix.

---

## Заключение

С успешной установкой и настройкой сервера Zabbix вы теперь создали основную компоненту вашей системы мониторинга.
Мы рассмотрели установку пакета сервера Zabbix, настройку параметров подключения к базе данных
и настройку брандмауэра для разрешения входящих соединений с сервером Zabbix. Кроме того,
мы запустили службу сервера Zabbix и проверили ее работу.

Ваш сервер Zabbix теперь готов общаться с агентами, отправителями и прокси-серверами Zabbix.
Следующим шагом будет установка и настройка веб-интерфейса Zabbix, который предоставит пользовательский интерфейс для взаимодействия с вашей системой мониторинга.

Давайте перейдем к следующей главе для настройки веб-интерфейса Zabbix.

---

## Вопросы

1. Какую версию Zabbix следует установить для совместимости и стабильности?
2. Какие журналы Zabbix следует проверять при устранении неполадок?

---

## Полезные ссылки

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)