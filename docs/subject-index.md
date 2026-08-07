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
[A](#index-letter-a) · [B](#index-letter-b) · [C](#index-letter-c) · [D](#index-letter-d) · [E](#index-letter-e) · [F](#index-letter-f) · [G](#index-letter-g) · [H](#index-letter-h) · [I](#index-letter-i) · [J](#index-letter-j) · [L](#index-letter-l) · [M](#index-letter-m) · [N](#index-letter-n) · [O](#index-letter-o) · [P](#index-letter-p) · [R](#index-letter-r) · [S](#index-letter-s) · [T](#index-letter-t) · [U](#index-letter-u) · [V](#index-letter-v) · [W](#index-letter-w) · [Z](#index-letter-z)
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
- <span id="index-agent-encryption"></span>**agent encryption**
    - *See* [Zabbix agent, encryption](#index-zabbix-agent-encryption)
- <span id="index-alert-scripts"></span>**alert scripts**
    - [creating custom scripts](ch07-zabbix-alerts/scripts.md){ .index-target }
    - *See also* [alerting](#index-alerting), [media types](#index-media-types)
- <span id="index-alerting"></span>**alerting**
    - <span id="index-alerting-actions"></span>[actions](ch07-zabbix-alerts/actions.md){ .index-target }[](ch07-zabbix-alerts/actions.md#conclusion){ .index-range-end }
    - <span id="index-alerting-custom-scripts"></span>[custom scripts](ch07-zabbix-alerts/scripts.md){ .index-target }
    - <span id="index-alerting-media-types"></span>[media types](ch07-zabbix-alerts/media-types.md){ .index-target }[](ch07-zabbix-alerts/media-types.md#conclusion){ .index-range-end }
- <span id="index-api"></span>**API**
    - *See* [Zabbix API](#index-zabbix-api)
- <span id="index-api-tokens"></span>**API tokens**
    - [using with the Zabbix API](ch12-zabbix-api/self-engaging.md){ .index-target }
    - *See also* [Zabbix API](#index-zabbix-api)
- <span id="index-automated-pdf-reports"></span>**automated PDF reports**
    - [creating](ch11-zabbix-visualisation/automated-pdf-reports.md){ .index-target }[](ch11-zabbix-visualisation/automated-pdf-reports.md#conclusion){ .index-range-end }
    - *See also* [reports](#index-reports), [Zabbix web service](#index-zabbix-web-service)

## B {#index-letter-b}

- <span id="index-backups"></span>**backups**
    - [creating and restoring](ch14-zabbix-maintenance/taking-backups.md){ .index-target }[](ch14-zabbix-maintenance/taking-backups.md#conclusion){ .index-range-end }
- <span id="index-browser-items"></span>**browser items**
    - [configuring browser monitoring](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - *See also* [web monitoring](#index-web-monitoring)

## C {#index-letter-c}

- <span id="index-calculated-items"></span>**calculated items**
    - [creating and using](ch04-zabbix-collecting-data/calculated.md){ .index-target }[](ch04-zabbix-collecting-data/calculated.md#conclusion){ .index-range-end }
    - *See also* [items](#index-items)
- <span id="index-clickhouse"></span>**ClickHouse**
    - [storing Zabbix data](ch13-advanced-security/storing-data-in-clickhousedb.md){ .index-target }

## D {#index-letter-d}

- <span id="index-dashboards"></span>**dashboards**
    - [creating and configuring](ch11-zabbix-visualisation/dashboards.md){ .index-target }[](ch11-zabbix-visualisation/dashboards.md#conclusion){ .index-range-end }
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
- <span id="index-dependent-items"></span>**dependent items**
    - [configuring](ch04-zabbix-collecting-data/dependent.md){ .index-target }[](ch04-zabbix-collecting-data/dependent.md#conclusion){ .index-range-end }
    - *See also* [low-level discovery](#index-low-level-discovery), [preprocessing](#index-preprocessing)
- <span id="index-discovery"></span>**discovery**
    - <span id="index-discovery-active-agent-autoregistration"></span>[active agent autoregistration](ch10-zabbix-discovery/active-agent-autoregistration.md){ .index-target }[](ch10-zabbix-discovery/active-agent-autoregistration.md#conclusion){ .index-range-end }
    - <span id="index-discovery-network-discovery"></span>[network discovery](ch10-zabbix-discovery/network-host-discovery.md){ .index-target }[](ch10-zabbix-discovery/network-host-discovery.md#conclusion){ .index-range-end }
    - *See also* [low-level discovery](#index-low-level-discovery)

## E {#index-letter-e}

- <span id="index-external-authentication"></span>**external authentication**
    - <span id="index-external-authentication-http"></span>[HTTP authentication](ch02-zabbix-installation/http.md){ .index-target }[](ch02-zabbix-installation/http.md#conclusion){ .index-range-end }
    - <span id="index-external-authentication-ldap"></span>[LDAP and Active Directory](ch02-zabbix-installation/ldap-ad.md){ .index-target }[](ch02-zabbix-installation/ldap-ad.md#conclusion){ .index-range-end }
    - <span id="index-external-authentication-saml"></span>[SAML authentication](ch02-zabbix-installation/saml.md){ .index-target }[](ch02-zabbix-installation/saml.md#conclusion){ .index-range-end }
- <span id="index-external-checks"></span>**external checks**
    - [creating and using](ch04-zabbix-collecting-data/external-checks.md){ .index-target }[](ch04-zabbix-collecting-data/external-checks.md#conclusion){ .index-range-end }

## F {#index-letter-f}

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
    - *See also* [proxy groups](#index-proxy-groups)
- <span id="index-host-groups"></span>**host groups**
    - [creating and managing](ch02-zabbix-installation/host-groups.md){ .index-target }[](ch02-zabbix-installation/host-groups.md#conclusion){ .index-range-end }
- <span id="index-host-interfaces"></span>**host interfaces**
    - [configuring](ch04-zabbix-collecting-data/host-interfaces.md){ .index-target }[](ch04-zabbix-collecting-data/host-interfaces.md#conclusion){ .index-range-end }
    - *See also* [hosts](#index-hosts)
- <span id="index-hosts"></span>**hosts**
    - [creating and configuring](ch04-zabbix-collecting-data/hosts.md){ .index-target }[](ch04-zabbix-collecting-data/hosts.md#conclusion){ .index-range-end }
    - *See also* [host groups](#index-host-groups), [host interfaces](#index-host-interfaces)
- <span id="index-http-agent-items"></span>**HTTP agent items**
    - [configuring](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
    - *See also* [web monitoring](#index-web-monitoring)

## I {#index-letter-i}

- <span id="index-icmp-checks"></span>**ICMP checks**
    - [configuring simple checks](ch04-zabbix-collecting-data/simple-checks.md){ .index-target }[](ch04-zabbix-collecting-data/simple-checks.md#conclusion){ .index-range-end }
- <span id="index-internal-health"></span>**internal health**
    - [monitoring Zabbix health](ch14-zabbix-maintenance/internal-health.md){ .index-target }[](ch14-zabbix-maintenance/internal-health.md#conclusion){ .index-range-end }
- <span id="index-ipmi"></span>**IPMI**
    - [configuring IPMI monitoring](ch04-zabbix-collecting-data/ipmi.md){ .index-target }[](ch04-zabbix-collecting-data/ipmi.md#conclusion){ .index-range-end }
- <span id="index-items"></span>**items**
    - <span id="index-items-browser"></span>[browser items](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - <span id="index-items-calculated"></span>[calculated items](ch04-zabbix-collecting-data/calculated.md){ .index-target }[](ch04-zabbix-collecting-data/calculated.md#conclusion){ .index-range-end }
    - <span id="index-items-dependent"></span>[dependent items](ch04-zabbix-collecting-data/dependent.md){ .index-target }[](ch04-zabbix-collecting-data/dependent.md#conclusion){ .index-range-end }
    - <span id="index-items-http-agent"></span>[HTTP agent items](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
    - <span id="index-items-script"></span>[script items](ch04-zabbix-collecting-data/script.md){ .index-target }[](ch04-zabbix-collecting-data/script.md#conclusion){ .index-range-end }
    - <span id="index-items-trapper"></span>[trapper items](ch04-zabbix-collecting-data/zabbix-trapper.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-trapper.md#conclusion){ .index-range-end }

## J {#index-letter-j}

- <span id="index-java-management-extensions"></span>**Java Management Extensions**
    - *See* [JMX](#index-jmx)
- <span id="index-jmx"></span>**JMX**
    - [monitoring Java applications](ch04-zabbix-collecting-data/jmx.md){ .index-target }[](ch04-zabbix-collecting-data/jmx.md#conclusion){ .index-range-end }

## L {#index-letter-l}

- <span id="index-ldap"></span>**LDAP**
    - [configuring LDAP and Active Directory authentication](ch02-zabbix-installation/ldap-ad.md){ .index-target }[](ch02-zabbix-installation/ldap-ad.md#conclusion){ .index-range-end }
    - *See also* [external authentication](#index-external-authentication)
- <span id="index-lld"></span>**LLD**
    - *See* [low-level discovery](#index-low-level-discovery)
- <span id="index-low-level-discovery"></span>**low-level discovery**
    - <span id="index-low-level-discovery-custom"></span>[custom LLD](ch08-zabbix-lld/custom.md){ .index-target }[](ch08-zabbix-lld/custom.md#conclusion){ .index-range-end }
    - <span id="index-low-level-discovery-dependent-items"></span>[LLD with dependent items](ch08-zabbix-lld/lld-with-dependent-items.md){ .index-target }[](ch08-zabbix-lld/lld-with-dependent-items.md#conclusion){ .index-range-end }
    - <span id="index-low-level-discovery-snmp"></span>[SNMP LLD](ch08-zabbix-lld/snmp-lld.md){ .index-target }[](ch08-zabbix-lld/snmp-lld.md#conclusion){ .index-range-end }
    - *See also* [discovery](#index-discovery)

## M {#index-letter-m}

- <span id="index-maintenance"></span>**maintenance**
    - [creating and managing maintenance periods](ch14-zabbix-maintenance/maintenance.md){ .index-target }[](ch14-zabbix-maintenance/maintenance.md#conclusion){ .index-range-end }
- <span id="index-maps"></span>**maps**
    - [creating and configuring](ch11-zabbix-visualisation/maps.md){ .index-target }[](ch11-zabbix-visualisation/maps.md#conclusion){ .index-range-end }
    - *See also* [dashboards](#index-dashboards), [visualisation](#index-visualisation)
- <span id="index-mariadb"></span>**MariaDB**
    - <span id="index-mariadb-installation"></span>[installing](ch01-zabbix-components/mariadb.md){ .index-target }[](ch01-zabbix-components/mariadb.md#conclusion){ .index-range-end }
    - <span id="index-mariadb-partitioning"></span>[partitioning](ch13-advanced-security/partitioning-database.md){ .index-target }
    - *See also* [database](#index-database)
- <span id="index-master-items"></span>**master items**
    - *See* [dependent items](#index-dependent-items)
- <span id="index-media-types"></span>**media types**
    - [configuring](ch07-zabbix-alerts/media-types.md){ .index-target }[](ch07-zabbix-alerts/media-types.md#conclusion){ .index-range-end }
    - *See also* [actions](#index-actions), [alerting](#index-alerting)
- <span id="index-mfa"></span>**MFA**
    - *See* [multi-factor authentication](#index-multi-factor-authentication)
- <span id="index-multi-factor-authentication"></span>**multi-factor authentication**
    - [configuring](ch02-zabbix-installation/mfa.md){ .index-target }[](ch02-zabbix-installation/mfa.md#conclusion){ .index-range-end }

## N {#index-letter-n}

- <span id="index-network-discovery"></span>**network discovery**
    - [discovering hosts](ch10-zabbix-discovery/network-host-discovery.md){ .index-target }[](ch10-zabbix-discovery/network-host-discovery.md#conclusion){ .index-range-end }
    - *See also* [discovery](#index-discovery)

## O {#index-letter-o}

- <span id="index-odbc"></span>**ODBC**
    - [database monitoring](ch04-zabbix-collecting-data/database-odbc.md){ .index-target }
    - *See also* [database](#index-database)

## P {#index-letter-p}

- <span id="index-passive-checks"></span>**passive checks**
    - *See* [Zabbix agent, passive checks](#index-zabbix-agent-passive-checks)
- <span id="index-postgresql"></span>**PostgreSQL**
    - <span id="index-postgresql-installation"></span>[installing](ch01-zabbix-components/postgresql.md){ .index-target }[](ch01-zabbix-components/postgresql.md#conclusion){ .index-range-end }
    - <span id="index-postgresql-partitioning-with-timescaledb"></span>[partitioning with TimescaleDB](ch13-advanced-security/partitioning-postgresql-database.md){ .index-target }[](ch13-advanced-security/partitioning-postgresql-database.md#conclusion){ .index-range-end }
    - *See also* [database](#index-database)
- <span id="index-preprocessing"></span>**preprocessing**
    - [transforming item values](ch04-zabbix-collecting-data/preprocessing.md){ .index-target }[](ch04-zabbix-collecting-data/preprocessing.md#conclusion){ .index-range-end }
    - *See also* [dependent items](#index-dependent-items), [items](#index-items)
- <span id="index-proxy-groups"></span>**proxy groups**
    - [configuring and managing](ch03-zabbix-proxies/proxy-groups.md){ .index-target }[](ch03-zabbix-proxies/proxy-groups.md#conclusion){ .index-range-end }
    - *See also* [high availability](#index-high-availability), [Zabbix proxy](#index-zabbix-proxy)

## R {#index-letter-r}

- <span id="index-reports"></span>**reports**
    - <span id="index-reports-automated-pdf-reports"></span>[automated PDF reports](ch11-zabbix-visualisation/automated-pdf-reports.md){ .index-target }[](ch11-zabbix-visualisation/automated-pdf-reports.md#conclusion){ .index-range-end }
    - <span id="index-reports-built-in-reports"></span>[built-in reports](ch11-zabbix-visualisation/built-in-reports.md){ .index-target }[](ch11-zabbix-visualisation/built-in-reports.md#conclusion){ .index-range-end }

## S {#index-letter-s}

- <span id="index-saml"></span>**SAML**
    - [configuring authentication](ch02-zabbix-installation/saml.md){ .index-target }[](ch02-zabbix-installation/saml.md#conclusion){ .index-range-end }
    - *See also* [external authentication](#index-external-authentication)
- <span id="index-script-items"></span>**script items**
    - [creating and using](ch04-zabbix-collecting-data/script.md){ .index-target }[](ch04-zabbix-collecting-data/script.md#conclusion){ .index-range-end }
- <span id="index-selinux"></span>**SELinux**
    - [configuring for Zabbix](ch13-advanced-security/selinux-zabbix.md){ .index-target }[](ch13-advanced-security/selinux-zabbix.md#conclusion){ .index-range-end }
- <span id="index-simple-checks"></span>**simple checks**
    - [configuring ICMP and service checks](ch04-zabbix-collecting-data/simple-checks.md){ .index-target }[](ch04-zabbix-collecting-data/simple-checks.md#conclusion){ .index-range-end }
- <span id="index-snmp"></span>**SNMP**
    - <span id="index-snmp-low-level-discovery"></span>[low-level discovery](ch08-zabbix-lld/snmp-lld.md){ .index-target }[](ch08-zabbix-lld/snmp-lld.md#conclusion){ .index-range-end }
    - <span id="index-snmp-polling"></span>[polling](ch04-zabbix-collecting-data/snmp-polling.md){ .index-target }[](ch04-zabbix-collecting-data/snmp-polling.md#conclusion){ .index-range-end }
    - <span id="index-snmp-trapping"></span>[trapping](ch04-zabbix-collecting-data/snmp-trapping.md){ .index-target }[](ch04-zabbix-collecting-data/snmp-trapping.md#conclusion){ .index-range-end }
- <span id="index-ssh-checks"></span>**SSH checks**
    - [configuring SSH checks](ch04-zabbix-collecting-data/ssh-telnet.md){ .index-target }[](ch04-zabbix-collecting-data/ssh-telnet.md#conclusion){ .index-range-end }

## T {#index-letter-t}

- <span id="index-tags"></span>**tags**
    - [using in templates](ch06-zabbix-templates/templates.md){ .index-target }[](ch06-zabbix-templates/templates.md#conclusion){ .index-range-end }
- <span id="index-telnet-checks"></span>**Telnet checks**
    - [configuring Telnet checks](ch04-zabbix-collecting-data/ssh-telnet.md){ .index-target }[](ch04-zabbix-collecting-data/ssh-telnet.md#conclusion){ .index-range-end }
- <span id="index-templates"></span>**templates**
    - [creating and using](ch06-zabbix-templates/templates.md){ .index-target }[](ch06-zabbix-templates/templates.md#conclusion){ .index-range-end }
    - *See also* [low-level discovery](#index-low-level-discovery), [user macros](#index-user-macros)
- <span id="index-timescaledb"></span>**TimescaleDB**
    - [partitioning PostgreSQL](ch13-advanced-security/partitioning-postgresql-database.md){ .index-target }[](ch13-advanced-security/partitioning-postgresql-database.md#conclusion){ .index-range-end }
- <span id="index-trapper-items"></span>**trapper items**
    - [creating and using](ch04-zabbix-collecting-data/zabbix-trapper.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-trapper.md#conclusion){ .index-range-end }
- <span id="index-triggers"></span>**triggers**
    - <span id="index-triggers-advanced-expressions"></span>[advanced expressions](ch05-zabbix-triggers/advanced-triggers.md){ .index-target }[](ch05-zabbix-triggers/advanced-triggers.md#conclusion){ .index-range-end }
    - <span id="index-triggers-creating"></span>[creating and configuring](ch05-zabbix-triggers/triggers.md){ .index-target }[](ch05-zabbix-triggers/triggers.md#conclusion){ .index-range-end }

## U {#index-letter-u}

- <span id="index-upgrades"></span>**upgrades**
    - [planning and performing](ch14-zabbix-maintenance/upgrades.md){ .index-target }[](ch14-zabbix-maintenance/upgrades.md#conclusion){ .index-range-end }
    - *See also* [backups](#index-backups)
- <span id="index-user-groups"></span>**user groups**
    - [creating and managing](ch02-zabbix-installation/user-groups.md){ .index-target }[](ch02-zabbix-installation/user-groups.md#conclusion){ .index-range-end }
    - *See also* [user roles](#index-user-roles)
- <span id="index-user-macros"></span>**user macros**
    - [using in templates](ch06-zabbix-templates/templates.md){ .index-target }[](ch06-zabbix-templates/templates.md#conclusion){ .index-range-end }
- <span id="index-user-parameters"></span>**user parameters**
    - [creating custom items](ch09-zabbix-extending/user-parameters.md){ .index-target }[](ch09-zabbix-extending/user-parameters.md#conclusion){ .index-range-end }
- <span id="index-user-roles"></span>**user roles**
    - [creating and managing](ch02-zabbix-installation/user-roles.md){ .index-target }[](ch02-zabbix-installation/user-roles.md#conclusion){ .index-range-end }
    - *See also* [user groups](#index-user-groups)

## V {#index-letter-v}

- <span id="index-vault"></span>**Vault**
    - [storing Zabbix secrets](ch13-advanced-security/using-vault.md){ .index-target }[](ch13-advanced-security/using-vault.md#conclusion){ .index-range-end }
- <span id="index-visualisation"></span>**visualisation**
    - <span id="index-visualisation-dashboards"></span>[dashboards](ch11-zabbix-visualisation/dashboards.md){ .index-target }[](ch11-zabbix-visualisation/dashboards.md#conclusion){ .index-range-end }
    - <span id="index-visualisation-graphs"></span>[graphs](ch11-zabbix-visualisation/graphs.md){ .index-target }[](ch11-zabbix-visualisation/graphs.md#conclusion){ .index-range-end }
    - <span id="index-visualisation-maps"></span>[maps](ch11-zabbix-visualisation/maps.md){ .index-target }[](ch11-zabbix-visualisation/maps.md#conclusion){ .index-range-end }

## W {#index-letter-w}

- <span id="index-web-monitoring"></span>**web monitoring**
    - <span id="index-web-monitoring-browser-items"></span>[browser items](ch04-zabbix-collecting-data/browser.md){ .index-target }[](ch04-zabbix-collecting-data/browser.md#conclusion){ .index-range-end }
    - <span id="index-web-monitoring-http-agent-items"></span>[HTTP agent items](ch04-zabbix-collecting-data/http.md){ .index-target }[](ch04-zabbix-collecting-data/http.md#conclusion){ .index-range-end }
- <span id="index-windows-monitoring"></span>**Windows monitoring**
    - <span id="index-windows-monitoring-disk-health"></span>[monitoring disk health](ch15-zabbix-real-world-examples/disk-health-windows.md){ .index-target }
    - <span id="index-windows-monitoring-overview"></span>[monitoring Windows](ch16-windows/windows.md){ .index-target }

## Z {#index-letter-z}

- <span id="index-zabbix-agent"></span>**Zabbix agent**
    - <span id="index-zabbix-agent-active-checks"></span>[active checks](ch04-zabbix-collecting-data/zabbix-agent-active.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-agent-active.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-agent-encryption"></span>[encryption](ch13-advanced-security/agent-security.md){ .index-target }[](ch13-advanced-security/agent-security.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-agent-passive-checks"></span>[passive checks](ch04-zabbix-collecting-data/zabbix-agent-passive.md){ .index-target }[](ch04-zabbix-collecting-data/zabbix-agent-passive.md#conclusion){ .index-range-end }
- <span id="index-zabbix-api"></span>**Zabbix API**
    - [using the API](ch12-zabbix-api/self-engaging.md){ .index-target }
    - *See also* [API tokens](#index-api-tokens)
- <span id="index-zabbix-architecture"></span>**Zabbix architecture**
    - [understanding components and data flow](ch01-zabbix-components/architecture.md){ .index-target }
- <span id="index-zabbix-frontend"></span>**Zabbix frontend**
    - [installing](ch01-zabbix-components/zabbix-frontend.md){ .index-target }[](ch01-zabbix-components/zabbix-frontend.md#conclusion){ .index-range-end }
    - [navigating and configuring](ch02-zabbix-installation/frontend.md){ .index-target }[](ch02-zabbix-installation/frontend.md#conclusion){ .index-range-end }
- <span id="index-zabbix-proxy"></span>**Zabbix proxy**
    - <span id="index-zabbix-proxy-active-and-passive-modes"></span>[active and passive modes](ch03-zabbix-proxies/active-passive-proxies.md){ .index-target }[](ch03-zabbix-proxies/active-passive-proxies.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-proxy-containers"></span>[running as containers](ch03-zabbix-proxies/proxies-as-container.md){ .index-target }[](ch03-zabbix-proxies/proxies-as-container.md#conclusion){ .index-range-end }
    - <span id="index-zabbix-proxy-proxy-groups"></span>[proxy groups](ch03-zabbix-proxies/proxy-groups.md){ .index-target }[](ch03-zabbix-proxies/proxy-groups.md#conclusion){ .index-range-end }
- <span id="index-zabbix-server"></span>**Zabbix server**
    - [installing](ch01-zabbix-components/zabbix-server.md){ .index-target }[](ch01-zabbix-components/zabbix-server.md#conclusion){ .index-range-end }
    - *See also* [high availability](#index-high-availability), [internal health](#index-internal-health)
- <span id="index-zabbix-web-service"></span>**Zabbix web service**
    - [installing and configuring](ch03-zabbix-proxies/web-services.md){ .index-target }[](ch03-zabbix-proxies/web-services.md#conclusion){ .index-range-end }
    - *See also* [automated PDF reports](#index-automated-pdf-reports)

</div>
