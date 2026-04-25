---
description: |
    Learn Zabbix system requirements: supported OS, database options, hardware
    specs, firewall ports, and time sync needed for a smooth installation.
tags: [beginner]
---

# Requisitos de sistema

## Requisitos

O Zabbix tem requisitos específicos de hardware e software que devem ser
atendidos, e esses requisitos podem mudar com o tempo. Eles também dependem do
tamanho de sua configuração e da pilha de software que você selecionar. Antes de
comprar hardware ou instalar uma versão de banco de dados, é essencial consultar
a documentação do Zabbix para obter os requisitos mais atualizados para a versão
que você planeja instalar. Você pode encontrar os requisitos mais recentes
[https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements).
Certifique-se de selecionar a versão correta do Zabbix na lista.

Para configurações menores ou de teste, o Zabbix pode ser executado
confortavelmente em um sistema com 2 CPUs e 8 GB de RAM. No entanto, o tamanho
da sua configuração, o número de itens que você monitora, os acionadores que
cria e o tempo que planeja reter os dados afetarão os requisitos de recursos.
Nos ambientes virtualizados de hoje, minha recomendação é começar com pouco e
aumentar a escala conforme necessário.

Você pode instalar todos os componentes (servidor Zabbix, banco de dados,
servidor Web) em uma única máquina ou distribuí-los em vários servidores. Para
simplificar, anote os detalhes do servidor:

| Componente                 | Endereço IP |
| -------------------------- | ----------- |
| Servidor Zabbix            |             |
| Servidor de banco de dados |             |
| Servidor Web               |             |

???+ dica

    Zabbix package names often use dashes (`-`) in their names, such as `zabbix-get`
    or `zabbix-sender`, but the binaries themselves may use underscores (`_`),
    like `zabbix_sender` or `zabbix_server`. This naming discrepancy can sometimes
    be confusing, particularly if you are using packages from non-official Zabbix
    repositories.

    Always check if a binary uses a dash or an underscore when troubleshooting.

???+ aviso

    Starting from Zabbix 7.2, only MySQL (including its forks) and PostgreSQL are
    supported as back-end databases. Earlier versions of Zabbix also included support
    for Oracle Database; however, this support was discontinued with Zabbix 7.0 LTS,
    making it the last LTS version to officially support Oracle DB.

---

## Configuração básica do sistema operacional

Sistemas operacionais, tantas opções, cada uma com suas próprias vantagens e
base de usuários fiéis. Embora o Zabbix possa ser instalado em uma ampla gama de
plataformas, documentar o processo para cada sistema operacional disponível
seria impraticável. Para manter este livro focado e eficiente, optamos por
abordar apenas as opções mais usadas: As distribuições baseadas no Ubuntu e no
Red Hat.

Como nem todo mundo tem acesso a uma assinatura do Red Hat Enterprise Linux
(RHEL) ou do SUSE Linux Enterprise Server (SLES), mesmo que uma conta de
desenvolvedor forneça acesso limitado, optamos pelo Rocky Linux ou pelo openSUSE
Leap como uma alternativa prontamente disponível. Para este livro, usaremos o
Rocky Linux 9.x, o openSUSE Leap 16 e o Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://opensuse.org/>
- <https://ubuntu.com/>

???+ nota

    OS installation steps are outside the scope of this book, but a default or even a
    minimal installation of your preferred OS should be sufficient. Please refrain from
    installing graphical user interfaces (GUIs) or desktop environments, as they are
    unnecessary for server setups and consume valuable resources.

Depois de instalar o sistema operacional de sua preferência, há algumas
configurações essenciais a serem realizadas antes de prosseguir com a instalação
do Zabbix. Execute as etapas a seguir em **todos** os servidores que hospedarão
os componentes do Zabbix (ou seja, servidor Zabbix, servidor de banco de dados e
servidor da Web).

---

### Atualizar o sistema

