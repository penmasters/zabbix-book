---
description: |
    Lees meer over de systeemvereisten van Zabbix: ondersteunde OS, database-opties, 
    hardwarespecificaties, firewallpoorten en tijdsynchronisatie die nodig zijn voor
    een soepele installatie.
tags: [beginner]
---

# Systeemvereisten

## Vereisten

Zabbix heeft specifieke hardware- en softwarevereisten waaraan voldaan moet
worden, en deze vereisten kunnen na verloop van tijd veranderen. Ze zijn ook
afhankelijk van de grootte van je installatie en de softwarestack die je kiest.
Voordat je hardware aanschaft of een databaseversie installeert, is het
essentieel om de Zabbix-documentatie te raadplegen voor de meest recente
vereisten voor de versie die je van plan bent te installeren. Je kunt de meest
recente vereisten vinden
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Zorg ervoor dat je de juiste Zabbix-versie uit de lijst selecteert.

Voor kleinere of testopstellingen kan Zabbix gemakkelijk draaien op een systeem
met 2 CPU-cores en 8 GB RAM. Echter, de grootte van je setup, het aantal items dat
je monitort, de triggers die je aanmaakt en hoe lang je van plan bent gegevens
te bewaren, zullen invloed hebben op de benodigde bronnen. In de
gevirtualiseerde omgevingen van vandaag is mijn advies om klein te beginnen en
zo nodig op te schalen.

Je kunt alle componenten (Zabbix server, database, webserver) op één machine
installeren of verdelen over meerdere servers. Noteer voor de eenvoud de
servergegevens:

| Component      | IP-adres |
| -------------- | -------- |
| Zabbix server  |          |
| Databaseserver |          |
| Webserver      |          |

???+ tip

    Zabbix-pakketnamen bevatten vaak koppeltekens (`-`), zoals `zabbix-get`
    of `zabbix-sender`, terwijl de uitvoerbare bestanden underscores (`_`) kunnen
    gebruiken, zoals `zabbix_sender` of `zabbix_server`. Dit verschil kan verwarrend
    zijn, vooral wanneer je pakketten uit niet-officiële Zabbix-repositories gebruikt.

    Controleer bij troubleshooting altijd of de naam van het uitvoerbare bestand
    een koppelteken of een underscore bevat.

???+ warning

    Vanaf Zabbix 7.2 worden alleen MySQL (inclusief forks) en PostgreSQL
    ondersteund als backend-databases. Eerdere Zabbix-versies ondersteunden ook
    Oracle Database. Die ondersteuning is stopgezet na Zabbix 7.0 LTS,
    de laatste LTS-versie met officiële ondersteuning voor Oracle DB.

---

## Basisconfiguratie van het OS

Besturingssystemen, zoveel keuzes, elk met zijn eigen voordelen en trouwe
gebruikers. Hoewel Zabbix op een groot aantal platformen geïnstalleerd kan
worden, zou het onpraktisch zijn om het proces voor elk beschikbaar
besturingssysteem te documenteren. Om dit boek doelgericht en efficiënt te
houden, hebben we ervoor gekozen om alleen de meest gebruikte opties te
behandelen: Ubuntu en Red Hat gebaseerde distributies.

Omdat niet iedereen toegang heeft tot een Red Hat Enterprise Linux (RHEL) of een
SUSE Linux Enterprise Server (SLES) abonnement, ook al biedt een
ontwikkelaarsaccount beperkte toegang, hebben we gekozen voor Rocky Linux
respectievelijk openSUSE Leap als een gemakkelijk beschikbaar alternatief. Voor
dit boek gebruiken we Rocky Linux 9.x, openSUSE Leap 16 en Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ note

    De installatie van het besturingssysteem valt buiten het bereik van dit boek.
    Een standaardinstallatie of zelfs een minimale installatie van je gekozen OS
    volstaat. Installeer bij voorkeur geen grafische gebruikersinterface (GUI)
    of desktopomgeving: die is voor servers niet nodig en verbruikt extra resources.

Zodra je het OS van je voorkeur hebt geïnstalleerd, zijn er een paar essentiële
configuraties die je moet uitvoeren voordat je verder gaat met de installatie
van Zabbix. Voer de volgende stappen uit op **alle** servers die Zabbix
componenten zullen hosten (d.w.z., Zabbix server, database server en webserver).

---

### Het systeem bijwerken

Voordat je de Zabbix-componenten of andere nieuwe software installeert, is het
verstandig om ervoor te zorgen dat je besturingssysteem up-to-date is met de
laatste patches en beveiligingsfixes. Dit zal helpen om de stabiliteit van het
systeem en de compatibiliteit met de software die je gaat installeren te
behouden. Zelfs als je OS-installatie recent is, is het nog steeds aan te raden
om een update uit te voeren om er zeker van te zijn dat je de nieuwste pakketten
hebt.

