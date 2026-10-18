---
description: |
    Esta seção do livro The Zabbix Book intitulada "Instalando o servidor Zabbix"
    guia você através da instalação e configuração do servidor Zabbix em várias distribuições Linux. Ela abrange a instalação do pacote do servidor Zabbix, a configuração das configurações de conexão com o banco de dados e a configuração do firewall para permitir conexões entrantes ao servidor Zabbix. Além disso, fornece instruções sobre como iniciar e habilitar o serviço do servidor Zabbix, validar a configuração e verificar o arquivo de log do servidor para quaisquer problemas.
tags: [beginner]
---

# Instalando o servidor Zabbix

Agora que adicionamos o repositório Zabbix com os softwares necessários, estamos
prontos para instalar tanto o servidor Zabbix quanto o servidor web. Lembre-se de que
o servidor web não precisa ser instalado na mesma máquina do servidor Zabbix; eles podem ser hospedados em sistemas separados se desejado.

Para instalar os componentes do servidor Zabbix, execute o seguinte comando:

!!! info "Instale o zabbix server"

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


Após a instalação bem-sucedida do pacote do servidor Zabbix, precisamos configurar o
servidor Zabbix para se conectar ao banco de dados. Isso requer a modificação do arquivo
de configuração do servidor Zabbix.

O arquivo de configuração do servidor Zabbix oferece uma opção para incluir arquivos adicionais
de configuração para parâmetros personalizados. Em um ambiente de produção, é geralmente melhor evitar alterar diretamente o arquivo de configuração original. Em vez disso,
você pode criar e incluir arquivos de configuração separados para quaisquer parâmetros adicionais ou modificados. Essa abordagem garante que seu arquivo de configuração original permaneça inalterado, o que é particularmente útil ao realizar atualizações
ou gerenciar configurações com ferramentas como Ansible, Puppet ou SaltStack.

