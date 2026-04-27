---
description: |
    This section from The Zabbix Book titled "Installing the Zabbix server" 
    guides you through the installation and configuration of the Zabbix server 
    on various Linux distributions. It covers the installation of the Zabbix 
    server package, configuration of the database connection settings, and setup 
    of the firewall to allow incoming connections to the Zabbix server. 
    Additionally, it provides instructions for starting and enabling the Zabbix 
    server service, validating the configuration, and checking the server's log
    file for any issues. 
tags: [beginner]
---

# Instalando o Zabbix Server

Agora que adicionamos o repositório Zabbix com o software necessário, estamos
prontos para instalar o servidor Zabbix e o servidor Web. Lembre-se de que o
servidor Web não precisa ser instalado na mesma máquina que o servidor Zabbix;
eles podem ser hospedados em sistemas separados, se desejado.

Para instalar os componentes do servidor Zabbix, execute o seguinte comando:

!!! info "Instalar o servidor zabbix"

    Red Hat
    ``` bash
    # For MySQL/MariaDB backend:
    dnf install zabbix-server-mysql
    # For PostgreSQL backend:
    dnf install zabbix-server-pgsql
    ```

    SUSE
    ``` bash
    # For MySQL/MariaDB backend:
    zypper install zabbix-server-mysql
    # For PostgreSQL backend:
    zypper install zabbix-server-pgsql
    ``` 

    Ubuntu
    ``` bash
    # For MySQL/MariaDB backend:
    sudo apt install zabbix-server-mysql
    # For PostgreSQL backend:
    sudo apt install zabbix-server-pgsql
    ```

Depois de instalar com sucesso o pacote do Zabbix Server, precisamos configurar
o Zabbix Server para se conectar ao banco de dados. Para isso, é necessário
modificar o arquivo de configuração do Zabbix Server.

O arquivo de configuração do servidor Zabbix oferece uma opção para incluir
arquivos de configuração adicionais para parâmetros personalizados. Em um
ambiente de produção, geralmente é melhor evitar alterar diretamente o arquivo
de configuração original. Em vez disso, você pode criar e incluir arquivos de
configuração separados para quaisquer parâmetros adicionais ou modificados. Essa
abordagem garante que o arquivo de configuração original permaneça intocado, o
que é particularmente útil ao realizar atualizações ou gerenciar configurações
com ferramentas como Ansible, Puppet ou SaltStack.