Om je systeem bij te werken, voer je de volgende opdracht uit op basis van je
OS:

!!! info "Werk je systeem bij"

    Red Hat
    ```bash
    dnf update
    ```

    SUSE
    ```bash
    zypper refresh
    zypper update
    ```

    Ubuntu
    ```bash
    sudo apt update
    sudo apt upgrade
    ```
???+ note "Wat is apt, dnf of zypper?"

    - DNF (Dandified YUM) is een package manager voor recente Red Hat-gebaseerde systemen (commando `dnf`).
    - ZYpp (Zen / YaST Packages Patches Patterns Products) is de package manager
    voor SUSE-gebaseerde systemen (commando `zypper`).
    - APT (Advanced Package Tool) is de package manager voor Debian- en Ubuntu-gebaseerde systemen (commando `apt`).

    Gebruik je een andere distributie, vervang `dnf`/`zypper`/`apt` dan door de
    bijbehorende package manager, zoals `yum`, `pacman`, `emerge` of `apk`.

    Houd er rekening mee dat pakketnamen per distributie kunnen verschillen.

???+ tip

    Regelmatige systeemupdates zijn belangrijk voor de beveiliging en prestaties.
    Overweeg automatische updates of plan vaste onderhoudsvensters om je systemen
    up-to-date te houden.

---

### Sudo

Standaard draaien de Zabbix processen zoals de Zabbix server en agent onder hun
eigen ongeprivilegieerde gebruikersaccounts (bijvoorbeeld `zabbix`). Er zijn
echter scenario's waarbij verhoogde rechten nodig zijn, zoals het uitvoeren van
aangepaste scripts of commando's waarvoor root-toegang nodig is. Ook zullen we
door dit boek heen bepaalde administratieve taken uitvoeren waarvoor `sudo` op
het systeem nodig is.

Meestal is `sudo` al aanwezig op de meeste systemen, maar wanneer je een
minimale installatie van je OS hebt uitgevoerd, kan het ontbreken. Daarom moeten
we ervoor zorgen dat het geïnstalleerd is.

Dit zal de Zabbix-gebruiker ook toelaten om specifieke geconfigureerde
commando's uit te voeren met verhoogde rechten zonder volledig te moeten
overschakelen naar de root-gebruiker.

!!! info "Wat is sudo?"

    `sudo` (afkorting van "superuser do") is een command-line tool waarmee
    bevoegde gebruikers commando's kunnen uitvoeren met de rechten van een andere
    gebruiker, meestal de superuser (`root`). Op Unix-achtige systemen wordt
    `sudo` vaak gebruikt om beheertaken uit te voeren zonder als `root` in te loggen.

Om `sudo` te installeren, voer het volgende commando uit op basis van je OS:

!!! info "sudo installeren"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    Op Ubuntu is `sudo` normaal gesproken standaard geïnstalleerd. De gebruiker
    die tijdens de installatie wordt aangemaakt, beheert root-toegang via `sudo`.

Als `sudo` al geïnstalleerd is, zullen deze commando's je informeren dat de
laatste versie al aanwezig is en dat er geen verdere actie nodig is. Zo niet,
dan zal de pakketbeheerder doorgaan met de installatie.

---

### Firewall

Vervolgens moeten we ervoor zorgen dat de firewall geïnstalleerd en
geconfigureerd is. Een firewall is een cruciaal beveiligingsonderdeel dat helpt
om je server te beschermen tegen ongeautoriseerde toegang en potentiële
bedreigingen door inkomend en uitgaand netwerkverkeer te controleren op basis
van vooraf bepaalde beveiligingsregels.

Voer het volgende commando uit om de firewall te installeren en in te schakelen:

