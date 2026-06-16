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

Neste capítulo, explicaremos o que é um proxy, por que você pode precisar dele
ou considerá-lo, quais são os requisitos básicos e qual é a diferença entre
_Proxies ativos_ e _Proxies passivos_.

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

???+ dica

    To ensure smooth communication, it is considered best practice to allocate two 
    trapper processes per _Active proxy_ on the _Zabbix server_. This configuration 
    optimizes performance and prevents potential bottlenecks.

![Comunicação proxy ativa](ch03-active-communication.png)

_3.1 Comunicação de proxy ativo_

---

### Proxy passivo

Ao contrário de um _proxy ativo_ , um _proxy no modo passivo_ terá suas
configurações operacionais controladas pelo _servidor Zabbix_ .

Portanto, a configuração dos proxies _passivos_ requer alterações nos arquivos
de configuração do servidor _Zabbix_ e do proxy _Zabbix_, pois agora é o
servidor que controla quando e como os dados do proxy são solicitados por meio
do uso de pollers.

As configurações mais importantes que podemos encontrar no arquivo de
configuração do _proxy_ são:

- `ProxyMode`: `1` - Define o proxy no modo 'Passivo'.
- `Servidor:` IP ou DNS do servidor _Zabbix_
- `ProxyOfflineBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas) se não conseguirmos acessar o servidor _Zabbix_.
- `ProxyLocalBuffer`: Por quanto tempo gostaríamos de manter os dados no banco
  de dados (em horas), mesmo quando já tiverem sido enviados para o servidor
  _Zabbix_.

E, finalmente, as definições de configuração que precisamos alterar em nosso
servidor _Zabbix_:

- `StartProxyPollers`: O número de pollers para contatar proxies.
- `ProxyConfigFrequency`: Substitui o `ConfigFrequency` e define a frequência
  com que o _Zabbix Server_ enviará alterações de configuração para todos os
  proxies.
- `ProxyDataFrequency`: Com que frequência o servidor _Zabbix_ solicitará dados
  monitorados de nossos proxies.

???+ dica

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

![Comunicação proxy passiva](ch03-passive-communication.png)

_3.2 Comunicação proxy passiva_

---

## Opções de controle de tempo de execução de proxy

Assim como o servidor _Zabbix_, nosso proxy oferece suporte a opções de controle
de tempo de execução. Sempre verifique as opções mais recentes com a opção
`--help`. Mas aqui está uma breve visão geral das opções disponíveis para uso.

`zabbix_proxy --runtime-control housekeeper_execute`

: Aciona a execução imediata do processo housekeeper do Zabbix no proxy. O
housekeeper é responsável pela limpeza de dados desatualizados (por exemplo,
histórico antigo, tendências ou eventos) de acordo com os períodos de retenção
configurados no Zabbix. Esse comando força o housekeeper a ser executado agora,
em vez de aguardar o intervalo programado.

`zabbix_proxy --runtime-control log_level_increase=target`

: Aumenta o nível de verbosidade do registro para um processo-alvo específico
(por exemplo, por tipo, como `configuration syncer`, `housekeeper`, `icmp
pinger`, por tipo e número, como `poller,3` ou por PID). Isso é útil para
depuração ou solução de problemas, pois fornece uma saída de registro mais
detalhada para o alvo especificado. Para obter uma lista completa dos alvos
disponíveis, consulte a [man-page of
`zabbix_proxy`](https://www.zabbix.com/documentation/current/en/manpages/zabbix_proxy).
*Exemplo*: `log_level_increase="http poller"` tornaria os registros relacionados
ao http poller mais detalhados.

`zabbix_proxy --runtime-control log_level_decrease=target`

: Diminui o nível de verbosidade do registro para um destino específico,
reduzindo a quantidade de saída de registro gerada. Isso é útil para diminuir o
ruído nos registros após a depuração ou para otimizar o desempenho reduzindo a
sobrecarga de E/S. *Exemplo*: `log_level_decrease=trapper,2` reduziria a
verbosidade dos registros relacionados ao trapper do segundo processo do
trapper.

`zabbix_proxy --runtime-control snmp_cache_reload`

: Força o proxy a recarregar seu cache de SNMP. Isso é útil se você tiver feito
alterações nas configurações de SNMP (por exemplo, cadeias de caracteres de
comunidade, OIDs ou IPs de dispositivos atualizados) e quiser que o proxy
obtenha imediatamente as novas configurações sem reiniciar todo o serviço.

`zabbix_proxy --runtime-control diaginfo=section`

: Gera informações de diagnóstico para uma seção específica da operação do
proxy. Normalmente, isso é usado para solução de problemas ou análise de
desempenho. O parâmetro section pode visar áreas como cache de histórico,
pré-processamento ou bloqueios. *Exemplo*: `diaginfo=preprocessing` forneceria
estatísticas detalhadas sobre o gerenciador de pré-processamento.

---

## Firewall de proxy

Nossos proxies funcionam como pequenos servidores _Zabbix_, portanto, quando se
trata de portas para conexão com agentes, SNMP, ... nada muda, todas as portas
precisam ser configuradas da mesma forma que em um servidor _Zabbix_.

Quando se trata da porta para o proxy, isso depende do fato de nosso proxy ser
`ativo` ou `passivo`.

- **Proxy ativo:** O servidor Zabbix precisa ter a porta `10051/tcp` aberta para
  que o proxy possa se conectar.
- **Proxy passivo:** Precisa ter a porta `10051/tcp` aberta no proxy para que o
  `servidor ` possa se conectar ao proxy.

Observe que, para que um agente _Zabbix ativo_ ou um _remetente Zabbix_ se
comunique com seu proxy, seja ele ativo ou passivo, será necessário que a porta
`10051/tcp` esteja aberta em seu servidor proxy:

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
