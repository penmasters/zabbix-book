---
description: |
    Configure Zabbix High Availability com servidores em cluster, banco de dados compartilhado e Keepalived para failover do VIP—garantindo monitoramento sem interrupções.
tags: [expert]
---

# Configuração HA

Nesta seção, configuraremos o Zabbix em uma configuração de Alta Disponibilidade (HA).
Esta funcionalidade nativa, introduzida no Zabbix 6, é uma importante melhoria que garante a continuidade do monitoramento mesmo se um servidor Zabbix falhar. Com HA, quando um servidor Zabbix cai,
outro pode assumir o controle de forma transparente.

Para esta guia, usaremos dois servidores Zabbix e um banco de dados, mas a configuração permite
a adição de mais servidores Zabbix se necessário.

![HA-Setup](./ha-setup/ch01.10-HA-setup.png)

_1.10 Configuração HA_

É importante notar que a configuração HA do Zabbix é simples, fornecendo redundância
sem recursos complexos como balanceamento de carga. Apenas um nó será o nó ativo,
todos os outros nós estarão em modo standby. Todos os servidores Zabbix em standby no cluster HA monitorarão o nó ativo através de batidas cardíacas usando o banco de dados compartilhado. Não é necessário
nenhum software adicional de clustering ou até mesmo portas de firewall para o servidor
Zabbix. No entanto, para a interface frontal, usaremos Keepalived para fornecer um
IP Virtual (VIP) para fins de failover.

Assim como em nossa configuração básica, documentaremos detalhes importantes para os servidores
nesta configuração HA. Abaixo está a lista de servidores e alguns lugares para adicionar seus
endereços IP respectivos para sua conveniência:

| Servidor          | Endereço IP |
| :-------------- | :--------- |
| Zabbix Server 1 |            |
| Zabbix Server 2 |            |
| Banco de Dados   |            |
| IP Virtual       |            |

???+ note

    Nosso banco de dados (DB) nesta configuração não está configurado para HA. Como ele não é
    um componente do Zabbix, você precisará implementar sua própria solução para HA de banco de dados,
    como uma SAN HA ou uma configuração de cluster de banco de dados. A configuração de cluster de banco de dados
    está fora do escopo desta guia e não relacionada ao Zabbix, então ela não será abordada aqui.

---

## Instalando o Banco de Dados

Consulte a seção [_Componentes do Zabbix: Banco de Dados_](database.md) para instruções detalhadas
sobre como configurar o banco de dados. Essa seção fornece orientações passo a passo sobre como instalar um banco de dados PostgreSQL ou MariaDB em um nó dedicado executando
Ubuntu, SUSE ou Rocky Linux. Os mesmos procedimentos de instalação aplicam-se quando configurando o
banco de dados para esta configuração.

---

## Instalando o cluster Zabbix

Configurar um cluster Zabbix envolve configurar vários servidores Zabbix para trabalhar juntos,
providenciando alta disponibilidade. Embora o processo seja semelhante à configuração de um único servidor Zabbix, existem etapas adicionais de configuração necessárias para
ativar HA (Alta Disponibilidade).

Comece preparando os sistemas e instalando o servidor Zabbix em todos os sistemas conforme descrito nas seções [_Preparando o servidor para o Zabbix_](preparation.md) e
[_Instalando o servidor Zabbix_](zabbix-server.md) do capítulo _Componentes do Zabbix_.

Tenha em mente que:

- você precisa pular a etapa de população do banco de dados em todos os servidores, exceto no primeiro servidor Zabbix, pois
  o banco de dados é compartilhado entre todos os servidores Zabbix.
- você precisa pular a ativação e inicialização do serviço zabbix-server em todos os servidores,
  como iniciaremos mais tarde após a configuração HA ser concluída.
- certifique-se de que todos os servidores Zabbix podem se conectar ao servidor de banco de dados.
  Por exemplo, se você estiver usando PostgreSQL, assegure-se de que o arquivo `pg_hba.conf`
  esteja configurado para permitir conexões de todos os servidores Zabbix.
- todos os servidores Zabbix devem usar o mesmo nome do banco de dados, usuário e senha
  para se conectar ao banco de dados.
- todos os servidores Zabbix devem ser da mesma versão principal.

Quando todos os servidores Zabbix estiverem instalados e configurados para acessar o servidor de banco de dados,
podemos prosseguir com a configuração HA.

---

### Configurando o Servidor Zabbix 1

Adicione um novo arquivo de configuração para a configuração HA no primeiro servidor Zabbix:

!!! info "Adicionar configuração do servidor Zabbix HA"

    ``` bash
    sudo vi /etc/zabbix/zabbix_server.d/high-availability.conf
    ```


    Insira a seguinte linha no arquivo de configuração para habilitar o modo HA.

    ```ini
    HANodeName=zabbix1  # or choose a name you prefer
    ```


    Especifique o endereço do nó frontend para cenários de failover:

    ```ini
    NodeAddress=<Zabbix server 1 ip>:10051
    ```