Antes de instalar os componentes do Zabbix ou qualquer novo software, é uma
prática recomendada garantir que seu sistema operacional esteja atualizado com
os patches e as correções de segurança mais recentes. Isso ajudará a manter a
estabilidade e a compatibilidade do sistema com o software que você está prestes
a instalar. Mesmo que a instalação do sistema operacional seja recente, ainda é
recomendável executar uma atualização para garantir que você tenha os pacotes
mais recentes.

Para atualizar seu sistema, execute o seguinte comando de acordo com seu sistema
operacional:

!!! info "Atualize seu sistema"

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
???+ nota "O que é apt, dnf ou zypper"?

    - DNF (Dandified YUM) is a package manager used in recent Red Hat-based systems (invoked as `dnf`).
    - ZYpp (Zen / YaST Packages Patches Patterns Products) is the package manager 
    used on SUSE-based systems (invoked as `zypper`) and 
    - APT (Advanced Package Tool) is the package manager used on Debian/Ubuntu-based systems (invoked as `apt`). 

    If you're using another distribution, replace `dnf`/`zypper`/`apt` with your appropriate 
    package manager, such as `yum`, `pacman`, `emerge`, `apk` or ... .

    Do note that package names may also vary from distribution to distribution.

???+ dica

    Regularly updating your system is crucial for security and performance.
    Consider setting up automatic updates or scheduling regular maintenance windows
    to keep your systems current.

---

### Sudo

Por padrão, os processos do Zabbix, como o servidor e o agente Zabbix, são
executados em suas próprias contas de usuário sem privilégios (por exemplo,
`zabbix`). No entanto, há cenários em que são necessários privilégios elevados,
como a execução de scripts personalizados ou comandos que precisam de acesso
root. Além disso, ao longo deste livro, executaremos determinadas tarefas
administrativas que exigem `sudo` no sistema.

Normalmente, o `sudo` já está presente na maioria dos sistemas, mas quando você
executou uma instalação mínima do seu sistema operacional, ele pode estar
ausente. Portanto, precisamos garantir que ele esteja instalado.

Isso também permitirá que o usuário do Zabbix execute comandos específicos
configurados com privilégios elevados sem a necessidade de mudar totalmente para
o usuário root.

!!! info "O que é sudo"

    `sudo` (short for "superuser do") is a command-line utility that allows
    permitted users to execute commands with the security privileges of another
    user, typically the superuser (root). It is commonly used in Unix-like
    operating systems to perform administrative tasks without needing to log in
    as the root user.

Para instalar o `sudo`, execute o seguinte comando de acordo com seu sistema
operacional:

!!! info "Instalar sudo"

    Red Hat
    ```bash
    dnf install sudo
    ```

    SUSE
    ```bash
    zypper install sudo
    ```

    Ubuntu

    On Ubuntu, `sudo` is normally installed by default. Root access is managed
    through `sudo` for the initial user created during installation.

Se o `sudo` já estiver instalado, esses comandos informarão que a versão mais
recente já está presente e que nenhuma ação adicional é necessária. Caso
contrário, o gerenciador de pacotes continuará a instalá-la.

---

### Firewall

Em seguida, precisamos garantir que o firewall esteja instalado e configurado. O
firewall é um componente de segurança essencial que ajuda a proteger o servidor
contra acesso não autorizado e possíveis ameaças, controlando o tráfego de
entrada e saída da rede com base em regras de segurança predeterminadas.

Para instalar e ativar o firewall, execute o seguinte comando:

!!! info "Instalar e ativar o firewall"

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
???+ nota "O que é firewalld / ufw"

    Firewalld is the replacement for iptables in RHEL- and SUSE-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps.
    Ubuntu makes use of UFW which is merely a frontend for iptables.

Durante a instalação do Zabbix nos próximos capítulos, precisaremos abrir portas
específicas no firewall para permitir a comunicação entre os componentes do
Zabbix.

Em vez de apenas abrir portas, como faremos nos próximos capítulos, você também
pode optar por definir zonas de firewall dedicadas para casos de uso
específicos. Essa abordagem aumenta a segurança ao isolar serviços e restringir
o acesso com base em níveis de confiança. Por exemplo...

