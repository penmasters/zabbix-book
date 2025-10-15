---
description: | Узнайте системные требования Zabbix: поддерживаемые ОС, параметры
базы данных, спецификации оборудования, порты брандмауэра и синхронизация
времени, необходимые для беспроблемной установки. теги: [beginner]
---

# Системные требования

## Требования

У Zabbix есть определенные требования к аппаратному и программному обеспечению,
которые должны быть выполнены, и эти требования могут меняться со временем. Они
также зависят от размера вашей установки и выбранного стека программного
обеспечения. Прежде чем приобретать оборудование или устанавливать версию базы
данных, необходимо ознакомиться с документацией Zabbix, чтобы узнать самые
последние требования к версии, которую вы планируете установить. Вы можете найти
последние требования
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Убедитесь, что выбрали правильную версию Zabbix из списка.

Для небольших или тестовых установок Zabbix может комфортно работать на системе
с 2 процессорами и 8 ГБ оперативной памяти. Однако размер вашей установки,
количество элементов для отслеживания, создаваемые триггеры и длительность
хранения данных будут влиять на требования к ресурсам. В современных
виртуализированных средах я советую начинать с малого и наращивать масштаб по
мере необходимости.

Вы можете установить все компоненты (сервер Zabbix, базу данных, веб-сервер) на
одной машине или распределить их по нескольким серверам. Для простоты обратите
внимание на детали сервера:

| Компонент          | IP-адрес |
| ------------------ | -------- |
| Сервер Zabbix      |          |
| Сервер базы данных |          |
| Веб-сервер         |          |

???+ tip

    Zabbix package names often use dashes (`-`) in their names, such as `zabbix-get`
    or `zabbix-sender`, but the binaries themselves may use underscores (`_`),
    like `zabbix_sender` or `zabbix_server`. This naming discrepancy can sometimes
    be confusing, particularly if you are using packages from non-official Zabbix
    repositories.
    Always check if a binary uses a dash or an underscore when troubleshooting.

???+ note

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Базовая конфигурация ОС

Операционных систем множество вариантов, каждая со своими преимуществами и
лояльной пользовательской базой. Хотя Zabbix можно установить на широкий спектр
платформ, документировать процесс для каждой доступной ОС было бы непрактично.
Чтобы сделать эту книгу целенаправленной и эффективной, мы решили рассказать
только о наиболее распространенных вариантах: дистрибутивах на базе Ubuntu и Red
Hat.

Поскольку не у всех есть доступ к подписке на Red Hat Enterprise Linux (RHEL),
даже если учетная запись разработчика предоставляет ограниченный доступ, мы
выбрали Rocky Linux в качестве легкодоступной альтернативы. В этой книге мы
будем использовать Rocky Linux 9.x и Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://ubuntu.com/>

### Брандмауэр

Перед установкой Zabbix необходимо правильно подготовить операционную систему. В
первую очередь необходимо убедиться, что брандмауэр установлен и настроен.

Чтобы установить и включить брандмауэр, выполните следующую команду:

!!! info "Установите и включите брандмауэр"

    Red Hat
    ```yaml
    dnf install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```yaml
    sudo apt install ufw
    sudo ufw enable
    ```

После установки нужно настроить необходимые порты. Для Zabbix нам нужно
разрешить доступ к порту `10051/tcp`, через который траппер Zabbix прослушивает
входящие данные. Используйте следующую команду, чтобы открыть этот порт в
брандмауэре:

!!! info "Разрешить доступ к трапперу Zabbix"

    Red Hat
    ```yaml
    firewall-cmd --add-service=zabbix-server --permanent
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    ```

Если служба не распознается, то можете вручную указать порт:

!!! info "Добавить порт вместо имени службы"

    ```yaml
    firewall-cmd --add-port=10051/tcp --permanent
    ```

???+ note

    "Firewalld is the replacement for iptables in RHEL-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps."
    Ubuntu makes use of UFW and is merely a frontend for iptables.

Альтернативный подход заключается в определении специальных зон брандмауэра для
конкретных случаев использования. Например...

!!! info "Создать зону firewalld"

    ```yaml
    firewall-cmd --new-zone=postgresql-access --permanent
    ```

Вы можете подтвердить создание зоны, выполнив следующую команду:

!!! info "Проверьте создание зоны"

    ```yaml
    firewall-cmd --get-zones
    ```

block dmz drop external home internal nm-shared postgresql-access public trusted
work

Использование зон в firewalld для настройки правил брандмауэра для PostgreSQL
дает ряд преимуществ в плане безопасности, гибкости и простоты управления. Вот
почему зоны полезны:

- **Детальный контроль доступа :**
  - Зоны firewalld позволяют устанавливать разные уровни доверия для различных
    сетевых интерфейсов и диапазонов IP-адресов. Вы можете определить, каким
    системам разрешено подключаться к PostgreSQL в зависимости от их уровня
    доверия.
- **Упрощенное управление правилами:**
  - Вместо того чтобы вручную определять сложные правила iptables, зоны
    предоставляют организованный способ группировки и управления правилами
    брандмауэра на основе сценариев использования.
- **Повышенная безопасность:**
  - Ограничивая доступ к PostgreSQL в определенной зоне, вы предотвращаете
    несанкционированные подключения из других интерфейсов или сетей.
- **Динамическая конфигурация:**
  - firewalld поддерживает временные и постоянные конфигурации правил, что
    позволяет вносить изменения, не нарушая существующих соединений.
- **Поддержка нескольких интерфейсов:**
  - Если сервер имеет несколько сетевых интерфейсов, зоны позволяют использовать
    различные политики безопасности для каждого интерфейса.

Если собрать все вместе, это будет выглядеть следующим образом:

!!! info "Firewalld с конфигурацией зоны"

    ```yaml
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Где `IP-адрес источника` является единственным адресом, с которого разрешено
устанавливать соединение с базой данных.