???+ warning

    O `NodeAddress` deve corresponder ao IP ou nome FQDN do nó servidor Zabbix.
    Sem este parâmetro, o front-end Zabbix não será capaz de se conectar ao nó ativo.
    Como resultado, o front-end não poderá exibir o status da fila e outras informações.


---

### Configurando o Servidor Zabbix 2

Repita as etapas de configuração para o segundo servidor Zabbix. Ajuste os `HANodeName`
e `NodeAddress` conforme necessário para este servidor.

???+ example "Configuração HA do servidor Zabbix 2 high-availability.conf"

    ```ini
    HANodeName=zabbix2  # or choose a name you prefer
    NodeAddress=<Zabbix server 2 ip>:10051
    ```


Você pode adicionar mais servidores repetindo as mesmas etapas, garantindo que cada servidor tenha um `HANodeName` único
e o correto `NodeAddress` configurado.

---

### Iniciando o Servidor Zabbix

Após a configuração de ambos os servidores, habilite e inicie o serviço zabbix-server em cada um:

!!! info "Habilitar e iniciar o serviço zabbix-server"

    ```
    sudo systemctl enable zabbix-server --now
    ```


---

### Verificando a Configuração

Verifique os arquivos de log em ambos os servidores para garantir que eles tenham iniciado corretamente e
estejam operando nos respectivos modos HA.

No primeiro servidor:

!!! info "Verificar logs por mensagens HA"

    ``` bash
    sudo grep HA /var/log/zabbix/zabbix_server.log
    ```


Nos logs do sistema, você deve observar as seguintes entradas, indicando a inicialização
do Gerenciador de Alta Disponibilidade (HA):

