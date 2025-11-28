---
description: |
    This chapter from The Zabbix Book, titled "Frontend Installation," provides a
    step-by-step guide to setting up the Zabbix web interface. Learn how to install
    required packages, configure PHP, and integrate with Apache or Nginx for a
    secure and fully functional monitoring frontend.
tags: [beginner]
---

# Explicação do front-end

Este capítulo abordará os conceitos básicos que precisamos conhecer no que diz
respeito à interface de usuário do Zabbix e o que precisamos saber antes de
começar a mergulhar totalmente em nossa ferramenta de monitoramento. Veremos
como a interface do usuário funciona, como adicionar um host, grupos de
usuários, itens... para que tenhamos uma boa compreensão do básico. Isso é algo
que às vezes é esquecido e pode levar a frustrações por não sabermos por que as
coisas não funcionam como esperávamos que funcionassem. Portanto, mesmo que você
seja um usuário avançado, pode ser útil dar uma olhada neste capítulo.

Vamos começar

---

## Visão geral da interface

Com o Zabbix 7, a interface do usuário após o login foi um pouco alterada. Nosso
menu no lado esquerdo da tela passou por uma pequena reformulação. Vamos nos
aprofundar nisso. Quando fazemos login em nossa configuração do Zabbix pela
primeira vez com nosso usuário Admin, vemos uma página

Assim, temos nossa ` janela principal `em <font color='green'>verde</font>,
nosso `menu principal `marcado em <font color='red'>vermelho</font> e nossos
`links` marcados em <font color='gold'>amarelo</font>.

![Visão geral](ch02-frontend-overview.png)

_2.1 Visão geral_

O menu principal pode ser ocultado, recolhendo-o completamente ou reduzindo-o a
um conjunto de pequenos ícones. Quando clicamos no botão com as duas setas à
esquerda:

![Recolher](ch02-frontend-collapse.png)

_2.2 Recolher_

Você verá que o menu se reduz a um conjunto de pequenos ícones. Pressionar ">>"
fará com que o `menu principal do` volte ao seu estado original.

Ao clicar no ícone que se parece com uma caixa com uma seta para fora, ao lado
do botão "<<", você ocultará completamente o `menu principal do site ` .

![Ocultar](ch02-frontend-hide.png)

_2.3 Ocultar_

Para trazer de volta nosso `menu principal ` é bastante fácil, basta procurar o
botão à esquerda com três linhas horizontais e clicar nele. Isso mostrará o
`menu principal ` , mas ele não permanecerá. Quando clicarmos na caixa com a
seta apontando para o canto inferior direito, o `menu principal ` será mantido
em sua posição.

Outra maneira de aumentar a tela, bastante útil para monitores em `equipes NOK`,
por exemplo, é o botão `kiosk mode`. Esse botão, no entanto, está localizado no
lado esquerdo da tela e se parece com quatro setas apontando para cada canto da
tela. Pressionar esse botão removerá todos os menus e deixará apenas a` janela
principal ` para o foco.

![Expandir](ch02-frontend-expand.png)

_2.4 Expandir_

Quando quisermos sair do modo de quiosque, o botão será alterado para duas setas
apontando para a parte interna da tela. Ao pressionar esse botão, voltaremos ao
estado original.

![Expandir](ch02-frontend-shrink.png)

_2.5 Reduzir_

???+ dica

    We can also enter and exit kiosk mode by making use of parameters in our Zabbix
    url: `/zabbix.php?action=dashboard.view&kiosk=1` - activate kiosk mode or
    `/zabbix.php?action=dashboard.view&kiosk=0` - activate normal mode.

