# Systeemvereisten

## Vereisten

Zabbix heeft specifieke hardware- en softwarevereisten waaraan voldaan moet
worden, en deze vereisten kunnen na verloop van tijd veranderen. Ze zijn ook
afhankelijk van de grootte van je installatie en de softwarestack die je kiest.
Voordat je hardware aanschaft of een databaseversie installeert, is het
essentieel om de Zabbix documentatie te raadplegen voor de meest recente
vereisten voor de versie die je van plan bent te installeren. Je kunt de meest
recente vereisten vinden
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Zorg ervoor dat je de juiste Zabbix-versie uit de lijst selecteert.

Voor kleinere of testopstellingen kan Zabbix gemakkelijk draaien op een systeem
met 2 CPU's en 8 GB RAM. Echter, de grootte van je setup, het aantal items dat
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

    Zabbix package names often use dashes (`-`) in their names, such as `zabbix-get`
    or `zabbix-sender`, but the binaries themselves may use underscores (`_`),
    like `zabbix_sender` or `zabbix_server`. This naming discrepancy can sometimes
    be confusing, particularly if you are using packages from non-official Zabbix
    repositories.
    Always check if a binary uses a dash or an underscore when troubleshooting.

???+ note

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Basis OS-configuratie

Besturingssystemen, zoveel keuzes, elk met zijn eigen voordelen en trouwe
gebruikers. Hoewel Zabbix op een groot aantal platformen geïnstalleerd kan
worden, zou het onpraktisch zijn om het proces voor elk beschikbaar
besturingssysteem te documenteren. Om dit boek doelgericht en efficiënt te
houden, hebben we ervoor gekozen om alleen de meest gebruikte opties te
behandelen: Ubuntu en Red Hat gebaseerde distributies.

Omdat niet iedereen toegang heeft tot een Red Hat Enterprise Linux (RHEL)
abonnement, ook al biedt een ontwikkelaarsaccount beperkte toegang, hebben we
gekozen voor Rocky Linux als een gemakkelijk beschikbaar alternatief. Voor dit
boek gebruiken we Rocky Linux 9.x en Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://ubuntu.com/>

### Firewall

Voordat je Zabbix installeert, is het essentieel om het besturingssysteem goed
voor te bereiden. De eerste stap is ervoor zorgen dat de firewall is
geïnstalleerd en geconfigureerd.

Voer het volgende commando uit om de firewall te installeren en in te schakelen:

!!! info "Installeer en schakel de firewall in"

    Red Hat
    ```yaml
    dnf install firewalld
    systemctl enable firewalld --now
    ```

    Ubuntu
    ```yaml
    sudo apt install ufw
    sudo ufw enable
    ```

Eenmaal geïnstalleerd, kun je de nodige poorten configureren. Voor Zabbix moeten
we toegang toestaan tot poort `10051/tcp`, waar de Zabbix trapper luistert naar
inkomende gegevens. Gebruik het volgende commando om deze poort te openen in de
firewall:

!!! info "Zabbix trapper toegang verlenen"

    Red Hat
    ```yaml
    firewall-cmd --add-service=zabbix-server --permanent
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    ```

Als de service niet wordt herkend, kun je de poort handmatig opgeven:

!!! info "Voeg poort toe in plaats van de servicenaam"

    ```yaml
    firewall-cmd --add-port=10051/tcp --permanent
    ```

???+ note

    "Firewalld is the replacement for iptables in RHEL-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps."
    Ubuntu makes use of UFW and is merely a frontend for iptables.

Een alternatieve aanpak is om speciale firewallzones te definiëren voor
specifieke gebruikssituaties. Bijvoorbeeld...

!!! info "Creëer een firewalld zone"

    ```yaml
    firewall-cmd --new-zone=postgresql-access --permanent
    ```

Je kunt het aanmaken van de zone bevestigen door het volgende commando uit te
voeren:

!!! info "De aanmaak van de zone verifiëren"

    ```yaml
    firewall-cmd --get-zones
    ```

block dmz drop external home internal nm-shared postgresql-access public trusted
work

Het gebruik van zones in firewalld om firewall regels voor PostgreSQL te
configureren biedt verschillende voordelen op het gebied van beveiliging,
flexibiliteit en beheergemak. Hier lees je waarom zones nuttig zijn:

- **Granulaire toegangscontrole :**
  - firewalld zones staan verschillende vertrouwensniveaus toe voor
    verschillende netwerkinterfaces en IP bereiken. Je kunt definiëren welke
    systemen verbinding mogen maken met PostgreSQL op basis van hun
    vertrouwensniveau.
- **Vereenvoudigd regelbeheer:**
  - In plaats van het handmatig definiëren van complexe iptable regels, bieden
    zones een georganiseerde manier om firewall regels te groeperen en te
    beheren op basis van gebruiksscenario's.
- **Verbeterde beveiliging:**
  - Door PostgreSQL toegang te beperken tot een specifieke zone, voorkom je
    ongeautoriseerde verbindingen vanaf andere interfaces of netwerken.
- **Dynamische configuratie:**
  - firewalld ondersteunt runtime en permanente regelconfiguraties, waardoor
    veranderingen mogelijk zijn zonder bestaande verbindingen te verstoren.
- **Ondersteuning voor meerdere interfaces:**
  - Als de server meerdere netwerkinterfaces heeft, staan zones een verschillend
    beveiligingsbeleid toe voor elke interface.

Alles bij elkaar zou het er als volgt uitzien:

!!! info "Firewall met zoneconfiguratie"

    ```yaml
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Waarbij het `bron IP` het enige adres is dat een verbinding met de database tot
stand mag brengen.

---

### Tijdserver

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
    ```yaml
    dnf install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```yaml
    sudo apt install chrony
    ```

Controleer na de installatie of Chrony is ingeschakeld en draait door de status
te controleren met het volgende commando:

!!! info "Controleer status chronyd"

    ```yaml
    systemctl status chronyd
    ```

???+ note "wat is apt of dnf"

    dnf is a package manager used in Red Hat-based systems. If you're using another
    distribution, replace `dnf` with your appropriate package manager, such as `zypper`,
    `apt`, or `yum`.

???+ note "Wat is Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Zodra Chrony geïnstalleerd is, is de volgende stap ervoor te zorgen dat de
juiste tijdzone ingesteld is. U kan uw huidige tijdsconfiguratie bekijken met
het commando `timedatectl`:

!!! info "controleer de tijdconfiguratie"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 15:09:14 UTC
    Universal time: Thu 2023-11-16 15:09:14 UTC
    RTC time: Thu 2023-11-16 15:09:15
    Time zone: UTC (UTC, +0000)
    System clock synchronized: yes
    NTP service: active
    RTC in local TZ: no
    ```

Zorg ervoor dat de Chrony service actief is (raadpleeg indien nodig de vorige
stappen). Om de juiste tijdzone in te stellen, kunt u eerst alle beschikbare
tijdzones oplijsten met het volgende commando:

!!! info "lijst de tijdzones"

    ```yaml
    timedatectl list-timezones
    ```

Deze opdracht toont een lijst met beschikbare tijdzones, zodat je de tijdzone
kunt selecteren die het dichtst bij je locatie ligt. Bijvoorbeeld:

!!! info "Lijst van alle beschikbare tijdzones"

    ```yaml
    Africa/Abidjan
    Africa/Accra
    ...
    Pacific/Tongatapu
    Pacific/Wake
    Pacific/Wallis
    UTC
    ```

Zodra je je tijdzone hebt geïdentificeerd, configureer je deze met het volgende
commando:

!!! info "Tijdzone instellen"

    ```yaml
    timedatectl set-timezone Europe/Brussels
    ```

Gebruik het commando `timedatectl` opnieuw om te controleren of de tijdzone
juist is ingesteld:

!!! info "Controleer de tijd en zone"

    ```yaml
    timedatectl
    ```

    ``` yaml
    Local time: Thu 2023-11-16 16:13:35 CET
    Universal time: Thu 2023-11-16 15:13:35 UTC
    RTC time: Thu 2023-11-16 15:13:36
    **Time zone: Europe/Brussels (CET, +0100)**
    System clock synchronized: yes
    NTP service: active
    RTC in local TZ: no
    ```

???+ note

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

### Chrony-synchronisatie controleren

Om ervoor te zorgen dat Chrony met de juiste tijdservers synchroniseert, kunt u
het volgende commando uitvoeren:

!!! info "chrony verifiëren"

    ```yaml
    chronyc
    ```

De uitvoer moet lijken op:

!!! Info "Controleer uw chrony uitvoer"

    ```yaml
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Eenmaal in de Chrony prompt, typ het volgende om de bronnen te controleren:

!!! info ""

    ```yaml
    chronyc> sources
    ```

Voorbeelduitvoer:

!!! info "Controleer de bronnen van uw tijdserver"

    ```bash
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

In dit voorbeeld bevinden de gebruikte NTP-servers zich buiten je lokale regio.
Het wordt aanbevolen om over te schakelen naar tijdservers in je eigen land of,
indien beschikbaar, naar een speciale bedrijfstijdserver. U kunt lokale
NTP-servers hier vinden: [www.ntppool.org](https://www.ntppool.org/).

---

### Tijdservers bijwerken

Om de tijdservers bij te werken, wijzig je het bestand `/etc/chrony.conf` voor
Red Hat gebaseerde systemen, en als je Ubuntu gebruikt bewerk je
`/etc/chrony/chrony.conf`. Vervang de bestaande NTP-server door een die dichter
bij je locatie staat.

Voorbeeld van de huidige configuratie:

!!! info "voorbeeld ntp pool configuratie"

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

    Change the pools you want to a local time server:

    ```yaml
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Herstart de Chrony service na deze wijziging om de nieuwe configuratie toe te
passen:

!!! info "De chrony service opnieuw starten"

    ```yaml
    systemctl restart chronyd
    ```

### Bijgewerkte tijdservers controleren

Controleer de tijdbronnen opnieuw om er zeker van te zijn dat de nieuwe lokale
servers in gebruik zijn:

!!! info "Controleer chrony bronnen"

    ```yaml
    chronyc> sources
    ```

Voorbeeld van verwachte uitvoer met lokale servers:

!!! info "Voorbeeld uitvoer"

    ```yaml
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Dit bevestigt dat het systeem nu lokale tijdservers gebruikt.

## Conclusie

Zoals we hebben gezien, moet er, voordat er over de Zabbix pakketten wordt
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
  daadwerkelijke Zabbix installatieproces?
- Als we Zabbix gaan installeren, laten we dan eens nadenken over
  netwerkcommunicatie. Welke belangrijke poorten moet je door de firewall
  toestaan zodat de Zabbix server en agents effectief met elkaar kunnen
  communiceren?

## Nuttige URL's

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
