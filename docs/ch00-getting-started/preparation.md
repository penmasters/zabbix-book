---
description: |
    This section from The Zabbix Book titled "Preparing the system for Zabbix" 
    outlines the preliminary steps required before installing any Zabbix component.
    It includes instructions adding the official Zabbix repository for different
    Linux distributions, such as Rocky Linux, openSUSE, and Ubuntu. The section
    also provides specific remarks and tips for each operating system to ensure
    a smooth installation process.
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

![Zabbix Download](./basic-installation/ch01-basic-installation-zabbixdownload.png)

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

## Conclusion

With the preparation of your system for Zabbix now complete, you have successfully
configured your environment for the installation of Zabbix components. We've covered 
the steps to add the official Zabbix repository to your system, preparing it for the 
installation of Zabbix server, database, and frontend components.

Your system is now ready for the next steps. In the following chapter, we will
delve into the installation of the Zabbix components, guiding you through the
process of setting up the Zabbix server, database, and frontend. 

---

## Questions

---

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
