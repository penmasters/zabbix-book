---
description : | Ce chapitre du livre Zabbix, intitulé " Frontend Installation ",
fournit un guide étape par étape pour configurer l'interface web de Zabbix.
Apprenez à installer les paquets nécessaires, à configurer PHP et à intégrer
Apache ou Nginx pour obtenir une interface de surveillance sécurisée et
entièrement fonctionnelle. tags : [beginner]
---

# Frontend expliqué

Ce chapitre va couvrir les bases que vous devez connaître à propos de
l'interface utilisateur de Zabbix et les choses que vous devez savoir avant de
pouvoir commencer à exploiter pleinement votre outil de surveillance. Nous
verrons comment fonctionne l'interface utilisateur, comment ajouter un hôte, des
groupes, des utilisateurs, des éléments... afin d'avoir une bonne compréhension
des bases. C'est quelque chose qui est parfois oublié et qui peut conduire à des
frustration, ne pas savoir pourquoi les choses ne fonctionnent pas comme nous
l'avions prévu. Donc, même si vous êtes un utilisateur avancé, il peut être
utile de jeter un coup d'oeil à ce chapitre.

Commençons

---

## Aperçu de l'interface

Avec Zabbix 7, l'interface de connexion utilisateur a légèrement changé. Notre
menu sur le côté gauche de l'écran a été légèrement remanié. Voyons cela de plus
près. Lorsque nous nous connectons à notre installation Zabbix pour la première
fois avec notre utilisateur Admin, nous voyons une page

comme ceci où nous avons la `fenêtre principale` en
<font color='green'>vert</font> le `menu principal` marqué en
<font color='red'>rouge</font> et les `liens` marqués en
<font color='gold'>jaune</font>.

