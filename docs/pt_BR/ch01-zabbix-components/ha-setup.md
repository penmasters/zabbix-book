---
description: |
    Set up Zabbix High Availability with clustered servers, shared DB, and Keepalived
    for VIP failover—ensuring zero-downtime monitoring.
tags: [expert]
---

# Configuração do HA

Nesta seção, definiremos o Zabbix em uma configuração de alta disponibilidade
(HA). Esse recurso, introduzido no Zabbix 6, é um aprimoramento crucial que
garante o monitoramento contínuo mesmo se um servidor Zabbix falhar. Com a HA,
quando um servidor Zabbix fica inativo, outro pode assumir o controle sem
problemas.

Para este guia, usaremos dois servidores Zabbix e um banco de dados, mas a
configuração permite adicionar mais servidores Zabbix, se necessário.

![Configuração-HA](./ha-setup/ch01-HA-setup.png)

_1.1 Configuração de HA_

É importante observar que a configuração do Zabbix HA é simples, fornecendo
redundância sem recursos complexos, como balanceamento de carga.

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

Consulte o capítulo [_Instalação básica_](basic-installation.md) para obter
instruções detalhadas sobre a configuração do banco de dados. Esse capítulo
fornece orientação passo a passo sobre a instalação de um banco de dados
PostgreSQL ou MariaDB em um nó dedicado que executa o Ubuntu ou o Rocky Linux.
As mesmas etapas de instalação se aplicam à configuração do banco de dados para
essa instalação.

---

## Instalando o cluster no Zabbix

A configuração de um cluster no Zabbix envolve a configuração de vários
servidores Zabbix para trabalharem juntos, proporcionando alta disponibilidade.
Embora o processo seja semelhante à configuração de um único servidor Zabbix, há
etapas adicionais de configuração necessárias para ativar a HA (High
Availability).

Adicione os Repositórios Zabbix aos seus servidores.

Primeiro, adicione o repositório Zabbix a ambos os servidores Zabbix:

!!! info "adicionar repositório zabbix"

    Redhat

    ``` yaml
    rpm -Uvh https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
    dnf clean all
    ```

    Ubuntu

    ``` yaml
    sudo wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo apt update
    ```

Quando isso for feito, poderemos instalar os pacotes do servidor zabbix.

!!! info "instalar pacotes do servidor zabbix"

    Redhat

    ``` yaml
    dnf install zabbix-server-pgsql
    ```
    or if your database is MySQL or MariaDB
    ```
    dnf install zabbix-server-mysql
    ```

    Ubuntu

    ``` yaml
    sudo apt install zabbix-server-pgsql
    ```
    or if your database is MySQL or MariaDB
    ``` yaml
    sudo apt install zabbix-server-mysql
    ```

---

### Configuração do Zabbix Server 1

Edite o arquivo de configuração do servidor Zabbix,

!!! info "editar o arquivo de configuração do servidor"

    ``` yaml
    sudo vi /etc/zabbix/zabbix_server.conf
    ```

Atualize as seguintes linhas para se conectar ao banco de dados:

!!! informações ""

    ``` yaml
    DBHost=<zabbix db ip>
    DBName=<name of the zabbix DB>
    DBUser=<name of the db user>
    DBSchema=<db schema for the PostgreSQL DB>
    DBPassword=<your secret password>
    ```

Configure os parâmetros de HA para esse servidor:

!!! informações ""

    ```yaml
    HANodeName=zabbix1 (or choose a name you prefer)
    ```

Especifique o endereço do nó front-end para cenários de failover:

!!! informações ""

    ``` yaml
    NodeAddress=<Zabbix server 1 ip>:10051
    ```

---

### Configuração do Zabbix Server 2

Repita as etapas de configuração para o segundo servidor Zabbix. Ajuste o
`HANodeName` e o `NodeAddress` conforme necessário para esse servidor.

---

### Iniciando o Zabbix Server

Depois de configurar os dois servidores, ative e inicie o serviço zabbix-server
em cada um deles:

!!! info "restart zabbix-server service" (reiniciar o serviço zabbix-server)

    ```
    sudo systemctl enable zabbix-server --now
    ```

???+ nota

    The `NodeAddress` must match the IP or FQDN name of the Zabbix server node.
    Without this parameter the Zabbix front-end is unable to connect to the active
    node. The result will be that the frontend is unable to display the status
    the queue and other information.

---

### Verificação da configuração