???+ example "Mensagens de log HA no nó ativo"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22597:20240309:155230.353 starting HA manager
    22597:20240309:155230.362 HA manager started in active mode
    ```


Essas mensagens de log confirmam que o processo do gerenciador HA foi iniciado e assumiu
o papel ativo. Isso significa que a instância Zabbix agora é o nó principal no cluster HA, lidando com todas as operações de monitoramento. Se um evento de failover ocorrer,
outro nó standby assumirá baseado na estratégia HA configurada.

Executando o mesmo comando no segundo servidor (e em quaisquer nós adicionais):

???+ example "Mensagens de log HA no nó standby"

    ```shell-session
    localhost:~> sudo grep HA /var/log/zabbix/zabbix_server.log
    22304:20240309:155331.163 starting HA manager
    22304:20240309:155331.174 HA manager started in standby mode
    ```


Essas mensagens confirmam que o processo do gerenciador HA foi invocado e
lançado com sucesso no modo standby. Isso sugere que o nó está operacional,
mas não atuando como a instância HA ativa, aguardando transições de estado adicionais
baseadas na estratégia HA configurada.

Nesta etapa, seu cluster Zabbix foi bem configurado para Alta Disponibilidade (HA). Os logs do sistema confirmam que o gerenciador HA foi inicializado e está em execução no modo standby,
indicando que as mecânicas de failover estão em vigor. Esta configuração garante monitoramento ininterrupto, mesmo em caso de falha do servidor, permitindo transições automáticas de papel
baseadas na configuração HA.

---

## Instalando o frontend

Antes de prosseguir com a instalação e configuração do servidor web, é essencial instalar algum tipo de software de clustering ou usar um balanceador de carga
na frente dos frontends Zabbix para poder ter um IP Virtual compartilhado (VIP).

???+ note
    Existem várias opções disponíveis para software de clustering e balanceadores de carga,
    incluindo Pacemaker, Corosync, HAProxy, F5 Big-Ip, Citrix NetScaler e vários balanceadores de carga em nuvem.
    Cada uma dessas soluções oferece um conjunto variado de recursos e capacidades além de fornecer apenas um VIP para failover.
    Mas para o propósito desta guia, nos concentraremos em uma abordagem minimalista para alcançar alta disponibilidade para o frontend Zabbix usando Keepalived.

Keepalived é como um auxiliar que garante que um computador assuma se outro parar de funcionar. Ele dá a eles um IP mágico compartilhado
para que os usuários não percebam quando um servidor falha. Se o principal falhar, o backup entra em ação imediatamente ao assumir o IP.

Keepalived é um tipo minimalista de software de clustering que permite o uso de
um (VIP) para serviços front-end, garantindo failover transparente e continuidade do serviço.

!!! warning "Alta Disponibilidade no SUSE Linux Enterprise Server (SLES)"

    No SUSE Linux Enterprise Server (SLES), Keepalived não está incluído na
    assinatura padrão, portanto, não disponível nos repositórios padrão.

    Para ser capaz de instalar e usar o Keepalived no SLES de forma suportada,
    você precisará obter a assinatura adicional 'SUSE Linux Enterprise High Availability
    Extension' (SLE HA). Esta assinatura fornece acesso aos pacotes necessários e atualizações
    para Keepalived e outros componentes de alta disponibilidade.
    Após obter a assinatura, você pode habilitar os repositórios apropriados e prosseguir com a instalação do Keepalived conforme descrito nesta guia:

    ```bash
    SUSEConnect -p sle-ha/16/x86_64 -r ADDITIONAL_REGCODE
    ```

    Onde `ADDITIONAL_REGCODE` é o código de registro fornecido com sua
    'SUSE Linux Enterprise High Availability Extension' assinatura.

---

### Configurando keepalived

Em todos os servidores que hospedarão o frontend Zabbix, precisamos instalar o Keepalived.
Como mencionado anteriormente, isso pode ser feito em servidores separados para dividir as funções do servidor
e do front-end, mas nesta guia instalaremos o Keepalived nos dois servidores Zabbix para garantir alta disponibilidade tanto do frontend quanto do servidor.

!!! info "Instalar keepalived"

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


Em seguida, precisamos modificar a configuração do Keepalived em todos os servidores. Embora as
configurações sejam semelhantes, cada servidor requer ajustes sutis. Começaremos com o Servidor 1. Para editar o arquivo de configuração do Keepalived, use o seguinte comando:

!!! info "Editar a configuração keepalived"

    ```bash
    sudo vi /etc/keepalived/keepalived.conf
    ```


Se o arquivo contiver conteúdo existente, ele deve ser limpo e substituído
pelos seguintes parágrafos:

!!! info ""

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


???+ warning

    Substitua `enp0s1` pelo nome da interface de sua máquina e substitua o `password`
    por algo seguro. Para o `virtual_ipaddress`, use um IP livre da sua rede.
    Este será usado como nosso VIP.Nós podemos agora fazer a mesma modificação no nosso segundo ou qualquer servidor Zabbix subsequente.
Apague novamente tudo no arquivo `/etc/keepalived/keepalived.conf` como fizemos antes e substitua por linhas seguintes:

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


Assim como com o 1º servidor Zabbix, substitua `enp0s1` pelo nome da interface da sua máquina e substitua o `password` pela sua senha e preencha o `virtual_ipaddress` conforme feito antes.

Certifique-se de que o firewall permite o tráfego do Keepalived em todos os servidores. O protocolo VRRP é diferente do padrão IP e usa o endereço multicast `224.0.0.18`. Portanto, precisamos explicitamente permitir esse tráfego através do firewall. Execute os seguintes comandos em todos os servidores:

!!! info "Permita o tráfego do keepalived pelo firewall"

    Red Hat / SUSE
    ```yaml
    firewall-cmd --add-rich-rule='rule protocol value="vrrp" accept' --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```yaml
    sudo ufw allow to 224.0.0.18 comment ‘keepalived multicast’
    ```


Isso finaliza a configuração do Keepalived. Podemos agora continuar adaptando o frontend.

---

### Instalar e configurar o frontend

Instale o frontend Zabbix em todos os servidores Zabbix, parte da cluster seguindo as etapas descritas na seção [_Installing the frontend_](zabbix-frontend.md).

???+ warning

    Usuários do Ubuntu precisam usar o VIP na configuração do Nginx, junto com o IP local no diretivo listen da configuração.

???+ note

    Não se esqueça de configurar ambos os front-ends. Além disso, esta é uma nova configuração. Lembre-se que em uma configuração existente precisamos comentar as linhas `$ZBX_SERVER` e `$ZBX_SERVER_PORT` no arquivo `/etc/zabbix/web/zabbix.conf.php`. Nosso frontend verificará qual nó está ativo lendo a tabela de nós no banco de dados.

Você pode verificar qual nó está ativo consultando a tabela `ha_node` no banco de dados Zabbix. Esta tabela contém informações sobre todos os nós na cluster HA, incluindo seu status. Para verificar o status dos nós, você pode executar a seguinte consulta SQL:

!!! info ""

    ```sql
    select * from ha_node;

    ```


???+ example "Verifique a tabela ha_node em um banco de dados PostgreSQL"

    ```psql
    zabbix=> select * from ha_node;
             ha_nodeid         |  name   |   address       | port  | lastaccess | status |       ha_sessionid
    ---------------------------+---------+-----------------+-------+------------+--------+---------------------------
     cm8agwr2b0001h6kzzsv19ng6 | zabbix1 | xxx.xxx.xxx.xxx | 10051 | 1742133911 |      0 | cm8apvb0c0000jkkzx1ojuhst
     cm8agyv830001ell0m2nq5o6n | zabbix2 | localhost       | 10051 | 1742133911 |      3 | cm8ap7b8u0000jil0845p0w51
    (2 rows)
    ```


