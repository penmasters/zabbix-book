---
description: |
    Learn how Zabbix proxies enhance scalability and distributed monitoring. This
    chapter guides you through setting up basic proxies, explores active vs. passive
    modes, container deployment, proxy groups, and the web services component
    helping you architect a resilient and efficient Zabbix infrastructure.
---

# Proxies et service web Zabbix

Ce chapitre couvre deux composants qui sont installés séparément du serveur
Zabbix et qui étendent les possibilités d'une installation Zabbix. Ils ont peu
de choses en commun d'un point de vue technique, mais ils sont souvent absents
des configurations de base et ont tous deux un impact significatif sur la façon
dont un environnement de surveillance évolue et fonctionne. Le premier est le
proxy Zabbix, un nœud de collecte de données distribué. Le second est le service
web Zabbix, un composant nécessaire à la génération programmée de rapports PDF.

## Le proxy Zabbix

Un proxy Zabbix est un processus qui collecte des données de surveillance au nom
du serveur Zabbix. Du point de vue des hôtes surveillés, un proxy se comporte de
la même manière que le serveur : il accepte les connexions d'agents passifs,
lance des vérifications actives, exécute des requêtes SNMP, exécute des
vérifications externes et traite l'IPMI. La différence réside dans ce qu'il
advient des données après leur collecte. Un proxy met en mémoire tampon les
données collectées localement dans sa propre base de données et les transmet au
serveur Zabbix à intervalles réguliers, au lieu d'écrire directement dans la
base de données du serveur.

Ce comportement de mise en mémoire tampon est la propriété architecturale qui
rend les proxys utiles. Le serveur Zabbix n'a besoin de maintenir qu'une seule
connexion par proxy, quel que soit le nombre d'hôtes surveillés par le proxy. Le
serveur n'a pas besoin d'atteindre directement les hôtes surveillés, et le proxy
peut continuer à collecter et à stocker des données même si la connexion au
serveur est temporairement indisponible.

### Quand utiliser un proxy

Les mandataires sont la bonne solution dans trois situations récurrentes.

La première concerne les sites distants. Lorsque les hôtes surveillés se
trouvent dans une succursale, un centre de données dans une autre région ou un
environnement cloud avec un accès réseau restreint, il n'est pas pratique
d'ouvrir des règles de pare-feu du serveur Zabbix à chaque hôte individuel. Un
proxy placé à cet endroit n'a besoin que d'une seule connexion sortante ou
entrante au serveur, et gère toutes les collectes de données locales en interne.

La seconde est la segmentation du réseau. Dans les environnements où les
systèmes surveillés se trouvent dans des segments de réseau isolés - un réseau
OT de production, un environnement PCI, une DMZ - un proxy peut être placé à
l'intérieur du segment avec un accès aux hôtes surveillés tandis que le serveur
Zabbix reste à l'extérieur. Le proxy comble la frontière de la collecte sans que
le serveur n'ait besoin d'accéder directement aux zones sensibles du réseau.

The third is load distribution. A single Zabbix server has limits on how many
items it can collect per second before performance degrades. Distributing
collection across multiple proxies offloads the polling work from the server and
allows the installation to scale horizontally. The server focuses on processing,
storing, and presenting data while the proxies handle the collection.

### Active and passive proxies

Zabbix proxies operate in one of two modes, which describe the direction of the
connection between the proxy and the server.

In active mode the proxy initiates the connection to the Zabbix server. The
proxy contacts the server to retrieve its configuration and to submit collected
data. This mode is preferred in most deployments because it requires only
outbound connectivity from the proxy, which is easier to permit through
firewalls than inbound connections to the server.

In passive mode the server initiates the connection to the proxy. The server
contacts the proxy to request configuration synchronisation and data submission.
This mode is less common and requires the Zabbix server to be able to reach the
proxy directly.

### Data buffering and resilience

Because a proxy stores collected data in its own local database before
forwarding it to the server, monitoring continues uninterrupted during
connectivity disruptions. When the connection to the server is restored, the
proxy forwards all buffered data in sequence. The length of time data can be
buffered is limited by the proxy's local database capacity and the
`ProxyLocalBuffer` and `ProxyOfflineBuffer` configuration parameters, which
control how long the proxy retains data locally.

This resilience property is particularly relevant for remote locations with
unreliable WAN links. A proxy at a remote site will continue collecting data
during an outage and deliver it to the server once connectivity is restored,
preserving the monitoring record without gaps.

### Proxy groups

Zabbix 7.0 introduced proxy groups, which change how proxies are managed in
environments that require high availability or automatic load balancing at the
proxy layer.

Before proxy groups, a host was assigned to a specific proxy. If that proxy
became unavailable, the hosts it monitored stopped being collected until the
proxy recovered or hosts were manually reassigned. Scaling collection meant
manually distributing hosts across proxies and rebalancing that distribution as
the environment grew.

With proxy groups, hosts are assigned to a group rather than to an individual
proxy. The Zabbix server monitors the state of all proxies in the group and
distributes monitored hosts across the available proxies automatically. If a
proxy in the group becomes unavailable, the server redistributes its hosts to
the remaining proxies in the group. When the proxy recovers, the server
rebalances the distribution again. No manual intervention is required.

