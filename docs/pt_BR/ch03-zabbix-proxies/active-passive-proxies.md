---
description: |
    This chapter from The Zabbix Book, titled "Active and Passive Proxies," explores
    the two proxy modes available in Zabbix. It explains how active proxies push
    data to the server, while passive proxies wait for polling requests. The guide
    covers setup, use cases, and how to choose the right mode for your environment.
tags: [advanced]
---

# Proxies ativos e passivos

Independentemente de você querer instalar um proxy ativo ou passivo, grande
parte das etapas de instalação e configuração são as mesmas.

---

## Configuração da GUI do Zabbix

Há duas coisas que precisamos fazer quando queremos configurar um proxy Zabbix e
uma dessas etapas é adicionar o proxy no frontend do Zabbix. Então, no menu,
vamos selecionar `Administration` => `Proxies` e clicar no canto superior
direito em `Create proxy`.

![Criar proxy](ch03-add-active-proxy.png)

_3.3 Criar proxy_

Uma vez pressionado, um novo formulário modal será exibido, no qual precisaremos
preencher algumas informações.

---

### Proxy ativo

Para proxies ativos, só precisamos digitar o campo _Proxy name_. Aqui,
digitaremos `ProxyA` para nos lembrar de que esse será um proxy ativo. Não se
preocupe com os outros campos, pois eles serão abordados posteriormente. No
campo _Description_, você pode inserir algum texto para deixar ainda mais claro
que este é um proxy ativo.

???+ nota

    For Zabbix active proxies, you only need to specify the hostname during configuration.
    This hostname acts as the unique identifier that the Zabbix server uses to distinguish
    between different active proxies and manage their data correctly.

![Proxy ativo](ch03-new-active-proxy.png)

_3.4 Novo proxy_

---

### Proxy passivo

Para o proxy passivo, digitaremos `ProxyP` como _Nome do proxy_, mas agora
também precisamos especificar o campo _Interface_. Aqui adicionamos o IP do host
em que nosso proxy é executado. Você também notou que usamos a mesma porta
`10051` que o servidor Zabbix __ para nos comunicarmos com o nosso proxy.

![Proxy passivo](ch03-new-passive-proxy.png)

_3.5 Novo proxy passivo_

---

## Instalando o proxy

Em seguida, precisamos colocar o software proxy Zabbix em um sistema que
funcionará como Zabbix Proxy. Configure um novo sistema ou VM e certifique-se de
que ele atenda aos requisitos descritos no capítulo [_Vamos começar:
Requerimentos_](../ch00-getting-started/Requirements.md).

Como o proxy do Zabbix é, na verdade, um pequeno _servidor Zabbix_, também
precisamos nos certificar de que o sistema esteja preparado para o Zabbix,
conforme descrito em [_Preparando o servidor para o
Zabbix_](../ch00-getting-started/preparation.md).

Agora que seu sistema está pronto e sabe onde encontrar os pacotes de software
Zabbix, podemos realmente instalar o software Zabbix Proxy. É bastante simples,
mas há uma coisa que precisamos decidir antecipadamente. Os proxies do Zabbix
precisam de um local para armazenar suas informações e podem usar uma destas
três opções: MySQL/MariaDB, PostgreSQL ou SQLite3.

Abordaremos apenas o SQlite, pois o MySQL e o PostgreSQL já foram abordados no
capítulo [_Zabbix componentes e instalação:
Database_](../ch01-zabbix-components/database.md).

???+ nota

    The only thing that is a bit different when you setup a MySQL or
    PostgreSQL database for use with a Zabbix Proxy instead of a Zabbix Server 
    are the scripts you will need to setup the DB structure. 

    - For MySQL/MariaDB they are located in `/usr/share/zabbix/sql-scripts/mysql/proxy.sql`.
    - For PostgreSQL they can be found in `/usr/share/zabbix/sql-scripts/postgresql/proxy.sql`.

!!! info "Instalar zabbix-proxy-sqlite3"

    Red Hat
    ```
    dnf install zabbix-proxy-sqlite3
    ```

    SUSE
    ```
    zypper install zabbix-proxy-sqlite3
    ```

    Ubuntu
    ```
    sudo apt install zabbix-proxy-sqlite3
    ```

???+ dica

    If you want to use MySQL or PostgreSQL then you can use the package `zabbix-proxy-mysql`
    or `zabbix-proxy-pgsql` depending on your needs.

---

## Configuração do proxy

Agora que instalamos os pacotes necessários, ainda precisamos fazer algumas
alterações na configuração.

