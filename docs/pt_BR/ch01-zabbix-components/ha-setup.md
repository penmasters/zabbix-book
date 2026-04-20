---
description: |
    Set up Zabbix High Availability with clustered servers, shared DB, and Keepalived
    for VIP failover—ensuring zero-downtime monitoring.
tags: [expert]
---

# Configuração do HA

Nesta seção, definiremos o Zabbix em uma configuração de alta disponibilidade
(HA). Esse recurso nativo, introduzido no Zabbix 6, é um aprimoramento crucial
que garante o monitoramento contínuo mesmo se um servidor Zabbix falhar. Com a
HA, quando um servidor Zabbix fica inativo, outro pode assumir o controle sem
problemas.

Para este guia, usaremos dois servidores Zabbix e um banco de dados, mas a
configuração permite adicionar mais servidores Zabbix, se necessário.

![Configuração-HA](./ha-setup/ch01-HA-setup.png)

_1.1 Configuração de HA_

É importante observar que a configuração do Zabbix HA é simples, fornecendo
redundância sem recursos complexos como balanceamento de carga. Apenas um nó
será um nó ativo, todos os outros nós estarão em standby. Todos os servidores
Zabbix em standby no cluster HA monitorarão o nó ativo por meio de heartbeats
usando o banco de dados compartilhado. Não é necessário nenhum software de
cluster adicional ou mesmo portas de firewall para o próprio servidor Zabbix. No
entanto, para o front-end, usaremos o Keepalived para fornecer um IP virtual
(VIP) para fins de failover.

Assim como em nossa configuração básica, documentaremos os principais detalhes
dos servidores nessa configuração de HA. Abaixo está a lista de servidores e um
local para adicionar seus respectivos endereços IP para sua conveniência:

| Servidor          | Endereço IP |
| ----------------- | ----------- |
| Servidor Zabbix 1 |             |
| Servidor Zabbix 2 |             |
| Banco de dados    |             |
| IP virtual        |             |

???+ nota

    Our database (DB) in this setup is not configured for HA. Since it's not a
    Zabbix component, you will need to implement your own solution for database
    HA, such as a HA SAN or a database cluster setup. A DB cluster configuration
    is out of the scope of this guide and unrelated to Zabbix, so it will not be
    covered here.

---

## Instalação do banco de dados

Consulte o capítulo [_Zabbix components: Database_](database.md) para obter
instruções detalhadas sobre a configuração do banco de dados. Esse capítulo
fornece orientações passo a passo sobre a instalação de um banco de dados
PostgreSQL ou MariaDB em um nó dedicado executando Ubuntu, SUSE ou Rocky Linux.
As mesmas etapas de instalação se aplicam ao configurar o banco de dados para
essa instalação.

---

## Instalando o cluster no Zabbix

A configuração de um cluster no Zabbix envolve a configuração de vários
servidores Zabbix para trabalharem juntos, proporcionando alta disponibilidade.
Embora o processo seja semelhante à configuração de um único servidor Zabbix, há
etapas adicionais de configuração necessárias para ativar a HA (High
Availability).

Comece preparando os sistemas e instalando o Zabbix Server em todos os sistemas,
seguindo as etapas das seções [_Preparando o servidor para o
Zabbix_](preparation.md) e [_Instalando o Zabbix Server_](zabbix-server.md) do
capítulo _Componentes do Zabbix_.

Observe que:

- você precisa ignorar a etapa de população do banco de dados em todos os
  servidores Zabbix, exceto no primeiro, pois o banco de dados é compartilhado
  entre todos os servidores Zabbix.
- você precisa ignorar a ativação e a inicialização do serviço zabbix-server em
  todos os servidores, pois o iniciaremos mais tarde, depois que a configuração
  de HA estiver concluída.
- certifique-se de que todos os servidores Zabbix possam se conectar ao servidor
  de banco de dados. Por exemplo, se você estiver usando o PostgreSQL,
  certifique-se de que o arquivo `pg_hba.conf` esteja configurado para permitir
  conexões de todos os servidores Zabbix.