Verifique os arquivos de registro em ambos os servidores para garantir que eles
tenham sido iniciados corretamente e estejam operando em seus respectivos modos
HA.

No primeiro servidor:

!!! info "verifique se há mensagens de HA nos registros"

    ``` yaml
    sudo grep HA /var/log/zabbix/zabbix_server.log
    ```

Nos logs do sistema, observe as seguintes entradas, indicando a inicialização do
gerenciador de alta disponibilidade (HA):

!!! informações ""

    ``` yaml
    22597:20240309:155230.353 starting HA manager
    22597:20240309:155230.362 HA manager started in active mode
    ```

Essas mensagens de registro confirmam que o processo do gerenciador de HA foi
iniciado e assumiu a função ativa. Isso significa que a instância do Zabbix é
agora o nó primário no cluster de HA, lidando com todas as operações de
monitoramento. Se ocorrer um evento de failover, outro nó de espera assumirá o
controle com base na estratégia de HA configurada.

No segundo servidor (e em quaisquer nós adicionais):

!!! informações ""

    ``` yaml
    grep HA /var/log/zabbix/zabbix_server.log
    ```

Nos logs do sistema, as seguintes entradas indicam a inicialização do
gerenciador de alta disponibilidade (HA):

!!! informações ""

    ```yaml
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
essencial instalar o Keepalived. O Keepalived permite o uso de um IP virtual
(VIP) para serviços de front-end, garantindo um failover perfeito e a
continuidade do serviço. Ele fornece uma estrutura robusta para balanceamento de
carga e alta disponibilidade, o que o torna um componente essencial para a
manutenção de uma infraestrutura resiliente.

---

### Configuração do keepalived

???+ nota

    Keepalived is like a helper that makes sure one computer takes over if another
    one stops working. It gives them a shared magic IP address so users don't notice
    when a server fails. If the main one breaks, the backup jumps in right away.
    You can replace it with tools like Pacemaker, Corosync, or cloud load balancers
    that do the same “take over” job. So let's get started. On both our servers
    we have to install keepalived.

!!! info "instalar keepalived"

    Redhat
    ``` yaml
    dnf install keepalived
    ```

    Ubuntu
    ``` yaml
    sudo apt install keepalived
    ```

Em seguida, precisamos modificar a configuração do Keepalived em ambos os
servidores. Embora as configurações sejam semelhantes, cada servidor requer
pequenos ajustes. Começaremos com o Servidor 1. Para editar o arquivo de
configuração do Keepalived, use o seguinte comando:

!!! info "editar a configuração do keepalived"

    RedHat and Ubuntu
    ``` yaml
    sudo vi /etc/keepalived/keepalived.conf
    ```

Se o arquivo contiver algum conteúdo existente, ele deverá ser limpo e
substituído pelas seguintes linhas:

!!! informações ""

    ```yaml
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

???+ aviso

    Replace `enp0s1` with the interface name of your machine and replace the `password`
    with something secure. For the virtual_ipaddress use a free IP from your network.
    This will be used as our VIP.

Agora podemos fazer a mesma modificação em nosso servidor `second` Zabbix.
Exclua tudo novamente no mesmo arquivo, como fizemos antes, e substitua-o pelas
seguintes linhas:

