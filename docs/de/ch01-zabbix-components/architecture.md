---
description: |
    Diese Abschnitt aus dem Buch "The Zabbix Book" mit dem Titel "Zabbix-Architektur"
    erklärt die modulare Struktur einer Zabbix-Einrichtung. Es hebt die Rollen jedes
    Komponenten und ihre Abhängigkeiten hervor, während es eine Einführung in den
    Ablauf der Installation der Komponenten im nächsten Abschnitt bietet.
tags: [beginner]
---

# Zabbix-Architektur

In diesem Kapitel gehen wir durch den Prozess des Installierens des Zabbix-Servers.
Es gibt viele verschiedene Möglichkeiten, einen Zabbix-Server einzurichten. Wir werden
die am häufigsten verwendeten Einrichtungen mit MariaDB und PostgreSQL auf RHEL- und SLES-basierten
Distributionen sowie Ubuntu abdecken.

Bevor Sie die Installation beginnen, ist es wichtig, die Architektur von Zabbix zu verstehen.
Der Zabbix-Server ist in modularem Aufbau strukturiert und besteht aus drei Hauptkomponenten,
die wir im Detail besprechen werden.

- Der Zabbix-Server
- Der Zabbix-Webserver
- Die Zabbix-Datenbank

!!! abstract "Erstellung von DB-Benutzern"

    In unserer Einrichtung werden wir 2 DB-Benutzer `zabbix-web` und `zabbix-srv` erstellen.
    Der zabbix-web-Benutzer wird für die Frontend-Verbindung zu unserer Zabbix-Datenbank verwendet.
    Der zabbix-srv-Benutzer wird von unserem Zabbix-Server zur Datenbankverbindung genutzt.
    Dies ermöglicht es uns, die Berechtigungen für jeden Benutzer auf das zu beschränken,
    was strikt erforderlich ist.


![Übersicht](ch01.1-basic-installation-zabbixserver.png){ align=left }

_1.1 Zabbix-Basiseinrichtung
geteilt_

Alle diese Komponenten können entweder auf einem einzelnen Server installiert werden oder über drei separate Server verteilt.
Der Kern des Systems ist der Zabbix-Server, oft als "Hirn" bezeichnet. Diese Komponente ist für die Verarbeitung von Triggerberechnungen und das Senden von Warnungen verantwortlich. Die Datenbank dient als Speicherort für die Konfiguration des Zabbix-Servers und alle gesammelten Daten. Der Webserver bietet die Benutzeroberfläche (Frontend) zur Interaktion mit dem System. Es ist wichtig zu beachten, dass der Zabbix-API Teil der Frontend-Komponente ist, nicht des Zabbix-Servers selbst.

Diese Komponenten müssen zusammenfließen, wie im obigen Diagramm dargestellt. Der Zabbix-Server muss Konfigurationen lesen und Monitoring-Daten in die Datenbank speichern, während das Frontend Zugriff auf Lesen und Schreiben von Konfigurationsdaten benötigt. Darüber hinaus muss das Frontend in der Lage sein, den Status des Zabbix-Servers zu überprüfen und zusätzliche notwendige Informationen abzurufen, um einen reibungslosen Betrieb sicherzustellen.

Für unsere Einrichtung werden wir zwei virtuelle Maschinen (VMs) verwenden: eine VM wird sowohl den Zabbix-Server als auch das Zabbix-Web-Frontend hosten, während die zweite VM die Zabbix-Datenbank hostet.

???+ note

    Es ist vollkommen möglich, alle Komponenten auf einer einzelnen VM oder jede Komponente auf einer separaten VM zu installieren.
    Der Grund, warum wir in unserem Beispiel die Datenbank trennen, liegt darin, dass die Datenbank wahrscheinlich der erste Bestandteil sein wird,
    der Ihnen Leistungsprobleme bereitet. Es ist auch die Komponente, die bei der Trennung von den anderen Komponenten etwas mehr Aufmerksamkeit erfordert.
    Deshalb haben wir in diesem Beispiel entschieden, die Datenbank vom Rest der Einrichtung zu trennen.

Wir werden folgende Themen abdecken:

- Installation unserer Datenbank basierend auf MariaDB.
- Installation unserer Datenbank basierend auf PostgreSQL.
- Installieren des Zabbix-Servers.
- Installieren des Frontends.