- todos os servidores Zabbix devem usar o mesmo nome de banco de dados, usuário
  e senha para se conectar ao banco de dados.
- todos os servidores Zabbix devem ter a mesma versão principal.

Quando todos os servidores Zabbix estiverem instalados e configurados para
acessar o banco de dados, poderemos prosseguir com a configuração do HA.

---

### Configuração do Zabbix Server 1

Adicione um novo arquivo de configuração para a configuração de HA no primeiro
servidor Zabbix:

!!! info "Adicionar configuração do servidor Zabbix de alta disponibilidade"

    ``` bash
    sudo vi /etc/zabbix/zabbix_server.d/high-availability.conf
    ```

    Insert the following line into the configuration file to enable HA mode.

    ```ini
    HANodeName=zabbix1  # or choose a name you prefer
    ```

    Specify the frontend node address for failover scenarios:

    ```ini
    NodeAddress=<Zabbix server 1 ip>:10051
    ```

???+ Aviso

    The `NodeAddress` must match the IP or FQDN name of the Zabbix server node.
    Without this parameter the Zabbix front-end is unable to connect to the active
    node. The result will be that the frontend is unable to display the status
    the queue and other information.


---

### Configuração do Zabbix Server 2

Repita as etapas de configuração para o segundo servidor Zabbix. Ajuste o
`HANodeName` e o `NodeAddress` conforme necessário para esse servidor.

???+ example "Zabbix server 2 HA configuration high-availability.conf"

    ```ini
    HANodeName=zabbix2  # or choose a name you prefer
    NodeAddress=<Zabbix server 2 ip>:10051
    ```

You can add more servers by repeating the same steps, ensuring each server has a
unique `HANodeName` and the correct `NodeAddress` set.

---

### Iniciando o Zabbix Server

Depois de configurar os dois servidores, ative e inicie o serviço zabbix-server
em cada um deles:

!!! info "ativar e iniciar o serviço zabbix-server"

    ```
    sudo systemctl enable zabbix-server --now
    ```

---

### Verificação da configuração

Verifique os arquivos de registro em ambos os servidores para garantir que eles
tenham sido iniciados corretamente e estejam operando em seus respectivos modos
HA.

No primeiro servidor:

!!! info "verifique se há mensagens de HA nos registros"

    ``` bash
    sudo grep HA /var/log/zabbix/zabbix_server.log
    ```

Nos logs do sistema, observe as seguintes entradas, indicando a inicialização do
gerenciador de alta disponibilidade (HA):

???+ example "HA log messages on active node"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22597:20240309:155230.353 starting HA manager
    22597:20240309:155230.362 HA manager started in active mode
    ```

These log messages confirm that the HA manager process has started and has
assumed the active role. This means that the Zabbix instance is now the primary
node in the HA cluster, handling all monitoring operations. If a failover event
occurs, another standby node will take over based on the configured HA strategy.

Running the same command on the second server (and any additional nodes):

???+ example "HA log messages on standby node"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22304:20240309:155331.163 starting HA manager
    22304:20240309:155331.174 HA manager started in standby mode
    ```

Essas mensagens confirmam que o processo do gerenciador de HA foi invocado e
iniciado com sucesso no modo de espera. Isso sugere que o nó está operacional,
mas não está atuando no momento como a instância de HA ativa, aguardando outras
transições de estado com base na estratégia de HA configurada.

Nesta etapa, seu cluster do Zabbix está configurado com sucesso para alta
disponibilidade (HA). Os registros do sistema confirmam que o gerenciador de HA
foi inicializado e está sendo executado no modo de espera, indicando que os
mecanismos de failover estão em vigor. Essa configuração garante o monitoramento
ininterrupto, mesmo no caso de falha do servidor, permitindo transições
automáticas de função com base na configuração de HA.

---

## Instalando o front-end

Antes de prosseguir com a instalação e a configuração do servidor Web, é
essencial instalar algum tipo de software de clustering ou usar um balanceador
de carga na frente dos front-ends do Zabbix para poder ter um IP virtual (VIP)
compartilhado.