Assim como no servidor Zabbix (ou no agente, nesse caso), o arquivo de
configuração oferece uma opção para incluir arquivos de configuração adicionais
para parâmetros personalizados. Em geral, e especialmente em um ambiente de
produção, é melhor evitar alterar diretamente o arquivo de configuração
original. Em vez disso, você pode criar e incluir arquivos de configuração
separados para quaisquer parâmetros adicionais ou modificados.

No SUSE 16 e posterior, esse recurso já está ativado e configurado por padrão em
`/usr/etc/zabbix/zabbix_proxy.conf`.

Em outras distribuições, talvez seja necessário ativá-lo manualmente em
`/etc/zabbix/zabbix_proxy.conf`.

Para ativar esse recurso, certifique-se de que a próxima linha exista e não
esteja comentada (com um `#` na frente dela):

!!! info ""

    ```ini
    Include=/etc/zabbix/zabbix_proxy.d/*.conf
    ```

O caminho `/etc/zabbix/zabbix_proxy.d/` já deve ter sido criado pelo pacote
instalado, mas verifique se ele realmente existe.

Agora, criaremos um arquivo de configuração personalizado `general.conf` neste
diretório `/etc/zabbix/zabbix_proxy.d/` que conterá algumas configurações gerais
de proxy:

- A primeira opção que teremos de definir é `ProxyMode`:
    - Defina isso como `0` para um proxy _Ativo_.
    - Defina isso como `1` para um proxy _Passivo_.

- A outra opção importante é a `Server`, cujo padrão é `127.0.0.1`, portanto,
  precisamos substituí-la pelo IP ou nome DNS do nosso _Zabbix Server_.

???+ nota

    You can fill in multiple servers here in case you have more than one _Zabbix Server_
    connecting to your proxy. Also the port can be added here in case your server
    listens on another port then the standard port `10051`. Just be careful to not
    add the IP and DNS name for the same server as this can return double values.

- Outra opção importante é `Hostname`, especialmente em um proxy _Active_.
  Lembre-se de que, em nosso frontend, demos ao nosso proxy _Active_ o nome
  `ProxyA`, portanto, agora temos que preencher exatamente o mesmo nome aqui
  para o hostname. Assim como um agente _Zabbix_ no modo _active_ _ Zabbix
  server_ usará o nome como um identificador exclusivo.\
  Para um proxy _passivo_, essa opção é menos importante, mas, para maior
  clareza, é melhor mantê-la igual: `ProxyP` no nosso caso.

- Em um_Proxy ativo_ , você também pode considerar a configuração de
  `ProxyConfigFrequency` e `DataSenderFrequency` para ajustar a comunicação com
  o _Servidor Zabbix_ , mas, de modo geral, os padrões devem ser suficientes.

- Outras opções a serem consideradas são `ProxyOfflineBuffer` e
  `ProxyLocalBuffer` para garantir que o proxy possa acompanhar as interrupções
  do servidor Zabbix e a quantidade de dados monitorados que ele ingere.

O arquivo `general.conf` agora deve ter pelo menos a seguinte aparência:

???+ exemplo "/etc/zabbix/zabbix_proxy.d/general.conf"

    ``` ini
    ProxyMode=0
    Server=192.168.0.50
    Hostname=ProxyA
    ```

Para definir as configurações do banco de dados, crie um arquivo de configuração
dedicado em `/etc/zabbix/zabbix_proxy.d/database.conf`. Esse arquivo conterá os
parâmetros de conexão do banco de dados.

Para implementações do SQLite3, apenas o parâmetro `DBName` requer configuração,
especificando o caminho para o arquivo de banco de dados. O Zabbix Proxy criará
e utilizará automaticamente esse arquivo de banco de dados em sua inicialização.

???+ exemplo "/etc/zabbix/zabbix_proxy.d/database.conf"

    ```ini
    DBName=/var/lib/zabbix/zabbix_proxy.db
    ```

Você pode escolher qualquer local para o arquivo de banco de dados, mas deve se
certificar de que o diretório existe e pode ser gravado pelo processo do Zabbix
proxy.

Em nosso exemplo, escolhemos o _home_-dir padrão do `zabbix`-user conforme
configurado pelos pacotes do Zabbix. Você pode verificar o diretório inicial do
usuário em seu host usando o comando `getent passwd`:

Exemplo "Verifique o homedir padrão do usuário zabbix"

    ```shell-session
    localhost:~>getent passwd zabbix
    zabbix:x:476:476:Zabbix Monitoring System:/var/lib/zabbix:/sbin/nologin
    ```