!!! exemplo "Criar uma zona firewalld para acesso ao banco de dados"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    ```

Você pode confirmar a criação da zona executando o seguinte comando:

!!! exemplo "Verificar a criação da zona"

    ```shell-session
    localhost:~ # firewall-cmd --get-zones
    block dmz drop external home internal nm-shared db_zone public trusted work
    ```

O uso de zonas no firewalld para configurar regras de firewall oferece várias
vantagens em termos de segurança, flexibilidade e facilidade de gerenciamento.
Veja a seguir por que as zonas são vantajosas:

- **Controle de acesso granular :**

As zonas firewalld permitem diferentes níveis de confiança para diferentes
interfaces de rede e intervalos de IP. Você pode definir quais sistemas têm
permissão para se conectar ao PostgreSQL com base em seu nível de confiança.

- **Gerenciamento simplificado de regras:**

Em vez de definir manualmente regras complexas do iptables, as zonas oferecem
uma maneira organizada de agrupar e gerenciar regras de firewall com base em
cenários de uso.

- **Segurança aprimorada:**

: Ao restringir o acesso de aplicativos a uma zona específica, você evita
conexões não autorizadas de outras interfaces ou redes.

- **Configuração dinâmica:**

O firewalld suporta configurações de regras permanentes e em tempo de execução,
permitindo alterações sem interromper as conexões existentes.

- **Suporte a várias interfaces:**

: Se o servidor tiver várias interfaces de rede, as zonas permitirão políticas
de segurança diferentes para cada interface.

Juntando tudo para adicionar uma zona para, neste exemplo, o PostgreSQL, ficaria
assim:

!!! exemplo "Firewalld com configuração de zona para acesso ao banco de dados
PostgreSQL"

    ```bash
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Onde o ` IP de origem` é o único endereço permitido para estabelecer uma conexão
com o banco de dados.

Se você quiser usar zonas ao usar o firewalld, adapte as instruções dos
capítulos a seguir de acordo.

---

### Servidor de tempo

Outra etapa crucial é a configuração do servidor de horário e a sincronização do
servidor Zabbix usando um cliente NTP. A sincronização precisa do horário é
vital para o Zabbix, tanto para o servidor quanto para os dispositivos que ele
monitora. Se um dos hosts tiver um fuso horário incorreto, isso pode gerar
confusão, como investigar um problema no Zabbix que parece ter acontecido horas
antes do que realmente aconteceu.

Para instalar e ativar o chrony, nosso cliente NTP, use o seguinte comando:

!!! info "Instalar cliente NTP"

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

Após a instalação, verifique se o Chrony está ativado e em execução, verificando
seu status com o seguinte comando:

!!! info "Verifique o status do serviço chronyd."

    ```bash
    systemctl status chronyd
    ```

???+ nota "O que é Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Depois que o Chrony estiver instalado, a próxima etapa é garantir que o fuso
horário correto esteja definido. Você pode ver a configuração do horário atual
usando o comando `timedatectl`:

!!! exemplo "Verifique a configuração da hora"

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

Certifique-se de que o serviço Chrony esteja ativo (consulte as etapas
anteriores, se necessário). Para definir o fuso horário correto, primeiro, você
pode listar todos os fusos horários disponíveis com o seguinte comando:

!!! info "List the timezones"

    ```bash
    timedatectl list-timezones
    ```

Esse comando exibirá uma lista de fusos horários disponíveis, permitindo que
você selecione o mais próximo de sua localização. Por exemplo:

!!! example "List of all the timezones available"

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

Depois de identificar seu fuso horário, configure-o usando o seguinte comando:

!!! info "Definir o fuso horário"

    ```bash
    timedatectl set-timezone Europe/Brussels
    ```

Para verificar se o fuso horário foi configurado corretamente, use novamente o
comando `timedatectl`:

!!! example "Check the time and zone"

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

???+ nota

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

