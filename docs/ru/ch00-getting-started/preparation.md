---
description: |
    Этот раздел книги Zabbix Book под названием «Подготовка системы для Zabbix»
    описывает предварительные действия перед установкой любого компонента Zabbix.
    В нем приведены инструкции по добавлению официального репозитория Zabbix и
    подготовке системы к запуску контейнеров с помощью Podman.
tags: [beginner]
---

# Подготовка системы для Zabbix

Перед установкой любого компонента Zabbix необходимо убедиться, что серверы
соответствуют требованиям, описанным в предыдущем разделе:
[Системные требования](Requirements.md).

Если база данных, сервер и/или веб-интерфейс Zabbix будут установлены на разных
машинах, подготовьте каждый сервер отдельно по приведенным здесь инструкциям.
Серверы, на которых будет работать прокси Zabbix, подготавливаются так же.

---

## Отключение SELinux в RHEL

В тестовой или лабораторной среде на базе Red Hat можно временно перевести
SELinux в разрешающий режим, чтобы он не мешал установке и первоначальной
настройке Zabbix.

Не отключайте SELinux в производственной среде. Там SELinux должен оставаться
включенным и работать в режиме enforcing. Инструкции по настройке необходимых
для Zabbix политик приведены в разделе о SELinux главы, посвященной расширенной
настройке и безопасности.

Чтобы проверить текущее состояние SELinux, выполните команду `sestatus`.

!!! info "Состояние SELinux"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   enforcing
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Как видно, система работает в режиме enforcing. Для временного перехода SELinux
в режим permissive выполните `setenforce 0`.

!!! info "Временно перевести SELinux в режим permissive"

    ```console
    ~# setenforce 0
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Теперь используется режим permissive, но после перезагрузки это изменение будет
потеряно. Чтобы сделать его постоянным, измените файл `/etc/selinux/config`,
заменив `enforcing` на `permissive`.

То же самое можно сделать следующей командой:

!!! info "Постоянно настроить режим permissive для SELinux"

    Red Hat
    ``` bash
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Эта команда изменит файл конфигурации. При следующем запуске `sestatus` текущий
режим и режим в файле конфигурации будут указаны как permissive.

!!! info "Повторно проверить состояние SELinux"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          permissive
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

---

## Установка репозитория Zabbix