Em SUSE 16 e versões posteriores, essa funcionalidade já está habilitada e configurada por padrão.
(veja também [https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc](https://documentation.suse.com/sles/16.0/html/SLE-differences-faq/index.html#sle16-differences-faq-basesystem-etc)).
Portanto, nos sistemas SUSE, o arquivo de configuração do servidor Zabbix é localizado em
`/usr/etc/zabbix/zabbix_server.conf`, e está configurado para incluir todos os arquivos `.conf` no diretório
`/etc/zabbix_server/zabbix_server.d/`.

Em outras distribuições, você pode precisar habilitá-la manualmente:

Para habilitar essa funcionalidade, certifique-se de que a próxima linha existe e não está comentada
(com um `#` na frente dela) em `/etc/zabbix/zabbix_server.conf`:

!!! info ""

    ```ini
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    Include=/etc/zabbix/zabbix_server.d/*.conf
    ```


O caminho `/etc/zabbix/zabbix_server.d/` já deve ter sido criado pelo
pacote instalado, mas certifique-se de que realmente existe.

Agora criaremos um arquivo de configuração personalizado `database.conf` no diretório `/etc/zabbix/zabbix_server.d/`
que conterá nossas configurações de conexão com o banco de dados:

!!! info "Adicione as configurações de conexão do banco de dados Zabbix"

    ``` bash
    vi /etc/zabbix/zabbix_server.d/database.conf
    ```


    Adicione as seguintes linhas no arquivo de configuração para corresponder à sua configuração de banco de dados:

    ```ini
    # Zabbix database configuration
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>  # Only for PostgreSQL
    DBUser=<database-user>
    DBPassword=<database-password>
    DBPort=<database-port>
    ```


Substitua `<database-host>`, `<database-name>`, `<database-schema>`, `<database-user>`,
`<database-password>` e `<database-port>` pelos valores apropriados para sua
configuração. Isso garante que o servidor Zabbix possa se comunicar com seu banco de dados.

Certifique-se de que não há `#` (símbolo de comentário) na frente dos parâmetros de configuração,
pois o Zabbix tratará linhas iniciadas com `#` como comentários, ignorando-as durante a execução.
Além disso, verifique novamente por linhas de configuração duplicadas; se houver várias
linhas com o mesmo parâmetro, o Zabbix usará o valor da última ocorrência.

Para nossa configuração, a configuração será assim:

!!! example "Exemplo database.conf"

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


!!! note "Para PostgreSQL em HA"

    Com o Zabbix 8.0 é agora possível adicionar mais de 1 IP para DBHost. Dessa forma
    é possível configurar um ambiente HA com PostgreSQL sem a necessidade de usar um
    balanceador de carga. O Zabbix detectará o banco ativo por conta própria. Ex:
    DBHost=192.168.10.2:5432,192.168.10.3:5432

Neste exemplo:

- `DBHost` se refere ao host onde seu banco de dados está rodando (use localhost se estiver
  na mesma máquina).
- `DBName` é o nome do banco de dados Zabbix.
- `DBSchema` é o nome do esquema usado no PostgreSQL (somente necessário para PostgreSQL).
- `DBUser` é o usuário do banco de dados.
- `DBPassword` é a senha para o usuário do banco de dados.
- `DBPort` é o número da porta em que seu servidor de banco de dados está escutando (padrão para
  MySQL/MariaDB é 3306 e PostgreSQL é 5432).

Certifique-se de que as configurações refletem a configuração do banco de dados do seu ambiente.

---

## Configure o firewall para permitir conexões Zabbix trapper

Voltando à sua máquina servidor Zabbix, precisamos garantir que o firewall esteja configurado
para permitir conexões entrantes ao servidor Zabbix.

Seu servidor Zabbix precisa aceitar conexões entrantes de agentes, enviadores e proxies do Zabbix. Por padrão,
o Zabbix usa a porta `10051/tcp` para essas conexões.
Para permitir essas conexões, você precisa abrir essa porta no seu firewall.

!!! info "Abra o firewall para zabbix-trapper"

    Red Hat / SUSE
    ``` bash
    sudo firewall-cmd --add-service=zabbix-trapper --permanent
    sudo firewall-cmd --reload
    ```


    Ubuntu
    ``` bash
    sudo ufw allow 10051/tcp
    ```


Se o serviço não for reconhecido usando `firewall-cmd --add-service`, você pode especificar manualmente a porta:

!!! info "Adicione a porta em vez do nome do serviço"

    ```bash
    firewall-cmd --add-port=10051/tcp --permanent
    ```


---

## Iniciando o servidor Zabbix

Com a configuração atualizada do servidor Zabbix para se conectar ao seu banco de dados, você
pode agora iniciar e habilitar o serviço do servidor Zabbix. Execute o seguinte comando
para habilitar o serviço do servidor Zabbix e garantir que ele seja iniciado automaticamente no boot:

???+ note

    Antes de reiniciar o servidor Zabbix após modificar sua configuração, é considerada uma boa prática validar a configuração para prevenir possíveis problemas. Executar um teste de configuração garante que quaisquer erros sejam detectados
    antes, evitando downtime causado por uma configuração inválida. Isso pode ser feito usando o seguinte comando: `zabbix-server -T`

!!! info "Habilitar e iniciar serviço zabbix-server"

    Red Hat, SUSE e Ubuntu
    ``` bash
    sudo systemctl enable zabbix-server --now
    ```


Este comando iniciará imediatamente o serviço do servidor Zabbix e configurará para que ele seja lançado no início da inicialização do sistema. Para verificar se o servidor Zabbix está funcionando corretamente,
verifique o arquivo de log para mensagens. Você pode visualizar as entradas mais recentes no
arquivo `Zabbix server` usando:

!!! info "Verificar o arquivo de log"

    ```bash
    tail /var/log/zabbix/zabbix_server.log
    ```


Procure por mensagens indicando que o servidor foi iniciado com sucesso. Se houver
qualquer problema, o arquivo de log fornecerá detalhes para ajudar na solução de problemas.

!!! example "Saída de exemplo"

    ```
    12074:20250225:145333.529 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
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
    12074:20250225:145333.545 current database version (mandatory/optional): 08000000/08000000
    12074:20250225:145333.545 required mandatory version: 08000000
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


Se houve um erro e o servidor não conseguiu se conectar ao banco de dados você veria algo como isso no arquivo de log do servidor:

!!! example "Exemplo de log com erros"

    ```
    12068:20250225:145309.018 Starting Zabbix Server. Zabbix 8.0.0 (revision dd0d9c26a3a).
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

Nesse caso, verifique suas configurações de conexão com o banco de dados no
arquivo `/etc/zabbix/zabbix_server.d/database.conf` e certifique-se de que o banco de dados
esteja corretamente populado conforme descrito nos passos anteriores. Também verifique as regras do firewall e quando usando PostgreSQL, certifique-se de que `pg_hba.conf` esteja configurado corretamente
para permitir conexões do servidor Zabbix.

Vamos verificar o serviço do servidor Zabbix para ver se ele está habilitado para sobreviver
a um reboot

!!! info "Verificar status do serviço zabbix-server"

    ```bash
    sudo systemctl status zabbix-server
    ```


???+ example "Saída de exemplo"
    ```shell-session
    localhost:~> sudo systemctl status zabbix-server

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


Isso conclui nosso capítulo sobre a instalação e configuração do servidor Zabbix.

---

## Conclusão

Com a instalação e configuração bem-sucedidas do servidor Zabbix, você agora estabeleceu o componente principal de seu sistema de monitoramento. Cobrimos a
instalação do pacote do servidor Zabbix, a configuração das configurações de conexão com o banco de dados e a configuração do firewall para permitir conexões entrantes ao servidor Zabbix. Além disso, iniciamos o serviço do servidor Zabbix e verificamos sua operação.

Seu servidor Zabbix está agora pronto para se comunicar com os agentes, enviadores e proxies Zabbix.
A próxima etapa é instalar e configurar a interface frontal do Zabbix, que fornecerá a interface de usuário para interagir com seu sistema de monitoramento.

Vamos prosseguir para o próximo capítulo para configurar a interface frontal do Zabbix.

---

## Perguntas

1. Qual versão do Zabbix eu devo instalar para compatibilidade e estabilidade?
2. Quais logs do Zabbix eu devo verificar para resolver problemas comuns?

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)