A proxy group requires a minimum number of online proxies to be considered
operational, which is configurable per group. If the number of available proxies
in a group falls below this threshold, the group is considered degraded and the
server generates a problem event. This threshold gives you explicit control over
the acceptable level of redundancy within a group.

Proxy groups are the recommended approach for any deployment where proxy
availability is a concern or where the monitored host population is large enough
to warrant distributing collection across multiple proxies with automatic
rebalancing.

```mermaid
flowchart LR
    subgraph hosts ["Remote hosts"]
        H1[Host] & H2[Host] & H3[Host] & H4[Host]
    end

    subgraph group ["Proxy group"]
        P1[Proxy 1]
        P2[Proxy 2]
        P3[Proxy 3
        unavailable]
    end

    H1 & H2 --> P1
    H3 & H4 --> P2
    H3 -.->|redistributed| P3

    P1 & P2 --> S[Zabbix server]
    S --> DB[(Database)]
```

### Deploying proxies as Podman containers with Quadlet

A proxy is a natural fit for container deployment. It is a single process with a
well-defined configuration file, it exposes one port, it has no web interface,
and its only external dependency is the database it uses for local buffering.
Podman is the container runtime used in this chapter because it runs containers
without a daemon and does not require root privileges, which makes it a
practical choice for proxy deployments on standard RHEL-based systems.

This chapter uses Quadlet to manage the proxy container. Quadlet is a Podman
feature, available from Podman 4.4 onwards, that generates systemd unit files
from a declarative container definition. Rather than writing a systemd service
file manually or relying on `podman generate systemd`, you write a small
`.container` file that describes the image, volumes, environment variables, and
network configuration, and Quadlet translates that into a systemd unit at
runtime. The proxy container then behaves as a native systemd service: it starts
automatically on boot, respects dependency ordering, restarts on failure
according to the policy you define, and is managed with the standard `systemctl`
commands that any Linux administrator already knows.

The practical benefit over a bare `podman run` command is that there is no
separate step to generate and install a service file, no risk of the generated
file drifting out of sync with the actual container configuration, and no
dependency on a running Podman daemon. The `.container` file is the single
source of truth for both the container and its service behaviour.

The primary operational consideration when running a proxy in a container is
data persistence. The proxy's local buffer database must survive container
restarts, which means the database directory needs to be mounted from the host
or managed through a named volume. If the database is lost on a restart, any
data that was buffered but not yet forwarded to the server is lost with it. This
chapter covers how to configure the volume mount in the Quadlet `.container`
file correctly so that buffered data is preserved across container lifecycle
events.

Running proxies as Quadlet-managed containers also simplifies deployment
consistency across multiple sites. The same container image and `.container`
file can be deployed at a remote location with minimal environment-specific
changes, reducing the operational overhead of maintaining proxy installations
across many sites.

## The Zabbix web service

The Zabbix web service is a separate process that the Zabbix server uses to
generate scheduled reports in PDF format. It is not involved in data collection,
trigger evaluation, or alerting. Its sole function is to render the Zabbix
frontend as it would appear in a browser and capture the result as a PDF, which
can then be delivered by email on a defined schedule.

The web service uses a headless Chromium instance to render the frontend. This
means the host running the web service must have Chromium or Google Chrome
installed, and the web service must be able to reach the Zabbix frontend over
HTTP or HTTPS. The Zabbix server communicates with the web service over a
dedicated port, which defaults to 10053.

### When scheduled reports are useful

Scheduled reports are used when stakeholders need a regular summary of
monitoring data without logging into Zabbix directly. Common use cases are
weekly availability summaries delivered to management, daily dashboard snapshots
sent to operations teams at the start of a shift, and periodic compliance
reports that need to be archived or distributed by email.

The content of a scheduled report is determined by the dashboard selected when
the report is configured. Any dashboard visible in the Zabbix frontend can be
rendered as a scheduled report, including dashboards with graphs, top hosts
widgets, problem lists, and SLA reports.

### Relationship to the Zabbix server

The web service does not need to run on the same host as the Zabbix server, but
it must be reachable from the server and must itself be able to reach the Zabbix
frontend. In practice, many installations run the web service on the same host
as the frontend for simplicity, but separating it is a valid option in
environments where the frontend runs on dedicated web servers.

The web service is only required if you intend to use scheduled reports. If your
installation does not need PDF report delivery, the web service does not need to
be installed.

## What this chapter covers

This chapter starts with a practical proxy setup: installing the proxy package,
configuring the connection to the Zabbix server, and adding the proxy to the
frontend.

From there the chapter covers the internal mechanics of proxy operation, how to
choose between active and passive mode, and how to configure and use proxy
groups for automatic host distribution and high availability at the proxy layer.

It then covers deploying that same proxy as a Podman container managed by
Quadlet, including how to write the `.container` definition file and configure
volume mounts for data persistence.

The final part of the chapter covers the Zabbix web service: what it requires to
run, how to install and configure it, how to connect it to the Zabbix server,
and how to create and schedule a report against an existing dashboard.

By the end of this chapter you will understand where proxies fit in a Zabbix
architecture, when to deploy them as packages versus Quadlet-managed containers,
how proxy groups change the operational model for distributed deployments, and
how the web service enables scheduled PDF reporting without any additional
third-party tooling.
