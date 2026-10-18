---
description: |
    Cette section du livre The Zabbix Book intitulée "Architecture de Zabbix" explique la
    structure modulaire d'une installation Zabbix. Elle met en lumière les rôles de chaque composant
    et leurs interdépendances, tout en fournissant une introduction à la façon dont nous allons
    effectuer l'installation des composants dans les sections suivantes.
tags: [beginner]
---

# Architecture de Zabbix

Dans ce chapitre, nous allons parcourir le processus d'installation du serveur Zabbix.
Il existe de nombreuses façons différentes de configurer un serveur Zabbix. Nous couvrirons les
configurations les plus courantes avec MariaDB et PostgreSQL sur des distributions basées sur RHEL,
SLES et Ubuntu.

Avant de commencer l'installation, il est important de comprendre l'architecture
de Zabbix.
Le serveur Zabbix est structuré de manière modulaire, composé de trois principaux composants,
que nous examinerons en détail.

- Le serveur Zabbix
- Le serveur web Zabbix
- La base de données Zabbix

!!! abstract "Création des utilisateurs DB"

    Dans notre configuration, nous allons créer 2 utilisateurs DB `zabbix-web` et `zabbix-srv`.
    L'utilisateur zabbix-web sera utilisé pour le front-end pour se connecter à notre base de données Zabbix.
    L'utilisateur zabbix-srv sera utilisé par notre serveur Zabbix pour se connecter à la base de données.
    Cela nous permet de limiter les permissions pour chaque utilisateur uniquement aux éléments strictement
    nécessaires.


![aperçu](ch01.1-basic-installation-zabbixserver.png){ align=left }

_1.1 Installation de base de Zabbix
en plusieurs étapes_

Tous ces composants peuvent être installés sur un seul serveur ou répartis
sur trois serveurs distincts. Le cœur du système est le serveur Zabbix, souvent
référencé comme le "cerveau". Ce composant est responsable des calculs de déclencheurs et de l'envoi d'alertes.
La base de données sert de stockage pour la configuration du serveur Zabbix et toutes les données qu'il collecte.
Le serveur web fournit l'interface utilisateur (front-end) pour interagir avec le système. Il est important de noter
que l'API Zabbix fait partie du composant front-end, pas du serveur Zabbix lui-même.

Ces composants doivent fonctionner ensemble en parfaite harmonie, comme illustré dans le diagramme ci-dessus.
Le serveur Zabbix doit lire les configurations et stocker les données de surveillance dans la base de données,
tandis que le front-end a besoin d'accès pour lire et écrire des données de configuration. De plus, le front-end
doit être en mesure de vérifier l'état du serveur Zabbix et récupérer des informations supplémentaires nécessaires
pour assurer un fonctionnement fluide.

Pour notre configuration, nous utiliserons deux machines virtuelles (VM) : une VM hébergera à la fois le serveur Zabbix
et le front-end web Zabbix, tandis que la deuxième VM hébergera la base de données Zabbix.

???+ note

    Il est tout à fait possible d'installer tous les composants sur une seule VM ou chaque composant
    sur une VM distincte.
    La raison pour laquelle nous séparons la base de données dans notre exemple est parce que celle-ci sera probablement
    le premier composant qui vous causera des problèmes de performance. C'est également le composant
    qui nécessite un peu plus d'attention lorsque nous le séparons des autres composants,
    c'est pourquoi nous avons choisi dans cet exemple de séparer la base de données
    du reste de la configuration.

Nous couvrirons les sujets suivants :

- Installer notre base de données basée sur MariaDB.
- Installer notre base de données basée sur PostgreSQL.
- Installer le serveur Zabbix.
- Installer le front-end.