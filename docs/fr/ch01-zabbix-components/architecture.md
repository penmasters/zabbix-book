---
description: |
    This section from The Zabbix Book titled "Zabbix architecture" explains the 
    modular structure of a Zabbix setup. It highlights the roles of each component
    and their interdependencies, while providing an introduction to how we will 
    perform the installation of the components in next sections.
tags: [beginner]
---

# Architecture de Zabbix

Dans ce chapitre, nous allons suivre le processus d'installation du serveur
Zabbix. Il existe de nombreuses façons de configurer un serveur Zabbix. Nous
couvrirons les configurations les plus courantes avec MariaDB et PostgreSQL sur
les distributions basées sur RHEL et SLES et Ubuntu.

Avant de commencer l'installation, il est important de comprendre l'architecture
de Zabbix. Le serveur Zabbix est structuré de manière modulaire et se compose de
trois éléments principaux, que nous allons examiner en détail.

- Le serveur Zabbix
- Le serveur web Zabbix (frontend)
- La base de données Zabbix

!!! abstract "Creation of DB users"

    In our setup we will create 2 DB users `zabbix-web` and `zabbix-srv`. The 
    zabbix-web user will be used for the frontend to connect to our zabbix database.
    The zabbix-srv user will be used by our zabbix server to connect to the database.
    This allows us to limit the permissions for every user to only what is strictly
    needed.


![overview](ch01-basic-installation-zabbixserver.png){ align=left }

_1.1 Zabbix basic split installation_

All of these components can either be installed on a single server or
distributed across three separate servers. The core of the system is the Zabbix
server, often referred to as the "brain." This component is responsible for
processing trigger calculations and sending alerts. The database serves as the
storage for the Zabbix server's configuration and all the data it collects. The
web server provides the user interface (front-end) for interacting with the
system. It is important to note that the Zabbix API is part of the front-end
component, not the Zabbix server itself.

These components must function together seamlessly, as illustrated in the
diagram above. The Zabbix server must read configurations and store monitoring
data in the database, while the front-end needs access to read and write
configuration data. Furthermore, the front-end must be able to check the status
of the Zabbix server and retrieve additional necessary information to ensure
smooth operation.

For our setup, we will be using two virtual machines (VMs): one VM will host
both the Zabbix server and the Zabbix web front-end, while the second VM will
host the Zabbix database.

???+ note

    It is perfectly possible to install all components on one single VM or every component
    on a separate VM.
    The reason why we split the DB in our example is because the database will probably be
    the first component giving you performance headaches. It is also the component
    that needs some extra attention when we split it from the other components,
    so for this reason we have chosen in this example to split the database 
    from the rest of the setup.

We will cover the following topics:

- Install our Database based on MariaDB.
- Install our Database based on PostgreSQL.
- Installing the Zabbix server.
- Install the frontend.