Observação Há várias opções disponíveis para software de clustering e
balanceadores de carga, incluindo Pacemaker, Corosync, HAProxy, F5 Big-Ip,
Citrix NetScaler e vários balanceadores de carga em nuvem. Cada uma dessas
soluções oferece uma gama de recursos e capacidades que vão além do simples
fornecimento de um VIP para fins de failover. Mas, para os fins deste guia,
vamos nos concentrar em uma abordagem minimalista para obter alta
disponibilidade para o frontend do Zabbix usando o Keepalived.

O Keepalived é como um auxiliar que garante que um computador assuma o controle
se outro parar de funcionar. Ele fornece a eles um endereço IP mágico
compartilhado para que os usuários não percebam quando um servidor falha. Se o
principal falhar, o backup entra em ação imediatamente, assumindo o controle do
IP.

O Keepalived é um tipo mínimo de software de clustering que permite o uso de um
(VIP) para serviços de front-end, garantindo um failover perfeito e a
continuidade do serviço.

!!! aviso "Alta disponibilidade no SUSE Linux Enterprise Server (SLES)"

    On SUSE Linux Enterprise Server (SLES), Keepalived is not included in the
    default subscription hence unavailable in the default repositories.

    To be able to install and use Keepalived on SLES in a supported way, you
    will need to obtain the additional 'SUSE Linux Enterprise High Availability
    Extension' subscription (SLE HA). This subscription provides access to the necessary
    packages and updates required for Keepalived and other high availability
    components.
    After obtaining the subscription, you can enable the appropriate
    repositories and proceed with the installation of Keepalived as outlined
    in this guide:

    ```bash
    SUSEConnect -p sle-ha/16/x86_64 -r ADDITIONAL_REGCODE
    ```
    Where `ADDITIONAL_REGCODE` is the registration code provided with your
    'SUSE Linux Enterprise High Availability Extension' subscription.

---

### Configuração do keepalived

Em todos os servidores que hospedarão o Zabbix fronted, temos que instalar o
keepalived. Como mencionado anteriormente, isso pode ser feito em servidores
separados para dividir as funções de servidor e front-end, mas neste guia
instalaremos o keepalived em ambos os servidores Zabbix para garantir a alta
disponibilidade do front-end e do servidor.

!!! info "instalar keepalived"

    Red Hat
    ```bash
    dnf install keepalived
    ```

    SUSE
    ```bash
    zypper install keepalived
    ```

    Ubuntu
    ```bash
    sudo apt install keepalived
    ```

Em seguida, precisamos modificar a configuração do Keepalived em todos os
servidores. Embora as configurações sejam semelhantes, cada servidor requer
pequenos ajustes. Começaremos com o Servidor 1. Para editar o arquivo de
configuração do Keepalived, use o seguinte comando:

!!! info "editar a configuração do keepalived"

    ```bash
    sudo vi /etc/keepalived/keepalived.conf
    ```

Se o arquivo contiver algum conteúdo existente, ele deverá ser limpo e
substituído pelas seguintes linhas:

!!!info ""

    ```
    vrrp_track_process track_nginx {
        process nginx
        weight 10
    }

    vrrp_instance VI_1 {
        state MASTER
        interface enp0s1
        virtual_router_id 51
        priority 244
        advert_int 1
        authentication {
            auth_type PASS
            auth_pass 12345
        }
        virtual_ipaddress {
            xxx.xxx.xxx.xxx
        }
        track_process {
             track_nginx
          }
    }
    ```

???+ Aviso

    Replace `enp0s1` with the interface name of your machine and replace the `password`
    with something secure. For the `virtual_ipaddress` use a free IP from your network.
    This will be used as our VIP.

Agora podemos fazer a mesma modificação em nosso segundo servidor Zabbix ou em
qualquer outro subsequente. Exclua novamente tudo o que estiver no arquivo
`/etc/keepalived/keepalived.conf` como fizemos anteriormente e substitua-o pelas
seguintes linhas:

!!!info ""

    ```
    vrrp_track_process track_nginx {
          process nginx
          weight 10
    }

    vrrp_instance VI_1 {
        state BACKUP
        interface enp0s1
        virtual_router_id 51
        priority 243
        advert_int 1
        authentication {
            auth_type PASS
            auth_pass 12345
        }
        virtual_ipaddress {
           xxx.xxx.xxx.xxx
        }
        track_process {
             track_nginx
          }
    }
    ```

Assim como em nosso primeiro servidor Zabbix, substitua `enp0s1` pelo nome da
interface de sua máquina e substitua `password` por sua senha e preencha
`virtual_ipaddress` como feito anteriormente.

Certifique-se de que o firewall permita o tráfego Keepalived em todos os
servidores. O protocolo VRRP é diferente do protocolo IP padrão e usa o endereço
multicast `224.0.0.18`. Portanto, precisamos permitir explicitamente esse
tráfego pelo firewall. Execute os seguintes comandos em todos os servidores:

!!! info "Permitir tráfego keepalived através do firewall"

    Red Hat / SUSE
    ```yaml
    firewall-cmd --add-rich-rule='rule protocol value="vrrp" accept' --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```yaml
    sudo ufw allow to 224.0.0.18 comment ‘keepalived multicast’
    ```

Isso encerra a configuração do keepalived. Agora podemos continuar adaptando o
frontend.

---

### Instalar e configurar o front-end

Instale o front-end do Zabbix em todos os servidores Zabbix, parte do cluster,
seguindo as etapas descritas na seção [_Instalando o
front-end_](zabbix-frontend.md).

???+ Aviso

    Ubuntu users need to use the VIP in the setup of Nginx, together with the local
    IP in the listen directive of the config.

???+ nota

    Don't forget to configure both front-ends. Also this is a new setup. Keep in
    mind that with an existing setup we need to comment out the lines  `$ZBX_SERVER`
    and `$ZBX_SERVER_PORT` in `/etc/zabbix/web/zabbix.conf.php`. Our frontend 
    will check what node is active by reading the node table in the database.


Você pode verificar qual nó está ativo consultando a tabela `ha_node` no banco
de dados do Zabbix. Essa tabela contém informações sobre todos os nós do cluster
de HA, inclusive o status deles. Para verificar o status dos nós, você pode
executar a seguinte consulta SQL:

!!!info ""

    ```sql
    select * from ha_node;

    ```

Exemplo "Verifique a tabela ha_node em um banco de dados PostgreSQL"

    ```psql
    zabbix=> select * from ha_node;
             ha_nodeid         |  name   |   address       | port  | lastaccess | status |       ha_sessionid
    ---------------------------+---------+-----------------+-------+------------+--------+---------------------------
     cm8agwr2b0001h6kzzsv19ng6 | zabbix1 | xxx.xxx.xxx.xxx | 10051 | 1742133911 |      0 | cm8apvb0c0000jkkzx1ojuhst
     cm8agyv830001ell0m2nq5o6n | zabbix2 | localhost       | 10051 | 1742133911 |      3 | cm8ap7b8u0000jil0845p0w51
    (2 rows)
    ```

Nesse caso, o nó `zabbix2` é identificado como o nó ativo, conforme indicado por
seu valor de status `3`, que designa um estado ativo. Os valores de status
possíveis são os seguintes:

- `0` - Vários nós podem permanecer em modo de espera.
- `1` - Um nó detectado anteriormente foi desligado.
- `2` - Um nó foi detectado anteriormente, mas ficou indisponível sem um
  desligamento adequado.
- `3` - O nó está ativo no momento.

Essa classificação permite o monitoramento eficaz e o gerenciamento de estado
dentro do cluster.

Depois que o front-end estiver instalado em todos os servidores, precisaremos
iniciar e ativar o serviço Keepalived para garantir que ele seja iniciado
automaticamente na inicialização e comece a gerenciar o VIP:

!!! info "iniciar e ativar o keepalived"

    ```yaml
    sudo systemctl enable keepalived nginx --now
    ```


---

### Verificar o funcionamento correto

To verify that the setup is functioning correctly, access your Zabbix server
using the Virtual IP (VIP). Navigate to Reports → System Information in the
menu. At the bottom of the page, you should see a list of servers, with at least
one marked as active. The number of servers displayed will depend on the total
configured in your HA setup.

![1º frontend ativo](ha-setup/ch01-HA-check1.png)

_1.2 verificar HA_

Desligue ou reinicie o servidor de front-end ativo e observe que o `Zabbix
front-end ` permanece acessível. Ao recarregar a página, você notará que o outro
servidor de front-end `` assumiu o papel de instância ativa, garantindo um
failover quase perfeito e alta disponibilidade.

![2st ativar frontend](ha-setup/ch01-HA-check2.png)

_1.3 verificar HA_

Além de monitorar o status dos nós de HA, o Zabbix fornece vários comandos de
tempo de execução que permitem aos administradores gerenciar as configurações de
failover e remover dinamicamente os nós inativos.

Um desses comandos é:

!!!info ""

    ```bash
    zabbix_server -R ha_set_failover_delay=10m
    ```

Esse comando ajusta o atraso do failover, que define quanto tempo o Zabbix
espera antes de promover um nó em espera para o status ativo. O atraso pode ser
definido em um intervalo de **10 segundos** a **15 minutos**.

Para remover um nó que seja **stopped** ou **unreachable**, o seguinte comando
de tempo de execução deve ser usado:

!!!info ""

    ```bash
    sudo zabbix_server -R ha_remove_node=`zabbix1`
    ```

A execução desse comando remove o nó do cluster de HA. Após a remoção
bem-sucedida, a saída confirma a ação:

!!! exemplo "Remoção de um nó"

    ```shell-session
    localhost:~ # zabbix_server -R ha_remove_node=`zabbix1`
    Removed node "zabbix1" with ID "cm8agwr2b0001h6kzzsv19ng6"
    ```

Se o nó removido ficar disponível novamente, ele poderá ser adicionado
automaticamente quando se reconectar ao cluster. Esses comandos de tempo de
execução oferecem flexibilidade para gerenciar a alta disponibilidade no Zabbix
sem exigir a reinicialização completa do processo `zabbix_server`.

---

## Conclusão

Neste capítulo, configuramos com sucesso um ambiente Zabbix de alta
disponibilidade (HA), configurando o servidor Zabbix e o frontend para
redundância. Primeiro, estabelecemos a HA para o servidor Zabbix, garantindo que
os serviços de monitoramento permaneçam disponíveis mesmo em caso de falha. Em
seguida, nos concentramos no front-end, implementando um IP virtual (VIP) com o
Keepalived para fornecer failover perfeito e acessibilidade contínua.

Além disso, configuramos o firewall para permitir o tráfego do Keepalived e
garantimos que o serviço seja iniciado automaticamente após uma reinicialização.
Com essa configuração, o front-end do Zabbix pode alternar dinamicamente entre
os servidores, minimizando o tempo de inatividade e aumentando a confiabilidade.

Embora a HA do banco de dados seja uma consideração importante, ela está fora do
escopo desta configuração. No entanto, essa base fornece um ponto de partida
robusto para a criação de uma infraestrutura de monitoramento resiliente que
pode ser aprimorada conforme necessário.

---

## Perguntas

1. O que é o Zabbix High Availability (HA) e por que ele é importante?
2. Como o Zabbix determina qual nó está ativo em uma configuração de HA?
3. Vários nós do Zabbix podem estar ativos simultaneamente em um cluster HA? Por
   que sim ou por que não?
4. Que arquivo(s) de configuração é(são) necessário(s) para ativar o HA no
   Zabbix?

---

## URLs úteis

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
- <https://www.zabbix.com/documentation/7.2/en/manual/concepts/server/ha>
