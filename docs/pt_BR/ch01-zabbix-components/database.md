---
description: |
  This section from The Zabbix Book titled "Database choices" helps you select
  the appropriate database backend and packages for your Zabbix installation.
tags: [beginner]
---

# Opções de banco de dados

## Escolhendo um back-end de banco de dados para o Zabbix

Uma decisão crítica ao gerenciar as instalações do Zabbix é selecionar o backend
do banco de dados. O Zabbix suporta várias opções de banco de dados:
MySQL/Percona, MariaDB, PostgreSQL (incluindo TimescaleDB) e Oracle (até o
Zabbix 7.0).

Aviso "Oracle Database deprecation" (depreciação do banco de dados Oracle)

    Zabbix 7.0 marks the final release to offer support for Oracle Database.
    Consequently, systems running Zabbix 7.0 or any prior version must undertake
    a database migration to either PostgreSQL, MySQL, or a compatible fork such
    as MariaDB before upgrading to a later Zabbix release. This migration is a
    mandatory step to ensure continued functionality and compatibility with future
    Zabbix versions.

Todos os bancos de dados suportados têm desempenho semelhante em cargas de
trabalho típicas do Zabbix, e o Zabbix os trata da mesma forma em termos de
funcionalidade. Dessa forma, a escolha depende principalmente da sua
familiaridade ou da familiaridade da sua equipe com um sistema de banco de dados
específico. Uma exceção notável é o TimescaleDB, uma extensão do PostgreSQL
otimizada para dados de séries temporais. Isso o torna especialmente adequado
para aplicativos de monitoramento como o Zabbix, que lidam com grandes volumes
de dados com registro de data e hora.

Em ambientes de grande escala com coleta de dados de alta frequência, o
TimescaleDB pode oferecer benefícios significativos de desempenho, incluindo
velocidades de consulta aprimoradas e compactação integrada para reduzir os
requisitos de armazenamento. No entanto, essas vantagens são acompanhadas de
maior complexidade durante a instalação e de algumas restrições à retenção de
dados históricos.

???+ dica "Instalação do TimescaleDB"

    Given its advanced nature, TimescaleDB is not essential for most Zabbix users.
    As such, its installation is beyond the scope of this chapter. If you plan to
    use TimescaleDB, refer to [Partitioning PostgreSQL with TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md)
    for detailed guidance after installing PostgreSQL.

---

## Escolhendo a origem para a instalação do banco de dados

Neste capítulo, vamos nos concentrar na instalação do MariaDB e do PostgreSQL,
pois eles são os bancos de dados mais comumente usados com o Zabbix. Para
instalações do MySQL ou do Percona, com exceção dos comandos de instalação de
pacotes, as etapas são muito semelhantes às do MariaDB.

Ao instalar o MariaDB ou o PostgreSQL, você deve determinar a origem a partir da
qual deseja instalar o servidor de banco de dados. Há duas opções principais
disponíveis:

1. **Pacotes fornecidos pelo fornecedor**

: Estão incluídos nos repositórios de software da maioria das distribuições
Linux e são mantidos pelo fornecedor da distribuição.

    **Advantages:**

    - **Simplified installation:** Packages are readily available via the
      distribution’s package manager.
    - **Vendor support:** For enterprise distributions (e.g., RHEL, SLES),
      active subscriptions include official support.
    - **Compatibility:** Guaranteed integration with other system packages and
      dependencies.
      - **Distribution-specific optimizations:** Includes tailored configurations
        (e.g., logrotate, bash completion,...).
      - **Long-term maintenance:** Security and bug fixes are backported by the
        vendor for the duration of the distribution’s support lifecycle.

    **Disadvantages:**

      - **Version lock-in:** Major distribution upgrades may automatically introduce
        newer database versions, potentially requiring compatibility checks with
        Zabbix.
      - **Vendor modifications:** Default configurations, log directories, and data
        paths may be altered to align with distribution-specific standards.

2. **Repositórios oficiais do MariaDB/PostgreSQL**

: Esses repositórios fornecem pacotes diretamente do MariaDB/PostgreSQL e
oferecem acesso às versões estáveis mais recentes.

    **Advantages:**

    - **Up-to-date versions:** Immediate access to the latest features, security
      patches, and bug fixes. However, make sure Zabbix is compatible with the
      chosen version.
    - **Enterprise support:** Option to purchase MariaDB Enterprise or Enterprise DB
      respectively, which includes professional support and additional features.

    **Disadvantages:**

    - **Manual version management:** Users must proactively monitor and upgrade 
      to new major versions to ensure continued security and bug fix coverage.

???+ aviso "Compatibilidade da versão do banco de dados"

    Whether you plan to use the OS vendor-provided packages or the official 
    database-vendor packages, ensure that the database version is supported
    by your Zabbix version to avoid potential integration issues. 
    Check the [Zabbix documentation](https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software)
    for the latest supported versions.

Antes de instalar o software do banco de dados, certifique-se de que o servidor
atenda aos requisitos de configuração e esteja preparado conforme descrito no
capítulo anterior: [_Getting started_](../ch00-getting-started/Requirements.md).

---

## Conclusão

Discutimos os vários backends de banco de dados suportados pelo Zabbix. Também
examinamos as vantagens e desvantagens de usar pacotes fornecidos pelo
fornecedor em comparação com os repositórios oficiais para instalar o MariaDB e
o PostgreSQL.

Munido desse conhecimento, agora você está pronto para prosseguir com a
instalação do backend do banco de dados escolhido. Nos próximos capítulos, nós o
orientaremos no processo de instalação do MariaDB ou do PostgreSQL, garantindo
que sua instância do Zabbix esteja equipada com um sistema de banco de dados
robusto e eficiente.

Agora que você tem uma compreensão clara das opções de banco de dados
disponíveis, vamos passar à instalação do backend de banco de dados de sua
preferência.

---

## Perguntas

1. Devo escolher MySQL ou PostgreSQL como back-end de banco de dados? Por quê?
2. Devo usar os pacotes fornecidos pelo fornecedor do sistema operacional ou
   devo instalar os pacotes oficiais do fornecedor do banco de dados? Por quê?

---

## URLs úteis

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
