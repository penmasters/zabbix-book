---
description: |
    This chapter from The Zabbix Book, titled "Proxy Basics," introduces the role
    of proxies in a Zabbix environment. It explains how proxies collect monitoring
    data, forward it to the server, and help reduce load in distributed setups.
    The guide covers installation, configuration, and when to use proxies for
    scalability and efficiency.
tags: [beginner]
---

# Proxy basics

In this chapter we will explain what a proxy is, why you may need or consider
it, what the basic requirements are and what the difference is between _Active
proxies_ and _Passive proxies_.

---

## O que é um Zabbix Proxy

Um proxy Zabbix é, na verdade, um tipo de processo leve do servidor Zabbix que
coleta dados de monitoramento de dispositivos em nome do servidor Zabbix real.
Ele foi projetado para descarregar o servidor ao lidar com tarefas de coleta de
dados, o que é particularmente útil em ambientes distribuídos ou ao monitorar
locais remotos com conectividade limitada.

O proxy reúne os dados de desempenho e disponibilidade solicitados dos
dispositivos, aplicativos e serviços monitorados e, em seguida, encaminha essas
informações para o servidor Zabbix para processamento e armazenamento. Essa
arquitetura ajuda a reduzir o tráfego de rede, simplifica as configurações de
firewall de rede e melhora a eficiência geral do seu sistema de monitoramento.

Em resumo, um proxy Zabbix pode ser usado para:

- Monitore locais remotos
- Monitore dispositivos em segmentos de rede separados
- Monitore os locais que têm conexões não confiáveis
- Descarregue o servidor Zabbix ao monitorar milhares de dispositivos
- Simplifique a manutenção e o gerenciamento

---

## Requisitos de proxy

Se quiser configurar alguns proxies para testes ou em seu ambiente de produção,
você precisará de alguns hosts Linux para a instalação. Embora os proxies também
estejam disponíveis como contêineres (portanto, você não precisa necessariamente
de VMs completas), usaremos uma VM nesta demonstração para mostrar o processo de
instalação. Não se preocupe, também abordaremos as implementações de
contêineres.

Embora os proxies sejam geralmente leves, desde o Zabbix 4.2 eles podem executar
o pré-processamento do valor do item, o que pode exigir muito da CPU. Portanto,
o número de CPUs e de memória de que você precisará depende de:

- Quantas máquinas você estará monitorando
- Quantas regras de pré-processamento você implementará em seus hosts

---

### Atualizações da configuração do proxy

Para que um proxy saiba quais dispositivos deve monitorar, ele receberá
atualizações de configuração do servidor _servidor Zabbix_. Elas incluem:

- Itens de monitoramento, acionadores ou modelos novos ou modificados atribuídos
  ao proxy.
- Alterações nas configurações do host ou nas regras de coleta de dados.

Antes do Zabbix 7.0, uma sincronização completa da configuração era realizada
pelos proxies a cada 3600 segundos (1 hora) por padrão. Com a introdução do
Zabbix 7.0, esse comportamento mudou significativamente. Agora, a sincronização
da configuração ocorre com muito mais frequência, a cada 10 segundos por padrão,
mas é uma atualização incremental. Isso significa que, em vez de transferir toda
a configuração, apenas as entidades modificadas são sincronizadas, o que aumenta
muito a eficiência e reduz a sobrecarga da rede.

Na inicialização do proxy, ainda é realizada uma sincronização completa da
configuração. Posteriormente, tanto o servidor quanto o proxy mantêm uma revisão
da configuração. Quando uma alteração é feita no servidor, somente as
diferenças, com base nesses números de revisão, são aplicadas à configuração do
proxy, em vez de uma substituição completa de toda a configuração, como nas
versões anteriores. Essa abordagem incremental permite a propagação quase em
tempo real das alterações de configuração e, ao mesmo tempo, minimiza o consumo
de recursos.

???+ nota: Configurações de configuração versus atualizações de configuração

    When working with a Zabbix proxy, it’s important to distinguish between two 
    types of "configuration":

    - **Proxy Configuration Settings**

    :   These are the local settings defined in the proxy’s configuration file. 
        They control how the proxy operates.

    - **Configuration Updates from the Zabbix Server**

    :   These are dynamic updates pushed by the Zabbix server to the proxy.
        They include:

        - New or modified monitoring items, triggers, or templates assigned to the proxy.
        - Changes to host configurations or data collection rules. 

---

## Limitação de proxy

Imagine que você precise reiniciar seu servidor Zabbix e que todos os proxies
comecem a enviar os dados que coletaram durante o tempo de inatividade do
servidor Zabbix.