#### Verificação da sincronização do Chrony

Para garantir que o Chrony esteja sincronizando com os servidores de horário
corretos, você pode executar o seguinte comando:

!!! info "Verificar chrony"

    ```bash
    chronyc
    ```

O resultado deve ser semelhante:

!!! example "Verify your chrony output"

    ``` shell-session
    localhost:~ # chronyc
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Once inside the Chrony prompt, type the `sources` command to check the used time
sources:

Exemplo de saída:

!!! example "Check your time server sources"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- 51-15-20-83.rev.poneytel>     2   9   377   354   +429us[ +429us] +/-  342ms
    ^- 5.255.99.180                  2  10   377   620  +7424us[+7424us] +/-   37ms
    ^- hachi.paina.net               2  10   377   412   +445us[ +445us] +/-   39ms
    ^* leontp1.office.panq.nl        1  10   377   904  +6806ns[ +171us] +/- 2336us
    ```

Neste exemplo, os servidores NTP em uso estão localizados fora de sua região
local. Recomenda-se mudar para servidores de horário em seu país ou, se
disponível, para um servidor de horário dedicado da empresa. Você pode encontrar
servidores NTP locais aqui: [www.ntppool.org](https://www.ntppool.org/).

---

#### Atualizando os servidores de horário

To update the time servers, modify the Chrony configuration file:

!!! info "Edit chrony config file"

    Red Hat
    ```bash
    vi /etc/chrony.conf
    ```

    SUSE
    ```bash
    vi /etc/chrony.d/pool.conf
    ```
    On SUSE, the pool configuration is located in a separate file. You can
    edit that file directly or add a new configuration file in the same directory.
    In the latter case, ensure to disable or remove the existing pool configuration
    to avoid conflicts.

    Ubuntu
    ```bash
    sudo vi /etc/chrony/chrony.conf
    ```

Replace the existing NTP server pool with one closer to your location.

Exemplo da configuração atual:

!!! example "Example ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool 2.centos.pool.ntp.org iburst
    ```

Change the pools you want to a local time server:

!!! info "Change ntp pool config"

    ```
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    pool be.pool.ntp.org iburst
    ```

Depois de fazer essa alteração, reinicie o serviço Chrony para aplicar a nova
configuração:

!!! info "Restart the chrony service"

    ```bash
    systemctl restart chronyd
    ```

#### Verificação de servidores de horário atualizados

Verifique novamente as fontes de horário para garantir que os novos servidores
locais estejam em uso:

!!! info "Verificar as fontes do chrony "

    ```
    chronyc> sources
    ```

Exemplo de saída esperada com servidores locais:

!!! example "Exemplo de saída"

    ```shell-session
    chronyc> sources
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Isso confirma que o sistema agora está usando servidores de horário local.

## Conclusão

As we have seen, before even considering the Zabbix packages, attention must be
paid to the environment in which it will reside. A properly configured and
up-to-date operating system, an open path through the firewall, and accurate
timekeeping are not mere suggestions, but essential building blocks. Having laid
this groundwork, we can now proceed with confidence to the Zabbix installation,
knowing that the underlying system is prepared for the task.

## Perguntas

- Por que você acha que a sincronização precisa do tempo é tão crucial para um
  sistema de monitoramento como o Zabbix?
- Agora que as bases estão estabelecidas, qual você prevê que será a primeira
  etapa do processo de instalação do Zabbix?
- À medida que avançamos na instalação do Zabbix, vamos pensar na comunicação da
  rede. Quais são as principais portas que você prevê que precisarão passar pelo
  firewall para que o servidor Zabbix e os agentes interajam de forma eficaz?

## URLs úteis

- [https://www.ntppool.org/zone](https://www.ntppool.org/zone)
- [https://www.redhat.com/en/blog/beginners-guide-firewalld](https://www.redhat.com/en/blog/beginners-guide-firewalld)
- [https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations](https://www.linuxjournal.com/content/understanding-firewalld-multi-zone-configurations)