???+ nota

    There are many other page parameters we can use. A full list can be found at
    [https://www.zabbix.com/documentation/7.4/en/manual/web_interface/page_parameters](https://www.zabbix.com/documentation/7.4/en/manual/web_interface/page_parameters)
    Zabbix also has a global search menu that we can use to find hosts, host groups
    and templates.

Se digitarmos na caixa de pesquisa a palavra `server`, você verá que teremos uma
visão geral de todos os `modelos ` , `grupos de hosts ` e hosts ` com o servidor
de nomes. É por isso que essa caixa é chamada de `global search`.

![Pesquisa global](ch02-global-search.png)

_2.6 Pesquisa global_

Este é o nosso resultado depois de procurarmos a palavra `server`. Se você tiver
uma configuração padrão do Zabbix, sua página deverá ter mais ou menos a mesma
aparência.

![Resultado da pesquisa global](ch02-global-search-result.png)

_2.7 Resultado de pesquisa global_

---

## Menu principal

Vamos agora examinar brevemente as seções constituintes do menu principal do
aplicativo. O `menu principal ` , situado na interface à esquerda, compreende um
total de nove seções distintas:

| Nome do menu        | Detalhes                                                                                                 |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| Painéis de controle | Contém uma visão geral de todos os painéis aos quais temos acesso.                                       |
| Monitoramento       | Mostra-nos os hosts, problemas, dados mais recentes, mapas, ...                                          |
| Serviços            | Uma visão geral de todos os serviços e configurações de SLA.                                             |
| Inventário          | Uma visão geral de nossos dados de inventário coletados.                                                 |
| Relatórios          | Mostra as informações do sistema, relatórios agendados, registros de auditoria, registros de ações, etc. |
| Coleta de dados     | Contém todos os itens relacionados à coleta de dados, como hosts, modelos, manutenção, descoberta, ...   |
| Alerta              | A configuração de nossos tipos de mídia, scripts e ações                                                 |
| Usuários            | Configuração do usuário, como funções de usuário, grupos de usuários, autenticação, toques de API, ...   |
| Administração       | A parte administrativa que contém todas as configurações globais, housekeeper, proxies, fila, ...        |

---

## Menu de links

Imediatamente subjacente ao menu principal do aplicativo na interface do lado
esquerdo está o menu `Links`. Esse módulo fornece uma coleção de hiperlinks
pertinentes para acesso do usuário.

| Nome do menu             | Detalhes                                                                                                                                                                                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Apoio                    | Isso nos leva à página de suporte técnico que você pode comprar da Zabbix. Lembre-se de que seu parceiro local também pode vender esses contratos e ajudá-lo em seu próprio idioma. [Seus distribuidores locais](https://www.zabbix.com/distributors) |
| Integrações              | A página oficial do zabbix [página de integração](https://www.zabbix.com/integrations)                                                                                                                                                                |
| Ajuda                    | O link para a documentação de sua [versão do Zabbix](https://www.zabbix.com/documentation/7.0/)                                                                                                                                                       |
| Configurações do usuário | As configurações do perfil do usuário.                                                                                                                                                                                                                |
| Sair                     | Sair da sessão atual.                                                                                                                                                                                                                                 |

Alguns elementos interativos ainda precisam ser abordados na parte direita da
tela.

![Editar painel de controle](ch02-edit-dashboard.png)

_2.8 Editar painel de controle_

O botão `Edit dashboard` facilita a modificação da configuração do painel do
usuário, um recurso que será detalhado nas seções seguintes. Localizado na
margem esquerda extrema, há um ícone de marca de consulta ('?'), cuja ativação
redireciona o usuário para o portal de documentação do Zabbix, fornecendo
detalhes abrangentes sobre as funcionalidades do painel. Por outro lado, o
controle situado na margem direita, representado por três linhas horizontais,
fornece acesso a operações como compartilhamento, renomeação e exclusão de
painéis definidos pelo usuário.

---

## Informações do sistema

O painel de controle também apresenta um painel dedicado denominado `Informações
do sistema`. Esse widget fornece uma visão geral em tempo real do status
operacional da implantação do Zabbix. Agora examinaremos os pontos de dados
individuais apresentados nesse painel, pois sua interpretação é crucial para a
compreensão do sistema.

</br>

![Informações do sistema](ch02-system-information.png)

_2.9 Informações do sistema_

| Parâmetro                                            | Valor                                                                                                                                                                                                                                                                           | Detalhes                                                                                                                                                                                                                                                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| O servidor Zabbix está em execução                   | O status do nosso servidor zabbix, se ele estiver em execução, sim ou não, e se estiver em execução em nosso host local ou em outro IP e em qual porta o servidor zabbix está escutando. Se nenhum trapper estiver escutando, o restante das informações não poderá ser exibido | IP e porta do servidor Zabbix                                                                                                                                                                                                                                                                          |
| Versão do servidor Zabbix                            | Isso nos mostra a versão do servidor `Zabbix`. Portanto, a versão que você vê na parte inferior da tela é a versão do front-end do Zabbix e pode ser diferente, mas deve estar na mesma versão principal.                                                                       | Número da versão                                                                                                                                                                                                                                                                                       |
| Versão de front-end do Zabbix                        | Essa é a versão do frontend e deve corresponder ao que você vê na parte inferior da tela.                                                                                                                                                                                       | Número da versão                                                                                                                                                                                                                                                                                       |
| Número de hosts (ativado/desativado)                 | O número total de hosts configurados em nosso sistema                                                                                                                                                                                                                           | Quantos deles estão ativados e desativados?                                                                                                                                                                                                                                                            |
| Número de modelos                                    | O número de modelos instalados em nosso servidor Zabbix.                                                                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                        |
| Número de itens (ativado/desativado/não suportado)   | Essa linha nos mostra o número de itens que configuramos no total, neste caso 99                                                                                                                                                                                                | 90 estão ativados e 0 estão desativados, mas 9 deles não têm suporte. Esse último número é importante, pois são itens que não estão funcionando. Veremos mais tarde por que isso acontece e como corrigi-lo. Por enquanto, lembre-se de que um grande número de itens sem suporte não é uma boa ideia. |
| Número de gatilhos(Ativado/desativado [problema/ok]) | O número de gatilhos configurados                                                                                                                                                                                                                                               | Number of enabled and disabled triggers. Just as with items we also see if there are triggers that are in a problem state or ok state. A trigger in a problem state is a non working trigger something we need to monitor and fix. We will cover this also later.                                      |
| Number of users (online)                             | Here we see the number of users that are configured on our system                                                                                                                                                                                                               | The number of users currently online.                                                                                                                                                                                                                                                                  |
| Required server performance, nvps                    | The number of new values per second that Zabbix will process per second.                                                                                                                                                                                                        | This is just an estimated number as some values we get are unknown so the real value is probably higher. So we can have some indication about how many IOPS we need and how busy our database is. A better indication is probably the internal item `zabbix[wcache,values,all]`                        |
| Global scripts on Zabbix server                      | It notifies us that the Global scripts are enabled or disabled in the server config.                                                                                                                                                                                            | Global scripts can be used in our frontend, actions, ... but need to be activated first                                                                                                                                                                                                                |
| High availability cluster                            | It will show us if Zabbix HA cluster is disabled or not                                                                                                                                                                                                                         | Failover delay once HA is activated                                                                                                                                                                                                                                                                    |

???+ nota

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

???+ Note

    At time of writing there is no Dashboard import/export functionality in zabbix.
    So when upgrading dashboards it needs to be created by hand. It was on the roadmap
    for 7 but didn't made it so feel free to vote <https://support.zabbix.com/browse/ZBXNEXT-5419>

## Conclusão

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

## Perguntas

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

## URLs úteis

- https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/dashboards

- https://blog.zabbix.com/handy-tips-6-organize-your-dashboards-and-create-slideshows-with-dashboard-pages/17511/

- https://blog.zabbix.com/interactive-dashboard-creation-for-large-organizations-and-msps/30132/
