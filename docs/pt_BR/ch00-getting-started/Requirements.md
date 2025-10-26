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

???+ nota

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
(RHEL), mesmo que uma conta de desenvolvedor forneça acesso limitado, optamos
pelo Rocky Linux como uma alternativa prontamente disponível. Para este livro,
usaremos o Rocky Linux 9.x e o Ubuntu LTS 24.04.x.

- <https://rockylinux.org/>
- <https://ubuntu.com/>

### Firewall

Antes de instalar o Zabbix, é essencial preparar adequadamente o sistema
operacional. A primeira etapa é garantir que o firewall esteja instalado e
configurado.

Para instalar e ativar o firewall, execute o seguinte comando:

!!! info "Instalar e ativar o firewall"

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

Depois de instalado, você pode configurar as portas necessárias. Para o Zabbix,
precisamos permitir o acesso à porta `10051/tcp`, que é onde o coletor do Zabbix
escuta os dados recebidos. Use o seguinte comando para abrir essa porta no
firewall:

!!! info "Permitir acesso ao Zabbix trapper"

    Red Hat
    ```yaml
    firewall-cmd --add-service=zabbix-server --permanent
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    ```

Se o serviço não for reconhecido, você poderá especificar manualmente a porta:

!!! info "Adicionar porta em vez do nome do serviço"

    ```yaml
    firewall-cmd --add-port=10051/tcp --permanent
    ```