!!! info "Installeer en schakel de firewall in"

    Red Hat
    ```bash
    dnf install firewalld
    systemctl enable firewalld --now
    ```
    SUSE
    ```bash
    zypper install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```bash
    sudo apt install ufw
    sudo ufw enable
    ```
???+ note "Wat is firewalld / ufw?"

    Firewalld wordt op RHEL- en SUSE-gebaseerde systemen gebruikt voor het beheren
    van firewallregels en laat wijzigingen direct ingaan zonder de service opnieuw
    te starten. Als je distributie geen [https://www.firewalld.org](https://www.firewalld.org)
    gebruikt, raadpleeg dan de documentatie van je OS. Ubuntu gebruikt UFW,
    een gebruiksvriendelijke interface voor firewallbeheer.

Tijdens de Zabbix-installatie in de volgende hoofdstukken moeten we specifieke
poorten openen in de firewall om communicatie tussen Zabbix-componenten mogelijk
te maken.

In plaats van alleen poorten te openen, zoals we in de volgende hoofdstukken
zullen doen, kun je er ook voor kiezen om speciale firewall zones te definiëren
voor specifieke gebruikssituaties. Deze aanpak verbetert de beveiliging door
diensten te isoleren en toegang te beperken op basis van vertrouwensniveaus.
Bijvoorbeeld...

!!! example "Maak een firewalld zone voor databasetoegang"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Je kunt het aanmaken van de zone bevestigen door het volgende commando uit te
voeren:

!!! example "Het aanmaken van de zone verifiëren"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

Het gebruik van zones in firewalld om firewallregels te configureren biedt
verschillende voordelen op het gebied van veiligheid, flexibiliteit en
beheergemak. Hier wordt uitgelegd waarom zones nuttig zijn:

- **Granulaire toegangscontrole:**

  firewalld-zones staan verschillende vertrouwensniveaus toe voor verschillende
netwerkinterfaces en IP-bereiken. Je kunt definiëren welke systemen verbinding
mogen maken met PostgreSQL op basis van hun vertrouwensniveau.

- **Vereenvoudigd regelbeheer:**

  In plaats van het handmatig definiëren van complexe iptables-regels, bieden
zones een georganiseerde manier om firewallregels te groeperen en te beheren op
basis van gebruiksscenario's.

- **Verbeterde beveiliging:**

  Door de toegang tot applicaties te beperken tot een specifieke zone, voorkom
je ongeoorloofde verbindingen vanaf andere interfaces of netwerken.

- **Dynamische configuratie:**

  Firewalld ondersteunt runtime en permanente regelconfiguraties, waardoor
veranderingen mogelijk zijn zonder bestaande verbindingen te verstoren.

- **Ondersteuning voor meerdere interfaces:**

  Als de server meerdere netwerkinterfaces heeft, staan zones een verschillend
beveiligingsbeleid toe voor elke interface.

Om alles samen te voegen en een zone toe te voegen voor, in dit voorbeeld,
PostgreSQL zou het er als volgt uitzien:

!!! example "Firewalld met zoneconfiguratie voor PostgreSQL databasetoegang"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Waarbij het `bron-IP-adres` het enige adres is dat een verbinding met de database tot
stand mag brengen.

Als je zones wilt gebruiken wanneer je firewalld gebruikt, zorg er dan voor dat
je de instructies in de volgende hoofdstukken dienovereenkomstig aanpast.

---

### Tijdsynchronisatie

Een andere cruciale stap is het configureren van de tijdserver en het
synchroniseren van de Zabbix server met behulp van een NTP client. Nauwkeurige
tijdsynchronisatie is van vitaal belang voor Zabbix, zowel voor de server als
voor de apparaten die het bewaakt. Als een van de hosts een onjuiste tijdzone
heeft, kan dat tot verwarring leiden, zoals het onderzoeken van een probleem in
Zabbix dat uren eerder lijkt te zijn gebeurd dan in werkelijkheid het geval was.

Gebruik het volgende commando om chrony, onze NTP-cliënt, te installeren en in
te schakelen:

!!! info "NTP-cliënt installeren"

    Red Hat
    ```bash
    dnf install chrony
    systemctl enable chronyd --now
    ```

    SUSE
    ```bash
    zypper install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```bash
    sudo apt install chrony
    ```

Controleer na de installatie of Chrony is ingeschakeld en draait door de status
te controleren met het volgende commando:

!!! info "Controleer status chronyd"

    ```bash
    systemctl status chronyd
    ```