Isso criaria uma enorme quantidade de dados sendo enviados ao mesmo tempo para o
servidor Zabbix e possivelmente o deixaria de joelhos em pouco tempo. Desde a
versão 6, o Zabbix adicionou uma proteção para esse tipo de situação. Quando o
cache de histórico do Zabbix Server estiver cheio, o acesso de gravação do cache
de histórico será limitado: o Zabbix Server deixará de aceitar dados de proxies
quando o uso do cache de histórico atingir 80%. Em vez disso, esses proxies
serão colocados em uma lista de limitação. Isso continuará até que o uso do
cache caia para 60%. Agora o servidor começará a aceitar dados dos proxies um a
um, definidos pela lista de limitação. Isso significa que o primeiro proxy que
tentou fazer upload de dados durante o período de limitação será atendido
primeiro e, até que isso seja feito, o servidor não aceitará dados de outros
proxies.

Esta tabela lhe dá uma visão geral de como e quando o throttling funciona no
Zabbix.

| Uso do cache de gravação do histórico | Modo de servidor Zabbix | Ação do servidor Zabbix                                                                                                             |
| ------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Alcança 80%                           | Esperar                 | Deixa de aceitar dados de proxy, mas mantém uma lista de limitação (lista priorizada de proxies a serem contatados posteriormente). |
| Cai para 60%                          | Limitado                | Começa a processar a lista de limitação, mas ainda não aceita dados de proxy.                                                       |
| Cai para 20%                          | Normal                  | Elimina a lista de limitação e começa a aceitar dados de proxy normalmente.                                                         |

Isso pode causar atrasos na detecção de problemas, pois você terá que esperar
que todos os dados relevantes sejam recebidos e processados pelo servidor
Zabbix, mas você não perderá nenhum dado histórico.

---

## Proxy ativo versus passivo

Os proxies do Zabbix estão disponíveis desde o Zabbix 1.6. Naquela época, eles
estavam disponíveis apenas como o que conhecemos hoje como **Active proxies**.
_Active_ significa que o proxy iniciará a conexão por si só com o Zabbix Server.
Na versão 1.8.3, foram introduzidos os proxies _passivos_. Isso permite que o
servidor se conecte ao proxy, e não o contrário.

Conforme mencionado anteriormente, os agentes do Zabbix podem ser ativos _e
passivos_. No entanto, os proxies não podem ser ambos, portanto, temos que
escolher a forma de comunicação quando configuramos um proxy.

???+ nota "Agente ativo/passivo no proxy ativo/passivo?

    Remember that choosing the proxy mode _active_ or _passive_ has no impact on 
    how Zabbix agents can communicate with this proxy. It's perfectly fine to have
    an _active proxy_ and a _passive agent_ working together.

---

### Proxy ativo

No modo _active_, o proxy assume o controle total de suas configurações
operacionais. Isso inclui gerenciar quando ele verifica se há novas atualizações
de configuração e quando envia os dados coletados para o servidor.

É importante observar que as principais configurações de um _proxy ativo_ são
definidas exclusivamente na configuração do _proxy Zabbix_ . Qualquer ajuste
nesses parâmetros deve ser feito diretamente nos arquivos de configuração do
proxy.

Essas são as definições de configuração de proxy que você precisará definir no
modo _active_:

- `ProxyMode`: `0` - Define o proxy no modo 'Ativo'
- `Servidor`: IP ou DNS do servidor Zabbix
- `Hostname`: Nome do proxy - precisa ser exatamente o mesmo que o configurado
  no frontend.
- `ProxyOfflineBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas) se não conseguirmos acessar o servidor _Zabbix_.
- `ProxyLocalBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas), mesmo quando já tiverem sido enviados para o servidor
  _Zabbix_.
- `ProxyConfigFrequency`: Substitui o `ConfigFrequency` em versões anteriores e
  define a frequência com que solicitamos atualizações de configuração (a cada
  10 segundos) do _Zabbix Server_.
- `DataSenderFrequency`: Com que frequência os dados são enviados para o
  servidor _Zabbix_ (a cada segundo).

Ao configurar recursos para um _proxy ativo_ , é importante levar em conta seu
comportamento de conexão com o _servidor Zabbix_ . Durante a operação, o proxy
pode utilizar até dois processos trapper no servidor:

- Um trapper é dedicado a enviar os dados coletados para o servidor.
- O outro trapper é reservado para recuperar atualizações de configuração.

???+ tip

    To ensure smooth communication, it is considered best practice to allocate two 
    trapper processes per _Active proxy_ on the _Zabbix server_. This configuration 
    optimizes performance and prevents potential bottlenecks.

![Active proxy communication](ch03-active-communication.png)

_3.1 Active proxy communication_

---

### Proxy passivo