No SUSE 16 e posterior, esse recurso já está ativado e configurado por padrão.
(consulte também [Documentação do
SUSE](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Portanto, nos sistemas SUSE, o arquivo de configuração do servidor Zabbix está
localizado em `/usr/etc/zabbix/zabbix_server.conf`, e está configurado para
incluir todos os arquivos `.conf` do diretório
`/etc/zabbix_server/zabbix_server.d/`.

Em outras distribuições, talvez seja necessário ativá-la manualmente:

Para ativar esse recurso, certifique-se de que a próxima linha exista e não
esteja comentada (com um `#` na frente) em `/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```

O caminho `/etc/zabbix/zabbix_server.d/` já deve ter sido criado pelo pacote
instalado, mas verifique se ele realmente existe.

Agora, criaremos um arquivo de configuração personalizado `database.conf` no
diretório `/etc/zabbix/zabbix_server.d/` que manterá nossas configurações de
conexão com o banco de dados:

!!! info "Adicionar configurações de conexão do banco de dados Zabbix"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```

    Add the following lines in the configuration file to match your database setup:

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```

Substitua `<database-host>`, `<database-name>`, `<database-schema>`,
`<database-user>`, `<database-password>` e `<database-port>` pelos valores
apropriados para sua configuração. Isso garante que o servidor Zabbix possa se
comunicar com seu banco de dados.

Certifique-se de que não há nenhum # (símbolo de comentário) na frente dos
parâmetros de configuração, pois o Zabbix tratará as linhas que começam com #
como comentários, ignorando-as durante a execução. Além disso, verifique se há
linhas de configuração duplicadas; se houver várias linhas com o mesmo
parâmetro, o Zabbix usará o valor da última ocorrência.

Para nossa instalação, a configuração será semelhante a esta:

!!! exemplo "Exemplo de banco de dados.conf"

    MariaDB/MySQL:
    ```ini
    # MariaDB database configuration
    DBHost=<ip or dns of your MariaDB server>
    DBName=zabbix
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=3306
    ```

    PostgreSQL:
    ```ini
    # PostgreSQL database configuration
    DBHost=<ip or dns of your PostgreSQL server>
    DBName=zabbix
    DBSchema=zabbix_server
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=5432
    ```

Neste exemplo:

- DBHost refere-se ao host em que seu banco de dados está sendo executado (use
  localhost se estiver na mesma máquina).
- DBName é o nome do banco de dados do Zabbix.
- DBSchema é o nome do esquema usado no PostgreSQL (necessário apenas para o
  PostgreSQL).
- DBUser é o usuário do banco de dados.
- DBPassword é a senha do usuário do banco de dados.
- DBPort é o número da porta na qual o seu servidor de banco de dados está
  escutando (o padrão para MySQL/MariaDB é 3306 e para PostgreSQL é 5432).

Certifique-se de que as configurações reflitam a configuração do banco de dados
de seu ambiente.

---

## Configurar o firewall para permitir conexões do Zabbix trapper

De volta à sua máquina do servidor Zabbix, precisamos garantir que o firewall
esteja configurado para permitir conexões de entrada com o servidor Zabbix.

Seu servidor Zabbix precisa aceitar conexões de entrada dos agentes, remetentes
e proxies do Zabbix. Por padrão, o Zabbix usa a porta `10051/tcp` para essas
conexões. Para permitir essas conexões, é necessário abrir essa porta em seu
firewall.

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

Se o serviço não for reconhecido usando `firewall-cmd --add-service`, você
poderá especificar manualmente a porta:

!!! info "Adicionar porta em vez do nome do serviço"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```

---

## Iniciando o servidor Zabbix

Com a configuração do servidor Zabbix atualizada para se conectar ao seu banco
de dados, agora você pode iniciar e ativar o serviço do servidor Zabbix. Execute
o seguinte comando para ativar o servidor Zabbix e garantir que ele seja
iniciado automaticamente na inicialização:

???+ nota

    Before restarting the Zabbix server after modifying its configuration, it is
    considered best practice to validate the configuration to prevent potential
    issues. Running a configuration check ensures that any errors are detected
    beforehand, avoiding downtime caused by an invalid configuration. This can
    be accomplished using the following command: `zabbix-server -T`

!!! info "ativar e iniciar o serviço zabbix-server"

    Red Hat, SUSE and Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```

Esse comando iniciará o serviço do servidor Zabbix imediatamente e o configurará
para ser iniciado na inicialização do sistema. Para verificar se o servidor
Zabbix está funcionando corretamente, verifique se há mensagens no arquivo de
registro. É possível visualizar as entradas mais recentes no arquivo de registro
`Zabbix server` usando:

!!! info "Verifique o arquivo de registro"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```

Procure mensagens que indiquem que o servidor foi iniciado com êxito. Se houver
algum problema, o arquivo de registro fornecerá detalhes para ajudar na solução
de problemas.

!!! example "Exemplo de saída"

    ```
    12074:20250225:145333.529 Starting Zabbix Server. Zabbix 7.2.4 (revision c34078a4563).
    12074:20250225:145333.530 ****** Enabled features ******
    12074:20250225:145333.530 SNMP monitoring:           YES
    12074:20250225:145333.530 IPMI monitoring:           YES
    12074:20250225:145333.530 Web monitoring:            YES
    12074:20250225:145333.530 VMware monitoring:         YES
    12074:20250225:145333.530 SMTP authentication:       YES
    12074:20250225:145333.530 ODBC:                      YES
    12074:20250225:145333.530 SSH support:               YES
    12074:20250225:145333.530 IPv6 support:              YES
    12074:20250225:145333.530 TLS support:               YES
    12074:20250225:145333.530 ******************************
    12074:20250225:145333.530 using configuration file: /etc/zabbix/zabbix_server.conf
    12074:20250225:145333.545 current database version (mandatory/optional): 07020000/07020000
    12074:20250225:145333.545 required mandatory version: 07020000
    12075:20250225:145333.557 starting HA manager
    12075:20250225:145333.566 HA manager started in active mode
    12074:20250225:145333.567 server #0 started [main process]
    12076:20250225:145333.567 server #1 started [service manager #1]
    12077:20250225:145333.567 server #2 started [configuration syncer #1]
    12078:20250225:145333.718 server #3 started [alert manager #1]
    12079:20250225:145333.719 server #4 started [alerter #1]
    12080:20250225:145333.719 server #5 started [alerter #2]
    12081:20250225:145333.719 server #6 started [alerter #3]
    12082:20250225:145333.719 server #7 started [preprocessing manager #1]
    12083:20250225:145333.719 server #8 started [lld manager #1]
    ```

Se houvesse um erro e o servidor não conseguisse se conectar ao banco de dados,
você veria algo assim no arquivo de registro do servidor:

!!! exemplo "Exemplo de registro com erros"

    ```
    12068:20250225:145309.018 Starting Zabbix Server. Zabbix 7.2.4 (revision c34078a4563).
    12068:20250225:145309.018 ****** Enabled features ******
    12068:20250225:145309.018 SNMP monitoring:           YES
    12068:20250225:145309.018 IPMI monitoring:           YES
    12068:20250225:145309.018 Web monitoring:            YES
    12068:20250225:145309.018 VMware monitoring:         YES
    12068:20250225:145309.018 SMTP authentication:       YES
    12068:20250225:145309.018 ODBC:                      YES
    12068:20250225:145309.018 SSH support:               YES
    12068:20250225:145309.018 IPv6 support:              YES
    12068:20250225:145309.018 TLS support:               YES
    12068:20250225:145309.018 ******************************
    12068:20250225:145309.018 using configuration file: /etc/zabbix/zabbix_server.conf
    12068:20250225:145309.027 [Z3005] query failed: [1146] Table 'zabbix.users' doesn't exist [select userid from users limit 1]
    12068:20250225:145309.027 cannot use database "zabbix": database is not a Zabbix database
    ```
Se esse for o caso, verifique novamente as configurações de conexão do banco de
dados no arquivo `/etc/zabbix/zabbix_server.d/database.conf` e certifique-se de
que o banco de dados esteja preenchido corretamente, conforme descrito nas
etapas anteriores. Verifique também as regras de firewall e, ao usar o
PostgreSQL, certifique-se de que `pg_hba.conf` esteja configurado corretamente
para permitir conexões do servidor Zabbix.

Vamos verificar o serviço do servidor Zabbix para ver se ele está ativado de
modo a sobreviver a uma reinicialização

!!! info "verificar o status do serviço zabbix-server"

    ```bash
    sudo systemctl status zabbix-server
    ```

???+ exemplo "Example output" ```shell-session localhost:~> sudo systemctl
status zabbix-server

    ● zabbix-server.service - Zabbix Server
         Loaded: loaded (/usr/lib/systemd/system/zabbix-server.service; enabled; preset: disabled)
         Active: active (running) since Tue 2025-02-25 14:53:33 CET; 26min ago
       Main PID: 12074 (zabbix_server)
          Tasks: 77 (limit: 24744)
         Memory: 71.5M
            CPU: 18.535s
         CGroup: /system.slice/zabbix-server.service
                 ├─12074 /usr/sbin/zabbix_server -c /etc/zabbix/zabbix_server.conf
                 ├─12075 "/usr/sbin/zabbix_server: ha manager"
                 ├─12076 "/usr/sbin/zabbix_server: service manager #1 [processed 0 events, updated 0 event tags, deleted 0 problems, synced 0 service updates, idle 5.027667 sec during 5.042628 sec]"
                 ├─12077 "/usr/sbin/zabbix_server: configuration syncer [synced configuration in 0.051345 sec, idle 10 sec]"
                 ├─12078 "/usr/sbin/zabbix_server: alert manager #1 [sent 0, failed 0 alerts, idle 5.030391 sec during 5.031944 sec]"
                 ├─12079 "/usr/sbin/zabbix_server: alerter #1 started"
                 ├─12080 "/usr/sbin/zabbix_server: alerter #2 started"
                 ├─12081 "/usr/sbin/zabbix_server: alerter #3 started"
                 ├─12082 "/usr/sbin/zabbix_server: preprocessing manager #1 [queued 0, processed 0 values, idle 5.023818 sec during 5.024830 sec]"
                 ├─12083 "/usr/sbin/zabbix_server: lld manager #1 [processed 0 LLD rules, idle 5.017278sec during 5.017574 sec]"
                 ├─12084 "/usr/sbin/zabbix_server: lld worker #1 [processed 1 LLD rules, idle 21.031209 sec during 21.063879 sec]"
                 ├─12085 "/usr/sbin/zabbix_server: lld worker #2 [processed 1 LLD rules, idle 43.195541 sec during 43.227934 sec]"
                 ├─12086 "/usr/sbin/zabbix_server: housekeeper [startup idle for 30 minutes]"
                 ├─12087 "/usr/sbin/zabbix_server: timer #1 [updated 0 hosts, suppressed 0 events in 0.017595 sec, idle 59 sec]"
                 ├─12088 "/usr/sbin/zabbix_server: http poller #1 [got 0 values in 0.000071 sec, idle 5 sec]"
                 ├─12089 "/usr/sbin/zabbix_server: browser poller #1 [got 0 values in 0.000066 sec, idle 5 sec]"
                 ├─12090 "/usr/sbin/zabbix_server: discovery manager #1 [processing 0 rules, 0 unsaved checks]"
                 ├─12091 "/usr/sbin/zabbix_server: history syncer #1 [processed 4 values, 3 triggers in 0.027382 sec, idle 1 sec]"
                 ├─12092 "/usr/sbin/zabbix_server: history syncer #2 [processed 0 values, 0 triggers in 0.000077 sec, idle 1 sec]"
                 ├─12093 "/usr/sbin/zabbix_server: history syncer #3 [processed 0 values, 0 triggers in 0.000076 sec, idle 1 sec]"
                 ├─12094 "/usr/sbin/zabbix_server: history syncer #4 [processed 0 values, 0 triggers in 0.000020 sec, idle 1 sec]"
                 ├─12095 "/usr/sbin/zabbix_server: escalator #1 [processed 0 escalations in 0.011627 sec, idle 3 sec]"
                 ├─12096 "/usr/sbin/zabbix_server: proxy poller #1 [exchanged data with 0 proxies in 0.000081 sec, idle 5 sec]"
                 ├─12097 "/usr/sbin/zabbix_server: self-monitoring [processed data in 0.000068 sec, idle 1 sec]"
    ```

Isso conclui nosso capítulo sobre a instalação e a configuração do servidor
Zabbix.

---

## Conclusão

Com a instalação e a configuração bem-sucedidas do servidor Zabbix, você
estabeleceu o componente central do seu sistema de monitoramento. Cobrimos a
instalação do pacote do Zabbix Server, a configuração das definições de conexão
do banco de dados e a configuração do firewall para permitir conexões de entrada
com o Zabbix Server. Além disso, iniciamos o serviço do Zabbix Server e
verificamos seu funcionamento.

Seu servidor Zabbix agora está pronto para se comunicar com os agentes,
remetentes e proxies do Zabbix. A próxima etapa é instalar e configurar o
front-end do Zabbix, que fornecerá a interface do usuário para interagir com o
sistema de monitoramento.

Vamos prosseguir para o próximo capítulo para configurar o front-end do Zabbix.

---

## Perguntas

1. Qual versão do Zabbix devo instalar para garantir a compatibilidade e a
   estabilidade?
2. Quais logs do Zabbix devo verificar para solucionar problemas comuns?

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
