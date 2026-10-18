---
description: |
  Diese Abschnitt aus dem Zabbix-Buch mit dem Titel "Datenbanken wählen" hilft Ihnen, die geeignete Datenbanksystembasis und Pakete für Ihre Zabbix-Installation zu wählen.
tags: [beginner]
---

# Datenbanken wählen

## Auswahl der Datenbanksystembasis für Zabbix

Ein kritischer Entscheid bei der Verwaltung von Zabbix-Installationsumgebungen ist die Wahl der Datenbanksystembasis. Zabbix unterstützt mehrere Datenbankoptionen: MySQL/Percona, MariaDB,
PostgreSQL (einschließlich TimescaleDB) und Oracle (bis zur Zabbix-Version 7.0).

???+ warning "Oracle Database wird abgestellt"

    Mit Zabbix 7.0 markiert die letzte Version, die Unterstützung für Oracle Database anbietet.
    Folglich müssen Systeme, die Zabbix 7.0 oder eine frühere Version ausführen, eine Datenbankmigration auf PostgreSQL, MySQL oder einen kompatiblen Fork wie MariaDB vornehmen, bevor sie zu einer späteren Zabbix-Version aktualisiert werden können. Diese Migration ist ein zwingendes Vorgehen, um eine fortlaufende Funktionalität und Kompatibilität mit zukünftigen Zabbix-Versionen sicherzustellen.

Alle unterstützten Datenbanken leisten unter typischen Zabbix-Belastungen vergleichbare Leistung. Zabbix behandelt sie in Bezug auf Funktionalität gleichwertig. Die Wahl hängt daher vor allem von Ihrer oder der Kenntnis Ihres Teams eines bestimmten Datenbanksystems ab.
Eine bemerkenswerte Ausnahme bildet TimescaleDB, eine PostgreSQL-Erweiterung, die für zeitgesteuerte Daten optimiert ist. Dies macht es besonders gut geeignet für Überwachungsanwendungen wie Zabbix, die große Mengen an datumsbezogenen Daten verarbeiten.

In umfangreichen Umgebungen mit hoher Datensammlungsfrequenz kann TimescaleDB erhebliche Leistungsverbesserungen liefern, einschließlich verbesserten Abfragezeiten und eingebauter Komprimierung zur Reduzierung der Speicheranforderungen. Diese Vorteile kommen jedoch mit zusätzlicher Komplexität bei der Installation und einigen Einschränkungen für die Aufbewahrung historischer Daten.

???+ tip "TimescaleDB-Installation"

    Aufgrund seiner fortschrittlichen Natur ist TimescaleDB nicht unbedingt für die meisten Zabbix-Nutzer essentiell.
    Daher liegt seine Installation außerhalb des Rahmens dieses Kapitels. Wenn Sie TimescaleDB verwenden möchten, beziehen Sie sich auf [Partitioning PostgreSQL with TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md) nach der Installation von PostgreSQL für detaillierte Anweisungen.

---

## Auswahl der Quelle zur Datenbankinstallation

In diesem Kapitel konzentrieren wir uns auf die Installation von MariaDB und PostgreSQL, da diese die am häufigsten verwendeten Datenbanksysteme mit Zabbix sind. Für MySQL- oder Percona-Installationen unterscheiden sich die Schritte abgesehen von den Paketinstallationsbefehlen sehr ähnlich denen für MariaDB.

Beim Installieren von MariaDB oder PostgreSQL müssen Sie die Quelle bestimmen, aus der Sie die Datenbankserver installieren möchten. Es gibt zwei primäre Optionen:

1. **Vereins-Providerte Pakete**

