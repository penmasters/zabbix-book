---
description: |
  Cette section du livre Zabbix intitulée "Choix de la base de données" vous aide à sélectionner le backend et les packages de base de données appropriés pour votre installation Zabbix.
tags: [débutant]
---

# Choix de la base de données

## Sélection d'un backend de base de données pour Zabbix

Une décision critique lors de la gestion des installations Zabbix est la sélection du backend de base de données. Zabbix prend en charge plusieurs options de bases de données : MySQL/Percona, MariaDB, PostgreSQL (y compris TimescaleDB), et Oracle (jusqu'à Zabbix 7.0).

???+ warning "Dépréciation de la base de données Oracle"

    La version Zabbix 7.0 marque la dernière release offrant un support pour la base de données Oracle.
    Par conséquent, les systèmes exécutant Zabbix 7.0 ou toute version antérieure doivent entreprendre une migration vers une autre base de données telle que PostgreSQL, MySQL, ou une fourchette compatible comme MariaDB avant d'effectuer une mise à niveau vers une version ultérieure de Zabbix. Cette migration est une étape obligatoire pour garantir la continuité des fonctionnalités et la compatibilité avec les futures versions de Zabbix.

Toutes les bases de données prises en charge se comportent de manière similaire sous les charges de travail typiques de Zabbix, et Zabbix traite ces bases de données de manière équitable en termes de fonctionnalité. Par conséquent, le choix dépend principalement de votre ou de la familiarité de votre équipe avec un système de base de données particulier.
Une exception notable est TimescaleDB, une extension PostgreSQL optimisée pour les données sériées temporelles. Cela en fait un outil particulièrement adapté aux applications de supervision comme Zabbix qui gèrent des volumes importants de données timestampées.

Dans les environnements à grande échelle avec une collecte de données haute fréquence, TimescaleDB peut offrir des avantages significatifs en termes de performance, notamment des vitesses d'exécution améliorées et une compression intégrée pour réduire les exigences de stockage. Cependant, ces avantages viennent avec une complexité supplémentaire lors de l'installation et quelques restrictions sur la conservation des données historiques.

???+ tip "Installation de TimescaleDB"

    Étant donné sa nature avancée, TimescaleDB n'est pas essentielle pour la plupart des utilisateurs Zabbix.
    Par conséquent, son installation est en dehors du cadre de ce chapitre. Si vous prévoyez d'utiliser TimescaleDB, reportez-vous à [Partitioning PostgreSQL with TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md) pour des instructions détaillées après l'installation de PostgreSQL.

---

## Sélection de la source pour l'installation de la base de données

Dans ce chapitre, nous nous concentrerons sur l'installation de MariaDB et PostgreSQL, car elles sont les bases de données les plus couramment utilisées avec Zabbix. Pour les installations MySQL ou Percona, à l'exception des commandes d'installation des paquets, les étapes sont très similaires à celles de MariaDB.

Lors de l'installation de MariaDB ou PostgreSQL, vous devez déterminer la source à partir de laquelle vous souhaitez installer le serveur de base de données. Deux options principales sont disponibles :

1. **Paquets fournis par le fournisseur logiciel**

:   Ces paquets sont inclus dans les dépôts logiciels des distributions Linux et sont maintenus par le vendeur de la distribution.

    **Avantages :**
    
    - **Installation simplifiée :** Les paquets sont facilement disponibles via le gestionnaire de paquets de la distribution.
    - **Support du fournisseur :** Pour les distributions d'entreprise (par exemple, RHEL, SLES), des abonnements actifs incluent un support officiel.
    - **Compatibilité :** Intégration garantie avec d'autres paquets système et dépendances.
      - **Optimisations spécifiques à la distribution :** Inclut des configurations adaptées (par exemple, logrotate, bash completion,...).
      - **Maintenance à long terme :** Les correctifs de sécurité et les corrections de bogues sont rétroportés par le vendeur pour toute la durée du cycle de vie de support de la distribution.

    **Inconvénients :**
    
      - **Verrouillage sur la version :** Les mises à niveau importantes des distributions peuvent introduire automatiquement de nouvelles versions de base de données, potentiellement nécessitant des vérifications de compatibilité avec Zabbix.
      - **Modifications du fournisseur :** Les configurations par défaut, les répertoires de journalisation et les chemins de données peuvent être modifiés pour se conformer aux normes spécifiques à la distribution.

2. **Dépôts officiels MariaDB/PostgreSQL**

:   Ces dépôts fournissent des paquets directement depuis MariaDB/PostgreSQL et offrent l'accès aux dernières versions stables.

    **Avantages :**
    
    - **Versions à jour :** Accès immédiat aux fonctionnalités les plus récentes, correctifs de sécurité et corrections de bogues. Cependant, assurez-vous que Zabbix est compatible avec la version choisie.
    - **Support d'entreprise :** Option pour acheter MariaDB Enterprise ou Enterprise DB respectivement, qui inclut un support professionnel et des fonctionnalités supplémentaires.

    **Inconvénients :**
    
    - **Gestion manuelle de la version :** Les utilisateurs doivent surveiller activement et mettre à jour vers les nouvelles versions majeures pour garantir une couverture continue en matière de sécurité et de corrections de bogues.

???+ warning "Compatibilité des versions de base de données"

    Que vous prévoyez d'utiliser les paquets fournis par le système d'exploitation ou les paquets officiels du vendeur de la base de données, assurez-vous que la version de la base de données est prise en charge par votre version Zabbix pour éviter des problèmes potentiels d'intégration.
    Vérifiez [https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software](https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software) pour les versions les plus récentes prises en charge.

Avant l'installation du logiciel de base de données, assurez-vous que le serveur répond aux exigences de configuration et est prêt comme indiqué dans le chapitre précédent : [_Getting started_](../ch00-getting-started/Requirements.md).

---

## Conclusion

Nous avons discuté des différents backends de bases de données pris en charge par Zabbix. Nous avons également examiné les avantages et inconvénients d'utiliser les paquets fournis par le fournisseur logiciel ou les dépôts officiels pour installer MariaDB et PostgreSQL.

Armés de ces connaissances, vous êtes maintenant prêts à procéder avec l'installation du backend de base de données choisi. Dans les chapitres suivants, nous vous guiderons tout au long du processus d'installation pour MariaDB ou PostgreSQL, assurant que votre instance Zabbix est équipée d'un système de base de données robuste et efficace.

Maintenant que vous avez une compréhension claire des options de bases de données disponibles, passons à l'installation du backend de base de données de votre choix.

---

## Questions

1. Dois-je choisir MySQL ou PostgreSQL comme backend de la base de données ? Pourquoi ?
2. Dois-je utiliser les paquets fournis par le système d'exploitation, ou devrais-je installer des paquets officiels du vendeur de la base de données ? Pourquoi ?

---

## Liens utiles

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)