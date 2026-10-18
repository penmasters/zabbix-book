# Komponenten von Zabbix, grundlegende Funktionen und Installation

In diesem Kapitel erweitern wir das fundierte Wissen aus dem Abschnitt "Erste Schritte",
um eine umfassende Anleitung für Einsteiger anzubieten, die Zabbix zum ersten Mal installieren,
und für fortgeschrittene Benutzer, die ihre Konfiguration optimieren möchten.
Wir werden nicht nur die wesentlichen Schritte für eine grundlegende Installation abdecken,
sondern auch in die feineren Details der Zabbix-Architektur, Komponenten und Best Practices eintauchen.

Wir beginnen damit, den Installationsprozess durchzugehen, um sicherzustellen, dass Sie
eine solide Grundlage haben, auf die Sie aufbauen können. Von dort aus werden wir uns den Kernkomponenten von Zabbix zuwenden,
was jede einzelne tut, wie sie miteinander interagieren und warum sie für Ihre Überwachungslösung entscheidend sind.
Sie werden über Unterprozesse, ihre Rollen und wie diese zur Effizienz und Zuverlässigkeit von Zabbix beitragen lernen.

Darüber hinaus werden wir gute architektonische Entscheidungen erforschen, die Ihren Überwachungssetup beeinflussen können.
Ob Sie ein kleines Netzwerk oder eine groß angelegte Infrastruktur verwalten, frühzeitig richtige Designentscheidungen treffen
zahlt sich in Skalierbarkeit, Leistung und Wartung aus.

Dieses Kapitel ist darauf ausgelegt, Lesern mit unterschiedlichem Hintergrund zu dienen.
Wenn Sie einfach nur Zabbix installieren möchten, finden Sie hier klare, schrittweise Anweisungen. Für diejenigen,
die tiefer gehen wollen, bieten wir detaillierte Einblicke in das Funktionieren von Zabbix im Inneren an,
um Ihnen dabei zu helfen, fundierte Entscheidungen zu treffen, die Ihren Bedürfnissen und zukünftigen Wachstumsplänen entsprechen.

Am Ende dieses Kapitels werden Sie nicht nur eine funktionierende Zabbix-Installation haben,
sondern auch ein umfassendes Verständnis seiner Komponenten und Architektur, was Ihnen ermöglicht,
Zabbix in vollem Umfang zu nutzen, unabhängig von der Komplexität Ihrer Umgebung.

Lassen Sie uns auf diese detaillierte Reise in Zabbix gehen und uns mit dem Wissen ausstatten,
um sowohl eine leistungsstarke Überwachungslösung einzurichten als auch zu optimieren.

???+ note

    "Ab Version 7.0 hat Zabbix seine Lizenzierung von GPLv2 auf AGPLv3 umgestellt.
    Dies ist ein wichtiger Wechsel, den Benutzern und Beitragenden im Gedächtnis behalten sollten. Die Umstellung
    auf die AGPLv3 ist darauf ausgelegt, das 'Cloud-Loch' zu schließen, sodass jede Einrichtung,
    die Zabbix als gehostete Dienstleistung anbietet, ihre Änderungen der Gemeinschaft zurücksenden muss.
    Während dies die Integrität des Projekts schützt und eine langfristige Nachhaltigkeit sicherstellt,
    ist es eine Veränderung, die Organisationen überprüfen sollten, um eine Einhaltung ihrer internen
    Open-Source-Politiken zu gewährleisten."