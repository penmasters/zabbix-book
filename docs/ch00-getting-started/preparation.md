---
description: |
    This section from The Zabbix Book titled "Preparing the system for Zabbix" 
    outlines the preliminary steps required before installing any Zabbix component.
    It includes instructions adding the official Zabbix repository and preparing
    the system for running containers using Podman.
tags: [beginner]
---

# Preparing the system for Zabbix

Before installing any Zabbix component, we need to ensure that the server(s)
meet the configuration requirements outlined in the previous section: [System Requirements](Requirements.md).

If you plan to install the Zabbix database, server and/or frontend on separate 
machines, prepare each server individually according to the instructions provided
here. Also servers that will host a Zabbix Proxy, need to be prepared in the same
way.

---

## Disable SELinux on RHEL

Another critical step at this stage if you use Red Hat based systems is disabling
SELinux, which can interfere with the installation and operation of Zabbix.
We will revisit SELinux at the end of this chapter once our installation is finished.

To check the current status of SELinux, you can use the following command: `sestatus``

!!! info "Selinux status"

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

As shown, the system is currently in enforcing mode. To temporarily disable SELinux,
you can run the following command: `setenforce 0`

!!! info "Disable SeLinux"

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

Now, as you can see, the mode is switched to permissive. However, this change
is not persistent across reboots. To make it permanent, you need to modify the
SELinux configuration file located at `/etc/selinux/config`. Open the file and
replace enforcing with `permissive`.

Alternatively, you can achieve the same result more easily by running the
following command:

!!! info "Disable SeLinux permanent"

    Red Hat
    ``` bash
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

This line will alter the configuration file for you. So when we run `sestatus`
again we will see that we are in `permissive` mode and that our configuration
file is also in permissive mode.

!!! info "Verify selinux status again"

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

## Install the Zabbix repository

