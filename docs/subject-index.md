---
description: |
    An alphabetical subject index for the Zabbix Book, with links to the
    sections where each concept is explained or configured.
---

# Subject index

Use this index to find concepts, configuration tasks, and troubleshooting
topics throughout the book. On the website, each locator is a link. In the
print edition, locators are rendered as page numbers.

<!-- This file is generated. Edit index/en.yml and run
     python3 tools/build_subject_index.py instead. -->

<nav class="subject-index-letters" aria-label="Subject index letters" markdown>
[A](#index-letter-a) · [B](#index-letter-b) · [C](#index-letter-c) · [D](#index-letter-d) · [E](#index-letter-e) · [F](#index-letter-f) · [G](#index-letter-g) · [H](#index-letter-h) · [I](#index-letter-i) · [J](#index-letter-j) · [K](#index-letter-k) · [L](#index-letter-l) · [M](#index-letter-m) · [N](#index-letter-n) · [O](#index-letter-o) · [P](#index-letter-p) · [R](#index-letter-r) · [S](#index-letter-s) · [T](#index-letter-t) · [U](#index-letter-u) · [V](#index-letter-v) · [W](#index-letter-w) · [Z](#index-letter-z)
</nav>

<div class="subject-index" markdown>

## A {#index-letter-a}

- <span id="index-actions"></span>**actions**
    - [configuring alert actions](ch07-zabbix-alerts/actions.md){ .index-target }[](ch07-zabbix-alerts/actions.md#conclusion){ .index-range-end }
    - *See also* [alerting](#index-alerting), [media types](#index-media-types), [triggers](#index-triggers)
- <span id="index-active-agent-autoregistration"></span>**active agent autoregistration**
    - [configuring](ch10-zabbix-discovery/active-agent-autoregistration.md){ .index-target }[](ch10-zabbix-discovery/active-agent-autoregistration.md#conclusion){ .index-range-end }
    - *See also* [Zabbix agent, active checks](#index-zabbix-agent-active-checks)
- <span id="index-active-checks"></span>**active checks**
    - *See* [Zabbix agent, active checks](#index-zabbix-agent-active-checks)
- <span id="index-active-directory"></span>**Active Directory**
    - *See* [LDAP](#index-ldap)
- <span id="index-agent-encryption"></span>**agent encryption**
    - *See* [Zabbix agent, encryption](#index-zabbix-agent-encryption)
- <span id="index-alert-scripts"></span>**alert scripts**
    - [creating custom scripts](ch07-zabbix-alerts/scripts.md){ .index-target }
    - *See also* [alerting](#index-alerting), [media types](#index-media-types)
- <span id="index-alerting"></span>**alerting**
    - <span id="index-alerting-actions"></span>[actions](ch07-zabbix-alerts/actions.md){ .index-target }[](ch07-zabbix-alerts/actions.md#conclusion){ .index-range-end }
    - <span id="index-alerting-custom-scripts"></span>[custom scripts](ch07-zabbix-alerts/scripts.md){ .index-target }
    - <span id="index-alerting-delivery-troubleshooting"></span>[following the alerting pipeline](ch07-zabbix-alerts/chapter.md#where-alerting-problems-come-from){ .index-target }
    - <span id="index-alerting-media-types"></span>[media types](ch07-zabbix-alerts/media-types.md){ .index-target }[](ch07-zabbix-alerts/media-types.md#conclusion){ .index-range-end }
- <span id="index-allowkey"></span>**AllowKey**
    - *See* [Zabbix agent, item key restrictions](#index-zabbix-agent-item-key-restrictions)
- <span id="index-api"></span>**API**
    - *See* [Zabbix API](#index-zabbix-api)
- <span id="index-api-tokens"></span>**API tokens**
    - [creating API tokens](ch12-zabbix-api/API basics.md#creating-an-api-token){ .index-target }
    - [sending bearer tokens](ch12-zabbix-api/API basics.md#sending-the-token){ .index-target }
    - *See also* [Zabbix API](#index-zabbix-api), [Zabbix MCP server](#index-zabbix-mcp-server)
- <span id="index-apm"></span>**APM**
    - *See* [OpenTelemetry](#index-opentelemetry)
- <span id="index-application-performance-monitoring"></span>**application performance monitoring**
    - *See* [OpenTelemetry](#index-opentelemetry)
- <span id="index-approle"></span>**AppRole**
    - *See* [Vault, AppRole](#index-vault-approle)
- <span id="index-audit-log"></span>**audit log**
    - *See* [reports, audit log](#index-reports-audit-log)
- <span id="index-automated-pdf-reports"></span>**automated PDF reports**
    - [creating](ch11-zabbix-visualisation/automated-pdf-reports.md){ .index-target }[](ch11-zabbix-visualisation/automated-pdf-reports.md#conclusion){ .index-range-end }
    - *See also* [reports](#index-reports), [Zabbix web service](#index-zabbix-web-service)
- <span id="index-availability-reports"></span>**availability reports**
    - *See* [reports, availability](#index-reports-availability)

## B {#index-letter-b}

- <span id="index-backups"></span>**backups**
    - [choosing a backup strategy](ch14-zabbix-maintenance/taking-backups.md){ .index-target }
    - <span id="index-backups-backup-tools"></span>[choosing pgBackRest or Barman](ch14-zabbix-maintenance/taking-backups.md#pgbackrest-and-pgbarman-the-preferred-production-solution){ .index-target }
    - <span id="index-backups-clickhouse"></span>[backing up ClickHouse](ch13-advanced-security/storing-data-in-clickhousedb.md#backups){ .index-target }
    - <span id="index-backups-configuration-files"></span>[backing up configuration and scripts](ch14-zabbix-maintenance/taking-backups.md#other-important-config-files){ .index-target }
    - <span id="index-backups-mariadb"></span>[creating MariaDB logical backups](ch14-zabbix-maintenance/taking-backups.md#creating-a-logical-database-backup){ .index-target }
    - <span id="index-backups-postgresql-logical-backups"></span>[creating PostgreSQL logical backups](ch14-zabbix-maintenance/taking-backups.md#logical-dumps-with-pg_dump){ .index-target }
    - <span id="index-backups-postgresql-physical-backups"></span>[using physical backups and WAL archiving](ch14-zabbix-maintenance/taking-backups.md#physical-backups-and-wal-archiving){ .index-target }
- <span id="index-browser-items"></span>**browser items**
    - [configuring browser monitoring](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - <span id="index-browser-items-screenshots"></span>[capturing and storing screenshots](ch04-zabbix-collecting-data/browser.md#capturing-and-storing-screenshots){ .index-target }
    - <span id="index-browser-items-webdriver"></span>[configuring the WebDriver endpoint](ch04-zabbix-collecting-data/browser.md#architectural-requirements-setting-up-the-webdriver-endpoint){ .index-target }
    - *See also* [web monitoring](#index-web-monitoring)

## C {#index-letter-c}

- <span id="index-calculated-items"></span>**calculated items**
    - [creating and using](ch04-zabbix-collecting-data/calculated.md){ .index-target }[](ch04-zabbix-collecting-data/calculated.md#conclusion){ .index-range-end }
    - <span id="index-calculated-items-aggregation"></span>[aggregating data across items](ch04-zabbix-collecting-data/calculated.md#data-aggregation){ .index-target }
    - <span id="index-calculated-items-troubleshooting"></span>[troubleshooting calculated items](ch04-zabbix-collecting-data/calculated.md#troubleshooting-calculated-items){ .index-target }
    - *See also* [items](#index-items)
- <span id="index-cep"></span>**CEP**
    - *See* [complex event processing](#index-complex-event-processing)
- <span id="index-certificates"></span>**certificates**
    - <span id="index-certificates-agent-encryption"></span>[configuring agent certificates](ch13-advanced-security/agent-security.md#certificates){ .index-target }
    - <span id="index-certificates-let-s-encrypt"></span>[securing the frontend with Let's Encrypt](ch13-advanced-security/securing-frontend.md#securing-the-frontend-with-lets-encrypt-on-nginx){ .index-target }
    - <span id="index-certificates-self-signed-certificates"></span>[securing the frontend with a private CA](ch13-advanced-security/securing-frontend.md#securing-the-frontend-with-self-signed-certificates){ .index-target }
    - *See also* [TLS](#index-tls)
- <span id="index-clickhouse"></span>**ClickHouse**
    - [storing Zabbix data](ch13-advanced-security/storing-data-in-clickhousedb.md){ .index-target }
    - <span id="index-clickhouse-apm-telemetry"></span>[storing APM telemetry](ch04-zabbix-collecting-data/telemetry.md#how-apm-works-in-zabbix){ .index-target }
    - <span id="index-clickhouse-history-storage"></span>[configuring item history storage](ch13-advanced-security/storing-data-in-clickhousedb.md#configuring-zabbix){ .index-target }
    - <span id="index-clickhouse-retention"></span>[configuring retention and partitioning](ch13-advanced-security/storing-data-in-clickhousedb.md#configuring-retention-and-partitioning){ .index-target }
    - <span id="index-clickhouse-troubleshooting"></span>[troubleshooting history storage](ch13-advanced-security/storing-data-in-clickhousedb.md#troubleshooting){ .index-target }
- <span id="index-complex-event-processing"></span>**complex event processing**
    - [configuring CEP rules](ch07-zabbix-alerts/cep.md){ .index-target }[](ch07-zabbix-alerts/cep.md#conclusion){ .index-range-end }
    - *See also* [alerting](#index-alerting), [triggers](#index-triggers)
- <span id="index-containers"></span>**containers**
    - <span id="index-containers-podman-setup"></span>[preparing rootless Podman](ch00-getting-started/preparation.md#preparing-the-system-for-running-containers-using-podman){ .index-target }
    - <span id="index-containers-proxy-deployment"></span>[deploying proxies with Quadlet](ch03-zabbix-proxies/proxies-as-container.md#setting-up-containers){ .index-target }
    - <span id="index-containers-upgrading-proxies"></span>[upgrading proxy containers](ch03-zabbix-proxies/proxies-as-container.md#upgrading-our-containers){ .index-target }
    - <span id="index-containers-web-service-deployment"></span>[running the web service as a container](ch03-zabbix-proxies/web-services.md#installing-the-zabbix-web-service-as-a-container){ .index-target }
    - *See also* [Zabbix proxy](#index-zabbix-proxy), [Zabbix web service](#index-zabbix-web-service)
- <span id="index-context-macros"></span>**context macros**
    - *See* [user macros, context macros](#index-user-macros-context-macros)

## D {#index-letter-d}

- <span id="index-dashboards"></span>**dashboards**
    - [creating and configuring](ch11-zabbix-visualisation/dashboards.md){ .index-target }[](ch11-zabbix-visualisation/dashboards.md#conclusion){ .index-range-end }
    - <span id="index-dashboards-importing-and-exporting"></span>[importing and exporting dashboards](ch11-zabbix-visualisation/dashboards.md#exporting-and-importing-dashboards){ .index-target }
    - <span id="index-dashboards-sharing"></span>[sharing dashboards](ch11-zabbix-visualisation/dashboards.md#sharing-dashboards){ .index-target }
    - <span id="index-dashboards-widgets"></span>[adding and configuring widgets](ch11-zabbix-visualisation/dashboards.md#adding-and-configuring-widgets){ .index-target }
    - *See also* [graphs](#index-graphs), [maps](#index-maps)
- <span id="index-data-collection"></span>**data collection**
    - [understanding the data flow](ch04-zabbix-collecting-data/dataflow.md){ .index-target }[](ch04-zabbix-collecting-data/dataflow.md#conclusion){ .index-range-end }
    - *See also* [items](#index-items), [preprocessing](#index-preprocessing)
- <span id="index-database"></span>**database**
    - <span id="index-database-choosing"></span>[choosing a database](ch01-zabbix-components/database.md){ .index-target }[](ch01-zabbix-components/database.md#conclusion){ .index-range-end }
    - <span id="index-database-mariadb"></span>[installing MariaDB](ch01-zabbix-components/mariadb.md){ .index-target }[](ch01-zabbix-components/mariadb.md#conclusion){ .index-range-end }
    - <span id="index-database-monitoring-with-agent-2"></span>[monitoring with Zabbix agent 2](ch04-zabbix-collecting-data/database-agent.md){ .index-target }[](ch04-zabbix-collecting-data/database-agent.md#conclusion){ .index-range-end }
    - <span id="index-database-odbc-monitoring"></span>[monitoring with ODBC](ch04-zabbix-collecting-data/database-odbc.md){ .index-target }
    - <span id="index-database-postgresql"></span>[installing PostgreSQL](ch01-zabbix-components/postgresql.md){ .index-target }[](ch01-zabbix-components/postgresql.md#conclusion){ .index-range-end }
- <span id="index-denykey"></span>**DenyKey**
    - *See* [Zabbix agent, item key restrictions](#index-zabbix-agent-item-key-restrictions)
- <span id="index-dependent-items"></span>**dependent items**
    - [configuring](ch04-zabbix-collecting-data/dependent.md){ .index-target }[](ch04-zabbix-collecting-data/dependent.md#conclusion){ .index-range-end }
    - <span id="index-dependent-items-lld-lookup-keys"></span>[designing discovery and item payloads](ch16-zabbix-real-world-examples/filter-lld-without-jsonpath.md#the-two-approaches){ .index-target }
    - *See also* [low-level discovery](#index-low-level-discovery), [preprocessing](#index-preprocessing)
- <span id="index-discovery"></span>**discovery**
    - <span id="index-discovery-active-agent-autoregistration"></span>[active agent autoregistration](ch10-zabbix-discovery/active-agent-autoregistration.md){ .index-target }[](ch10-zabbix-discovery/active-agent-autoregistration.md#conclusion){ .index-range-end }
    - <span id="index-discovery-network-discovery"></span>[network discovery](ch10-zabbix-discovery/network-host-discovery.md){ .index-target }[](ch10-zabbix-discovery/network-host-discovery.md#conclusion){ .index-range-end }
    - *See also* [low-level discovery](#index-low-level-discovery)
- <span id="index-duo"></span>**Duo**
    - *See* [multi-factor authentication, Duo](#index-multi-factor-authentication-duo)

## E {#index-letter-e}

- <span id="index-email-notifications"></span>**email notifications**
    - *See* [media types, email](#index-media-types-email)
- <span id="index-event-log-monitoring"></span>**event log monitoring**
    - *See* [Windows monitoring, event logs](#index-windows-monitoring-event-logs)
- <span id="index-external-authentication"></span>**external authentication**
    - <span id="index-external-authentication-http"></span>[HTTP authentication](ch02-zabbix-installation/http.md){ .index-target }[](ch02-zabbix-installation/http.md#conclusion){ .index-range-end }
    - <span id="index-external-authentication-ldap"></span>[LDAP and Active Directory](ch02-zabbix-installation/ldap-ad.md){ .index-target }[](ch02-zabbix-installation/ldap-ad.md#conclusion){ .index-range-end }
    - <span id="index-external-authentication-saml"></span>[SAML authentication](ch02-zabbix-installation/saml.md){ .index-target }[](ch02-zabbix-installation/saml.md#conclusion){ .index-range-end }
- <span id="index-external-checks"></span>**external checks**
    - [creating and using](ch04-zabbix-collecting-data/external-checks.md){ .index-target }[](ch04-zabbix-collecting-data/external-checks.md#conclusion){ .index-range-end }

## F {#index-letter-f}

- <span id="index-firewalls"></span>**firewalls**
    - [configuring the host firewall](ch00-getting-started/Requirements.md#firewall){ .index-target }
    - [allowing proxy connections](ch03-zabbix-proxies/proxy-basics.md#proxy-firewall){ .index-target }
- <span id="index-frontend"></span>**frontend**
    - *See* [Zabbix frontend](#index-zabbix-frontend)
- <span id="index-frontend-scripts"></span>**frontend scripts**
    - [creating](ch09-zabbix-extending/frontend-scripts.md){ .index-target }[](ch09-zabbix-extending/frontend-scripts.md#conclusion){ .index-range-end }

## G {#index-letter-g}

- <span id="index-graphs"></span>**graphs**
    - [creating and configuring](ch11-zabbix-visualisation/graphs.md){ .index-target }[](ch11-zabbix-visualisation/graphs.md#conclusion){ .index-range-end }
    - *See also* [dashboards](#index-dashboards), [visualisation](#index-visualisation)

## H {#index-letter-h}

- <span id="index-high-availability"></span>**high availability**
    - [configuring Zabbix server HA](ch01-zabbix-components/ha-setup.md){ .index-target }[](ch01-zabbix-components/ha-setup.md#conclusion){ .index-range-end }
    - <span id="index-high-availability-frontend-failover"></span>[configuring Keepalived](ch01-zabbix-components/ha-setup.md#setting-up-keepalived){ .index-target }
    - *See also* [proxy groups](#index-proxy-groups)
- <span id="index-host-groups"></span>**host groups**
    - [creating and managing](ch02-zabbix-installation/host-groups.md){ .index-target }[](ch02-zabbix-installation/host-groups.md#conclusion){ .index-range-end }
- <span id="index-host-interfaces"></span>**host interfaces**
    - [configuring](ch04-zabbix-collecting-data/host-interfaces.md){ .index-target }[](ch04-zabbix-collecting-data/host-interfaces.md#conclusion){ .index-range-end }
    - *See also* [hosts](#index-hosts)
- <span id="index-hosts"></span>**hosts**
    - [creating and configuring](ch04-zabbix-collecting-data/hosts.md){ .index-target }[](ch04-zabbix-collecting-data/hosts.md#conclusion){ .index-range-end }
    - *See also* [host groups](#index-host-groups), [host interfaces](#index-host-interfaces)
- <span id="index-html-visualisation"></span>**HTML visualisation**
    - [displaying HTML in the Item history widget](ch16-zabbix-real-world-examples/html-for-the-win.md){ .index-target }
    - [building custom tables](ch16-zabbix-real-world-examples/html-for-the-win.md#tables){ .index-target }
    - *See also* [dashboards](#index-dashboards)
- <span id="index-http-agent-items"></span>**HTTP agent items**
    - [configuring](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
    - *See also* [web monitoring](#index-web-monitoring)

## I {#index-letter-i}

- <span id="index-icmp-checks"></span>**ICMP checks**
    - [configuring simple checks](ch04-zabbix-collecting-data/simple-checks.md){ .index-target }[](ch04-zabbix-collecting-data/simple-checks.md#conclusion){ .index-range-end }
- <span id="index-internal-health"></span>**internal health**
    - [monitoring Zabbix health](ch14-zabbix-maintenance/internal-health.md){ .index-target }[](ch14-zabbix-maintenance/internal-health.md#conclusion){ .index-range-end }
    - <span id="index-internal-health-cache-performance"></span>[monitoring cache and database performance](ch14-zabbix-maintenance/internal-health.md#cache-and-database-performance){ .index-target }
    - <span id="index-internal-health-pollers-and-processes"></span>[understanding internal worker processes](ch14-zabbix-maintenance/internal-health.md#internal-processes){ .index-target }
    - <span id="index-internal-health-queues"></span>[diagnosing delayed checks](ch14-zabbix-maintenance/internal-health.md#queue-metrics){ .index-target }
- <span id="index-ipmi"></span>**IPMI**
    - [understanding IPMI](ch04-zabbix-collecting-data/ipmi.md#understanding-ipmi){ .index-target }
    - [configuring native IPMI monitoring](ch04-zabbix-collecting-data/ipmi.md#native-ipmi-monitoring-in-zabbix){ .index-target }
    - *See also* [Redfish](#index-redfish)
- <span id="index-items"></span>**items**
    - <span id="index-items-browser"></span>[browser items](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - <span id="index-items-calculated"></span>[calculated items](ch04-zabbix-collecting-data/calculated.md){ .index-target }[](ch04-zabbix-collecting-data/calculated.md#conclusion){ .index-range-end }
    - <span id="index-items-dependent"></span>[dependent items](ch04-zabbix-collecting-data/dependent.md){ .index-target }[](ch04-zabbix-collecting-data/dependent.md#conclusion){ .index-range-end }
    - <span id="index-items-http-agent"></span>[HTTP agent items](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
    - <span id="index-items-script"></span>[script items](ch04-zabbix-collecting-data/script.md){ .index-target }[](ch04-zabbix-collecting-data/script.md#conclusion){ .index-range-end }
    - <span id="index-items-telemetry-query"></span>[querying telemetry as item values](ch04-zabbix-collecting-data/telemetry.md#telemetry-query-items-in-brief){ .index-target }
    - <span id="index-items-trapper"></span>[trapper items](ch04-zabbix-collecting-data/zabbix-trapper.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-trapper.md#conclusion){ .index-range-end }

## J {#index-letter-j}

- <span id="index-java-management-extensions"></span>**Java Management Extensions**
    - *See* [JMX](#index-jmx)
- <span id="index-jmx"></span>**JMX**
    - [monitoring Java applications](ch04-zabbix-collecting-data/jmx.md){ .index-target }[](ch04-zabbix-collecting-data/jmx.md#conclusion){ .index-range-end }
    - <span id="index-jmx-jolokia"></span>[monitoring JMX through Jolokia](ch04-zabbix-collecting-data/jmx.md#monitoring-jmx-through-jolokia){ .index-target }
- <span id="index-jolokia"></span>**Jolokia**
    - *See* [JMX, Jolokia](#index-jmx-jolokia)
- <span id="index-jsonpath"></span>**JSONPath**
    - [extracting values during preprocessing](ch04-zabbix-collecting-data/preprocessing.md#jsonpath-and-additional-steps){ .index-target }
    - [using LLD macros as lookup keys](ch16-zabbix-real-world-examples/filter-lld-without-jsonpath.md#approach-b-lld-macro-as-lookup-key-the-recommended-pattern){ .index-target }
    - *See also* [low-level discovery](#index-low-level-discovery), [preprocessing](#index-preprocessing)
- <span id="index-just-in-time-provisioning"></span>**just-in-time provisioning**
    - *See* [LDAP, provisioning](#index-ldap-provisioning)

## K {#index-letter-k}

- <span id="index-keepalived"></span>**Keepalived**
    - *See* [high availability, frontend failover](#index-high-availability-frontend-failover)

## L {#index-letter-l}

- <span id="index-ldap"></span>**LDAP**
    - [configuring LDAP and Active Directory authentication](ch02-zabbix-installation/ldap-ad.md){ .index-target }[](ch02-zabbix-installation/ldap-ad.md#conclusion){ .index-range-end }
    - <span id="index-ldap-provisioning"></span>[configuring just-in-time user provisioning](ch02-zabbix-installation/ldap-ad.md#just-in-time-user-provisioning){ .index-target }
    - *See also* [external authentication](#index-external-authentication)
- <span id="index-let-s-encrypt"></span>**Let's Encrypt**
    - *See* [certificates, Let's Encrypt](#index-certificates-let-s-encrypt)
- <span id="index-lld"></span>**LLD**
    - *See* [low-level discovery](#index-low-level-discovery)
- <span id="index-low-level-discovery"></span>**low-level discovery**
    - <span id="index-low-level-discovery-custom"></span>[custom LLD](ch08-zabbix-lld/custom.md){ .index-target }[](ch08-zabbix-lld/custom.md#conclusion){ .index-range-end }
    - <span id="index-low-level-discovery-dependent-items"></span>[LLD with dependent items](ch08-zabbix-lld/lld-with-dependent-items.md){ .index-target }[](ch08-zabbix-lld/lld-with-dependent-items.md#conclusion){ .index-range-end }
    - <span id="index-low-level-discovery-filtering"></span>[filtering discovered objects](ch08-zabbix-lld/lld-with-dependent-items.md#creating-a-low-level-discovery-lld-filter){ .index-target }
    - <span id="index-low-level-discovery-json-payload-design"></span>[using LLD macros as lookup keys](ch16-zabbix-real-world-examples/filter-lld-without-jsonpath.md#json-payload-design){ .index-target }
    - <span id="index-low-level-discovery-lifecycle"></span>[disabling and deleting lost resources](ch08-zabbix-lld/chapter.md#lifecycle-of-discovered-entities){ .index-target }
    - <span id="index-low-level-discovery-nested-discovery"></span>[configuring nested discovery prototypes](ch08-zabbix-lld/nested-lld.md){ .index-target }
    - <span id="index-low-level-discovery-overrides"></span>[overriding discovered objects](ch08-zabbix-lld/chapter.md#overrides){ .index-target }
    - <span id="index-low-level-discovery-snmp"></span>[SNMP LLD](ch08-zabbix-lld/snmp-lld.md){ .index-target }[](ch08-zabbix-lld/snmp-lld.md#conclusion){ .index-range-end }
    - *See also* [discovery](#index-discovery)

## M {#index-letter-m}

- <span id="index-maintenance"></span>**maintenance**
    - [creating and managing maintenance periods](ch14-zabbix-maintenance/maintenance.md){ .index-target }[](ch14-zabbix-maintenance/maintenance.md#conclusion){ .index-range-end }
    - <span id="index-maintenance-api-automation"></span>[creating maintenance through the API](ch14-zabbix-maintenance/maintenance.md#practical-example-creating-maintenance-via-the-api){ .index-target }
    - <span id="index-maintenance-problem-tag-filtering"></span>[filtering maintenance by problem tags](ch14-zabbix-maintenance/maintenance.md#5-problem-tag-filtering-advanced-suppression){ .index-target }
    - <span id="index-maintenance-scheduling-and-time-zones"></span>[understanding maintenance time zones](ch14-zabbix-maintenance/maintenance.md#time-zones-and-maintenance-schedule-logic){ .index-target }
- <span id="index-maps"></span>**maps**
    - [creating and configuring](ch11-zabbix-visualisation/maps.md){ .index-target }[](ch11-zabbix-visualisation/maps.md#conclusion){ .index-range-end }
    - *See also* [dashboards](#index-dashboards), [visualisation](#index-visualisation)
- <span id="index-mariadb"></span>**MariaDB**
    - <span id="index-mariadb-installation"></span>[installing](ch01-zabbix-components/mariadb.md){ .index-target }[](ch01-zabbix-components/mariadb.md#conclusion){ .index-range-end }
    - <span id="index-mariadb-partitioning"></span>[partitioning](ch13-advanced-security/partitioning-database.md){ .index-target }
    - *See also* [database](#index-database)
- <span id="index-master-items"></span>**master items**
    - *See* [dependent items](#index-dependent-items)
- <span id="index-mcp"></span>**MCP**
    - *See* [Zabbix MCP server](#index-zabbix-mcp-server)
- <span id="index-media-types"></span>**media types**
    - [configuring](ch07-zabbix-alerts/media-types.md){ .index-target }[](ch07-zabbix-alerts/media-types.md#conclusion){ .index-range-end }
    - <span id="index-media-types-delivery-troubleshooting"></span>[troubleshooting notification delivery](ch07-zabbix-alerts/media-types.md#troubleshooting-notification-delivery){ .index-target }
    - <span id="index-media-types-email"></span>[configuring email notifications](ch07-zabbix-alerts/media-types.md#email){ .index-target }
    - <span id="index-media-types-push-notifications"></span>[configuring push notifications](ch07-zabbix-alerts/media-types.md#push-notification){ .index-target }
    - <span id="index-media-types-webhooks"></span>[configuring webhook integrations](ch07-zabbix-alerts/media-types.md#webhook){ .index-target }
    - *See also* [actions](#index-actions), [alerting](#index-alerting)
- <span id="index-mfa"></span>**MFA**
    - *See* [multi-factor authentication](#index-multi-factor-authentication)
- <span id="index-mib-files"></span>**MIB files**
    - *See* [SNMP, MIB files](#index-snmp-mib-files)
- <span id="index-microsoft-entra-id"></span>**Microsoft Entra ID**
    - *See* [SAML, Microsoft Entra ID](#index-saml-microsoft-entra-id)
- <span id="index-model-context-protocol"></span>**Model Context Protocol**
    - *See* [Zabbix MCP server](#index-zabbix-mcp-server)
- <span id="index-multi-factor-authentication"></span>**multi-factor authentication**
    - [configuring](ch02-zabbix-installation/mfa.md){ .index-target }[](ch02-zabbix-installation/mfa.md#conclusion){ .index-range-end }
    - <span id="index-multi-factor-authentication-duo"></span>[configuring Duo MFA](ch02-zabbix-installation/mfa.md#duo-mfa-provider){ .index-target }
    - <span id="index-multi-factor-authentication-totp"></span>[configuring time-based one-time passwords](ch02-zabbix-installation/mfa.md#time-based-one-time-password){ .index-target }

## N {#index-letter-n}

- <span id="index-nested-lld"></span>**nested LLD**
    - *See* [low-level discovery, nested discovery](#index-low-level-discovery-nested-discovery)
- <span id="index-network-discovery"></span>**network discovery**
    - [discovering hosts](ch10-zabbix-discovery/network-host-discovery.md){ .index-target }[](ch10-zabbix-discovery/network-host-discovery.md#conclusion){ .index-range-end }
    - *See also* [discovery](#index-discovery)

## O {#index-letter-o}

- <span id="index-odbc"></span>**ODBC**
    - [database monitoring](ch04-zabbix-collecting-data/database-odbc.md){ .index-target }
    - <span id="index-odbc-discovery"></span>[discovering database objects](ch04-zabbix-collecting-data/database-odbc.md#low-level-discovery-with-odbc){ .index-target }
    - <span id="index-odbc-driver-setup"></span>[installing ODBC drivers](ch04-zabbix-collecting-data/database-odbc.md#driver-selection-and-installation){ .index-target }
    - [validating the ODBC stack](ch04-zabbix-collecting-data/database-odbc.md#validating-the-stack-before-touching-zabbix){ .index-target }
    - <span id="index-odbc-item-design"></span>[choosing scalar or bulk queries](ch04-zabbix-collecting-data/database-odbc.md#item-design-two-keys-different-philosophies){ .index-target }
    - <span id="index-odbc-performance"></span>[tuning queries and pollers](ch04-zabbix-collecting-data/database-odbc.md#operational-discipline){ .index-target }
    - *See also* [database](#index-database)
- <span id="index-oids"></span>**OIDs**
    - *See* [SNMP, object identifiers](#index-snmp-object-identifiers)
- <span id="index-opentelemetry"></span>**OpenTelemetry**
    - [understanding the APM data paths](ch04-zabbix-collecting-data/telemetry.md#how-apm-works-in-zabbix){ .index-target }
    - <span id="index-opentelemetry-collector-pipelines"></span>[using an OpenTelemetry Collector](ch04-zabbix-collecting-data/telemetry.md#alternative-opentelemetry-collector){ .index-target }
    - <span id="index-opentelemetry-data-sources"></span>[configuring global and component data sources](ch04-zabbix-collecting-data/telemetry.md#central-apm-storage-and-other-telemetry-data-sources){ .index-target }
    - <span id="index-opentelemetry-distributed-deployments"></span>[planning distributed telemetry storage](ch04-zabbix-collecting-data/telemetry.md#architecture-considerations-for-distributed-environments){ .index-target }
    - <span id="index-opentelemetry-latency-alerting"></span>[generating traces and alerting on span latency](ch04-zabbix-collecting-data/telemetry.md#lab-generate-traces-and-alert-on-span-latency){ .index-target }
    - <span id="index-opentelemetry-otlp-ingestion"></span>[receiving OTLP through a Zabbix proxy](ch04-zabbix-collecting-data/telemetry.md#1-proxy-configuration-receiving-otlp-data){ .index-target }
    - *See also* [ClickHouse](#index-clickhouse), [Telemetry query items](#index-telemetry-query-items)
- <span id="index-otlp"></span>**OTLP**
    - *See* [OpenTelemetry, OTLP ingestion](#index-opentelemetry-otlp-ingestion)

## P {#index-letter-p}

- <span id="index-passive-checks"></span>**passive checks**
    - *See* [Zabbix agent, passive checks](#index-zabbix-agent-passive-checks)
- <span id="index-performance-counters"></span>**performance counters**
    - *See* [Windows monitoring, performance counters](#index-windows-monitoring-performance-counters)
- <span id="index-permissions"></span>**permissions**
    - [understanding user roles and groups](ch02-zabbix-installation/user-roles.md#summary-role-vs-group){ .index-target }
    - <span id="index-permissions-api-access"></span>[distinguishing API methods from object permissions](ch12-zabbix-api/API basics.md#api-methods-versus-object-permissions){ .index-target }
    - <span id="index-permissions-host-access"></span>[resolving user-group permission precedence](ch02-zabbix-installation/user-groups.md#the-rule-of-precedence-deny-always-wins){ .index-target }
    - <span id="index-permissions-template-access"></span>[controlling template access](ch06-zabbix-templates/templates.md#permissions-and-access-control){ .index-target }
    - *See also* [user groups](#index-user-groups), [user roles](#index-user-roles)
- <span id="index-podman"></span>**Podman**
    - *See* [containers](#index-containers)
- <span id="index-postgresql"></span>**PostgreSQL**
    - <span id="index-postgresql-installation"></span>[installing](ch01-zabbix-components/postgresql.md){ .index-target }[](ch01-zabbix-components/postgresql.md#conclusion){ .index-range-end }
    - <span id="index-postgresql-partitioning-with-timescaledb"></span>[partitioning with TimescaleDB](ch13-advanced-security/partitioning-postgresql-database.md){ .index-target }[](ch13-advanced-security/partitioning-postgresql-database.md#conclusion){ .index-range-end }
    - *See also* [database](#index-database)
- <span id="index-pre-shared-keys"></span>**pre-shared keys**
    - *See* [Zabbix agent, pre-shared keys](#index-zabbix-agent-pre-shared-keys)
- <span id="index-preprocessing"></span>**preprocessing**
    - [understanding preprocessing](ch04-zabbix-collecting-data/preprocessing.md#preprocessing-functionality){ .index-target }
    - <span id="index-preprocessing-discarding-unchanged-values"></span>[discarding unchanged values with a heartbeat](ch04-zabbix-collecting-data/preprocessing.md#discard-unchanged-discard-unchanged-with-heartbeat){ .index-target }
    - <span id="index-preprocessing-javascript"></span>[transforming values with JavaScript](ch04-zabbix-collecting-data/preprocessing.md#javascript){ .index-target }
    - <span id="index-preprocessing-jsonpath"></span>[extracting JSON values](ch04-zabbix-collecting-data/preprocessing.md#jsonpath-and-additional-steps){ .index-target }
    - <span id="index-preprocessing-prometheus"></span>[extracting Prometheus metrics](ch04-zabbix-collecting-data/preprocessing.md#prometheus-pattern){ .index-target }
    - <span id="index-preprocessing-regular-expressions"></span>[extracting values with regular expressions](ch04-zabbix-collecting-data/preprocessing.md#regular-expression){ .index-target }
    - <span id="index-preprocessing-snmp-walk-conversion"></span>[converting an SNMP walk to JSON](ch04-zabbix-collecting-data/preprocessing.md#snmp-walk-to-json){ .index-target }
    - *See also* [dependent items](#index-dependent-items), [items](#index-items)
- <span id="index-prometheus"></span>**Prometheus**
    - [extracting Prometheus metrics during preprocessing](ch04-zabbix-collecting-data/preprocessing.md#prometheus-pattern){ .index-target }
- <span id="index-proxy-groups"></span>**proxy groups**
    - [configuring and managing](ch03-zabbix-proxies/proxy-groups.md){ .index-target }[](ch03-zabbix-proxies/proxy-groups.md#conclusion){ .index-range-end }
    - *See also* [high availability](#index-high-availability), [Zabbix proxy](#index-zabbix-proxy)
- <span id="index-psk"></span>**PSK**
    - *See* [Zabbix agent, pre-shared keys](#index-zabbix-agent-pre-shared-keys)

## R {#index-letter-r}

- <span id="index-redfish"></span>**Redfish**
    - [understanding Redfish](ch04-zabbix-collecting-data/ipmi.md#introduction-to-redfish){ .index-target }
    - [testing with a simulator](ch04-zabbix-collecting-data/ipmi.md#testing-redfish-with-a-simulator){ .index-target }
    - [monitoring Redfish with Zabbix](ch04-zabbix-collecting-data/ipmi.md#monitoring-redfish-with-zabbix){ .index-target }
    - *See also* [IPMI](#index-ipmi), [HTTP agent items](#index-http-agent-items)
- <span id="index-regular-expressions"></span>**regular expressions**
    - *See* [preprocessing, regular expressions](#index-preprocessing-regular-expressions)
- <span id="index-reports"></span>**reports**
    - <span id="index-reports-action-log"></span>[troubleshooting action delivery](ch11-zabbix-visualisation/built-in-reports.md#action-log){ .index-target }
    - <span id="index-reports-audit-log"></span>[reviewing configuration changes](ch11-zabbix-visualisation/built-in-reports.md#audit-log){ .index-target }
    - <span id="index-reports-automated-pdf-reports"></span>[automated PDF reports](ch11-zabbix-visualisation/automated-pdf-reports.md){ .index-target }[](ch11-zabbix-visualisation/automated-pdf-reports.md#conclusion){ .index-range-end }
    - <span id="index-reports-availability"></span>[checking historical availability](ch11-zabbix-visualisation/built-in-reports.md#availability-report){ .index-target }
    - <span id="index-reports-built-in-reports"></span>[built-in reports](ch11-zabbix-visualisation/built-in-reports.md){ .index-target }[](ch11-zabbix-visualisation/built-in-reports.md#conclusion){ .index-range-end }
    - <span id="index-reports-notifications"></span>[reviewing notification history](ch11-zabbix-visualisation/built-in-reports.md#notifications){ .index-target }

## S {#index-letter-s}

- <span id="index-saml"></span>**SAML**
    - [configuring authentication](ch02-zabbix-installation/saml.md){ .index-target }[](ch02-zabbix-installation/saml.md#conclusion){ .index-range-end }
    - <span id="index-saml-google-workspace"></span>[configuring Google Workspace](ch02-zabbix-installation/saml.md#google){ .index-target }
    - <span id="index-saml-microsoft-entra-id"></span>[configuring Microsoft Entra ID](ch02-zabbix-installation/saml.md#microsoft-entra-id-azure-ad){ .index-target }
    - *See also* [external authentication](#index-external-authentication)
- <span id="index-script-items"></span>**script items**
    - [creating and using](ch04-zabbix-collecting-data/script.md){ .index-target }[](ch04-zabbix-collecting-data/script.md#conclusion){ .index-range-end }
- <span id="index-secret-macros"></span>**secret macros**
    - *See* [user macros, secret macros](#index-user-macros-secret-macros)
- <span id="index-selinux"></span>**SELinux**
    - [configuring for Zabbix](ch13-advanced-security/selinux-zabbix.md){ .index-target }[](ch13-advanced-security/selinux-zabbix.md#conclusion){ .index-range-end }
- <span id="index-simple-checks"></span>**simple checks**
    - [configuring ICMP and service checks](ch04-zabbix-collecting-data/simple-checks.md){ .index-target }[](ch04-zabbix-collecting-data/simple-checks.md#conclusion){ .index-range-end }
- <span id="index-smart-monitoring"></span>**SMART monitoring**
    - *See* [Windows monitoring, disk health](#index-windows-monitoring-disk-health)
- <span id="index-snmp"></span>**SNMP**
    - <span id="index-snmp-low-level-discovery"></span>[low-level discovery](ch08-zabbix-lld/snmp-lld.md){ .index-target }[](ch08-zabbix-lld/snmp-lld.md#conclusion){ .index-range-end }
    - <span id="index-snmp-mib-files"></span>[understanding MIB files](ch04-zabbix-collecting-data/snmp-polling.md#what-is-a-mib){ .index-target }
    - [installing MIB files](ch04-zabbix-collecting-data/snmp-polling.md#deploying-bare-minimum-mib-files){ .index-target }
    - <span id="index-snmp-object-identifiers"></span>[understanding OIDs](ch04-zabbix-collecting-data/snmp-polling.md#what-is-an-oid){ .index-target }
    - <span id="index-snmp-polling"></span>[polling](ch04-zabbix-collecting-data/snmp-polling.md){ .index-target }[](ch04-zabbix-collecting-data/snmp-polling.md#conclusion){ .index-range-end }
    - <span id="index-snmp-snmpv3-security"></span>[choosing SNMPv3 security levels](ch04-zabbix-collecting-data/snmp-polling.md#snmpv3-security-levels){ .index-target }
    - <span id="index-snmp-trapping"></span>[trapping](ch04-zabbix-collecting-data/snmp-trapping.md){ .index-target }[](ch04-zabbix-collecting-data/snmp-trapping.md#conclusion){ .index-range-end }
- <span id="index-snmpv3"></span>**SNMPv3**
    - *See* [SNMP, SNMPv3 security](#index-snmp-snmpv3-security)
- <span id="index-ssh-checks"></span>**SSH checks**
    - [configuring SSH checks](ch04-zabbix-collecting-data/ssh-telnet.md#ssh-monitoring){ .index-target }
- <span id="index-ssl"></span>**SSL**
    - *See* [TLS](#index-tls)
- <span id="index-system-requirements"></span>**system requirements**
    - [planning hardware and software requirements](ch00-getting-started/Requirements.md#requirements){ .index-target }

## T {#index-letter-t}

- <span id="index-tags"></span>**tags**
    - [using tags and inheritance](ch06-zabbix-templates/templates.md#tags){ .index-target }
- <span id="index-telemetry-query-items"></span>**Telemetry query items**
    - [querying telemetry as regular item values](ch04-zabbix-collecting-data/telemetry.md#telemetry-query-items-in-brief){ .index-target }
    - [understanding timing and aggregation](ch04-zabbix-collecting-data/telemetry.md#understanding-query-timing-and-aggregation){ .index-target }
    - *See also* [OpenTelemetry](#index-opentelemetry), [items](#index-items)
- <span id="index-telnet-checks"></span>**Telnet checks**
    - [configuring Telnet checks](ch04-zabbix-collecting-data/ssh-telnet.md#telnet-monitoring){ .index-target }
- <span id="index-template-groups"></span>**template groups**
    - [organising template groups and permissions](ch06-zabbix-templates/templates.md#template-groups){ .index-target }
    - *See also* [templates](#index-templates), [permissions](#index-permissions)
- <span id="index-templates"></span>**templates**
    - [creating and using](ch06-zabbix-templates/templates.md){ .index-target }[](ch06-zabbix-templates/templates.md#conclusion){ .index-range-end }
    - <span id="index-templates-groups-and-permissions"></span>[configuring template groups](ch06-zabbix-templates/templates.md#template-groups){ .index-target }
    - [controlling template access](ch06-zabbix-templates/templates.md#permissions-and-access-control){ .index-target }
    - <span id="index-templates-importing-and-exporting"></span>[importing and exporting templates](ch06-zabbix-templates/templates.md#importing-and-exporting-templates){ .index-target }
    - <span id="index-templates-unlinking-and-clearing"></span>[choosing unlink or unlink and clear](ch06-zabbix-templates/templates.md#unlink-vs-unlink-and-clear){ .index-target }
    - <span id="index-templates-value-maps"></span>[configuring value maps](ch06-zabbix-templates/templates.md#value-maps){ .index-target }
    - *See also* [low-level discovery](#index-low-level-discovery), [user macros](#index-user-macros)
- <span id="index-time-synchronisation"></span>**time synchronisation**
    - [configuring Chrony and time sources](ch00-getting-started/Requirements.md#time-server){ .index-target }
    - *See also* [maintenance](#index-maintenance)
- <span id="index-timescaledb"></span>**TimescaleDB**
    - [partitioning PostgreSQL](ch13-advanced-security/partitioning-postgresql-database.md){ .index-target }[](ch13-advanced-security/partitioning-postgresql-database.md#conclusion){ .index-range-end }
- <span id="index-tls"></span>**TLS**
    - <span id="index-tls-agent-connections"></span>[encrypting agent communication](ch13-advanced-security/agent-security.md){ .index-target }
    - <span id="index-tls-frontend-https"></span>[securing frontend connections](ch13-advanced-security/securing-frontend.md){ .index-target }
    - <span id="index-tls-mcp-connections"></span>[enabling TLS on the MCP server](ch09-zabbix-extending/mcp-server.md#securing-the-connection-with-tls){ .index-target }
    - <span id="index-tls-vault-connections"></span>[verifying Vault TLS certificates](ch13-advanced-security/using-vault.md#tls-configuration){ .index-target }
    - *See also* [certificates](#index-certificates)
- <span id="index-trapper-items"></span>**trapper items**
    - [creating and using](ch04-zabbix-collecting-data/zabbix-trapper.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-trapper.md#conclusion){ .index-range-end }
- <span id="index-trigger-dependencies"></span>**trigger dependencies**
    - *See* [triggers, dependencies](#index-triggers-dependencies)
- <span id="index-triggers"></span>**triggers**
    - <span id="index-triggers-advanced-expressions"></span>[advanced expressions](ch05-zabbix-triggers/advanced-triggers.md){ .index-target }[](ch05-zabbix-triggers/advanced-triggers.md#conclusion){ .index-range-end }
    - <span id="index-triggers-creating"></span>[creating and configuring](ch05-zabbix-triggers/triggers.md){ .index-target }[](ch05-zabbix-triggers/triggers.md#conclusion){ .index-range-end }
    - <span id="index-triggers-dependencies"></span>[configuring trigger dependencies](ch05-zabbix-triggers/advanced-triggers.md#trigger-dependency){ .index-target }
    - <span id="index-triggers-flapping"></span>[reducing trigger flapping](ch05-zabbix-triggers/advanced-triggers.md#reducing-flapping-even-more){ .index-target }
    - <span id="index-triggers-multiple-problem-events"></span>[generating multiple problem events](ch05-zabbix-triggers/advanced-triggers.md#multiple-problem-event-generation){ .index-target }
    - <span id="index-triggers-recovery-expressions"></span>[configuring recovery expressions](ch05-zabbix-triggers/advanced-triggers.md#recovery-expression){ .index-target }

## U {#index-letter-u}

- <span id="index-upgrades"></span>**upgrades**
    - [planning and performing](ch14-zabbix-maintenance/upgrades.md){ .index-target }[](ch14-zabbix-maintenance/upgrades.md#conclusion){ .index-range-end }
    - <span id="index-upgrades-database-migration"></span>[choosing an upgrade or migration strategy](ch14-zabbix-maintenance/upgrades.md#choosing-the-right-approach){ .index-target }
    - <span id="index-upgrades-database-primary-keys"></span>[checking primary keys before upgrading](ch14-zabbix-maintenance/upgrades.md#a-crucial-detour-primary-keys-and-database-health){ .index-target }
    - *See also* [backups](#index-backups)
- <span id="index-user-groups"></span>**user groups**
    - [creating and managing](ch02-zabbix-installation/user-groups.md){ .index-target }[](ch02-zabbix-installation/user-groups.md#conclusion){ .index-range-end }
    - *See also* [user roles](#index-user-roles)
- <span id="index-user-macros"></span>**user macros**
    - [using template macros](ch06-zabbix-templates/templates.md#template-macros){ .index-target }
    - <span id="index-user-macros-context-macros"></span>[using context macros](ch05-zabbix-triggers/advanced-triggers.md#context-macros){ .index-target }
    - <span id="index-user-macros-precedence"></span>[resolving macro precedence](ch06-zabbix-templates/templates.md#macro-precedence-and-conflict-resolution){ .index-target }
    - <span id="index-user-macros-secret-macros"></span>[resolving secrets from Vault](ch13-advanced-security/using-vault.md#using-vault-secrets-as-macros-in-zabbix){ .index-target }
- <span id="index-user-parameters"></span>**user parameters**
    - [creating custom items](ch09-zabbix-extending/user-parameters.md){ .index-target }[](ch09-zabbix-extending/user-parameters.md#conclusion){ .index-range-end }
- <span id="index-user-roles"></span>**user roles**
    - [creating and managing](ch02-zabbix-installation/user-roles.md){ .index-target }[](ch02-zabbix-installation/user-roles.md#conclusion){ .index-range-end }
    - *See also* [user groups](#index-user-groups)

## V {#index-letter-v}

- <span id="index-value-maps"></span>**value maps**
    - [mapping item values to readable labels](ch06-zabbix-templates/templates.md#value-maps){ .index-target }
    - *See also* [templates](#index-templates)
- <span id="index-vault"></span>**Vault**
    - [storing Zabbix secrets](ch13-advanced-security/using-vault.md){ .index-target }[](ch13-advanced-security/using-vault.md#conclusion){ .index-range-end }
    - <span id="index-vault-approle"></span>[configuring AppRole authentication](ch13-advanced-security/using-vault.md#alternative-configure-approle-authentication-in-zabbix-80){ .index-target }
    - <span id="index-vault-secret-macros"></span>[using Vault secrets in macros](ch13-advanced-security/using-vault.md#using-vault-secrets-as-macros-in-zabbix){ .index-target }
    - <span id="index-vault-tls"></span>[securing Vault connections](ch13-advanced-security/using-vault.md#tls-configuration){ .index-target }
    - <span id="index-vault-troubleshooting"></span>[troubleshooting Vault integration](ch13-advanced-security/using-vault.md#troubleshooting){ .index-target }
- <span id="index-visualisation"></span>**visualisation**
    - <span id="index-visualisation-dashboards"></span>[dashboards](ch11-zabbix-visualisation/dashboards.md){ .index-target }[](ch11-zabbix-visualisation/dashboards.md#conclusion){ .index-range-end }
    - <span id="index-visualisation-graphs"></span>[graphs](ch11-zabbix-visualisation/graphs.md){ .index-target }[](ch11-zabbix-visualisation/graphs.md#conclusion){ .index-range-end }
    - <span id="index-visualisation-maps"></span>[maps](ch11-zabbix-visualisation/maps.md){ .index-target }[](ch11-zabbix-visualisation/maps.md#conclusion){ .index-range-end }

## W {#index-letter-w}

- <span id="index-web-monitoring"></span>**web monitoring**
    - <span id="index-web-monitoring-browser-items"></span>[browser items](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - <span id="index-web-monitoring-http-agent-items"></span>[HTTP agent items](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
- <span id="index-webdriver"></span>**WebDriver**
    - *See* [browser items, WebDriver](#index-browser-items-webdriver)
- <span id="index-webhooks"></span>**webhooks**
    - *See* [media types, webhooks](#index-media-types-webhooks)
- <span id="index-widgets"></span>**widgets**
    - *See* [dashboards, widgets](#index-dashboards-widgets)
- <span id="index-windows-monitoring"></span>**Windows monitoring**
    - <span id="index-windows-monitoring-autoregistration"></span>[setting Windows host metadata](ch15-windows/windows-zabbix-agent2-config-tips.md#metadata-and-autoregistration){ .index-target }
    - <span id="index-windows-monitoring-disk-health"></span>[monitoring disk health](ch16-zabbix-real-world-examples/disk-health-windows.md){ .index-target }
    - <span id="index-windows-monitoring-event-logs"></span>[monitoring Windows event logs](ch15-windows/windows.md#event-log-monitoring){ .index-target }
    - <span id="index-windows-monitoring-fleet-deployment"></span>[deploying agents with MSI and PowerShell](ch15-windows/windows-zabbix-agent2-config-tips.md#using-the-msi-installer){ .index-target }
    - <span id="index-windows-monitoring-overview"></span>[monitoring Windows](ch15-windows/windows.md){ .index-target }
    - <span id="index-windows-monitoring-performance-counters"></span>[collecting Windows performance counters](ch15-windows/windows.md#performance-counters){ .index-target }
    - <span id="index-windows-monitoring-registry"></span>[reading the Windows Registry](ch15-windows/windows.md#registryget-as-a-complement-to-wmi){ .index-target }
    - <span id="index-windows-monitoring-services"></span>[monitoring Windows services](ch15-windows/windows.md#service-state-via-serviceinfo){ .index-target }
    - <span id="index-windows-monitoring-wmi-queries"></span>[querying WMI](ch15-windows/windows.md#wmi-queries-with-wmiget-and-wmigetall){ .index-target }
- <span id="index-wmi"></span>**WMI**
    - *See* [Windows monitoring, WMI queries](#index-windows-monitoring-wmi-queries)

## Z {#index-letter-z}

- <span id="index-zabbix-agent"></span>**Zabbix agent**
    - <span id="index-zabbix-agent-active-checks"></span>[active checks](ch04-zabbix-collecting-data/zabbix-agent-active.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-agent-active.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-agent-certificates"></span>[configuring certificate encryption](ch13-advanced-security/agent-security.md#certificates){ .index-target }
    - <span id="index-zabbix-agent-encryption"></span>[encryption](ch13-advanced-security/agent-security.md){ .index-target }[](ch13-advanced-security/agent-security.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-agent-item-key-restrictions"></span>[restricting keys with AllowKey and DenyKey](ch04-zabbix-collecting-data/zabbix-agent-active.md#restricting-which-item-keys-the-agent-can-execute){ .index-target }
    - <span id="index-zabbix-agent-passive-checks"></span>[passive checks](ch04-zabbix-collecting-data/zabbix-agent-passive.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-agent-passive.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-agent-pre-shared-keys"></span>[configuring PSK encryption](ch13-advanced-security/agent-security.md#pre-shared-keys){ .index-target }
    - <span id="index-zabbix-agent-windows-fleet-deployment"></span>[configuring and deploying Windows agents](ch15-windows/windows-zabbix-agent2-config-tips.md){ .index-target }
- <span id="index-zabbix-api"></span>**Zabbix API**
    - [understanding requests and authentication](ch12-zabbix-api/API basics.md){ .index-target }
    - [automating Zabbix workflows](ch12-zabbix-api/self-engaging.md){ .index-target }
    - <span id="index-zabbix-api-compatibility"></span>[checking compatibility and breaking changes](ch12-zabbix-api/API basics.md#compatibility){ .index-target }
    - <span id="index-zabbix-api-error-handling"></span>[handling errors](ch12-zabbix-api/API basics.md#error-handling){ .index-target }
    - [troubleshooting API requests](ch12-zabbix-api/API basics.md#troubleshooting-common-api-errors){ .index-target }
    - <span id="index-zabbix-api-permissions"></span>[checking API and object permissions](ch12-zabbix-api/API basics.md#api-methods-versus-object-permissions){ .index-target }
    - *See also* [API tokens](#index-api-tokens)
- <span id="index-zabbix-architecture"></span>**Zabbix architecture**
    - [understanding components and data flow](ch01-zabbix-components/architecture.md){ .index-target }
- <span id="index-zabbix-frontend"></span>**Zabbix frontend**
    - [installing](ch01-zabbix-components/zabbix-frontend.md){ .index-target }[](ch01-zabbix-components/zabbix-frontend.md#conclusion){ .index-range-end }
    - [navigating and configuring](ch02-zabbix-installation/frontend.md){ .index-target }[](ch02-zabbix-installation/frontend.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-frontend-https"></span>[securing the frontend with HTTPS](ch13-advanced-security/securing-frontend.md){ .index-target }
- <span id="index-zabbix-mcp-server"></span>**Zabbix MCP server**
    - [installing and configuring](ch09-zabbix-extending/mcp-server.md#installing-and-configuring-the-mcp-server){ .index-target }
    - <span id="index-zabbix-mcp-server-ai-clients"></span>[connecting an AI application](ch09-zabbix-extending/mcp-server.md#connecting-an-ai-application){ .index-target }
    - <span id="index-zabbix-mcp-server-connection-testing"></span>[testing the connection and listing tools](ch09-zabbix-extending/mcp-server.md#testing-the-connection-and-listing-available-tools){ .index-target }
    - <span id="index-zabbix-mcp-server-tls"></span>[securing MCP connections](ch09-zabbix-extending/mcp-server.md#securing-the-connection-with-tls){ .index-target }
    - <span id="index-zabbix-mcp-server-tool-access"></span>[restricting tools and sensitive data](ch09-zabbix-extending/mcp-server.md#controlling-access-to-tools-and-sensitive-data){ .index-target }
    - *See also* [API tokens](#index-api-tokens), [Zabbix API](#index-zabbix-api)
- <span id="index-zabbix-proxy"></span>**Zabbix proxy**
    - <span id="index-zabbix-proxy-active-and-passive-modes"></span>[active and passive modes](ch03-zabbix-proxies/active-passive-proxies.md){ .index-target }[](ch03-zabbix-proxies/active-passive-proxies.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-proxy-apm-collector"></span>[receiving OTLP telemetry](ch04-zabbix-collecting-data/telemetry.md#1-proxy-configuration-receiving-otlp-data){ .index-target }
    - <span id="index-zabbix-proxy-containers"></span>[running as containers](ch03-zabbix-proxies/proxies-as-container.md){ .index-target }[](ch03-zabbix-proxies/proxies-as-container.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-proxy-proxy-groups"></span>[proxy groups](ch03-zabbix-proxies/proxy-groups.md){ .index-target }[](ch03-zabbix-proxies/proxy-groups.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-proxy-requirements"></span>[sizing proxies](ch03-zabbix-proxies/proxy-basics.md#proxy-requirements){ .index-target }
    - <span id="index-zabbix-proxy-runtime-control"></span>[using proxy runtime controls](ch03-zabbix-proxies/proxy-basics.md#proxy-runtime-control-options){ .index-target }
    - <span id="index-zabbix-proxy-throttling"></span>[understanding proxy throttling](ch03-zabbix-proxies/proxy-basics.md#proxy-throttling){ .index-target }
- <span id="index-zabbix-sender"></span>**Zabbix sender**
    - [sending monitoring values](ch04-zabbix-collecting-data/zabbix-trapper.md#how-to-send-data){ .index-target }
    - [sending historical values](ch04-zabbix-collecting-data/zabbix-trapper.md#you-can-travel-in-time-with-zabbix_sender){ .index-target }
    - [sending multiple values](ch04-zabbix-collecting-data/zabbix-trapper.md#sending-multiple-values-at-once){ .index-target }
    - *See also* [trapper items](#index-trapper-items)
- <span id="index-zabbix-server"></span>**Zabbix server**
    - [installing](ch01-zabbix-components/zabbix-server.md){ .index-target }[](ch01-zabbix-components/zabbix-server.md#conclusion){ .index-range-end }
    - *See also* [high availability](#index-high-availability), [internal health](#index-internal-health)
- <span id="index-zabbix-web-service"></span>**Zabbix web service**
    - [installing and configuring](ch03-zabbix-proxies/web-services.md){ .index-target }[](ch03-zabbix-proxies/web-services.md#conclusion){ .index-range-end }
    - *See also* [automated PDF reports](#index-automated-pdf-reports)

</div>
