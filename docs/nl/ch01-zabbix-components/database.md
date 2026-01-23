---
description: |
  This section from The Zabbix Book titled "Database choices" helps you select
  the appropriate database backend and packages for your Zabbix installation.
tags: [beginner]
---

# Database keuzes

## Een database-backend kiezen voor Zabbix

Een kritieke beslissing bij het beheren van Zabbix-installaties is het
selecteren van de database backend. Zabbix ondersteunt verschillende database
opties: MySQL/Percona, MariaDB, PostgreSQL (inclusief TimescaleDB) en Oracle
(tot Zabbix 7.0).

???+ warning "Oracle Database deprecatie"

    Zabbix 7.0 marks the final release to offer support for Oracle Database.
    Consequently, systems running Zabbix 7.0 or any prior version must undertake
    a database migration to either PostgreSQL, MySQL, or a compatible fork such
    as MariaDB before upgrading to a later Zabbix release. This migration is a
    mandatory step to ensure continued functionality and compatibility with future
    Zabbix versions.

Alle ondersteunde databases presteren vergelijkbaar onder typische Zabbix
workloads, en Zabbix behandelt ze gelijk in termen van functionaliteit. De keuze
hangt dus vooral af van de bekendheid van jou of je team met een bepaald
databasesysteem. Een opvallende uitzondering is TimescaleDB, een
PostgreSQL-extensie die is geoptimaliseerd voor tijdreeksgegevens. Dit maakt het
bijzonder geschikt voor monitoringtoepassingen zoals Zabbix, die grote
hoeveelheden gegevens met tijdstempels verwerken.

In grootschalige omgevingen met hoogfrequente gegevensverzameling kan
TimescaleDB aanzienlijke prestatievoordelen opleveren, waaronder verbeterde
query-snelheden en ingebouwde compressie om de opslagvereisten te verlagen. Deze
voordelen gaan echter gepaard met extra complexiteit tijdens de installatie en
enkele beperkingen voor het bewaren van historische gegevens.

Tip "TimescaleDB installatie".

    Given its advanced nature, TimescaleDB is not essential for most Zabbix users.
    As such, its installation is beyond the scope of this chapter. If you plan to
    use TimescaleDB, refer to [Partitioning PostgreSQL with TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md)
    for detailed guidance after installing PostgreSQL.

---

## De bron voor de installatie van de database kiezen

In dit hoofdstuk concentreren we ons op de installatie van MariaDB en
PostgreSQL, omdat dit de meest gebruikte databases zijn met Zabbix. Voor MySQL
of Percona installaties, behalve de commando's voor de pakketinstallatie, zijn
de stappen erg gelijkaardig aan die van MariaDB.

Bij de installatie van MariaDB of PostgreSQL moet je bepalen vanaf welke bron je
de databaseserver wilt installeren. Er zijn twee opties beschikbaar:

1. **Door leverancier geleverde pakketten**

: Deze staan in de software repositories van de meeste Linux distributies en
worden onderhouden door de distributieleverancier.

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

2. **Officiële MariaDB/PostgreSQL opslagplaatsen**

: These repositories provide packages directly from MariaDB/PostgreSQL and offer
access to the latest stable releases.

    **Advantages:**

    - **Up-to-date versions:** Immediate access to the latest features, security
      patches, and bug fixes. However, make sure Zabbix is compatible with the
      chosen version.
    - **Enterprise support:** Option to purchase MariaDB Enterprise or Enterprise DB
      respectively, which includes professional support and additional features.

    **Disadvantages:**

    - **Manual version management:** Users must proactively monitor and upgrade 
      to new major versions to ensure continued security and bug fix coverage.

???+ warning "Database version compatibility"

    Whether you plan to use the OS vendor-provided packages or the official 
    database-vendor packages, ensure that the database version is supported
    by your Zabbix version to avoid potential integration issues. 
    Check the [Zabbix documentation](https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software)
    for the latest supported versions.

Before installing the database software, ensure that the server meets the
configuration requirements and is prepared as outlined in the previous chapter:
[_Getting started_](../ch00-getting-started/Requirements.md).

---

## Conclusie

We have discussed the various database backends supported by Zabbix. We've also
examined the advantages and disadvantages of using vendor-provided packages
versus official repositories for installing MariaDB and PostgreSQL.

Armed with this knowledge, you are now ready to proceed with the installation of
your chosen database backend. In the following chapters, we will guide you
through the installation process for MariaDB or PostgreSQL, ensuring that your
Zabbix instance is equipped with a robust and efficient database system.

Now that you have a clear understanding of the database options available, let's
move on to the installation of your preferred database backend.

---

## Vragen

1. Should I choose MySQL or PostgreSQL as the database back-end? Why?
2. Should I use the packages provided by the OS vendor, or should I install
   database-vendor official packages? Why?

---

## Nuttige URL's

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