Neste caso, o nó `zabbix2` é identificado como o nó ativo, conforme indicado pelo seu valor de status `3`, que designa um estado ativo. Os possíveis valores de status são os seguintes:

- `0` – Múltiplos nós podem permanecer em modo standby.
- `1` – Um nó anteriormente detectado foi desligado.
- `2` – Um nó foi anteriormente detectado, mas ficou indisponível sem um desligamento adequado.
- `3` – O nó está atualmente ativo.

Esta classificação permite a monitoração e gerenciamento de estado efetivos dentro da cluster.

Uma vez que o frontend é instalado em todos os servidores, precisamos iniciar e habilitar o serviço Keepalived para garantir que ele inicie automaticamente no boot e comece a gerenciar o VIP:

!!! info "Iniciar e habilitar keepalived"

    ```yaml
    sudo systemctl enable keepalived nginx --now
    ```



---

### Verificar o funcionamento correto

Para verificar se a configuração está funcionando corretamente, acesse seu servidor Zabbix usando o IP Virtual (VIP). Navegue até `Reports` | `System Information` no menu. No final da página, você deve ver uma lista de servidores, com pelo menos um marcado como ativo. O número de servidores exibidos dependerá do total configurado em sua configuração HA.

![1ª frente ativa](ha-setup/ch01.11-HA-check1.png)

_1.11 verificar
HA_

Desligue ou reinicie o servidor frontend ativo e observe que o Zabbix frontend permanece acessível. Ao recarregar a página, você notará que outro frontend tomou conta como instância ativa, garantindo um failover quase imperceptível e alta disponibilidade.

![2ª frente ativa](ha-setup/ch01.12-HA-check2.png)

_1.12 verificar
HA_

Além de monitorar o status dos nós HA, o Zabbix fornece vários comandos em tempo real que permitem aos administradores gerenciar configurações de failover e remover dinamicamente nós inativos.

Um desses comandos é:

!!! info ""

    ```bash
    zabbix_server -R ha_set_failover_delay=10m
    ```


Este comando ajusta o atraso do failover, que define quanto tempo o Zabbix espera antes de promover um nó standby para status ativo. O atraso pode ser configurado dentro de uma faixa de **10 segundos** a **15 minutos**.

Para remover um nó que está ou seja **parado** ou **inacessível**, deve-se usar o seguinte comando em tempo real:

!!! info ""

    ```bash
    sudo zabbix_server -R ha_remove_node=`zabbix1`
    ```


A execução deste comando remove o nó da cluster HA. Após a remoção bem-sucedida, a saída confirma a ação:

!!! example "Remoção de um nó"

    ```shell-session
    localhost:~ # zabbix_server -R ha_remove_node=`zabbix1`
    Removed node "zabbix1" with ID "cm8agwr2b0001h6kzzsv19ng6"
    ```


Se o nó removido se tornar disponível novamente, ele pode ser adicionado automaticamente quando reconectar à cluster. Esses comandos em tempo real fornecem flexibilidade para gerenciar alta disponibilidade no Zabbix sem exigir um reinício completo do processo `zabbix_server`.

---

## Conclusão

Nesta seção, configuramos com sucesso um ambiente de alta disponibilidade (HA) Zabbix ao configurar tanto o servidor quanto o frontend Zabbix para redundância. Primeiro, estabelecemos HA para o servidor Zabbix, garantindo que os serviços de monitoramento permaneçam disponíveis mesmo em caso de falha. Em seguida, focamos no frontend, implementando um IP Virtual (VIP) com Keepalived para fornecer failover sem interrupção e acesso contínuo.

Além disso, configuramos o firewall para permitir o tráfego do Keepalived e garantimos que o serviço inicie automaticamente após uma reinicialização. Com essa configuração, o frontend Zabbix pode alternar dinamicamente entre servidores, minimizando o tempo de inatividade e melhorando a confiabilidade.

Embora a alta disponibilidade do banco de dados seja uma consideração importante, ela está fora do escopo desta configuração. No entanto, essa base fornece um ponto de partida robusto para construir uma infraestrutura de monitoramento resiliente que pode ser aprimorada conforme necessário.

---

## Perguntas

1. O que é Zabbix High Availability (HA) e por que é importante?
2. Como o Zabbix determina qual nó está ativo em uma configuração HA?
3. É possível ter múltiplos nós do Zabbix simultaneamente ativos em um cluster HA? Por quê ou por que não?
4. Quais arquivos de configuração são necessários para habilitar HA no Zabbix?

---

## URLs Úteis

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
- <https://www.zabbix.com/documentation/current/en/manual/concepts/server/ha>