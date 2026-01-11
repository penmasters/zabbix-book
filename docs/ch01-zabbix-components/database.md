---
description: |
  This section from The Zabbix Book titled "Database choices" helps you select
  the appropriate database backend and packages for your Zabbix installation.
tags: [beginner]
---

# Database choices

## Choosing a Database Backend for Zabbix

A critical decision when managing Zabbix installations is selecting the database
backend. Zabbix supports several database options: MySQL/Percona, MariaDB, 
PostgreSQL (including TimescaleDB), and Oracle (up to Zabbix 7.0).

???+ warning "Oracle Database deprecation"

    Zabbix 7.0 marks the final release to offer support for Oracle Database.
    Consequently, systems running Zabbix 7.0 or any prior version must undertake
    a database migration to either PostgreSQL, MySQL, or a compatible fork such
    as MariaDB before upgrading to a later Zabbix release. This migration is a
    mandatory step to ensure continued functionality and compatibility with future
    Zabbix versions.

All supported databases perform similarly under typical Zabbix workloads, and 
Zabbix treats them equally in terms of functionality. As such, the choice 
primarily depends on your or your team’s familiarity with a particular database system. 
One notable exception is TimescaleDB, a PostgreSQL extension optimized for 
time-series data. This makes it especially well-suited for monitoring applications 
like Zabbix, which handle large volumes of timestamped data.

In large-scale environments with high-frequency data collection, TimescaleDB can
deliver significant performance benefits, including improved query speeds and
built-in compression to reduce storage requirements. However, these advantages
come with added complexity during installation and a few restrictions on historical
data retention.

???+ tip "TimescaleDB installation"

    Given its advanced nature, TimescaleDB is not essential for most Zabbix users.
    As such, its installation is beyond the scope of this chapter. If you plan to
    use TimescaleDB, refer to [Partitioning PostgreSQL with TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md)
    for detailed guidance after installing PostgreSQL.

---

## Choosing the Source for Database Installation

In this chapter we will focus on installing MariaDB and PostgreSQL, as they are
the most commonly used databases with Zabbix. For MySQL or Percona installations,
except for the package installation commands, the steps are very similar to MariaDB.

When installing MariaDB or PostgreSQL you must determine the source 
from which you will want to install the database server. Two primary options are 
available:

1. **Vendor-Provided Packages**

:   These are included in the software repositories of most Linux distributions 
    and are maintained by the distribution vendor.
 
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

2. **Official MariaDB/PostgreSQL Repositories**

:   These repositories provide packages directly from MariaDB/PostgreSQL and offer
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

Before installing the database software, ensure that the server
meets the configuration requirements and is prepared as outlined in the previous 
chapter: [_Getting started_](../ch00-getting-started/Requirements.md).

---

## Conclusion

We have discussed the various database backends supported by Zabbix. We've also
examined the advantages and disadvantages of using vendor-provided packages
versus official repositories for installing MariaDB and PostgreSQL.

Armed with this knowledge, you are now ready to proceed with the installation 
of your chosen database backend. In the following chapters, we will guide you 
through the installation process for MariaDB or PostgreSQL, ensuring that your 
Zabbix instance is equipped with a robust and efficient database system.

Now that you have a clear understanding of the database options available, let's
move on to the installation of your preferred database backend.

---

## Questions

1. Should I choose MySQL or PostgreSQL as the database back-end? Why?
2. Should I use the packages provided by the OS vendor, or should I install
   database-vendor official packages? Why?

---

## Useful URLs

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
