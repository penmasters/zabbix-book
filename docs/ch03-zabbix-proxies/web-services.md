---
description: |
    +- 160 character description for seo
tags: [advanced]
---
# Web services

This chapter explains what the Zabbix Web service component is why you may need
or consider it, what the requirements are and finally how to install it..

---

## What is the Zabbix web service?

The Zabbix web service is an optional component that can be deployed on the same
server as the Zabbix server, proxy, frontend or on a separate server. The web service is responsible for handling certain tasks that require a headless browser.

Currently the Zabbix web service is primarily used for generating and sending
scheduled reports, but there are plans to expand its functionality in future
releases of Zabbix.

The actual usage of the Zabbix web service to generate reports is covered in the
[Scheduled reports](../ch11-zabbix-visualisation/scheduled-reports.md) chapter.

---

## Zabbix web service requirements

The Zabbix web service requires a linux-based operating system and a headless
Google Chrome or Chromium. 

??? note "Google Chrome vs Chromium"

    Both Google Chrome and Chromium are supported by the Zabbix web service.
    However, Google Chrome is a proprietary browser developed by Google, while
    Chromium is an open-source project that serves as the basis for Google Chrome.
    Depending on your organization's policies and preferences, you may choose
    one over the other.

!!! warning "Known Chromium issue on Ubuntu 20-based distributions"

    There is a known issue on Ubuntu 20 where Zabbix web service will be unable 
    to start Chronium because the Ubuntu-packaged version of Chromium is not
    allowed to use home directories outside of `/home`. However, by default, the
    `zabbix`-user, configured by the Zabbix web service package, uses 
    `/var/lib/zabbix` as its home directory, which causes Chromium to fail to
    start on such distributions.

The system you choose to install the Zabbix web service on should meet the
requirements as outlined in the [_Getting Started: Requirements_](../ch00-getting-started/Requirements.md)
chapter and should have sufficient resources to run a headless browser. 
The exact resource requirements will depend on the number of reports you plan to
generate and the complexity of those reports. As a general guideline, we 
recommend at least 2 CPU cores and 4 GB of RAM for a system that will be used to
generate reports for a small to medium-sized Zabbix installation.

Installing Google Chrome or Chromium on your system will pull in additional
dependencies, such as Qt libraries, audio/video codecs, OpenGL libraries, font
rendering libraries, and others. Depending on how you installed your linux
operating system, many of these dependencies are probably not yet installed on
your system. All together, these dependencies may require up to 1 Gb of additional
disk space on your system disk. 

This may also be a reason to choose a separate system for the Zabbix web service
installation, especially if you are installing Zabbix server or proxy on a minimal
system and want to keep those systems clean and minimal.

Alternatively, you can also run the Zabbix web service as a container using Podman
or Docker, which includes a headless browser in the container image and keep
you host system clean of all those dependency packages. 

---

## Installing the Zabbix web service

The Zabbix web service can be installed using packages provided by Zabbix
or can be run as a container using Podman or Docker. We will cover both methods
in the chapter, starting with the package installation.

As with other Zabbix components, the Zabbix web service can be installed on the
same system as the Zabbix server, proxy or frontend, or on a separate system. 
If you choose to install it on a separate system, ensure that the system meets
the requirements as outlined in the [_Getting Started: Requirements_](../ch00-getting-started/Requirements.md).

---

### Installing the Zabbix web service package

Before we can install the Zabbix web service package, we need to prepare the server for Zabbix installation as outlined in the [_Preparing the server for Zabbix_](../ch00-getting-started/preparation.md) chapters.

When the system is ready and know where to find the Zabbix software packages, we
can proceed with the installation of the Zabbix web service package. The package
is named `zabbix-web-service` and can be installed using the package manager of
your operating system.

!!! info "Install zabbix-web-service package"

    Red Hat
    ```bash
    sudo dnf install zabbix-web-service
    ```

    SUSE
    ```bash
    zypper install zabbix-web-service
    ```

    Ubuntu
    ```bash
    sudo apt-get install zabbix-web-service
    ```

As mentioned before, the Zabbix web service requires a headless Google Chrome or Chromium
browser to be installed on the system. If you do not have it installed already,
you can install it using the package manager of your operating system.