From the Zabbix Download page [https://www.zabbix.com/download](https://www.zabbix.com/download),
select the appropriate Zabbix version you wish to install. In this case, we will
be using Zabbix 8.0 LTS. Additionally, ensure you choose the correct OS distribution
for your environment, which will be Rocky Linux 9, openSUSE Leap 16 or Ubuntu 24.04 in our case.

We will be installing the Zabbix Server along with NGINX as the web server for
the front-end. Make sure to download the relevant packages for your chosen configuration.

![Zabbix Download](./getting-started/ch00-getting-started-zabbixdownload.png)

_1.2 Zabbix
download_

---

### Red Hat specific remarks

If you make use of a RHEL based system like Rocky then the first step is to disable
the Zabbix packages provided by the EPEL repository, if it's installed on your system.
To do this, edit the `/etc/yum.repos.d/epel.repo` file and add the following statement
to disable the EPEL repository by default:

!!! info "Exclude packages"

    Red Hat
    ``` ini
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ tip

    It's considered bad practice to keep the EPEL repository enabled all the time,
    as it may cause conflicts by unintentionally overwriting or installing unwanted
    packages. Instead, it's safer to enable the repository only when needed, by using
    the following command during installations: dnf install --enablerepo=epel <package-name>
    This ensures that EPEL is only enabled when explicitly required.

---

### OpenSUSE specific remarks

On openSUSE, Zabbix packages are also available in the default `repo-oss` repository. 
Unlike RHEL-based systems, openSUSE does not provide a built-in way to exclude
specific packages from individual repositories. However, the Zabbix packages
included in the default repositories are typically one to two LTS versions behind
the latest releases. As a result, they are unlikely to interfere with your
installation unless they are already installed.

In the next step, we will configure the official Zabbix repositories. As long
as you select a Zabbix repository version newer than the packages available in 
`repo-oss`, zypper will automatically install the most recent version.

???+ tip

    If you have already installed Zabbix packages from the default repositories, 
    it is recommended to either:

    - Remove them before proceeding, or
    - Upgrade them after adding the new Zabbix repositories, using the zypper 
      option `--allow-vendor-change`.

???+ note "Suse Linux Enterprise Server (SLES)"

    If you are using SLES, the Zabbix packages are not included in the default
    repositories. Therefore, you can proceed to add the official Zabbix repository
    without any concerns about conflicts with existing packages.

---

### Adding the Zabbix repository

Next, we will install the Zabbix repository on our operating system. After adding
the Zabbix repository, it is recommended to perform a repository cleanup to remove
old cache files and ensure the repository metadata is up to date. You can do this
by running:

!!! info "Add the zabbix repo"

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

This will refresh the repository metadata and prepare the system for Zabbix installation.

???+ note "What is a repository?"

    A repository in Linux is a configuration that allows you to access and install
    software packages. You can think of it like an "app store" where you find and
    download software from a trusted source, in this case, the Zabbix repository.
    Many repositories are available, but it's important to only add those you trust.
    The safest practice is to stick to the repositories provided by your operating
    system and only add additional ones when you're sure they are both trusted and necessary.

    For our installation, the Zabbix repository is provided by the vendor itself,
    making it a trusted source. Another popular and safe repository for
    Red Hat-based systems is EPEL (Extra Packages for Enterprise Linux), which is
    commonly used in enterprise environments.
    However, always exercise caution when adding new repositories to ensure
    system security and stability.

---

## Preparing the system for running containers using Podman

If you plan to run Zabbix components as containers using Podman, you need to
ensure that Podman is installed and properly configured on your system. Below
are the instructions for installing Podman on different operating systems.

You can skip this section if you do not plan to run any Zabbix components as containers on the current system.

???+ note "Why Podman?"

    Podman is a popular containerization tool that allows you to run and manage
    containers without requiring a daemon like Docker. It is the recommended
    container engine on most modern distributions and offers several advantages
    over Docker.

    Firstly, Podman enhances security by supporting rootless containers, allowing containers
    to run under non-privileged user accounts. Secondly, it integrates seamlessly with
    SELinux, enabling robust access control and policy enforcement. Thirdly, Podman
    works natively with systemd, which facilitates container lifecycle management through
    systemd units and quadlets.
    
### Installing Podman

To be able to run containers using Podman, we first need to install Podman and
some additional tools that will help us manage containers with SystemD.

!!! info "Install podman and needed tools"

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

### Configure Podman for user-based container management

Next, we will create a `podman`-user which will be running the container(s). You
are free to use a different username, e.g. `zabbix-proxy` for a user that will
be running only zabbix-proxy in a container.

!!! info "Create and init podman user"

    ```bash
    sudo useradd --comment "User for running container workloads" podman
    sudo -i -u podman
    mkdir -p ~/.local/share/containers
    mkdir -p ~/.config/containers/systemd/
    exit
    ```

When your system has SELinux enabled, execute the following command as `root`. 

!!! info "SELinux: Set file context mapping"

    ```bash
    semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
    ```

This command adds a SELinux file context mapping by creating an equivalence (-e)
between the default container storage directory `/var/lib/containers` and the user’s
Podman container storage path `/home/podman/.local/share/containers`. Essentially,
it tells SELinux to treat files in the user's container storage the same way it
treats files in the default system container storage, ensuring proper access
permissions under SELinux policy.

!!! info "SELinux: Apply file context mapping"

    ```bash
    restorecon -R -v /home/podman/.local/share/containers
    ```

After defining new SELinux contexts, this command recursively (`-R`) applies
the correct SELinux security contexts to the files in the specified directory.
The `-v` flag enables verbose output, showing what changes are made. This ensures
that all files in the container storage directory have the correct SELinux labels
as defined by the previous `semanage` commands.

!!! info "Enable lingering user processes"

    ```bash
    loginctl enable-linger podman
    ```

This command enables “linger” for the user `podman`. Linger allows user services
(such as containers managed by SystemD) to continue running even when the user
is not actively logged in. This is useful for running Podman containers in the
background and ensures that containerized proxies or other services remain active
after logout or system reboots.

As the final step in creating the Podman setup we need to to tell SystemD where 
the user-specific runtime files are stored:

!!! info "Set XDG_RUNTIME_DIR environment variable for podman user"

    ```bash
    sudo -u podman -i
    echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile && \
        source ~/.bash_profile
    ```

This line ensures that the `XDG_RUNTIME_DIR` environment variable is correctly set
for the `podman` user and is loaded in current and next sessions. 
This variable points to the location where user-specific runtime
files are stored, including the systemd user session bus. Setting it is essential
for enabling `systemctl --user` to function properly with Podman-managed containers.

Your system is now prepared for running Zabbix components as containers using Podman.

???+ warning "Known issue waiting for network-online.target"

    In case the starting of your containers takes about 90s and then ultimately
    fails to start. If you then see lines like this in your system logging 
    (`journalctl`):

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

    Then you are hitting a known [problem with the Podman Quadlets](https://github.com/containers/podman/issues/24796). 

    This is caused by the fact that the SystemD generated Quadlet service contains
    a dependency to the system-wide special target `network-online.target` which
    normally indicates the system's network is fully up and running. However on
    certain Linux distriutions or with specific networking configurations the
    system network components may not correctly notify SystemD that the network is
    "online", causing `network-online.target` to never get activated. This in turn
    makes that Podman will wait until it times out, thinking the network is not 
    yet available.

    As a workaround, you can create a dummy system service that will trigger 
    `network-online.target`:

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

???+ warning "Known issue waiting for network-online.target"

    In case the starting of your containers takes about 90s and then ultimately
    fail to start. If you then see lines like this in your system logging 
    (`journalctl`):

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

    Then you are hitting a known [problem with the Podman Quadlets](https://github.com/containers/podman/issues/24796). 

    This is caused by the fact that the SystemD generated Quadlet service contains
    a dependency to the system-wide special target `network-online.target` which
    normally indicates the system's network is fully up and running. However on
    certain Linux distriutions or with specific networking configurations the
    system network components may not correctly notify SystemD that the network is
    "online", causing `network-online.target` to never get activated. This in turn
    makes that Podman will wait until it times out, thinking the network is not 
    yet available.

    As a workaround, you can create a dummy system service that will trigger 
    `network-online.target`:

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

## Conclusion

With the preparation of your system for Zabbix now complete, you have successfully
configured your environment for the installation of Zabbix components. We've covered 
the steps to add the official Zabbix repository to your system, preparing it for the 
installation of Zabbix server, database, and frontend components.
And we have also prepared the system for running containers using Podman, if needed.

Your system is now ready for the next steps. In the following chapter, we will
delve into the installation of the Zabbix components, guiding you through the
process of setting up the Zabbix server, database, and frontend. 

---

## Questions

---

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
