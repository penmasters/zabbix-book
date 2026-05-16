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

## Proxy throttling

Imagine that you need to restart your Zabbix server and that all proxies start
to push the data they have gathered during the downtime of the Zabbix server.

This would create a huge amount of data being sent at once to the Zabbix server
and possibly bring it to its knees in no time. Since version 6, Zabbix has added
protection for this kind of situations. When the Zabbix server history cache is
full the history cache write access is being throttled: Zabbix server will stop
accepting data from proxies when history cache usage reaches 80%. Instead those
proxies will be put on a throttling list. This will continue until the cache
usage falls down to 60%. Now the server will start accepting data from the
proxies one by one, defined by the throttling list. This means the first proxy
that attempted to upload data during the throttling period will be served first
and until it's done the server will not accept data from other proxies.

This table gives you an overview of how and when throttling works in Zabbix.

| History write cache usage | Zabbix server mode | Zabbix server action                                                                                             |
| ------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------- |
| Reaches 80%               | Wait               | Stops accepting proxy data, but maintains a throttling list (prioritized list of proxies to be contacted later). |
| Drops to 60%              | Throttled          | Starts processing throttling list, but still not accepting proxy data.                                           |
| Drops to 20%              | Normal             | Drops the throttling list and starts accepting proxy data normally.                                              |

This may cause delays in detection of problems, as you will have to wait for all
relevant data to be received and processed by the Zabbix server; but you won't
lose any historical data.

---

## Active versus Passive proxy

Zabbix proxies have been available since Zabbix 1.6. At that time they where
available only as what we know today as **Active proxies**. _Active_ means that
the proxy will initiate the connection by itself to the Zabbix Server. In
version 1.8.3 _passive_ proxies where introduced. This allows the server to
connect to the proxy instead of the other way around.

As mentioned before Zabbix agents can be both active _and_ passive however
proxies cannot be both so we have to choose the way of the communication when we
configure a proxy.

???+ note "Active/Passive agent on Active/Passive proxy ?"

    Remember that choosing the proxy mode _active_ or _passive_ has no impact on 
    how Zabbix agents can communicate with this proxy. It's perfectly fine to have
    an _active proxy_ and a _passive agent_ working together.

---

### Proxy ativo

In _active_ mode, the proxy takes full control of its operational settings. This
includes managing when it checks for new configuration updates and when it sends
collected data to the server.

It’s important to note that the key settings for an _active proxy_ are defined
exclusively in the _Zabbix proxy_ configuration. Any adjustments to these
parameters should be made directly within the proxy configuration files.

These are the proxy configuration settings you will need to set in _active_
mode:

- `ProxyMode`: `0` - Sets the proxy in 'Active' mode
- `Server`: IP or DNS of the Zabbix server
- `Hostname`: Proxy name - this needs to be exactly the same as configured in
  the frontend.
- `ProxyOfflineBuffer`: How long we like to keep data in the DB (in hours) if we
  can't reach the _Zabbix server_.
- `ProxyLocalBuffer`: How long we like to keep data in the DB (in hours) even
  when it is already sent to the _Zabbix server_.
- `ProxyConfigFrequency`: Replaces `ConfigFrequency` in earlier versions and
  defines how often we request configuration updates (every 10 seconds) from the
  _Zabbix server_.
- `DataSenderFrequency`: How often data is sent to _Zabbix server_ (every
  second).

When configuring resources for an _Active proxy_, it’s important to account for
its connection behavior with the _Zabbix server_. During operation, the proxy
can utilize up to two trapper processes on the server:

- One trapper is dedicated to sending collected data to the server.
- The other trapper is reserved for retrieving configuration updates.

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
- `ProxyOfflineBuffer`: How long we like to keep data in the DB (in hours) if we
  can't reach the _Zabbix server_.
- `ProxyLocalBuffer`: How long we like to keep data in the DB (in hours) even
  when it is already sent to the _Zabbix server_.

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