На странице загрузки Zabbix
[https://www.zabbix.com/download](https://www.zabbix.com/download) выберите
нужную версию Zabbix. В этой книге используется Zabbix 8.0 LTS. Выберите также
подходящий дистрибутив: в наших примерах это Rocky Linux 9, openSUSE Leap 16 или
Ubuntu 24.04.

Мы установим сервер Zabbix и NGINX в качестве веб-сервера для веб-интерфейса.
Загрузите пакеты, соответствующие выбранной конфигурации.

![Zabbix Download](./getting-started/ch00.1-getting-started-zabbixdownload.png)

_0.1 Загрузка Zabbix_

---

### Особенности Red Hat

При использовании системы на базе RHEL, например Rocky Linux, сначала исключите
пакеты Zabbix из репозитория EPEL, если он установлен. Измените файл
`/etc/yum.repos.d/epel.repo` и добавьте следующую директиву:

!!! info "Исключить пакеты"

    Red Hat
    ``` ini
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ tip

    Не рекомендуется постоянно держать репозиторий EPEL включенным: это может
    привести к конфликтам из-за непреднамеренной замены или установки пакетов.
    Безопаснее включать его только при необходимости командой
    `dnf install --enablerepo=epel <package-name>`. В таком случае EPEL будет
    использоваться только по явному запросу.

---

### Особенности openSUSE

В openSUSE пакеты Zabbix также доступны в стандартном репозитории `repo-oss`.
В отличие от систем на базе RHEL, openSUSE не предоставляет встроенного способа
исключить отдельные пакеты из конкретного репозитория. Однако пакеты Zabbix в
стандартных репозиториях обычно отстают на одну или две версии LTS, поэтому они
не должны мешать установке, если только уже не установлены.

На следующем шаге мы настроим официальные репозитории Zabbix. Если выбранная
версия репозитория Zabbix новее пакетов в `repo-oss`, zypper автоматически
установит самую новую версию.

???+ tip

    Если пакеты Zabbix уже установлены из стандартных репозиториев, рекомендуется:

    - удалить их перед продолжением; или
    - обновить после добавления новых репозиториев Zabbix с параметром zypper
      `--allow-vendor-change`.

???+ note "SUSE Linux Enterprise Server (SLES)"

    В SLES пакеты Zabbix не входят в стандартные репозитории. Поэтому официальный
    репозиторий Zabbix можно добавить, не опасаясь конфликтов с существующими
    пакетами.

---

### Добавление репозитория Zabbix

Теперь установим репозиторий Zabbix в операционной системе. После его добавления
рекомендуется очистить кэш, чтобы удалить старые файлы и обновить метаданные:

!!! info "Добавить репозиторий Zabbix"

    Red Hat
    ``` bash
    rpm -Uvh https://repo.zabbix.com/zabbix/8.0/release/rocky/9/noarch/zabbix-release-latest-8.0.el9.noarch.rpm
    dnf clean all
    ```

    SUSE
    ``` bash
    rpm -Uvh --nosignature https://repo.zabbix.com/zabbix/8.0/release/sles/16/noarch/zabbix-release-latest-8.0.sles16.noarch.rpm
    zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'

    # Set the repository to auto-refresh to ensure it's always up to date
    zypper modifyrepo --refresh 'Zabbix Official Repository'
    ```

    Ubuntu
    ``` bash
    sudo wget https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo apt update
    ```

Эти команды обновят метаданные репозиториев и подготовят систему к установке
Zabbix.

???+ note "Что такое репозиторий?"

    Репозиторий в Linux — это конфигурация, позволяющая получать и устанавливать
    пакеты программного обеспечения. Его можно представить как магазин приложений,
    где программы загружаются из доверенного источника — в данном случае из
    репозитория Zabbix. Репозиториев существует много, но добавлять следует только
    те, которым вы доверяете. Безопаснее всего использовать репозитории операционной
    системы и добавлять другие, только если они надежны и действительно необходимы.

    Репозиторий Zabbix предоставляется самим производителем и является доверенным
    источником. Еще один популярный и надежный репозиторий для систем на базе
    Red Hat — EPEL (Extra Packages for Enterprise Linux), часто используемый в
    корпоративных средах. Тем не менее при добавлении новых репозиториев всегда
    соблюдайте осторожность, чтобы сохранить безопасность и стабильность системы.

---

## Подготовка системы к запуску контейнеров с помощью Podman

Если компоненты Zabbix будут работать в контейнерах Podman, убедитесь, что Podman
установлен и правильно настроен. Ниже приведены инструкции для разных операционных
систем.

Этот раздел можно пропустить, если на текущей системе компоненты Zabbix не будут
работать в контейнерах.

???+ note "Почему Podman?"

    Podman — популярный инструмент контейнеризации, который позволяет запускать
    контейнеры и управлять ими без демона, подобного Docker. Это рекомендуемый
    контейнерный движок для большинства современных дистрибутивов, обладающий
    рядом преимуществ перед Docker.

    Во-первых, Podman повышает безопасность благодаря rootless-контейнерам,
    работающим под непривилегированными учетными записями. Во-вторых, он тесно
    интегрирован с SELinux, обеспечивая надежный контроль доступа и применение
    политик. В-третьих, Podman нативно работает с systemd, что упрощает управление
    жизненным циклом контейнеров через юниты systemd и Quadlet.

### Установка Podman

Для запуска контейнеров сначала установите Podman и дополнительные инструменты,
необходимые для управления контейнерами через systemd.

!!! info "Установить Podman и необходимые инструменты"

    Red Hat
    ```bash
    dnf install podman policycoreutils-python-utils
    ```

    SUSE
    ```bash
    zypper install podman policycoreutils-python-utils
    ```

    Ubuntu
    ```bash
    sudo apt install podman
    ```

### Настройка Podman для управления контейнерами от имени пользователя

Создайте пользователя `podman`, от имени которого будут работать контейнеры.
Можно выбрать другое имя, например `zabbix-proxy` для пользователя, запускающего
в контейнере только прокси Zabbix.

!!! info "Создать и инициализировать пользователя Podman"

    ```bash
    sudo useradd --comment "User for running container workloads" podman
    sudo -i -u podman
    mkdir -p ~/.local/share/containers
    mkdir -p ~/.config/containers/systemd/
    exit
    ```

Если SELinux включен, выполните следующую команду от имени `root`.

!!! info "SELinux: задать сопоставление контекстов файлов"

    ```bash
    semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
    ```

Команда создает эквивалентность (`-e`) между стандартным каталогом хранения
контейнеров `/var/lib/containers` и пользовательским хранилищем Podman
`/home/podman/.local/share/containers`. SELinux будет обрабатывать файлы в
пользовательском хранилище так же, как в системном, и применять необходимые
разрешения своей политики.

!!! info "SELinux: применить сопоставление контекстов файлов"

    ```bash
    restorecon -R -v /home/podman/.local/share/containers
    ```

После определения новых контекстов SELinux эта команда рекурсивно (`-R`)
применяет правильные контексты безопасности к файлам каталога. Параметр `-v`
включает подробный вывод изменений. В результате все файлы хранилища получают
метки SELinux, заданные предыдущей командой `semanage`.

!!! info "Разрешить работу пользовательских процессов без активного сеанса"

    ```bash
    loginctl enable-linger podman
    ```

Эта команда включает «linger» для пользователя `podman`. Пользовательские службы,
например контейнеры под управлением systemd, продолжат работать без активного
сеанса. Контейнерные прокси и другие службы останутся активными после выхода
пользователя или перезагрузки системы.

На последнем этапе настройки Podman укажите systemd расположение пользовательских
файлов среды выполнения:

!!! info "Задать XDG_RUNTIME_DIR для пользователя Podman"

    ```bash
    sudo -u podman -i
    echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile && \
        source ~/.bash_profile
    ```

Эта строка задает переменную окружения `XDG_RUNTIME_DIR` для пользователя
`podman` и загружает ее в текущем и последующих сеансах. Переменная указывает
расположение пользовательских файлов среды выполнения, включая шину сеанса
systemd. Она необходима для корректной работы `systemctl --user` с контейнерами
под управлением Podman.

Система готова к запуску компонентов Zabbix в контейнерах Podman.

???+ warning "Известная проблема при ожидании network-online.target"

    Если запуск контейнеров занимает около 90 секунд и завершается ошибкой, а в
    системном журнале (`journalctl`) появляются подобные строки:

    ```
    systemd[1601]: Starting Wait for system level network-online.target as user....
    sh[3128]: inactive
    sh[3130]: inactive
    sh[3132]: inactive
    sh[3134]: inactive
    sh[3136]: inactive
    ...
    ...
    sh[3604]: inactive
    sh[3606]: inactive
    systemd[1601]: podman-user-wait-network-online.service: start operation timed out. Terminating.
    systemd[1601]: podman-user-wait-network-online.service: Main process exited, code=killed, status=15/TERM
    systemd[1601]: podman-user-wait-network-online.service: Failed with result 'timeout'.
    systemd[1601]: Failed to start Wait for system level network-online.target as user..
    ```

    это известная проблема Quadlet:
    [https://github.com/containers/podman/issues/24796](https://github.com/containers/podman/issues/24796).

    Служба Quadlet, созданная systemd, зависит от специальной системной цели
    `network-online.target`, которая обычно означает, что сеть полностью готова.
    В некоторых дистрибутивах Linux или сетевых конфигурациях сетевые компоненты
    могут не сообщить systemd, что сеть перешла в состояние «online». Тогда
    `network-online.target` не активируется, а Podman ожидает до истечения тайм-аута,
    считая, что сеть еще недоступна.

    В качестве обходного решения создайте фиктивную системную службу, которая
    активирует `network-online.target`:

    ```bash
    vi /etc/systemd/system/podman-network-online-dummy.service
    ```
    ```ini
    [Unit]
    Description=This is a dummy service to activate network-online.target
    After=network-online.target
    Wants=network-online.target

    [Service]
    ExecStart=/usr/bin/echo Activating network-online.target

    [Install]
    WantedBy=multi-user.target
    ```
    ```bash
    systemctl daemon-reload
    systemctl enable --now podman-network-online-dummy.service
    ```

---

## Заключение

Подготовка системы для Zabbix завершена. Среда настроена для установки компонентов
Zabbix. Мы добавили официальный репозиторий Zabbix и подготовили систему к
установке сервера Zabbix, базы данных и веб-интерфейса. При необходимости система
также подготовлена к запуску контейнеров с помощью Podman.

Теперь можно переходить к следующим шагам. В следующей главе мы установим
компоненты Zabbix и настроим сервер Zabbix, базу данных и веб-интерфейс.

---

## Вопросы

- Почему важно использовать официальный репозиторий Zabbix вместо пакетов,
  предоставляемых вашим дистрибутивом Linux?

- Почему SELinux должен оставаться включенным в производственной среде и к каким
  последствиям приводит переход в режим permissive?

---

## Полезные URL-адреса

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