???+ note "Wat is Chrony?"

    Chrony is een modern alternatief voor `ntpd` en biedt snelle en nauwkeurige
    tijdsynchronisatie. Ondersteunt je OS [https://chrony-project.org/](https://chrony-project.org/)
    niet, overweeg dan `ntpd`.

Zodra Chrony geïnstalleerd is, is de volgende stap ervoor te zorgen dat de
juiste tijdzone ingesteld is. Je kunt je huidige tijdsconfiguratie bekijken met
het commando `timedatectl`:

!!! example "Controleer de tijdconfiguratie"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 15:09:14 UTC
               Universal time: Thu 2023-11-16 15:09:14 UTC
                     RTC time: Thu 2023-11-16 15:09:15
                    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

Zorg ervoor dat de Chrony-service actief is (raadpleeg indien nodig de vorige
stappen). Om de juiste tijdzone in te stellen, kun je eerst alle beschikbare
tijdzones oplijsten met het volgende commando:

!!! info "Beschikbare tijdzones weergeven"

    ```bash
    timedatectl list-timezones
    ```

Deze opdracht toont een lijst met beschikbare tijdzones, zodat je de tijdzone
kunt selecteren die het dichtst bij je locatie ligt. Bijvoorbeeld:

!!! example "Lijst van alle beschikbare tijdzones"

    ```shell-session
    localhost:~ # timedatectl list-timezones
    Africa/Abidjan
    Africa/Accra
    ...
    Pacific/Tongatapu
    Pacific/Wake
    Pacific/Wallis
    UTC
    ```

Zodra je de tijdzone hebt geïdentificeerd, kun je deze configureren met het
volgende commando:

!!! info "Tijdzone instellen"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Gebruik het commando `timedatectl` opnieuw om te controleren of de tijdzone
juist is ingesteld:

!!! example "Controleer de tijd en zone"

    ```shell-session
    localhost:~ # timedatectl
                   Local time: Thu 2023-11-16 16:13:35 CET
               Universal time: Thu 2023-11-16 15:13:35 UTC
                     RTC time: Thu 2023-11-16 15:13:36
                    Time zone: Europe/Brussels (CET, +0100)
    System clock synchronized: yes
                  NTP service: active
              RTC in local TZ: no
    ```

???+ note

    Sommige beheerders gebruiken op alle servers de tijdzone UTC, zodat logs
    in omgevingen met meerdere locaties eenvoudig te vergelijken zijn.
    Zabbix ondersteunt tijdzone-instellingen per gebruiker. Daardoor kan de
    server op UTC blijven staan, terwijl gebruikers hun eigen tijdzone
    instellen via de interface.

---

#### Chrony-synchronisatie controleren

Om ervoor te zorgen dat Chrony met de juiste tijdservers synchroniseert, kun je
het volgende commando uitvoeren:

!!! info "Chrony controleren"

    ```bash
    chronyc
    ```

De uitvoer moet lijken op:

!!! example "Controleer je Chrony-uitvoer"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Typ op de Chrony prompt de opdracht `sources` om de gebruikte tijdbronnen te
controleren:

Voorbeelduitvoer:

!!! example "Controleer je tijdserver bronnen"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In dit voorbeeld bevinden de gebruikte NTP-servers zich buiten je lokale regio.
Het wordt aanbevolen om over te schakelen naar tijdservers in je eigen land of,
indien beschikbaar, naar een speciale bedrijfstijdserver. Je kunt lokale
NTP-servers hier vinden: [https://www.ntppool.org/](https://www.ntppool.org/).

---

#### Tijdsynchronisaties bijwerken

Wijzig het Chrony-configuratiebestand om de tijdservers bij te werken:

!!! info "Chrony-configuratiebestand bewerken"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    Op SUSE staat de poolconfiguratie in een apart bestand. Je kunt dit
    rechtstreeks bewerken of een nieuw configuratiebestand in dezelfde directory
    toevoegen. Schakel in dat laatste geval de bestaande poolconfiguratie uit
    of verwijder die om conflicten te voorkomen.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Vervang de bestaande NTP-serverpool door eentje die dichter bij jouw locatie
ligt.

Voorbeeld van de huidige configuratie:

!!! example "Voorbeeld van een NTP-poolconfiguratie"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Wijzig de gewenste pools naar een lokale tijdserver:

!!! info "NTP-poolconfiguratie wijzigen"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Herstart de Chrony-service na deze wijziging om de nieuwe configuratie toe te
passen:

!!! info "De chrony service opnieuw starten"

    ```bash
    systemctl restart chronyd
    ```

#### Bijgewerkte tijdservers controleren

Controleer de tijdbronnen opnieuw om er zeker van te zijn dat de nieuwe lokale
servers in gebruik zijn:

!!! info "Chrony-bronnen controleren"

    ```
    chronyc> sources
    ```

Voorbeeld van verwachte uitvoer met lokale servers:

!!! example "Voorbeeld uitvoer"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Dit bevestigt dat het systeem nu lokale tijdservers gebruikt.

## Conclusie

Zoals we gezien hebben, moet er, voordat er over de Zabbix-pakketten wordt
nagedacht, aandacht worden besteed aan de omgeving waarin het zich zal bevinden.
Een goed geconfigureerd besturingssysteem, een open pad door de firewall en
nauwkeurige tijdregistratie zijn niet slechts suggesties, maar essentiële
bouwstenen. Nu we deze basis gelegd hebben, kunnen we met vertrouwen verder gaan
met de installatie van Zabbix, wetende dat het onderliggende systeem voorbereid
is op de taak.

## Vragen

- Waarom denk je dat nauwkeurige tijdsynchronisatie zo cruciaal is voor een
  monitoringsysteem als Zabbix?
- Nu de basis is gelegd, wat is volgens jullie de eerste stap in het
  daadwerkelijke Zabbix-installatieproces?
- Als we Zabbix gaan installeren, laten we dan eens nadenken over
  netwerkcommunicatie. Welke belangrijke poorten moet je door de firewall
  toestaan zodat de Zabbix server en agents effectief met elkaar kunnen
  communiceren?

## Nuttige URL's

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