Verifique se o diretório existe com as permissões corretas e o contexto do
SELinux:

???+ example "Check existence of zabbix home-directory"

    ```shell-session
    localhost:~>ls -laZ /var/lib/zabbix
    total 0
    drwxr-xr-x. 1 zabbix zabbix unconfined_u:object_r:zabbix_var_lib_t:s0   0 Jan 10 20:01 .
    drwxr-xr-x. 1 root   root   system_u:object_r:var_lib_t:s0            364 Jan 10 20:05 ..
    ```

If the directory does not exist, is not owned by user `zabbix` or is missing the
SELinux label `zabbix_var_lib_t`, then you will need to correct this:

!!! info "Create zabbix home-dir"

    ```bash
    # Create the directory
    mkdir /var/lib/zabbix
    # Make user/group zabbix owner 
    chown zabbix:zabbix /var/lib/zabbix
    # Restore SELinux context labels
    restorecon -Rv /var/lib/zabbix
    ```

???+ dica

    See [_Advanced security: SELinux_](../ch13-advanced-security/selinux-zabbix.md)
    chapter for more details about SELinux and Zabbix.

???+ note "MariaDB/MySQL or PostgreSQL as database for Zabbix proxy"

    If you chose to use MariaDB/MySQL or PostgreSQL, please refer to [_Installing the Zabbix server_](../ch01-zabbix-components/zabbix-server.md) for the required database
    settings you will need to set in the `/etc/zabbix/zabbix_proxy.d/database.conf`-file.