In contrast to an _active proxy_, a proxy in _passive_ mode will have its
operational settings controlled by the _Zabbix server_.

Hence, configuring _passive_ proxies requires changes in in both the _Zabbix
server_ and the _Zabbix proxy_ configuration files as it is now the server that
controls when and how proxy data is requested by making use of pollers.

The most important setting we can find back in the _proxy_ configuration file
are:

- `ProxyMode`: `1` - Sets the proxy in 'Passive' mode
- `Server:` IP or DNS of the _Zabbix server_
- `ProxyOfflineBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas) se não conseguirmos acessar o servidor _Zabbix_.
- `ProxyLocalBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas), mesmo quando já tiverem sido enviados para o servidor
  _Zabbix_.

And finally the config settings we need to change on our _Zabbix server_:

- `StartProxyPollers`: The number of pollers to contact proxies.
- `ProxyConfigFrequency`: Replaces `ConfigFrequency` and defines how often
  _Zabbix server_ will sent configuration changes to all proxies.
- `ProxyDataFrequency`: How often _Zabbix server_ will request monitored data
  from our proxies.

???+ tip

    It is not required for `StartProxyPollers` to be equal to the number of 
    passive proxies you have as one poller can poll multiple proxies. The 
    recommended value however depends on your environment and workload. If you
    have multiple passive proxies and experience delays in configuration updates
    or incoming item values, you may increase this value. However, it is a good 
    practice to start with 1, monitor the performance and adjust in accordance.

    Zabbix provides out-of-the-box templates for monitoring _Zabbix server_ and 
    _Zabbix proxies_ internal metrics. Make sure to use them and closely watch
    the value of the `zabbix[proxy_history]` item on the proxies which represents
    the number of values the proxy has received that are yet to be sent to the 
    _Zabbix server_. 

![Passive proxy communication](ch03-passive-communication.png)

_3.2 Passive proxy communication_

---

## Proxy runtime control options

Just like the _Zabbix server_ our proxy supports runtime control options always
check latest options with the `--help` option. But here is a short overview of
options available to use.

`zabbix_proxy --runtime-control housekeeper_execute`

: Triggers the immediate execution of the Zabbix housekeeper process on the
proxy. The housekeeper is responsible for cleaning up outdated data (e.g., old
history, trends, or events) according to the configured retention periods in
Zabbix. This command forces the housekeeper to run now, instead of waiting for
its scheduled interval.

`zabbix_proxy --runtime-control log_level_increase=target`

: Increases the log verbosity level for a specific target process (e.g., by type
like `configuration syncer`, `housekeeper`, `icmp pinger`, by type and number
like `poller,3` or by PID). This is useful for debugging or troubleshooting, as
it provides more detailed log output for the specified target. For a full list
of available targets, check the [man-page of
`zabbix_proxy`](https://www.zabbix.com/documentation/current/en/manpages/zabbix_proxy).
*Example*: `log_level_increase="http poller"` would make http poller-related
logs more verbose.

`zabbix_proxy --runtime-control log_level_decrease=target`

: Decreases the log verbosity level for a specific target, reducing the amount
of log output generated. This is helpful to lower noise in logs after debugging
or to optimize performance by reducing I/O overhead. *Example*:
`log_level_decrease=trapper,2` would reduce the verbosity of trapper-related
logs of the second trapper process.

`zabbix_proxy --runtime-control snmp_cache_reload`

: Forces the proxy to reload its SNMP cache. This is useful if you've made
changes to SNMP configurations (e.g., updated community strings, OIDs, or device
IPs) and want the proxy to immediately pick up the new settings without
restarting the entire service.

`zabbix_proxy --runtime-control diaginfo=section`

: Generates diagnostic information for a specific section of the proxy’s
operation. This is typically used for troubleshooting or performance analysis.
The section parameter can target areas like history cache, preprocessing or
locks. *Example*: `diaginfo=preprocessing` would provide detailed statistics
about the preprocessing manager.

---

## Proxy firewall

Our proxies work like small _Zabbix servers_ so when it comes to the ports to
connect to agents, SNMP, ... nothing changes, all ports need to be configured
the same as you would on a _Zabbix server_.

When it comes to port for the proxy it depends on our proxy being `active` or
`passive`.

- **Active Proxy:** Zabbix server needs to have port `10051/tcp` open so proxy
  can connect.
- **Passive Proxy:** Needs to have port `10051/tcp` open on the proxy so that
  the `server` can connect to the proxy.

Do note that for an active _Zabbix Agent_ or _Zabbix Sender_ to communicate with
your proxy, whether it is an active or a passive one, this will require port
`10051/tcp` to be open on your proxy server:

!!! info "Abra o firewall para o zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```
