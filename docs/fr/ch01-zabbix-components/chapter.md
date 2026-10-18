# Composants Zabbix, fonctions de base et installation

Dans ce chapitre, nous approfondissons les connaissances fondamentales acquises dans
la section « Prise en main » afin de proposer un guide complet, tant aux débutants
qui installent Zabbix pour la première fois qu'aux utilisateurs avancés souhaitant
optimiser leur configuration. Nous aborderons non seulement les étapes essentielles
d'une installation de base, mais aussi les détails de l'architecture Zabbix, de ses
composants et des bonnes pratiques.

Nous commencerons par parcourir le processus d'installation afin de vous fournir une
base solide. Nous examinerons ensuite les principaux composants de Zabbix, leur rôle,
leurs interactions et les raisons pour lesquelles ils sont essentiels à votre solution
de supervision. Vous découvrirez les sous-processus, leurs fonctions et leur contribution
à l'efficacité et à la fiabilité de Zabbix.

Nous étudierons également les bons choix d'architecture, qui peuvent faire toute la
différence dans une configuration de supervision. Que vous gériez un petit réseau ou
une infrastructure à grande échelle, prendre les bonnes décisions de conception dès
le départ sera bénéfique en matière d'évolutivité, de performances et de maintenance.

Ce chapitre s'adresse à un large éventail de lecteurs. Si vous souhaitez simplement
mettre Zabbix en service, vous y trouverez des instructions claires et progressives.
Pour ceux qui veulent aller plus loin, nous expliquerons en détail le fonctionnement
interne de Zabbix afin de vous aider à faire des choix éclairés, adaptés à vos besoins
et à vos projets de croissance.

À la fin de ce chapitre, vous disposerez non seulement d'une installation Zabbix
opérationnelle, mais aussi d'une compréhension approfondie de ses composants et de
son architecture. Vous pourrez ainsi exploiter pleinement Zabbix, quelle que soit
la complexité de votre environnement.

Commençons ce parcours détaillé dans Zabbix et acquérons les connaissances nécessaires
pour mettre en place et optimiser une puissante solution de supervision.

???+ note

    « À partir de la version 7.0, Zabbix a remplacé sa licence GPLv2 par la licence
    AGPLv3. Il s'agit d'un changement important dont les utilisateurs et les contributeurs
    doivent tenir compte. L'adoption de l'AGPLv3 vise à combler la “faille du cloud” en
    garantissant que toute entité proposant Zabbix en tant que service hébergé restitue
    ses modifications à la communauté. Bien que cela protège l'intégrité du projet et
    assure sa pérennité, les organisations doivent examiner ce changement afin de
    garantir sa conformité avec leurs politiques internes relatives aux logiciels libres. »