![Vue d'ensemble](ch02-frontend-overview.png)

_2.1 Vue d'ensemble_

Le menu principal peut être caché en le réduisant complètement ou en le
réduisant à un ensemble de petites icônes. En cliquant sur le bouton avec les 2
flèches à gauche :

![Réduire](ch02-frontend-collapse.png)

_2.2 Réduction_

Vous verrez que le menu se réduit à un ensemble de petites icônes. En appuyant
sur ">>", le `menu principal` de reviendra à son état d'origine.

En cliquant sur l'icône qui ressemble à une boîte avec une flèche qui dépasse, à
côté du bouton "<<", vous masquerez complètement le `menu principal ` .

![Masquer](ch02-frontend-hide.png)

_2.3 Masquer_

Pour revenir à votre `menu principal` , c'est assez facile, il suffit de
chercher le bouton à gauche avec trois lignes horizontales et de cliquer dessus.
Cela affichera le `menu principal` mais il ne restera pas. Lorsque nous cliquons
sur la boîte avec la flèche pointant vers le bas à droite, le `menu principal`
est remis à sa place.

Une autre façon d'agrandir l'écran, très utile pour les moniteurs `NOC Teams`
par exemple, est le bouton `kiosk mode`. Celui-ci est situé sur le côté gauche
de l'écran et ressemble à 4 flèches pointant vers chaque coin de l'écran. En
appuyant sur ce bouton, tous les menus disparaissent et il ne reste plus que la
`fenêtre principale` sur laquelle vous pouvez vous concentrer.

![Expand](ch02-frontend-expand.png)

_2.4 Élargir_

Lorsque nous voulons quitter le mode kiosque, le bouton sera remplacé par 2
flèches pointant vers l'intérieur de l'écran. En appuyant sur ce bouton, nous
reviendrons à l'état d'origine.

![Expand](ch02-frontend-shrink.png)

_2.5 Réduire_

???+ tip

    We can also enter and exit kiosk mode by making use of parameters in our Zabbix
    url: `/zabbix.php?action=dashboard.view&kiosk=1` - activate kiosk mode or
    `/zabbix.php?action=dashboard.view&kiosk=0` - activate normal mode.

???+ note

    There are many other page parameters we can use. A full list can be found at
    [https://www.zabbix.com/documentation/7.4/en/manual/web_interface/page_parameters](https://www.zabbix.com/documentation/7.4/en/manual/web_interface/page_parameters)
    Zabbix also has a global search menu that we can use to find hosts, host groups
    and templates.

Si nous tapons dans la boîte de recherche le mot `server` vous verrez que nous
obtenons une vue d'ensemble de tous les `templates`, `host groups` et `hosts`
avec le serveur de nom dedans. C'est pourquoi on l'appelle la boîte de
`recherche globale` .

![Recherche globale](ch02-global-search.png)

_2.6 Recherche globale_

Voici notre résultat après avoir cherché le mot `serveur`. Si vous avez une
configuration Zabbix standard, votre page devrait ressembler plus ou moins à la
même chose.

![Résultat de la recherche globale](ch02-global-search-result.png)

_2.7 Résultat de la recherche globale_

---

## Menu principal

Nous allons maintenant examiner brièvement les éléments du menu principal de
l'application. Le `menu principal` , situé sur l'interface de gauche, comprend
au total neuf sections distinctes :

| Nom du menu         | Details                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Tableaux de bord    | Contient un aperçu de tous les tableaux de bord auxquels nous avons accès.                                                            |
| Monitoring          | Nous montre les hôtes, les problèmes, les dernières données, les cartes, ...                                                          |
| Services            | Une vue d'ensemble de tous les services et des paramètres SLA.                                                                        |
| Inventaire          | Une vue d'ensemble de nos données d'inventaire collectées.                                                                            |
| Rapports            | Affiche les informations système, les rapports planifiés, les journaux d'audit, les journaux d'action, etc.                           |
| Collecte de données | Contient tout ce qui est lié à la collecte de données comme les hôtes, les modèles, la maintenance, la découverte, ...                |
| Alerte              | La configuration de nos types de médias, scripts et actions                                                                           |
| Utilisateurs        | Configuration des utilisateurs comme les rôles d'utilisateurs, les groupes d'utilisateurs, l'authentification, les accès à l'API, ... |
| Administration      | La partie administration contenant tous les paramètres globaux, housekeeper, proxies, file d'attente, ...                             |

---

## Menu des liens

Immédiatement à côté du menu principal de l'application, sur la gauche de
l'interface, se trouve le menu `Links`. Ce module fournit une collection
d'hyperliens utiles pour les utilisateurs.

| Nom du menu                 | Details                                                                                                                                                                                                                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Support                     | Ceci nous amène à la page de support technique que vous pouvez acheter chez Zabbix. N'oubliez pas que votre partenaire local est également en mesure de vendre ces contrats et peut vous aider dans votre propre langue. [Vos distributeurs locaux](https://www.zabbix.com/distributors) |
| Intégrations                | La [page d'intégration] officielle de zabbix (https://www.zabbix.com/integrations)                                                                                                                                                                                                       |
| Aide                        | Le lien vers la documentation de votre [version Zabbix](https://www.zabbix.com/documentation/7.0/)                                                                                                                                                                                       |
| Paramètres de l'utilisateur | Les paramètres du profil de l'utilisateur.                                                                                                                                                                                                                                               |
| Déconnexion                 | Déconnexion de la session en cours.                                                                                                                                                                                                                                                      |

Quelques éléments interactifs restent à traiter dans la partie droite de
l'écran.

![Modifier le tableau de bord](ch02-edit-dashboard.png)

_2.8 Editer le tableau de bord_

Le bouton `Edit dashboard` facilite la modification de la configuration du
tableau de bord de l'utilisateur, une fonctionnalité qui sera développée dans
les sections suivantes. L'activation de cette icône redirige l'utilisateur vers
le portail de documentation de Zabbix, qui fournit des informations détaillées
sur les fonctionnalités du tableau de bord. Inversement, le contrôle situé dans
la marge de droite, représenté par trois lignes horizontales, permet d'accéder à
des opérations telles que le partage, le renommage et la suppression des
tableaux de bord définis par l'utilisateur.

---

## Informations sur le système

Le tableau de bord comporte également un panneau dédié intitulé `System
Information`. Ce widget fournit une vue d'ensemble en temps réel de l'état
opérationnel du déploiement de Zabbix. Nous allons maintenant examiner les
différents points de données présentés dans ce panneau, car leur interprétation
est cruciale pour la compréhension du système.

</br>

![Information système](ch02-system-information.png)

_2.9 Informations sur le système_

| Paramètre                                         | Valeur                                                                                                                                                                                                                                      | Details                                                                                                                                                                                                                                                                         |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Le serveur Zabbix fonctionne                      | The status of our zabbix server if it is running yes or no and if it is running on our localhost or another IP and on what port the zabbix server is listening. If no trapper is listening the rest of the information can not be displayed | IP and port of the Zabbix server                                                                                                                                                                                                                                                |
| Zabbix server version                             | This shows us the version of the `Zabbix server` so the version you see at the bottom of your screen is the one from the Zabbix frontend and can be different but should be in the same major version.                                      | Version Number                                                                                                                                                                                                                                                                  |
| Zabbix frontend version                           | This is the version of the frontend and should match with what you see at the bottom of your screen.                                                                                                                                        | Version Number                                                                                                                                                                                                                                                                  |
| Number of hosts (enabled/disabled)                | The total number of hosts configured on our system                                                                                                                                                                                          | How many of those are enabled and disabled                                                                                                                                                                                                                                      |
| Number of templates                               | The number of templates installed on our Zabbix server.                                                                                                                                                                                     |                                                                                                                                                                                                                                                                                 |
| Number of items (enabled/disabled/not supported)  | This line shows us the number of items we have configured in total in this case 99                                                                                                                                                          | 90 are enabled and 0 are disabled but 9 of them are unsupported. This last number is important as those are items not working. We will look into this later why it happens and how to fix it. For now remember that a high number of unsupported items is not a good idea.      |
| Number of triggers (Enabled/disabled[problem/ok]) | The number of triggers configured                                                                                                                                                                                                           | Number of enabled and disabled triggers. Just as with items we also see if there are triggers that are in a problem state or ok state. A trigger in a problem state is a non working trigger something we need to monitor and fix. We will cover this also later.               |
| Number of users (online)                          | Here we see the number of users that are configured on our system                                                                                                                                                                           | The number of users currently online.                                                                                                                                                                                                                                           |
| Required server performance, nvps                 | The number of new values per second that Zabbix will process per second.                                                                                                                                                                    | This is just an estimated number as some values we get are unknown so the real value is probably higher. So we can have some indication about how many IOPS we need and how busy our database is. A better indication is probably the internal item `zabbix[wcache,values,all]` |
| Global scripts on Zabbix server                   | It notifies us that the Global scripts are enabled or disabled in the server config.                                                                                                                                                        | Global scripts can be used in our frontend, actions, ... but need to be activated first                                                                                                                                                                                         |
| High availability cluster                         | It will show us if Zabbix HA cluster is disabled or not                                                                                                                                                                                     | Failover delay once HA is activated                                                                                                                                                                                                                                             |

???+ note

    `Global script` execution on Zabbix server can be enabled by going to the
    zabbix server configuration file and setting `EnableGlobalScripts=1`. For new
    installations, since Zabbix 7.0, global script execution on Zabbix server is
    disabled by default.

???+ Tip

     System information may display some additional warnings like when your database
     doesn't have the correct character set or collation UTF-8.
     Also when the database you used is lower or higher then the recommended version
     or when there are misconfigurations on housekeeper or TimescaleDB.
     Another warning you can see is about database history tables that aren't
     upgraded or primary keys that have not been set. This is possible if you are
     coming from an older version before Zabbix 6 and never did the upgrade.

---

## The main menu explained

It's important to know that we have seen so far our dashboard with the Admin
user and that this user is a `Zabbix Super Admin` user. This has a serious
impact on what we can see and do in Zabbix as this user has no restrictions.
Zabbix works with 3 different levels of users we have the regular `users`,
`Zabbix Admin` and `Zabbix Super Admin` users. Let's have a deeper look at the
differences :

![Main Menu sections](ch02-main-menu.png){ width=20% }

_2.10 Main menu sections_

- A `Zabbix User` will only see the <font color='red'>red</font> part of our
  `main menu` and will only be able to see our collected data.
- A `Zabbix Admin` will see the red part and the
  <font color='gold'>yellow</font> part of the `main menu` and is able to change
  our configuration.
- A `Zabbix Super Admin` will see the complete `main menu` and so is able to
  change the configuration and all the global settings.

  ***

  ![Monitoring Menu](ch02-monitoring-menu.png){ width=20% }

_2.11 Monitoring menu_

- **Problems**: This page will give us an overview of all the problems. With
  filter we can look at recent problems past problems and problems that are
  active now. There are many more filters tor drill down more.
- **Hosts**: This will give us a quick overview page with what's happening on
  our hosts and allows us to quickly go to the latest data, graphs and
  dashboards.
- **Latest data**: This page I probably use the most, it shows us all the
  information collected from all our hosts.
- **Maps**: The location where we can create map that are an overview of our IT
  infrastructure very useful to get a high level overview of the network.
- **Discovery**: When we run a network discovery this is the place where we can
  find the results.

---

![Services menu](ch02-services-menu.png){ width="20%" }

_2.12 Services menu_

- **Services**: This page will give us a high level overview of all services
  configured in Zabbix.
- **SLA**: An overview of all the SLAs configured in Zabbix.
- **SLA Report**: Here we can watch all SLA reports based on our filters.

---

![Inventory menu](ch02-inventory-menu.png){ width="20%" }

_2.13 Inventory menu_

- **Overview**: A place where we can watch all our inventory data that we have
  retrieved from our hosts.
- **Hosts**: Here we can filter by host and watch all inventory data for the
  hosts we have selected.

---

![Reports menu](ch02-reports-menu.png){ width="20%" }

_2.14 Inventory menu_

- **System information**: System information is a summary of key Zabbix server
  and system data.
- **Scheduled reports**: The place where we can schedule our reports, a `pdf` of
  the dashboard that will be sent at a specified time and date.
- **Availability report**: A nice overview where we can see what trigger has
  been in `ok`/`nok` state for how much % of the time
- **Top 100 triggers**: Another page I visit a lot here we have our top list
  with triggers that have been in a `NOK` state.
- **Audit log**: An overview of the user activity that happened on our system.
  Useful if we want to know who did what and when.
- **Action log**: A detailed overview of our actions can be found here. What
  mail was sent to who and when ...?
- **Notifications**: A quick overview of the number of notifications sent to
  each user.

---

![Data collection](ch02-datacollection-menu.png){ width="20%" }

_2.15 Data collection_

- **Template groups**: A place to logical group all templates together in
  different groups. Before it was mixed together with hosts in host groups.
- **Host groups**: A logical collection of different hosts put together. Host
  groups are used for our permissions.
- **Templates**: A set off entities like items and triggers can be grouped
  together on a template, A template can be applied to one or more hosts.
- **Hosts**: What we need in Zabbix to monitor A host, application, service ...
- **Maintenance**: The place to configure our maintenance windows. A maintenance
  can be planned in this location.
- **Event correlation**: When we have multiple events that fires triggers
  related we can configure correlations in this place.
- **Discovery**: Sometimes we like to use Zabbix to discover devices,
  services,... on our network. This can be done here.

---

![Alerts menu](ch02-alerts-menu.png){ width="20%" }

_2.16 Alerts menu_

- **Actions**: This menu allows us to configure actions based on `events` in
  Zabbix. We can create such actions for triggers, services, discovery,
  autoregistration and internal events.
- **Media types**: Zabbix can sent messages, emails etc ... based on the actions
  we have configured. Those media types need templates and need to be activated.
- **Scripts**: In Zabbix it's possible to make use of scripts in our actions and
  frontend. Those actions need to be created here first and configured.

---

![Users menu](ch02-users-menu.png){ width="20%" }

_2.17 Users menu_

- **User groups**: The `User groups` menu section enables the creation and
  management of user groupings for streamlined access and permission control.
- **User roles**: The `User roles` menu section defines sets of permissions that
  can be assigned to individual users, limiting their allowed actions based on
  the user type they have within the system.
- **Users**: The `Users` menu section provides the interface for managing
  individual user accounts, including creation and modification settings.
- **API tokens**: The `API tokens` menu section manages authentication
  credentials specifically designed for programmatic access to the system's
  Application Programming Interface (API), enabling secure automation and
  integration with external applications.
- **Authentication**: The `Authentication` menu section configures the methods
  and settings used to verify user identities and control access to the system.

---

![Administration menu](ch02-administration-menu.png){ width="20%" }

_2.18 Administration menu_

- **General**: The `General` menu section within administration allows
  configuration of core system-wide settings and parameters.
- **Audit log**: The `Audit log` menu section provides a chronological record of
  system activities and user actions for security monitoring and
  troubleshooting.
- **Housekeeping**: The `Housekeeping` menu section configures automated
  maintenance tasks for managing historical data and system performance.
- **Proxies**: The `Proxies` menu section manages the configuration and
  monitoring of proxy servers used for communication with managed hosts in
  distributed environments.
- **Macros**: The `Macros` menu section allows the definition and management of
  global variables for flexible system configuration.
- **Queue**: The `Queue` menu section provides real-time insight into the
  processing status of internal system tasks and data handling.

---

???+ info

    More information can be found in the online Zabbix documentation [here](https://www.zabbix.com/documentation/7.0/en/manual/web_interface/frontend_sections)

???+ info

    You will see that Zabbix is using the modal forms in the frontend on many places.
    The problem is that they are not movable. [This](https://github.com/gr8b/zabbix-module-uitwix/)
    module created by one of the Zabbix developers `UI Twix` will solve this problem
    for you.

???+ note

    At time of writing there is no Dashboard import/export functionality in zabbix.
    So when upgrading dashboards it needs to be created by hand. It was on the roadmap
    for 7 but didn't made it so feel free to vote <https://support.zabbix.com/browse/ZBXNEXT-5419>

## Conclusion

The Zabbix frontend serves as the central command center for monitoring,
configuration, and system awareness. In this chapter, you explored how to
navigate its interface from dashboards and the customizable main menu to
powerful tools like system information and global search. You learned how each
menu section (Monitoring, Data Collection, Alerts, Users, Administration, and
more) aligns with distinct functions, and how kiosk mode and layout controls
help optimize visibility during daily operations.

Additionally, the system information widget stands out as a real time diagnostic
snapshot, revealing critical metrics such as server status, number of hosts,
templates, items, triggers, and user activity all of which aid rapid
troubleshooting and performance assessment.

By mastering these frontend components, you're now better equipped to
confidently navigate Zabbix, manage user access, interpret monitoring data, and
maintain your environment more effectively. This foundational knowledge lays the
groundwork for deeper exploration into host configuration, authentication
mechanisms, and advanced monitoring workflows in the chapters that follow.

## Questions

- Which frontend section (Monitoring, Data Collection, Alerts, Users, or
  Administration) do you think you'll use most often in your daily work, and
  why?

- How can kiosk mode be useful in a real-world monitoring environment, and what
  types of dashboards would you display with it?

- What insights can the system information widget provide during
  troubleshooting, and how might it help identify issues with server
  performance?

- Why is it important to understand the difference between data displayed in
  “Monitoring” and configuration options found in “Data Collection”?

- If you were onboarding a new team member, which parts of the frontend would
  you show them first, and why?

## URL utiles

- https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/dashboards

- https://blog.zabbix.com/handy-tips-6-organize-your-dashboards-and-create-slideshows-with-dashboard-pages/17511/

- https://blog.zabbix.com/interactive-dashboard-creation-for-large-organizations-and-msps/30132/