!!!info ""

    ``` yaml
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
interface de sua máquina e substitua a senha `` por sua senha e preencha o
virtual_ipaddress como usado anteriormente.

Isso encerra a configuração do keepalived. Agora podemos continuar adaptando o
frontend.

---

### Instalar e configurar o front-end

Em ambos os servidores, podemos executar os seguintes comandos para instalar
nosso servidor Web e os pacotes de front-end do zabbix:

!!! info "install web server and config" (instalar servidor da web e
configuração)

    RedHat
    ```yaml
    dnf install nginx zabbix-web-pgsql zabbix-nginx-conf
    ```

    Ubuntu
    ```yaml
    sudo apt install nginx zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```

Além disso, é fundamental configurar o firewall. Regras adequadas de firewall
garantem uma comunicação perfeita entre os servidores e evitam falhas
inesperadas. Antes de prosseguir, verifique se as portas necessárias estão
abertas e aplique as regras de firewall necessárias de acordo.

!!! info "configurar o firewall"

    RedHat
    ```yaml
    firewall-cmd --add-service=http --permanent
    firewall-cmd --add-service=zabbix-server --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 10051/tcp
    sudo ufw allow 80/tcp
    ```

Com a configuração em vigor e o firewall devidamente configurado, podemos agora
iniciar o serviço Keepalived. Além disso, devemos ativá-lo para garantir que ele
seja iniciado automaticamente na reinicialização. Use os seguintes comandos para
fazer isso:

!!! info "iniciar e ativar o keepalived"

    RedHat and Ubuntu
    ```yaml
    sudo systemctl enable keepalived nginx --now
    ```

---

### Configurar o servidor da Web

O processo de configuração do frontend segue as mesmas etapas descritas na seção
`Basic Installation` em [Installing the
Frontend](basic-installation.md/#installing-the-frontend). Ao aderir a esses
procedimentos estabelecidos, garantimos consistência e confiabilidade na
implementação.

???+ aviso

    Ubuntu users need to use the VIP in the setup of Nginx, together with the local
    IP in the listen directive of the config.

???+ nota

    Don't forget to configure both front-ends. Also this is a new setup. Keep in
    mind that with an existing setup we need to comment out the lines  `$ZBX_SERVER`
    and `$ZBX_SERVER_PORT`. Our frontend will check what node is active by reading
    the node table in the database.

!!! informações ""

    ```yaml
    select * from ha_node;
    ```
    ```sql
    zabbix=# select * from ha_node;
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

---

### Verificar o funcionamento correto

Para verificar se a configuração está funcionando corretamente, acesse o
servidor `Zabbix` usando o IP virtual (VIP). Navegue até Reports → System
Information (Relatórios → Informações do sistema) no menu. Na parte inferior da
página, você deverá ver uma lista de servidores, com pelo menos um marcado como
ativo. O número de servidores exibidos dependerá do total configurado em sua
configuração de HA.

![1º frontend ativo](ha-setup/ch01-HA-check1.png)

_1.2 verificar HA_

Desligue ou reinicie o servidor de front-end ativo e observe que o front-end
`Zabbix` permanece acessível. Ao recarregar a página, você notará que o outro
servidor de front-end `` assumiu o papel de instância ativa, garantindo um
failover quase perfeito e alta disponibilidade.

![2st active frontend](ha-setup/ch01-HA-check2.png)

_1.3 verify HA_

In addition to monitoring the status of HA nodes, Zabbix provides several
runtime commands that allow administrators to manage failover settings and
remove inactive nodes dynamically.

One such command is:

!!! informações ""

    ```yaml
    zabbix_server -R ha_set_failover_delay=10m
    ```

This command adjusts the failover delay, which defines how long Zabbix waits
before promoting a standby node to active status. The delay can be set within a
range of **10 seconds** to **15 minutes**.

To remove a node that is either **stopped** or **unreachable**, the following
runtime command must be used:

!!! informações ""

    ```yaml
    zabbix_server -R ha_remove_node=`zabbix1`
    ```

Executing this command removes the node from the HA cluster. Upon successful
removal, the output confirms the action:

!!! informações ""

    ```yaml
    Removed node "zabbix1" with ID "cm8agwr2b0001h6kzzsv19ng6"
    ```

If the removed node becomes available again, it can be added back automatically
when it reconnects to the cluster. These runtime commands provide flexibility
for managing high availability in Zabbix without requiring a full restart of the
`zabbix_server` process.

---

## Conclusão

In this chapter, we have successfully set up a high-availability (HA) Zabbix
environment by configuring both the Zabbix server and frontend for redundancy.
We first established HA for the Zabbix server, ensuring that monitoring services
remain available even in the event of a failure. Next, we focused on the
frontend, implementing a Virtual IP (VIP) with Keepalived to provide seamless
failover and continuous accessibility.

Additionally, we configured the firewall to allow Keepalived traffic and ensured
that the service starts automatically after a reboot. With this setup, the
Zabbix frontend can dynamically switch between servers, minimizing downtime and
improving reliability.

While database HA is an important consideration, it falls outside the scope of
this setup. However, this foundation provides a robust starting point for
building a resilient monitoring infrastructure that can be further enhanced as
needed.

---

## Perguntas

1. What is Zabbix High Availability (HA), and why is it important?
2. How does Zabbix determine which node is active in an HA setup?
3. Can multiple Zabbix nodes be active simultaneously in an HA cluster? Why or
   why not?
4. What configuration file(s) are required to enable HA in Zabbix?

---

## URLs úteis

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
- <https://www.zabbix.com/documentation/7.2/en/manual/concepts/server/ha>