---

### Сервер времени

Еще один важный шаг - настройка сервера времени и синхронизация сервера Zabbix с
помощью NTP-клиента. Точная синхронизация времени жизненно важна для Zabbix, как
для сервера, так и для устройств, которые он контролирует. Если на одном из
узлов установлен неправильный часовой пояс, это может привести к путанице,
например, при расследовании проблемы в Zabbix, которая, как оказалось, произошла
на несколько часов раньше, чем на самом деле.

Чтобы установить и включить chrony - наш NTP-клиент, используйте следующую
команду:

!!! info "Установить NTP-клиент"

    Red Hat
    ```yaml
    dnf install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```yaml
    sudo apt install chrony
    ```

После установки убедитесь, что Chrony включен и работает, проверив его состояние
с помощью следующей команды:

!!! info "Проверка статуса chronyd"

    ```yaml
    systemctl status chronyd
    ```

???+ note "что такое apt или dnf"

    dnf is a package manager used in Red Hat-based systems. If you're using another
    distribution, replace `dnf` with your appropriate package manager, such as `zypper`,
    `apt`, or `yum`.

???+ note "что такое Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

После установки Chrony необходимо убедиться, что установлен правильный часовой
пояс. Просмотреть текущую конфигурацию времени можно с помощью команды
`timedatectl`:

!!! info "проверьте конфигурацию времени"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 15:09:14 UTC
    Universal time: Thu 2023-11-16 15:09:14 UTC
    RTC time: Thu 2023-11-16 15:09:15
    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
    NTP service: active
    RTC in local TZ: no
    ```

Убедитесь, что служба Chrony активна (при необходимости обратитесь к предыдущим
шагам). Чтобы установить правильный часовой пояс, сначала необходимо вывести все
доступные часовые пояса с помощью следующей команды:

!!! info "список часовых поясов"

    ```yaml
    timedatectl list-timezones
    ```

Эта команда отобразит список доступных часовых поясов, позволяя выбрать тот,
который ближе всего к вашему местоположению. Например:

!!! info "Список всех доступных часовых поясов"

    ```yaml
    Africa/Abidjan
    Africa/Accra
    ...
    Pacific/Tongatapu
    Pacific/Wake
    Pacific/Wallis
    UTC
    ```

Определив часовой пояс, установите его с помощью следующей команды:

!!! info "Установите часовой пояс"

    ```yaml
    timedatectl set-timezone Europe/Brussels
    ```

Чтобы убедиться, что часовой пояс настроен правильно, снова выполните команду
`timedatectl`:

!!! info "Проверьте время и часовой пояс"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 16:13:35 CET
    Universal time: Thu 2023-11-16 15:13:35 UTC
    RTC time: Thu 2023-11-16 15:13:36
    **Time zone: Europe/Brussels (CET, +0100)**
    System clock synchronized: yes
    NTP service: active
    RTC in local TZ: no
    ```

???+ note

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

### Проверка синхронизации Chrony

Чтобы убедиться, что Chrony синхронизируется с правильными серверами времени, вы
можете выполнить следующую команду:

!!! info "Проверьте chrony"

    ```yaml
    chronyc
    ```

Выходные данные должны быть похожи на:

!!! info "Проверьте вывод chrony"

    ```yaml
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

После ввода запроса Chrony введите следующее для проверки источников:

!!! info ""

    ```yaml
    chronyc> sources
    ```

Пример вывода:

!!! info "Проверьте источники своего сервера времени"

    ```bash
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

В этом примере используемые серверы NTP расположены за пределами вашего региона.
Рекомендуется переключиться на серверы времени в вашей стране или, если это
возможно, на выделенный сервер времени компании. Найти местные NTP-серверы можно
здесь: [www.ntppool.org](https://www.ntppool.org/).

---

### Обновление серверов времени

Чтобы обновить серверы времени, измените файл `/etc/chrony.conf` для систем на
базе Red Hat, а если используете Ubuntu, отредактируйте
`/etc/chrony/chrony.conf`. Замените существующий NTP-сервер на более близкий к
вашему местоположению.

Пример текущей конфигурации:

!!! info "example ntp pool config"

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

    Change the pools you want to a local time server:

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

After making this change, restart the Chrony service to apply the new
configuration:

!!! info "restart the chrony service"

    ```yaml
    systemctl restart chronyd
    ```

### Verifying Updated Time Servers

Check the time sources again to ensure that the new local servers are in use:

!!! info "Check chrony sources"

    ```yaml
    chronyc> sources
    ```

Example of expected output with local servers:

!!! info "Example output"

    ```yaml
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

This confirms that the system is now using local time servers.

## Conclusion

As we have seen, before even considering the Zabbix packages, attention must be
paid to the environment in which it will reside. A properly configured operating
system, an open path through the firewall, and accurate timekeeping are not mere
suggestions, but essential building blocks. Having laid this groundwork, we can
now proceed with confidence to the Zabbix installation, knowing that the
underlying system is prepared for the task.

## Questions

- Why do you think accurate time synchronization is so crucial for a monitoring
  system like Zabbix?
- Now that the groundwork is laid, what do you anticipate will be the first step
  in the actual Zabbix installation process?
- As we move towards installing Zabbix, let's think about network communication.
  What key ports do you anticipate needing to allow through the firewall for the
  Zabbix server and agents to interact effectively?

## Useful URLs

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