???+ nota

    "Firewalld is the replacement for iptables in RHEL-based systems and allows
    changes to take effect immediately without needing to restart the service.
    If your distribution does not use [Firewalld](https://www.firewalld.org),
    refer to your OS documentation for the appropriate firewall configuration steps."
    Ubuntu makes use of UFW and is merely a frontend for iptables.

Uma abordagem alternativa é definir zonas de firewall dedicadas para casos de
uso específicos. Por exemplo...

!!! info "Criar uma zona firewalld"

    ```yaml
    firewall-cmd --new-zone=postgresql-access --permanent
    ```

Você pode confirmar a criação da zona executando o seguinte comando:

!!! info "Verificar a criação da zona"

    ```yaml
    firewall-cmd --get-zones
    ```

Bloquear a DMZ e descartar todo o tráfego proveniente de redes externas,
permitindo apenas o acesso interno por meio das redes home, internal, nm-shared,
postgresql-access, public, trusted e work.

O uso de zonas no firewalld para configurar regras de firewall para o PostgreSQL
oferece várias vantagens em termos de segurança, flexibilidade e facilidade de
gerenciamento. Veja por que as zonas são vantajosas:

- **Controle de acesso granular :**
  - As zonas firewalld permitem diferentes níveis de confiança para diferentes
    interfaces de rede e intervalos de IP. Você pode definir quais sistemas têm
    permissão para se conectar ao PostgreSQL com base em seu nível de confiança.
- **Gerenciamento simplificado de regras:**
  - Em vez de definir manualmente regras complexas do iptables, as zonas
    oferecem uma maneira organizada de agrupar e gerenciar regras de firewall
    com base em cenários de uso.
- **Segurança aprimorada:**
  - Ao restringir o acesso do PostgreSQL a uma zona específica, você evita
    conexões não autorizadas de outras interfaces ou redes.
- **Configuração dinâmica:**
  - O firewalld suporta configurações de regras permanentes e em tempo de
    execução, permitindo alterações sem interromper as conexões existentes.
- **Suporte a várias interfaces:**
  - Se o servidor tiver várias interfaces de rede, as zonas permitirão políticas
    de segurança diferentes para cada interface.

Juntando tudo, ficaria assim:

!!! info "Firewalld com configuração de zona"

    ```yaml
    firewall-cmd --new-zone=db_zone --permanent
    firewall-cmd --zone=db_zone --add-service=postgresql --permanent
    firewall-cmd --zone=db_zone --add-source=xxx.xxx.xxx.xxx/32 --permanent
    firewall-cmd --reload
    ```

Onde o ` IP de origem` é o único endereço permitido para estabelecer uma conexão
com o banco de dados.

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
    ```yaml
    dnf install chrony
    systemctl enable chronyd --now
    ```

    Ubuntu
    ```yaml
    sudo apt install chrony
    ```

Após a instalação, verifique se o Chrony está ativado e em execução, verificando
seu status com o seguinte comando:

!!! info "Verifique o status do serviço chronyd."

    ```yaml
    systemctl status chronyd
    ```

???+ nota "O que é apt ou dnf"

    dnf is a package manager used in Red Hat-based systems. If you're using another
    distribution, replace `dnf` with your appropriate package manager, such as `zypper`,
    `apt`, or `yum`.

???+ nota "O que é Chrony"

    Chrony is a modern replacement for `ntpd`, offering faster and
    more accurate time synchronization. If your OS does not support
    [Chrony](https://chrony-project.org/), consider using
    `ntpd` instead.

Depois que o Chrony estiver instalado, a próxima etapa é garantir que o fuso
horário correto esteja definido. Você pode ver a configuração do horário atual
usando o comando `timedatectl`:

!!! info "verifique a configuração da hora"

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

Certifique-se de que o serviço Chrony esteja ativo (consulte as etapas
anteriores, se necessário). Para definir o fuso horário correto, primeiro, você
pode listar todos os fusos horários disponíveis com o seguinte comando:

!!! info "listar os fusos horários"

    ```yaml
    timedatectl list-timezones
    ```

Esse comando exibirá uma lista de fusos horários disponíveis, permitindo que
você selecione o mais próximo de sua localização. Por exemplo:

!!! info "Lista de todos os fusos horários disponíveis"

    ```yaml
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

    ```yaml
    timedatectl set-timezone Europe/Brussels
    ```

Para verificar se o fuso horário foi configurado corretamente, use novamente o
comando `timedatectl`:

!!! info "Verifique a hora e o fuso horário"

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

???+ nota

    Some administrators prefer installing all servers in the UTC time zone to
    ensure that server logs across global deployments are synchronized.
    Zabbix supports user-based time zone settings, which allows the server to
    remain in UTC while individual users can adjust the time zone via the
    interface if needed.

---

### Verificação da sincronização do Chrony

Para garantir que o Chrony esteja sincronizando com os servidores de horário
corretos, você pode executar o seguinte comando:

!!! info "Verificar chrony"

    ```yaml
    chronyc
    ```

O resultado deve ser semelhante:

!!! info "Verifique a saída do seu chrony"

    ```yaml
    chrony version 4.2
    Copyright (C) 1997-2003, 2007, 2009-2021 Richard P. Curnow and others
    chrony comes with ABSOLUTELY NO WARRANTY. This is free software, and
    you are welcome to redistribute it under certain conditions. See the
    GNU General Public License version 2 for details.

    chronyc>
    ```

Quando estiver no prompt do Chrony, digite o seguinte para verificar os
códigos-fonte:

!!! info ""

    ```yaml
    chronyc> sources
    ```

Exemplo de saída:

!!! info "Verifique as fontes do seu servidor de horário"

    ```bash
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

### Atualizando os servidores de horário

Para atualizar os servidores de horário, modifique o arquivo `/etc/chrony.conf`
para sistemas baseados no Red Hat e, se você usar o Ubuntu, edite
`/etc/chrony/chrony.conf`. Substitua o servidor NTP existente por um mais
próximo de sua localização.

Exemplo da configuração atual:

!!! info "exemplo de configuração do pool ntp"

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

Depois de fazer essa alteração, reinicie o serviço Chrony para aplicar a nova
configuração:

!!! info "reinicie o serviço chrony"

    ```yaml
    systemctl restart chronyd
    ```

### Verificação de servidores de horário atualizados

Verifique novamente as fontes de horário para garantir que os novos servidores
locais estejam em uso:

!!! info "Verificar as fontes do chrony "

    ```yaml
    chronyc> sources
    ```

Exemplo de saída esperada com servidores locais:

!!! info "Exemplo de saída"

    ```yaml
    MS Name/IP address         Stratum Poll Reach LastRx Last sample
    ===============================================================================
    ^- ntp1.unix-solutions.be        2   6    17    43   -375us[ -676us] +/-   28ms
    ^* ntp.devrandom.be              2   6    17    43   -579us[ -880us] +/- 2877us
    ^+ time.cloudflare.com           3   6    17    43   +328us[  +27us] +/- 2620us
    ^+ time.cloudflare.com           3   6    17    43
    ```

Isso confirma que o sistema agora está usando servidores de horário local.

## Conclusão

Como vimos, antes mesmo de considerar os pacotes do Zabbix, é preciso prestar
atenção ao ambiente em que ele residirá. Um sistema operacional configurado
adequadamente, um caminho aberto através do firewall e um controle preciso do
tempo não são meras sugestões, mas blocos de construção essenciais. Depois de
estabelecer essa base, agora podemos prosseguir com confiança para a instalação
do Zabbix, sabendo que o sistema subjacente está preparado para a tarefa.

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