:   Diese sind in den Softwaredepots der meisten Linux-Distributionen enthalten und werden vom Distributionsherausgeber gepflegt.

    **Vorteile:**

    - **Einfache Installation:** Pakete sind über das Verwaltungstool des Betriebssystems zugänglich.
    - **Unterstützung durch den Anbieter:** Für Unternehmensdistributions (z.B. RHEL, SLES) umfasst ein aktives Abonnement offizielle Unterstützung.
    - **Kompatibilität:** Gewährleistete Integration mit anderen Systempaketen und Abhängigkeiten.
      - **Distributionsspezifische Optimierungen:** Eingeschränkte Konfigurationen (z.B. Logrotate, Bash-Completion,...).
      - **Langfristige Wartung:** Sicherheits- und Fehlerbehebepatches werden vom Anbieter für den gesamten Lebenszyklus der Distribution zurückportiert.

    **Nachteile:**

      - **Versionen sind gebunden:** Große Distributionsaktualisierungen können neue Datenbankversionen automatisch einführen, was möglicherweise Kompatibilitätstests mit Zabbix erfordert.
      - **Anbietermodifikationen:** Standardkonfigurationen, Log-Verzeichnisse und Dateneingaben werden angepasst, um den Distributionsspezifischen Standards zu entsprechen.

2. **Offizielle MariaDB/PostgreSQL-Repositorien**

:   Diese Repositories bieten Pakete direkt von MariaDB/PostgreSQL an und ermöglichen Zugriff auf die neuesten stabilen Versionen.

    **Vorteile:**

    - **Aktuelle Versionen:** Sofortiger Zugang zu den neuesten Funktionen, Sicherheitspatches und Fehlerbehebungen. Stellen Sie sicher, dass Zabbix mit der gewählten Version kompatibel ist.
    - **Unternehmensunterstützung:** Option zur Erwerbung von MariaDB Enterprise oder Enterprise DB, die offizielle Unterstützung und zusätzliche Funktionen umfasst.

    **Nachteile:**

    - **Manuelle Versionsverwaltung:** Benutzer müssen proaktiv auf neue Hauptversionen aktualisieren, um fortlaufende Sicherheits- und Fehlerbehebepatches zu gewährleisten.

???+ warning "Datenbankversionskompatibilität"

    Unabhängig davon, ob Sie die von der OS-Anbieter bereitgestellten Pakete oder offizielle Datenbanksystemanbieter-Pakete verwenden möchten, stellen Sie sicher, dass die Datenbankversion von Ihrer Zabbix-Version unterstützt wird, um potenzielle Integrationsprobleme zu vermeiden.
    Überprüfen Sie [https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software](https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software)
    für die neuesten unterstützten Versionen.

Bevor Sie das Datenbanksystemsoftware installieren, stellen Sie sicher, dass der Server den Konfigurationsanforderungen entspricht und wie im vorherigen Kapitel [_Getting started_](../ch00-getting-started/Requirements.md) vorbereitet ist.

---

## Schlussfolgerung

Wir haben die verschiedenen Datenbanksystembasen diskutiert, die von Zabbix unterstützt werden. Wir haben auch die Vorteile und Nachteile der Verwendung von Vereins-Providerten Paketen im Vergleich zu offiziellen Repositories für die Installation von MariaDB und PostgreSQL untersucht.

Mit diesem Wissen sind Sie nun bereit, mit der Installation Ihrer gewählten Datenbanksystembasis fortzufahren. In den folgenden Kapiteln werden wir Ihnen durch den Installationsprozess für MariaDB oder PostgreSQL führen, um sicherzustellen, dass Ihre Zabbix-Instanz mit einem robusten und effizienten Datenbanksystem ausgestattet ist.

Nun haben Sie einen klaren Überblick über die verfügbaren Datenbankoptionen. Lassen Sie uns fortfahren zur Installation Ihrer bevorzugten Datenbanksystembasis.

---

## Fragen

1. Sollte ich MySQL oder PostgreSQL als Datenbanksystembasis wählen? Warum?
2. Sollte ich die von der OS-Anbieter bereitgestellten Pakete verwenden, oder sollte ich offizielle Datenbankanbieter-Pakete installieren? Warum?

---

## Nützliche URLs

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)