# Composants de Zabbix, fonctions de base et installation

Dans ce chapitre, nous approfondissons les connaissances fondamentales du chapitre "Prise en main" pour fournir un guide complet à la fois aux débutants qui installent Zabbix pour la première fois et aux utilisateurs avancés qui cherchent à optimiser leur configuration. Nous ne couvrirons pas seulement les étapes essentielles d'une installation de base, mais nous explorerons également les détails fins de l'architecture de Zabbix, ses composants et les meilleures pratiques.

Nous commencerons par vous guider tout au long du processus d'installation pour vous assurer une base solide à partir de laquelle construire. De là, nous passerons aux composants principaux de Zabbix, leur rôle respectif, comment ils interagissent et pourquoi ils sont essentiels à votre solution de supervision.
Vous apprendrez sur les sous-processus, leurs rôles et comment ils contribuent à l'efficacité et à la fiabilité de Zabbix.

De plus, nous explorerons des choix architecturaux judicieux qui peuvent faire ou défaire votre configuration de surveillance. Que vous gériez un petit réseau ou une infrastructure en grande échelle, prendre les bonnes décisions de conception dès le début paiera ses dividendes en termes d'évolutivité, de performance et de maintenance.

Ce chapitre est conçu pour répondre à un large éventail de lecteurs.
Si vous cherchez simplement à mettre Zabbix en route, vous trouverez des instructions claires et étape par étape. Pour ceux qui souhaitent plonger plus profondément, nous fournirons des insights détaillés sur la façon dont Zabbix fonctionne sous le capot, vous aidant à prendre des décisions éclairées alignées avec vos besoins et vos plans de croissance future.

À la fin de ce chapitre, non seulement vous aurez une installation fonctionnelle de Zabbix, mais aussi une compréhension approfondie de ses composants et de son architecture, vous permettant d'exploiter Zabbix dans toute sa pleine capacité, indépendamment de la complexité de votre environnement.

Partons sur ce voyage détaillé dans Zabbix et équipons-nous des connaissances nécessaires pour démarrer et optimiser une solution de surveillance puissante.

???+ note

    "À partir de la version 7.0, Zabbix a changé son modèle de licence de GPLv2 à AGPLv3.
    C'est un changement significatif que les utilisateurs et les contributeurs doivent garder à l'esprit. L'adoption de l'AGPLv3 est conçue pour fermer la 'brèche cloud', assurant qu任一个翻译结果都应保持原文结构和术语不变，以下是符合要求的法文翻译：

```markdown
# Composants de Zabbix, fonctions de base et installation

Dans ce chapitre, nous approfondissons les connaissances fondamentales du chapitre "Prise en main" pour fournir un guide complet à la fois aux débutants qui installent Zabbix pour la première fois et aux utilisateurs avancés qui cherchent à optimiser leur configuration. Nous ne couvrirons pas seulement les étapes essentielles d'une installation de base, mais nous explorerons également les détails fins de l'architecture de Zabbix, ses composants et les meilleures pratiques.

Nous commencerons par vous guider tout au long du processus d'installation pour vous assurer une base solide à partir de laquelle construire. De là, nous passerons aux composants principaux de Zabbix, leur rôle respectif, comment ils interagissent et pourquoi ils sont essentiels à votre solution de supervision.
Vous apprendrez sur les sous-processus, leurs rôles et comment ils contribuent à l'efficacité et à la fiabilité de Zabbix.

De plus, nous explorerons des choix architecturaux judicieux qui peuvent faire ou défaire votre configuration de surveillance. Que vous gériez un petit réseau ou une infrastructure en grande échelle, prendre les bonnes décisions de conception dès le début paiera ses dividendes en termes d'évolutivité, de performance et de maintenance.

Ce chapitre est conçu pour répondre à un large éventail de lecteurs.
Si vous cherchez simplement à mettre Zabbix en route, vous trouverez des instructions claires et étape par étape. Pour ceux qui souhaitent plonger plus profondément, nous fournirons des insights détaillés sur la façon dont Zabbix fonctionne sous le capot, vous aidant à prendre des décisions éclairées alignées avec vos besoins et vos plans de croissance future.

À la fin de ce chapitre, non seulement vous aurez une installation fonctionnelle de Zabbix, mais aussi une compréhension approfondie de ses composants et de son architecture, vous permettant d'exploiter Zabbix dans toute sa pleine capacité, indépendamment de la complexité de votre environnement.

Partons sur ce voyage détaillé dans Zabbix et équipons-nous des connaissances nécessaires pour démarrer et optimiser une solution de surveillance puissante.

???+ note

    "À partir de la version 7.0, Zabbix a changé son modèle de licence de GPLv2 à AGPLv3.
    C'est un changement significatif que les utilisateurs et les contributeurs doivent garder à l'esprit. L'adoption de l'AGPLv3 est conçue pour fermer la 'brèche cloud', assurant qu任一个翻译结果都应保持原文结构和术语不变，以下是符合要求的法文翻译：

```markdown
# Composants de Zabbix, fonctions de base et installation

Dans ce chapitre, nous approfondissons les connaissances fondamentales du chapitre "Prise en main" pour fournir un guide complet à la fois aux débutants qui installent Zabbix pour la première fois et aux utilisateurs avancés qui cherchent à optimiser leur configuration. Nous ne couvrirons pas seulement les étapes essentielles d'une installation de base, mais nous explorerons également les détails fins de l'architecture de Zabbix, ses composants et les meilleures pratiques.

Nous commencerons par vous guider tout au long du processus d'installation pour vous assurer une base solide à partir de laquelle construire. De là, nous passerons aux composants principaux de Zabbix, leur rôle respectif, comment ils interagissent et pourquoi ils sont essentiels à votre solution de supervision.
Vous apprendrez sur les sous-processus, leurs rôles et comment ils contribuent à l'efficacité et à la fiabilité de Zabbix.

De plus, nous explorerons des choix architecturaux judicieux qui peuvent faire ou défaire votre configuration de surveillance. Que vous gériez un petit réseau ou une infrastructure en grande échelle, prendre les bonnes décisions de conception dès le début paiera ses dividendes en termes d'évolutivité, de performance et de maintenance.

Ce chapitre est conçu pour répondre à un large éventail de lecteurs.
Si vous cherchez simplement à mettre Zabbix en route, vous trouverez des instructions claires et étape par étape. Pour ceux qui souhaitent plonger plus profondément, nous fournirons des insights détaillés sur la façon dont Zabbix fonctionne sous le capot, vous aidant à prendre des décisions éclairées alignées avec vos besoins et vos plans de croissance future.

À la fin de ce chapitre, non seulement vous aurez une installation fonctionnelle de Zabbix, mais aussi une compréhension approfondie de ses composants et de son architecture, vous permettant d'exploiter Zabbix dans toute sa pleine capacité, indépendamment de la complexité de votre environnement.

Partons sur ce voyage détaillé dans Zabbix et équipons-nous des connaissances nécessaires pour démarrer et optimiser une solution de surveillance puissante.

???+ note

    "À partir de la version 7.0, Zabbix a changé son modèle de licence de GPLv2 à AGPLv3.
    C'est un changement significatif que les utilisateurs et les contributeurs doivent garder à l'esprit. L'adoption de l'AGPLv3 est conçue pour fermer la 'brèche cloud', assurant qu'un entité offrant Zabbix en tant que service hébergé doit contribuer ses modifications au sein de la communauté. Bien que cela protège l'intégrité du projet et assure une durabilité à long terme, c'est un changement que les organisations doivent examiner pour s'assurer de leur conformité avec leurs politiques internes sur le logiciel libre."
```