???+ dica

    A list of all configuration options can be found in the Zabbix documentation.
    [https://www.zabbix.com/documentation/current/en/manual/appendix/config/zabbix_proxy](https://www.zabbix.com/documentation/current/en/manual/appendix/config/zabbix_proxy)

A notable configuration parameter that was added in `7.0` is `ProxyBufferMode`
which determines how collected monitoring data is stored by the proxy before it
is forwarded to the Zabbix server.

Possible buffer modes:

`disk` - Disk buffer (default for existing installations prior to Zabbix 7.0)

: All data is written to the Zabbix Proxy database immediately before it is sent
to the Zabbix server. In case of a proxy or system crash, all data is retained
and will be sent to the Zabbix server as soon as the proxy is started again.

    This is slower due to database I/O but is highly reliable.

`memory` - Memory buffer

: Data is stored in RAM and is not written to disk. This makes sure the data is
sent to the Zabbix server as quickly as possible as there is no I/O wait time
for the database involved. Downside is that when the proxy or the system crashes
when the proxy still has data in the buffer, not yet received by the server,
that data will be lost. Also when the RAM buffer overflows
(`ProxyMemoryBufferSize`), possibly due to a sudden burst of incoming items or
the Zabbix server being unavailable for some time, older data will be removed
from the buffer before it is sent to the Zabbix server.

`hybrid` - Hybrid buffer (default for new installations since Zabbix 7.0)

: Data is primarily stored in RAM but is automatically written to the database
when the memory buffer is full, the data is too old or when the proxy is
stopped. This makes sure that data is preserved in case the Zabbix server is
unreachable for a longer period or when there are bursts of many incoming items
and hereby balances speed and reliability.

???+ aviso

    In Proxies that where installed before `7.0` the data was first written to
    disk in the database and then sent to the `Zabbix server`. For these installations
    when we upgrade this remains the default behavior after upgrading to Zabbix
    7.x or higher. It's now recommended for performance reasons to use the new
    setting `hybrid` and to define the `ProxyMemoryBufferSize`.

Once you have made all the changes you need in the config file besides the ones
we have covered, we only need to enable the service and start our proxy. Of
course don't forget to open the firewall port `10051` on your _Zabbix server_
side for the active proxy.

!!! info "Enable and start the proxy service"

      ```bash
      sudo systemctl enable zabbix-proxy --now
      ```

If all goes well we can check the log file from our proxy and we will see that
Zabbix has created the database by itself.

???+ example "View Zabbix proxy logs"

    ```shell-session
    localhost:~> sudo tail -f /var/log/zabbix/zabbix_proxy.log`
    11134:20250519:152232.419 Starting Zabbix Proxy (active) [Zabbix proxy]. Zabbix 7.4.0beta2 (revision 7cd11a01d42).
    11134:20250519:152232.419 **** Enabled features ****
    11134:20250519:152232.419 SNMP monitoring:       YES
    11134:20250519:152232.419 IPMI monitoring:       YES
    11134:20250519:152232.419 Web monitoring:        YES
    11134:20250519:152232.419 VMware monitoring:     YES
    11134:20250519:152232.419 ODBC:                  YES
    11134:20250519:152232.419 SSH support:           YES
    11134:20250519:152232.419 IPv6 support:          YES
    11134:20250519:152232.419 TLS support:           YES
    11134:20250519:152232.419 **************************
    11134:20250519:152232.419 using configuration file: /etc/zabbix/zabbix_proxy.conf
    11134:20250519:152232.419 cannot open database file "/var/lib/zabbix/zabbix_proxy.db": [2] No such file or directory
    11134:20250519:152232.419 creating database ...
    11134:20250519:152232.478 current database version (mandatory/optional): 07030032/07030032
    11134:20250519:152232.478 required mandatory version: 07030032
    ```

In case of the _active_ proxy, we are now ready. Going back to our frontend we
should be able to see that our proxy is now online. Zabbix will also show the
version of our proxy and the last seen age.

![ProxyA ready](ch03-active-proxy-installed.png)

_3.6 Active proxy configured_

For the _passive_ proxy however, you will notice in the frontend that nothing
seems to be working at all even when we have configured everything correctly on
our proxy.

![Passive Proxy not working](ch03-passive-not-working.png)

_3.7 Proxy not working_

The explanation is rather easy as we run a _passive_ proxy, the _Zabbix server_
needs to poll our proxy. But we did not yet configure our Server to do that
currently. So next step is to add the needed proxy pollers in our server
configuration.

Edit or create a new configuration file in `/etc/zabbix/zabbix_server.d/` on the
_Zabbix Server_ machine to add the required `StartProxyPollers` setting.

!!! info "/etc/zabbix/zabbix_server.d/pollers.conf"

    ```ini
    StartProxyPollers=1
    ```

And restart the _Zabbix Server_ process.

!!! info "Restart Zabbix Server"

    ```bash
    sudo systemctl restart zabbix-server
    ```

Now going back to the frontend, we will see that our _passive proxy_ becomes
available. If it's not green give it a few seconds or check all steps again and
verify your log files.

![Passive Proxy working](ch03-passive-working.png)

_3.8 Proxy working_

You are now ready.

For your monitored hosts, this proxy will behave like the Zabbix server. Hence,
all hosts you want to be monitored by the proxy will now have to be configured
to have their `Server` and/or `ServerActive` configuration values set to the
IP/hostname of this proxy instead of the _Zabbix server_.

---

## Conclusão

This chapter has demonstrated the indispensable role of Zabbix proxies in
building robust, scalable, and distributed monitoring infrastructures. We've
explored the fundamental distinction between _active_ and _passive_ proxy modes,
highlighting how each serves different deployment scenarios and network
topologies. Understanding their individual strengths, from simplified firewall
configurations with _active proxies_ to the server-initiated control of _passive
proxies_, is crucial for optimal system design.

We delved into the comprehensive settings that govern proxy behavior,
emphasizing how proper configuration of parameters like proxy polling intervals
and data buffers, directly impacts performance and data accuracy. The evolution
of data storage mechanisms within the proxy, from purely memory-based approaches
to the flexible options of disk and hybrid storage, empowers administrators to
finely tune resource utilization and data persistence based on their specific
needs and the volume of monitored data.

Finally, we examined the critical advancements in configuration synchronization,
particularly the significant improvements introduced with Zabbix 7.0. The shift
towards more efficient and streamlined config sync processes, moving beyond the
limitations of earlier versions, underscores Zabbix's continuous commitment to
enhancing operational efficiency and simplifying large-scale deployments.

In essence, Zabbix proxies are far more than simple data forwarders; they are
intelligent intermediaries that offload significant processing from the central
Zabbix server, reduce network traffic, and enhance the resilience of your
monitoring solution. By carefully selecting the appropriate proxy type,
meticulously configuring its settings, and leveraging the latest features in
data storage and configuration management, you can unlock the full potential of
Zabbix to monitor even the most complex and geographically dispersed
environments with unparalleled efficiency and reliability. The knowledge gained
in this chapter will be instrumental in designing and maintaining a Zabbix
infrastructure that is not only robust today but also adaptable to future
monitoring challenges.

---

## Perguntas

- What is the fundamental difference between an active proxy and a passive proxy
  in terms of who initiates the connection?
- How does a network firewall configuration differ for active vs passive proxies
  when separated from the server by a network firewall?

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manpages/zabbix_proxy](https://www.zabbix.com/documentation/current/en/manpages/zabbix_proxy)