!!! info "Install Chromium browser"

    To be able to install Chromium on Red Hat-based systems, you may need to 
    install and enable the [EPEL repository](https://docs.fedoraproject.org/en-US/epel/) 
    first. This is not required for Fedora.

    Red Hat
    ```bash
    dnf install --enablerepo=epel chromium
    ```

    To be able to install Chromium on SLES-based systems, you may need to 
    install and enable the [SUSE Package Hub](https://packagehub.suse.com/)
    repository first. This is not required for openSUSE.

    SUSE
    ```bash
    zypper install chromium
    ```

    Ubuntu
    ```bash
    sudo apt-get install chromium-browser
    ```

Alternatively, you can also install Google Chrome by downloading the package
from the [Google Chrome website](https://www.google.com/chrome/) and installing
it using the package manager of your operating system.

#### Configuring the Zabbix web service

Now that the Zabbix web service package and a headless browser are installed, we
need to configure the Zabbix web service to allow Zabbix server to make requests
to the web service. This is done by editing the `/etc/zabbix/zabbix_web_service.conf` 
configuration file.

For now, the only configuration parameter that needs to be set is the `AllowedIP`
parameter, which defines the IP addresses that are allowed to connect to the
Zabbix web service. That is, if you have installed the web service on a separate
system than the Zabbix server or proxy:

!!! info "Edit zabbix_web_service.conf"

    SUSE only:
    On SUSE 16 and later, the configuration file is installed at `/usr/etc/zabbix/zabbix_web_service.conf` and needs to be copied to `/etc/zabbix/` before editing:
    ```bash
    cp /usr/etc/zabbix/zabbix_web_service.conf /etc/zabbix/
    ```

    ```bash
    sudo vi /etc/zabbix/zabbix_web_service.conf
    ```
    ```ini
    AllowedIP=<IP_ADDRESS_OF_ZABBIX_SERVER>
    ```

#### Starting the Zabbix web service

Now that the Zabbix web service is installed and configured, we can start the
service using the SystemD service manager.

!!! info "Start Zabbix web service"

    ```bash
    sudo systemctl enable zabbix-web-service --now
    ```

After this, the Zabbix web service should be up and running and ready to accept
connections on port 10053 (by default) from the Zabbix server.

---

### Installing the Zabbix web service as a container

The Zabbix web service can also be run as a container using Podman or Docker.
This method does not require a separate installation of a headless browser, as the
container image already includes one. This reduces the number of extra packages
you need to install on your system.

Before we can install and run the Zabbix web service container, we need to prepare
the system for running containers as outlined in the [_Getting Started: Preparation_](../ch00-getting-started/preparation.md#configure-podman-for-user-based-container-management)
chapter.

Once the system is ready for running containers, we can proceed with creating
a `.container` systemd unit file for the Zabbix web service container. This file
should be created in the `~/.config/containers/systemd/` directory of the user
`podman` (or whatever user you have chosen to run the containers as).

Ensure you are logged in as user `podman`.

!!! info "Switch to user podman"

    ```bash
    sudo -u podman -i
    ```

???+ example "Creation of a .container systemd unit file"

    ```bash
    vi ~/.config/containers/systemd/zabbix-web-service.container
    ```

    ```ini
    [Unit]
    Description=Zabbix Web Service Container

    [Container]
    Image=docker.io/zabbix/zabbix-web-service:7.0-centos-latest
    ContainerName=ZabbixWebService-Quadlet
    AutoUpdate=registry
    EnvironmentFile=ZabbixWebService.env
    PublishPort=10053:10053

    [Service]
    Restart=always

    [Install]
    WantedBy=default.target
    ```

The Zabbix web service container image is available on [Docker Hub](https://hub.docker.com/r/zabbix/zabbix-web-service).
Specifically, we are using the image tagged `7.0-centos-latest` in this example,
which is maintained by the Zabbix team and is based on CentOS.

Next, we need to create an environment file that will be used to configure the
Zabbix web service container. This file should be created in the same directory
as the `.container` unit file and should be named `ZabbixWebService.env`, as 
referenced in the unit file above.

This environment file allows us to override default container settings by specifying
environment variables used during container runtime. The list of supported variables
and their functions is clearly documented on the container's Docker Hub page.

???+ example "Creation of the environment file"

    ```bash
    vi ~/.config/containers/systemd/ZabbixWebService.env
    ```

    ```ini
    # IP address or DNS name of the Zabbix server
    ZBX_ALLOWEDIP=<IP_ADDRESS_OF_ZABBIX_SERVER>
    ```

With our configuration now complete, the final step is to reload the systemd user daemon
so it recognizes the new Quadlet unit. This can be done using the following command:

!!! info "Reload SystemD user daemon"

    ``` bash
    systemctl --user daemon-reload
    ```

If everything is set up correctly, systemd will automatically generate a service
unit for the container based on the `.container` file. You can verify that the
unit has been registered by checking the output of `systemctl --user list-unit-files`:

???+ example "Verify if the new unit is registered correctly"

    ```shell-session
    podman@localhost:~> systemctl --user list-unit-files | grep zabbix
    zabbix-web-service.service             generated -
    ```
 
Now you can start the Zabbix web service container using the
`systemctl --user start` command.

!!! info "Start Zabbix web service container"

    ```bash
    systemctl --user start zabbix-web-service.container 
    ```
