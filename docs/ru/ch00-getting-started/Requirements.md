---
description: |
    Learn Zabbix system requirements: supported OS, database options, hardware
    specs, firewall ports, and time sync needed for a smooth installation.
tags: [beginner]
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

???+ warning

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
только о наиболее распространенных вариантах: Ubuntu, Red Hat и дистрибутивах на
базе Suse.

Поскольку не у всех есть доступ к подписке на Red Hat Enterprise Linux (RHEL)
или SUSE Linux Enterprise Server (SLES), даже если учетная запись разработчика
предоставляет ограниченный доступ, мы выбрали Rocky Linux и openSUSE Leap в
качестве легкодоступной альтернативы. Для этой книги мы будем использовать Rocky
Linux 9.x, openSUSE Leap 16 и Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    OS installation steps are outside the scope of this book, but a default or even a
    minimal installation of your preferred OS should be sufficient. Please refrain from
    installing graphical user interfaces (GUIs) or desktop environments, as they are
    unnecessary for server setups and consume valuable resources.

После установки выбранной вами ОС необходимо выполнить несколько важных
настроек, прежде чем приступать к установке Zabbix. Выполните следующие действия
на **всех** серверах, на которых будут размещены компоненты Zabbix (т. е. сервер
Zabbix, сервер базы данных и веб-сервер).

---

### Обновление системы

Перед установкой компонентов Zabbix или любого другого нового программного
обеспечения лучше всего убедиться, что ваша операционная система обновлена
последними патчами и исправлениями безопасности. Это поможет сохранить
стабильность системы и совместимость с программным обеспечением, которое вы
собираетесь установить. Даже если ваша ОС установлена недавно, все равно
рекомендуется запустить обновление, чтобы убедиться, что у вас установлены
последние пакеты.

Для обновления системы выполните следующую команду в зависимости от вашей ОС:

!!! info "Обновите свою систему"

    Red Hat
    ```bash
    dnf update
    ```

    SUSE
    ```bash
    zypper refresh
    zypper update
    ```

    Ubuntu
    ```bash
    sudo apt update
    sudo apt upgrade
    ```
???+ note "Что такое apt, dnf или zypper"

    - DNF (Dandified YUM) is a package manager used in recent Red Hat-based systems (invoked as `dnf`).
    - ZYpp (Zen / YaST Packages Patches Patterns Products) is the package manager 
    used on SUSE-based systems (invoked as `zypper`) and 
    - APT (Advanced Package Tool) is the package manager used on Debian/Ubuntu-based systems (invoked as `apt`). 

    If you're using another distribution, replace `dnf`/`zypper`/`apt` with your appropriate 
    package manager, such as `yum`, `pacman`, `emerge`, `apk` or ... .

    Do note that package names may also vary from distribution to distribution.

???+ tip

    Regularly updating your system is crucial for security and performance.
    Consider setting up automatic updates or scheduling regular maintenance windows
    to keep your systems current.

---

### sudo

По умолчанию процессы Zabbix, такие как сервер и агент Zabbix, запускаются под
собственными учетными записями непривилегированных пользователей (например,
`zabbix`). Однако существуют сценарии, в которых требуются повышенные
привилегии, например, выполнение пользовательских сценариев или команд,
требующих доступа root. Также в этой книге мы будем выполнять некоторые
административные задачи, требующие `sudo` в системе.

Обычно в большинстве систем уже присутствует `sudo`, но при минимальной
установке вашей ОС он может отсутствовать. Поэтому нам необходимо убедиться, что
он установлен.

Это также позволит пользователю Zabbix выполнять определенные настроенные
команды с повышенными привилегиями без необходимости полностью переключаться на
пользователя root.

!!! info "Что такое sudo"

    `sudo` (short for "superuser do") is a command-line utility that allows
    permitted users to execute commands with the security privileges of another
    user, typically the superuser (root). It is commonly used in Unix-like
    operating systems to perform administrative tasks without needing to log in
    as the root user.

Чтобы установить `sudo` выполните следующую команду в зависимости от вашей ОС:

!!! info "Установка sudo"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    On Ubuntu, `sudo` is normally installed by default. Root access is managed
    through `sudo` for the initial user created during installation.

Если `sudo` уже установлена, эти команды сообщат вам, что последняя версия уже
присутствует и никаких дополнительных действий не требуется. Если же нет, то
менеджер пакетов продолжит установку.

---

### Брандмауэр

Далее необходимо убедиться, что брандмауэр установлен и настроен. Брандмауэр -
это важнейший компонент безопасности, помогающий защитить ваш сервер от
несанкционированного доступа и потенциальных угроз, контролируя входящий и
исходящий сетевой трафик на основе заранее установленных правил безопасности.

Чтобы установить и включить брандмауэр, выполните следующую команду:

!!! info "Установите и включите брандмауэр"

    Red Hat
    ```bash
    dnf install firewalld
    systemctl enable firewalld --now
    ```
    SUSE
    ```bash
    zypper install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```bash
    sudo apt install ufw
    sudo ufw enable
    ```
???+ note "Что такое firewalld / ufw"

    Firewalld is the replacement for iptables in RHEL- and SUSE-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps.
    Ubuntu makes use of UFW which is merely a frontend for iptables.

Во время установки Zabbix в следующих главах нам нужно будет открыть
определенные порты в брандмауэре для обеспечения связи между компонентами
Zabbix.

Помимо простого открытия портов, как мы будем делать в следующих главах, вы
также можете определить специальные зоны брандмауэра для конкретных случаев
использования. Такой подход повышает безопасность, изолируя службы и ограничивая
доступ на основе уровней доверия. Например...

!!! example "Создание зоны firewalld для доступа к базе данных"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Вы можете подтвердить создание зоны, выполнив следующую команду:

!!! example "Проверьте создание зоны"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Использование зон в firewalld для настройки правил брандмауэра дает несколько
преимуществ с точки зрения безопасности, гибкости и простоты управления. Вот
почему зоны полезны:

- **Детальный контроль доступа :**

: Зоны firewalld позволяют устанавливать разные уровни доверия для различных
сетевых интерфейсов и диапазонов IP-адресов. Вы можете определить, каким
системам разрешено подключаться к PostgreSQL в зависимости от их уровня доверия.

- **Упрощенное управление правилами:**

: Вместо того, чтобы вручную определять сложные правила iptables, зоны
предоставляют организованный способ группировки и управления правилами
брандмауэра на основе сценариев использования.

- **Повышенная безопасность:**

: Ограничивая доступ приложений к определенной зоне, вы предотвращаете
несанкционированные подключения из других интерфейсов или сетей.

- **Динамическая конфигурация:**

: firewalld поддерживает временные и постоянные конфигурации правил, что
позволяет вносить изменения, не нарушая существующих соединений.

- **Поддержка нескольких интерфейсов:**

: Если сервер имеет несколько сетевых интерфейсов, зоны позволяют использовать
различные политики безопасности для каждого интерфейса.

Если собрать все вместе, то чтобы добавить зону для, например, PostgreSQL, это
будет выглядеть следующим образом:

!!! example "Firewalld с настройкой зон для доступа к базе данных PostgreSQL"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Где `IP-адрес источника` является единственным адресом, с которого разрешено
устанавливать соединение с базой данных.

Если вы хотите использовать зоны при работе с firewalld, адаптируйте инструкции
в следующих главах соответствующим образом.

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
    ```bash
    dnf install chrony
    systemctl enable chronyd --now
    ```

    SUSE
    ```bash
    zypper install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```bash
    sudo apt install chrony
    ```

После установки убедитесь, что Chrony включен и работает, проверив его состояние
с помощью следующей команды:

!!! info "Проверка статуса chronyd"

    ```bash
    systemctl status chronyd
    ```

???+ note "что такое Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

После установки Chrony необходимо убедиться, что установлен правильный часовой
пояс. Просмотреть текущую конфигурацию времени можно с помощью команды
`timedatectl`:

!!! example "Проверьте конфигурацию времени"

    ```shell-session
    localhost:~ # timedatectl
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

!!! info "Список часовых поясов"

    ```bash
    timedatectl list-timezones
    ```

Эта команда отобразит список доступных часовых поясов, позволяя выбрать тот,
который ближе всего к вашему местоположению. Например:

!!! example "Список всех доступных часовых поясов"

    ```shell-session
    localhost:~ # timedatectl list-timezones
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

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Чтобы убедиться, что часовой пояс настроен правильно, снова выполните команду
`timedatectl`:

!!! example "Проверьте время и пояс"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 16:13:35 CET
               Universal time: Thu 2023-11-16 15:13:35 UTC
                     RTC time: Thu 2023-11-16 15:13:36
                    Time zone: Europe/Brussels (CET, +0100)
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

#### Проверка синхронизации Chrony

Чтобы убедиться, что Chrony синхронизируется с правильными серверами времени, вы
можете выполнить следующую команду:

!!! info "Проверьте chrony"

    ```bash
    chronyc
    ```

Выходные данные должны быть похожи на:

!!! example "Проверьте вывод chrony"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Войдя в приглашение Chrony, введите команду `sources`, чтобы проверить
используемые источники времени:

Пример вывода:

!!! example "Проверьте источники вашего сервера времени"

    ```shell-session
    chronyc> sources
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

#### Обновление серверов времени

Чтобы обновить серверы времени, измените конфигурационный файл Chrony:

!!! info "Редактирование файла конфигурации chrony"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    On SUSE, the pool configuration is located in a separate file. You can
    edit that file directly or add a new configuration file in the same directory.
    In the latter case, ensure to disable or remove the existing pool configuration
    to avoid conflicts.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Замените существующий пул NTP-серверов на более близкий к вашему местоположению.

Пример текущей конфигурации:

!!! example "Пример конфигурации пула ntp"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Измените нужный вам пул на локальный сервер времени:

!!! info "Изменить конфигурацию пула ntp"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

После внесения этих изменений перезапустите службу Chrony для применения новой
конфигурации:

!!! info "Перезапустите службу chrony"

    ```bash
    systemctl restart chronyd
    ```

#### Проверка обновленных серверов времени

Проверьте источники времени еще раз, чтобы убедиться, что новые местные серверы
используются:

!!! info "Проверьте источники chrony"

    ```
    chronyc> sources
    ```

Пример ожидаемого результата при использовании местных серверов:

!!! example "Пример вывода"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Это подтверждает, что система теперь использует местные серверы времени.

## Заключение

Как мы уже убедились, прежде чем рассматривать пакеты Zabbix, необходимо уделить
внимание среде, в которой они будут находиться. Правильно настроенная и
обновленная операционная система, открытый путь через брандмауэр и точный учет
времени - это не просто рекомендации, а важнейшие составляющие. Заложив эту
основу, мы можем с уверенностью приступить к установке Zabbix, зная, что базовая
система готова к выполнению задачи.

## Вопросы

- Как вы думаете, почему точная синхронизация времени так важна для такой
  системы мониторинга, как Zabbix?
- Теперь, когда фундамент заложен, что, по вашему мнению, будет первым шагом в
  процессе установки Zabbix?
- Приступая к установке Zabbix, давайте подумаем о сетевом взаимодействии. Какие
  ключевые порты необходимо разрешить через брандмауэр, чтобы сервер Zabbix и
  агенты могли эффективно взаимодействовать?

## Полезные URL-адреса

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
