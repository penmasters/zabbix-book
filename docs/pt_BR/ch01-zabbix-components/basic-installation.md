---
description: |
    Step‑by‑step guide to install Zabbix with MariaDB or PostgreSQL, setup server
    & frontend on Ubuntu or Rocky Linux, including security & repo configuration.
tags: [beginner]
---

# Instalação básica

Neste capítulo, discorreremos sobre o processo de instalação do Zabbix Server.
Há diversas maneiras de configurar um Zabbix Server. Abordaremos as
configurações mais comuns com o MariaDB e o PostgreSQL no Ubuntu e no Rocky
Linux.

Antes de iniciar a instalação, é importante entender a arquitetura do Zabbix. O
Zabbix Server é estruturado de forma modular, composto por três componentes
principais, que discutiremos em detalhes.

- O Zabbix Server
- O servidor web Zabbix (Frontend)
- O banco de dados do Zabbix

!!! info "Criação de Usuários do Banco de Dados"

    ``` yaml
    In our setup we will create 2 DB users `zabbix-web` and `zabbix-srv`. The 
    zabbix-web user will be used for the frontend to connect to our zabbix database.
    The zabbix-srv user will be used by our zabbix server to connect to the database.
    This allows us to limit the permissions for every user to only what is strictly
    needed.
    ```


![overview](ch01-basic-installation-zabbixserver.png){ align=left }

_1.1 Instalação da divisão básica do Zabbix_

Todos esses componentes podem ser instalados em um único servidor ou
distribuídos em três servidores separados. O núcleo do sistema é o Zabbix
Server, geralmente chamado de "cérebro". Esse componente é responsável pelo
processamento de cálculos de acionamento e pelo envio de alertas. O banco de
dados serve como armazenamento da configuração do servidor Zabbix e de todos os
dados que ele coleta. O servidor Web fornece a interface do usuário (front-end)
para interagir com o sistema. É importante observar que a API do Zabbix faz
parte do componente front-end, e não do próprio servidor Zabbix.

Esses componentes devem funcionar juntos de forma integrada, conforme ilustrado
no diagrama acima. O Zabbix Server deve ler as configurações e armazenar os
dados de monitoramento no banco de dados, enquanto o front-end precisa ter
acesso para ler e gravar os dados de configuração. Além disso, o front-end deve
ser capaz de verificar o status do Zabbix Server e recuperar informações
adicionais necessárias para garantir uma operação tranquila.

Para nossa configuração, usaremos duas máquinas virtuais (VMs): uma VM hospedará
o Zabbix Server e o Frontend, enquanto a segunda VM hospedará o banco de dados
do Zabbix.

???+ nota

    It's perfect possible to install all components on 1 single VM or every component
    on a separate VM.
    Reason we split the DB as an example is because the database will probably be
    the first component giving you performance headaches. It's also the component
    that needs some extra attention when we split it so for this reason we have
    chosen in this example to split the database from the rest of the setup.

???+ nota

    A crucial consideration for those managing Zabbix installations is the database
    back-end. Zabbix 7.0 marks the final release to offer support for Oracle Database.
    Consequently, systems running Zabbix 7.0 or any prior version must undertake
    a database migration to either PostgreSQL, MySQL, or a compatible fork such
    as MariaDB before upgrading to a later Zabbix release. This migration is a
    mandatory step to ensure continued functionality and compatibility with future
    Zabbix versions.

Abordaremos os seguintes tópicos:

- Instale nosso banco de dados baseado no MariaDB.
- Instale nosso banco de dados baseado no PostgreSQL.
- Instalando o Zabbix Server.
- Instale o front-end.

## Instalando o banco de dados MariaDB

Para iniciar o processo de instalação do servidor MariaDB, a primeira etapa
envolve a criação manual de um arquivo de configuração do repositório. Esse
arquivo, mariadb.repo no Rocky, deve ser colocado no diretório
/etc/yum.repos.d/. O arquivo de repositório permitirá que seu gerenciador de
pacotes localize e instale os componentes necessários do MariaDB. Para o Ubuntu,
precisamos importar as chaves do repositório e criar um arquivo, por exemplo,
'/etc/apt/sources.list.d/mariadb.sources'.

### Adicione o repositório MariaDB

Para criar o arquivo de repositório do MariaDB, execute o seguinte comando em
seu terminal:

!!! info "criar repositório mariadb"

    Red Hat
    ``` yaml
    vi /etc/yum.repos.d/mariadb.repo
    ```

    Ubuntu
    ``` yaml
    sudo apt install apt-transport-https curl
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp'

    sudo vi /etc/apt/sources.list.d/mariadb.sources
    ```

Isso abrirá um editor de texto no qual você poderá inserir os detalhes de
configuração do repositório. Depois que o repositório estiver configurado, você
poderá prosseguir com a instalação do MariaDB usando o gerenciador de pacotes.

???+ dica

    Always check Zabbix documentation for the latest supported versions.

A configuração mais recente pode ser encontrada aqui:
<https://mariadb.org/download/?t=repo-config>

Aqui está a configuração que você precisa adicionar ao arquivo:

!!! info "Repositório Mariadb"

    Red Hat
    ```yaml
    # MariaDB 11.4 RedHatEnterpriseLinux repository list - created 2025-02-21 10:15 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/rhel/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/rhel/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```

    Ubuntu
    ``` yaml
    # MariaDB 11.4 repository list - created 2025-02-21 11:42 UTC
    # https://mariadb.org/download/
    X-Repolib-Name: MariaDB
    Types: deb
    # deb.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # URIs: https://deb.mariadb.org/11.4/ubuntu
    URIs: https://mirror.bouwhuis.network/mariadb/repo/11.4/ubuntu
    Suites: noble
    Components: main main/debug
    Signed-By: /etc/apt/keyrings/mariadb-keyring.pgp
    ```

Depois de salvar o arquivo, verifique se tudo está devidamente configurado, e se
a versão do MariaDB é compatível com a versão do Zabbix, para evitar possíveis
problemas de integração.

Antes de prosseguir com a instalação do MariaDB, é uma prática recomendada
garantir que seu sistema operacional esteja atualizado com os patches e as
correções de segurança mais recentes. Isso ajudará a manter a estabilidade e a
compatibilidade do sistema com o software que você está prestes a instalar.

Para atualizar seu sistema operacional, execute o seguinte comando:

!!! info "Atualizar sistema operacional"

    Red Hat
    ```yaml
    dnf update
    ```

    Ubuntu
    ``` yaml
    sudo apt update && sudo apt upgrade
    ```

Esse comando buscará e instalará automaticamente as atualizações mais recentes
disponíveis para seu sistema, aplicando patches de segurança, melhorias de
desempenho e correções de bugs. Quando o processo de atualização estiver
concluído, você poderá prosseguir com a instalação do MariaDB.

---

### Instalar o banco de dados MariaDB

Com o sistema operacional atualizado e o repositório do MariaDB configurado,
agora você está pronto para instalar os pacotes do servidor e do cliente
MariaDB. Isso fornecerá os componentes necessários para executar e administrar a
sua base de dados.

Para instalar o servidor e o cliente MariaDB, execute o seguinte comando:

!!! info "Instalar o Mariadb"

    Red Hat
    ```yaml
    dnf install MariaDB-server
    ```

    Ubuntu
    ``` yaml
    sudo apt install mariadb-server
    ```

Esse comando realizará o download e instalará os pacotes do servidor e do
cliente, permitindo que você defina, configure e interaja com o banco de dados
MariaDB. Quando a instalação estiver concluída, você poderá iniciar e configurar
o serviço MariaDB.

Agora que o MariaDB está instalado, precisamos habilitar o serviço para iniciar
automaticamente na inicialização do sistema operacional, assim como iniciá-lo
imediatamente. Utilize o seguinte comando para realizar isso:

!!! info "Habilitar o serviço mariadb"

    Red Hat
    ```yaml
    systemctl enable mariadb --now
    ```

Esse comando habilitará e iniciará o serviço MariaDB. Quando o serviço estiver
em execução, você poderá verificar se a instalação foi bem-sucedida verificando
a versão do MariaDB usando o seguinte comando:

!!! info "Verificar versão do Mariadb"

    Red Hat and Ubuntu
    ```yaml
    sudo mariadb -V
    ```

A saída esperada deve ser similar a esta:

!!! informações ""

    ```yaml
    mariadb from 11.4.5-MariaDB, client 15.2 for Linux (aarch64) using EditLine wrapper
    ```

Para garantir que o serviço do MariaDB esteja funcionando corretamente, você
pode verificar o status com o seguinte comando:

!!! info "Obter status do mariadb"

    Red Hat and Ubuntu
    ```yaml
    sudo systemctl status mariadb
    ```

Você deverá ver um resultado semelhante a este, indicando que o serviço MariaDB
está ativo e em execução:

!!! info "mariadb service status example" (exemplo de status do serviço
mariadb")

    ```yaml
     mariadb.service - MariaDB 11.4.5 database server
          Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: disabled)
         Drop-In: /etc/systemd/system/mariadb.service.d
                  └─migrated-from-my.cnf-settings.conf
          Active: active (running) since Fri 2025-02-21 11:22:59 CET; 2min 8s ago
            Docs: man:mariadbd(8)
                  https://mariadb.com/kb/en/library/systemd/
         Process: 23147 ExecStartPre=/bin/sh -c systemctl unset-environment _WSREP_START_POSITION (code=exited, status=0/SUCCESS)
         Process: 23148 ExecStartPre=/bin/sh -c [ ! -e /usr/bin/galera_recovery ] && VAR= ||   VAR=`/usr/bin/galera_recovery`; [ $? -eq 0 ] && systemctl set-enviro>
    Process: 23168 ExecStartPost=/bin/sh -c systemctl unset-environment \_WSREP_START_POSITION (code=exited, status=0/SUCCESS)
    Main PID: 23156 (mariadbd)
    Status: "Taking your SQL requests now..."
    Tasks: 7 (limit: 30620)
    Memory: 281.7M
    CPU: 319ms
    CGroup: /system.slice/mariadb.service
    └─23156 /usr/sbin/mariadbd

    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] Plugin 'FEEDBACK' is disabled.
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] Plugin 'wsrep-provider' is disabled.
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] InnoDB: Buffer pool(s) load completed at 250221 11:22:58
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] Server socket created on IP: '0.0.0.0'.
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] Server socket created on IP: '::'.
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] mariadbd: Event Scheduler: Loaded 0 events
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: 2025-02-21 11:22:58 0 [Note] /usr/sbin/mariadbd: ready for connections.
    Feb 21 11:22:58 localhost.localdomain mariadbd[23156]: Version: '11.4.5-MariaDB'  socket: '/var/lib/mysql/mysql.sock'  port: 3306  MariaDB Server
    Feb 21 11:22:59 localhost.localdomain systemd[1]: Started MariaDB 11.4.5 database server.
    ```

Isso confirma que seu servidor MariaDB está funcionando e pronto para outras
configurações.

### Protegendo o banco de dados MariaDB

Para aumentar a segurança do seu servidor MariaDB, é essencial remover bancos de
dados de teste desnecessários, usuários anônimos e definir uma senha de raiz.
Isso pode ser feito usando o script mariadb-secure-installation, que fornece um
guia passo a passo para proteger seu banco de dados.

Execute o seguinte comando:

!!! info "Configuração segura do Mariadb"

    Red Hat and Ubuntu
    ```yaml
     sudo mariadb-secure-installation
    ```

!!! informações ""

    ```yaml
    NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
          SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!

    In order to log into MariaDB to secure it, we'll need the current
    password for the root user. If you've just installed MariaDB, and
    haven't set the root password yet, you should just press enter here.

    Enter current password for root (enter for none):
    OK, successfully used password, moving on...

    Setting the root password or using the unix_socket ensures that nobody
    can log into the MariaDB root user without the proper authorisation.

    You already have your root account protected, so you can safely answer 'n'.

    Switch to unix_socket authentication [Y/n] n
     ... skipping.

    You already have your root account protected, so you can safely answer 'n'.

    Change the root password? [Y/n] y
    New password:
    Re-enter new password:
    Password updated successfully!
    Reloading privilege tables..
     ... Success!


    By default, a MariaDB installation has an anonymous user, allowing anyone
    to log into MariaDB without having to have a user account created for
    them.  This is intended only for testing, and to make the installation
    go a bit smoother.  You should remove them before moving into a
    production environment.

    Remove anonymous users? [Y/n] y
     ... Success!

    Normally, root should only be allowed to connect from 'localhost'.  This
    ensures that someone cannot guess at the root password from the network.

    Disallow root login remotely? [Y/n] y
     ... Success!

    By default, MariaDB comes with a database named 'test' that anyone can
    access.  This is also intended only for testing, and should be removed
    before moving into a production environment.

    Remove test database and access to it? [Y/n] y
     - Dropping test database...
     ... Success!
     - Removing privileges on test database...
     ... Success!

    Reloading the privilege tables will ensure that all changes made so far
    will take effect immediately.

    Reload privilege tables now? [Y/n] y
     ... Success!

    Cleaning up...

    All done!  If you've completed all of the above steps, your MariaDB
    installation should now be secure.

    Thanks for using MariaDB!
    ```

O script mariadb-secure-installation o guiará por várias etapas importantes:

1. Defina uma senha de root, caso ainda não tenha sido definida.
2. Remover usuários anônimos.
3. Não permitir logins de raiz remotos.
4. Remova o banco de dados de teste.
5. Recarregue as tabelas de privilégios para garantir que as alterações tenham
   efeito.

Depois de concluída, sua instância do MariaDB estará significativamente mais
segura. Agora você está pronto para configurar o banco de dados para o Zabbix.

---

### Criar o banco de dados Zabbix

Com o MariaDB configurado e protegido, podemos prosseguir com a criação do banco
de dados para o Zabbix. Esse banco de dados armazenará todos os dados
necessários relacionados ao seu servidor Zabbix, incluindo informações de
configuração e dados de monitoramento.

Siga estas etapas para criar o banco de dados do Zabbix:

Faça login no shell do MariaDB como usuário root: Será solicitado que você
digite a senha de root que definiu durante o processo de instalação do
mariadb-secure-installation.

!!! info "Entre no Mariadb como usuário root"

    Red Hat and Ubuntu
    ```yaml
    mariadb -uroot -p
    ```

Quando estiver conectado ao shell do MariaDB, execute o seguinte comando para
criar um banco de dados para o Zabbix:

!!! info "Criar o banco de dados"

    `MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;`

???+ nota

     utf8mb4 is a proper implementation of UTF-8 in MySQL/MariaDB, supporting all
     Unicode characters, including emojis. The older utf8 charset in MySQL/MariaDB
     only supports up to three bytes per character and is not a true UTF-8 implementation,
     which is why utf8mb4 is recommended.

Esse comando cria um novo banco de dados chamado zabbix com o conjunto de
caracteres UTF-8, que é necessário para o Zabbix.

Crie um usuário dedicado para o Zabbix e conceda os privilégios necessários: Em
seguida, é necessário criar um usuário que o Zabbix usará para acessar o banco
de dados. Substitua a senha por uma senha forte de sua escolha.

!!! info "Criar usuários e conceder privilégios"

    ```sql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```

Isso cria novos usuários para o zabbix-web e o zabbix-srv, concede a eles acesso
ao banco de dados do zabbix e garante que os privilégios sejam aplicados
imediatamente.

Em alguns casos, especialmente ao configurar o Zabbix com o MariaDB, você pode
encontrar problemas relacionados a funções armazenadas e gatilhos se o registro
binário estiver ativado. Para resolver isso, você precisa definir a opção
log_bin_trust_function_creators como 1 no arquivo de configuração do MariaDB.
Isso permite que os usuários não raiz criem funções armazenadas e acionadores
sem exigir privilégios SUPER, que são restritos quando o registro em log binário
está ativado.

!!! info "Ativar temporariamente privilégios extras para usuários não root"

    ```sql
    MariaDB [(none)]> SET GLOBAL log_bin_trust_function_creators = 1;
    MariaDB [(none)]> QUIT
    ```

Neste ponto, seu banco de dados Zabbix está pronto e você pode prosseguir com a
configuração do servidor Zabbix para se conectar ao banco de dados.

???+ Aviso

    In the Zabbix documentation, it is explicitly stated that deterministic
    triggers need to be created during the schema import. On MySQL and MariaDB
    systems, this requires setting GLOBAL log_bin_trust_function_creators = 1
    if binary logging is enabled, and you lack superuser privileges.

    If the log_bin_trust_function_creators option is not set in the MySQL
    configuration file, it will block the creation of these triggers during
    schema import. This is essential because, without superuser access,
    non-root users cannot create triggers or stored functions unless this setting is applied.

    To summarize:

    - Binary logging enabled: If binary logging is enabled and the user does not
      have superuser privileges, the creation of necessary Zabbix triggers will
      fail unless log_bin_trust_function_creators = 1 is set.

    - Solution: Add log_bin_trust_function_creators = 1 to the [mysqld] section
      in your MySQL/MariaDB configuration file or temporarily set it at runtime
      with SET GLOBAL log_bin_trust_function_creators = 1 if you have sufficient
      permissions.

    This ensures that Zabbix can successfully create the required triggers during
    schema import without encountering privilege-related errors.

Se quisermos que o servidor Zabbix se conecte ao nosso banco de dados, também
precisaremos abrir a porta do firewall.

!!! info "Adicionar regras de firewall"

    Red Hat
    ``` yaml
    firewall-cmd --add-port=3306/tcp --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` yaml
    sudo ufw allow 3306/tcp
    ```

---

### Preencher o banco de dados do Zabbix Maria

Com os usuários e as permissões configurados corretamente, agora você pode
preencher o banco de dados com o esquema do Zabbix criado e outros elementos
necessários. Siga estas etapas:

Uma das primeiras coisas que precisamos fazer é adicionar o repositório Zabbix à
nossa máquina. Isso pode parecer estranho, mas na verdade faz sentido porque
precisamos preencher nosso banco de dados com os esquemas do Zabbix.

!!! info "Adicionar repositório Zabbix e instalar scripts"

    Red Hat
    ``` yaml
    rpm -Uvh https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
    dnf clean all
    dnf install zabbix-sql-scripts
    ```

    Ubuntu
    ``` yaml
    sudo wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo apt update
    sudo apt install zabbix-sql-scripts
    ```

Agora vamos fazer o upload dos dados do zabbix (estrutura do banco de dados,
imagens, usuário, ...) para isso, usamos o usuário `zabbix-srv` e fazemos o
upload de tudo em nosso banco de dados `zabbix`.

!!! info "Populate the database" (Preencher o banco de dados)

    Red Hat and Ubuntu
    ``` yaml
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```

???+ nota

    Depending on the speed of your hardware or virtual machine, the process may
    take anywhere from a few seconds to several minutes. Please be patient and
    avoid cancelling the operation; just wait for the prompt to appear.

Faça login novamente em seu banco de dados MySQL como root

!!! info "Entre no mariadb como usuário root"

    `mariadb -uroot -p`

Quando a importação do esquema do Zabbix estiver concluída e você não precisar
mais do parâmetro global log_bin_trust_function_creators, é uma boa prática
removê-lo por motivos de segurança.

Para reverter a alteração e definir o parâmetro global de volta para 0, use o
seguinte comando no shell do MariaDB:

!!! info "Desativar a função log_bin_trust novamente"

    ```sql
    mysql> SET GLOBAL log_bin_trust_function_creators = 0;
    Query OK, 0 rows affected (0.001 sec)
    ```

Esse comando desativará a configuração, garantindo que a postura de segurança
dos servidores permaneça robusta.

Isso conclui nossa instalação do MariaDB

---

## Instalação do banco de dados PostgreSQL

Para nossa configuração de banco de dados com o PostgreSQL, precisamos primeiro
adicionar nosso repositório PostgreSQL ao sistema. Até o momento, o PostgreSQL
13-17 é suportado, mas o melhor é dar uma olhada antes de instalá-lo, pois as
novas versões podem ser suportadas e as mais antigas podem não ser suportadas
tanto pelo Zabbix quanto pelo PostgreSQL. Normalmente, é uma boa ideia usar a
versão mais recente que é suportada pelo Zabbix. O Zabbix também suporta a
extensão TimescaleDB, sobre a qual falaremos mais tarde. Como você verá, a
configuração do PostgreSQL é muito diferente da do MySQL, não apenas na
instalação, mas também na proteção do banco de dados.

A tabela de compatibilidade pode ser encontrada em
[https://docs.timescale.com/self-hosted/latest/upgrades/upgrade-pg/](https://docs.timescale.com/self-hosted/latest/upgrades/upgrade-pg/)

---

### Adicionar o repositório PostgreSQL

Então, vamos começar configurando nosso repositório PostgreSQL com os seguintes
comandos.

!!! info "Adicionar repositório PostgreSQL"

    Red Hat
    ``` yaml
    Install the repository RPM:
    dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

    Disable the built-in PostgreSQL module:
    dnf -qy module disable postgresql
    ```

    Ubuntu
    ```
    # Import the repository signing key:
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

    # Create the repository configuration file:
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    # Update the package lists:
    sudo apt update
    ```

### Instalar os bancos de dados PostgreSQL

!!! info "Instalar o servidor Postgres"

    Red Hat
    ``` yaml
    # Install Postgres server:
    dnf install postgresql17-server

    # Initialize the database and enable automatic start:
    /usr/pgsql-17/bin/postgresql-17-setup initdb
    systemctl enable postgresql-17 --now
    ```

    Ubuntu
    ``` yaml
    sudo apt install postgresql-17
    ```

Para atualizar seu sistema operacional, execute o seguinte comando:

!!! info "atualizar o sistema operacional"

    Red Hat
    ``` yaml
    dnf update
    ```

    Ubuntu
    ``` yaml
    sudo apt update && sudo apt upgrade
    ```

---

### Protegendo o banco de dados PostgreSQL

O PostgreSQL lida com as permissões de acesso de forma diferente do MySQL e do
MariaDB. O PostgreSQL depende de um arquivo chamado pg_hba.conf para gerenciar
quem pode acessar o banco de dados, de onde e qual método de criptografia é
usado para autenticação.

???+ nota

    Client authentication in PostgreSQL is configured through the pg_hba.conf
    file, where "HBA" stands for Host-Based Authentication. This file specifies
    which users can access the database, from which hosts, and how they are authenticated.
    For further details, you can refer to the official PostgreSQL documentation."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Adicione as seguintes linhas, a ordem aqui é importante.

!!! info "Editar o arquivo pg_hba"

    Red hat
    ``` yaml
    vi /var/lib/pgsql/17/data/pg_hba.conf
    ```

    Ubuntu
    ``` yanl
    sudo vi /etc/postgresql/17/main/pg_hba.conf
    ```

O resultado deve ser semelhante a :

!!! info "exemplo pg_hba"

    ``` yaml
    # "local" is for Unix domain socket connections only
    local    zabbix     zabbix-srv                                                              scram-sha-256
    local    all            all                                                                            peer
    # IPv4 local connections
    host     zabbix     zabbix-srv          <ip from zabbix server/24>     scram-sha-256
    host     zabbix     zabbix-web        <ip from zabbix server/24>     scram-sha-256
    host     all            all                         127.0.0.1/32                            scram-sha-256
    ```

Depois de alterarmos o arquivo pg_hba, não se esqueça de reiniciar o postgres,
caso contrário as configurações não serão aplicadas. Mas antes de reiniciarmos,
vamos também editar o arquivo postgresql.conf e permitir que nosso banco de
dados escute em nossa interface de rede as conexões de entrada do servidor
zabbix. O Postgresql padrão só permitirá conexões do soquete.

!!! info "Editar arquivo postgresql.conf"

    Red Hat
    ``` yaml
    vi /var/lib/pgsql/17/data/postgresql.conf
    ```

    Ubuntu
    ``` yaml
    sudo vi /etc/postgresql/17/main/postgresql.conf
    ```

Para configurar o PostgreSQL para escutar em todas as interfaces de rede, você
precisa modificar o arquivo `postgresql.conf`. Localize a seguinte linha:

!!! informações ""

    ```yaml
    #listen_addresses = 'localhost'
    ```

e substituí-la por:

!!! informações ""

    `listen_addresses = '*'`

???+ nota

    This will enable PostgreSQL to accept connections from any network interface,
    not just the local machine. In production it's probably a good idea to limit
    who can connect to the DB.

Depois de fazer essa alteração, reinicie o serviço PostgreSQL para aplicar as
novas configurações:

!!! info "restart the DB server" (reinicie o servidor de banco de dados)

    Red Hat
    ``` yaml
    systemctl restart postgresql-17
    ```

    Ubuntu
    ``` yaml
    sudo systemctl restart postgresql
    ```

Se o serviço não for reiniciado, verifique se há erros de sintaxe no arquivo
pg_hba.conf, pois entradas incorretas podem impedir a inicialização do
PostgreSQL.

Em seguida, para preparar sua instância do PostgreSQL para o Zabbix, você
precisará criar as tabelas de banco de dados necessárias. Comece instalando o
repositório do Zabbix, como você fez para o servidor Zabbix. Em seguida, instale
o pacote Zabbix apropriado que contém as tabelas predefinidas, as imagens, os
ícones e outros elementos de banco de dados necessários para o aplicativo
Zabbix.

---

### Criar o banco de dados do Zabbix com o PostgreSQL

Para começar, adicione o repositório Zabbix ao seu sistema executando os
seguintes comandos:

!!! info "Adicionar pacote de repositórios de esquemas do zabbix"

    Red Hat
    ``` yaml
    dnf install https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
    dnf install zabbix-sql-scripts
    ```

    Ubuntu
    ``` yaml
    sudo wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo apt update
    sudo apt install zabbix-sql-scripts
    ```

Com os pacotes necessários instalados, agora você está pronto para criar os
usuários do Zabbix para o servidor e o front-end.

Primeiro, mude para o usuário `postgres` e crie o usuário do banco de dados do
servidor Zabbix:

!!! info "criar usuários do servidor"

    ```sql
    sudo su - postgres
    createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```

Em seguida, crie o usuário front-end do Zabbix, que será usado para se conectar
ao banco de dados:

!!! info "Criar usuário de front-end"

    ```sql
    createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```

Depois de criar os usuários, é necessário preparar o esquema do banco de dados.
Como root ou usuário comum, descompacte os arquivos de esquema necessários
executando o seguinte comando:

!!! info "Descompacte o patch do DB"

    Red Hat
    ``` yaml
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

    Ubuntu
    ``` yaml
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

???+ nota

    Zabbix seems to like to change the locations of the script to populate the
    DB every version or in between versions. If you encounter an error take a
    look at the Zabbix documentation there is a good chance that some location was
    changed.

Isso extrairá o esquema do banco de dados necessário para o servidor Zabbix.

Agora que os usuários foram criados, a próxima etapa é criar o banco de dados do
Zabbix. Primeiro, mude para o usuário `postgres` e execute o seguinte comando
para criar o banco de dados com o proprietário definido como zabbix-srv:

!!! info "Criar banco de dados"

    Red Hat
    ``` yaml
    su - postgres
    createdb -E Unicode -O zabbix-srv zabbix
    exit
    ```

    Ubuntu
    ``` yaml
    sudo su - postgres
    createdb -E Unicode -O zabbix-srv zabbix
    exit
    ```

Depois que o banco de dados for criado, verifique a conexão e certifique-se de
que a sessão correta do usuário esteja ativa. Para fazer isso, faça login no
banco de dados zabbix usando o usuário zabbix-srv:

!!! info "Faça login como usuário zabbix-srv"

    ```yaml
    psql -d zabbix -U zabbix-srv
    ```

Depois de fazer login, execute a seguinte consulta SQL para confirmar que tanto
o `session_user` quanto o `current_user` estão definidos como `zabbix-srv`:

!!! informações ""

    ```yaml
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```

Se a saída corresponder, você se conectou com sucesso ao banco de dados com o
usuário correto.

O PostgreSQL de fato difere significativamente do MySQL ou do MariaDB em vários
aspectos, e um dos principais recursos que o diferencia é o uso de esquemas. Ao
contrário do MySQL, em que os bancos de dados são mais independentes, o sistema
de esquema do PostgreSQL fornece um ambiente estruturado e multiusuário em um
único banco de dados.

Os esquemas funcionam como contêineres lógicos dentro de um banco de dados,
permitindo que vários usuários ou aplicativos acessem e gerenciem dados de forma
independente, sem conflitos. Esse recurso é especialmente valioso em ambientes
em que vários usuários ou aplicativos precisam interagir com o mesmo banco de
dados simultaneamente. Cada usuário ou aplicativo pode ter seu próprio esquema,
evitando interferências acidentais nos dados dos outros.

???+ nota

    PostgreSQL comes with a default schema, typically called public, but it's in
    general best practice to create custom schemas to better organize and separate
    database objects, especially in complex or multi-user environments.

    For more in-depth information, I recommend checking out the detailed guide at
    this URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    which explains the benefits and use cases for schemas in PostgreSQL.

Para finalizar a configuração do banco de dados para o Zabbix, precisamos
configurar as permissões do esquema para os usuários `zabbix-srv` e
`zabbix-web`.

Primeiro, criamos um esquema personalizado chamado `zabbix_server` e atribuímos
a propriedade ao usuário `zabbix-srv`:

!!! info "create the db schema" (criar o esquema do banco de dados)

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```

Em seguida, definimos o caminho de pesquisa `` para `zabbix_server` schema para
que seja o padrão da sessão atual:

!!! info "Definir caminho de pesquisa"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```

Para confirmar a configuração do esquema, você pode listar os esquemas
existentes:

!!! info "verify schema access" (verificar acesso ao esquema)

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```

Neste ponto, o usuário `zabbix-srv` tem acesso total ao esquema, mas o usuário
`zabbix-web` ainda precisa de permissões apropriadas para se conectar e
interagir com o banco de dados. Primeiro, concedemos a `USAGE` privilégios no
esquema para permitir que `zabbix-web` se conecte:

!!! info "Conceder acesso ao esquema para o usuário zabbix-web"

    ```psql
    zabbix=# GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```

---

### Preencher o banco de dados PostgreSQL do Zabbix

Agora, o usuário `zabbix-web` tem acesso adequado para interagir com o esquema,
mantendo a segurança ao limitar as permissões às operações essenciais.

Com os usuários e as permissões configurados corretamente, agora você pode
preencher o banco de dados com o esquema do Zabbix criado e outros elementos
necessários. Siga estas etapas:

- Execute o arquivo SQL para preencher o banco de dados. Execute o seguinte
  comando no shell `psql`:

???+ Aviso

    Make sure you did previous steps carefully so that you have selected the correct
    search_path.

!!! info "upload the DB schema to db zabbix" (carregar o esquema do banco de
dados para o banco de dados zabbix)

    ```sql
    sql zabbix=# \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```

???+ Aviso

    Depending on your hardware or VM performance, this process can take anywhere
    from a few seconds to several minutes. Please be patient and avoid cancelling
    the operation.

- Monitore o progresso à medida que o script é executado. Você verá uma saída
  semelhante a:

!!! info "Exemplo de saída"

    ```sql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    CREATE INDEX
    CREATE TABLE
    ...
    ...
    ...
    INSERT 0 10444
    DELETE 90352
    COMMIT
    ```

Quando o script for concluído e você retornar ao prompt `zabbix=#`, o banco de
dados deverá ser preenchido com sucesso com todas as tabelas, esquemas, imagens
e outros elementos necessários para o Zabbix.

Entretanto, `zabbix-web` ainda não pode executar nenhuma operação nas tabelas ou
sequências. Para permitir a interação básica dos dados sem conceder muitos
privilégios, conceda as seguintes permissões:

- Para tabelas: SELECT, INSERT, UPDATE e DELETE.
- Para sequências: SELECT e UPDATE.

!!! info "Grant rights on the schema to user zabbix-web" (Conceder direitos
sobre o esquema ao usuário zabbix-web)

    ```psql
    zabbix=# GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=# GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```

Verifique se os direitos estão corretos no esquema:

!!! info "Exemplo de direitos de esquema"

    ```psql
    zabbix=> \dn+
                                               List of schemas
         Name      |       Owner       |           Access privileges            |      Description
    ---------------+-------------------+----------------------------------------+------------------------
     public        | pg_database_owner | pg_database_owner=UC/pg_database_owner+| standard public schema
                   |                   | =U/pg_database_owner                   |
     zabbix_server | zabbix-srv        | "zabbix-srv"=UC/"zabbix-srv"          +|
                   |                   | "zabbix-web"=U/"zabbix-srv"            |
    ```

???+ nota

    If you encounter the following error during the SQL import:
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: no
        schema has been selected to create in` It indicates that the search_path setting
    might not have been correctly applied. This setting is crucial because it specifies
    the schema where the tables and other objects should be created. By correctly
    setting the search path, you ensure that the SQL script will create tables
    and other objects in the intended schema.

Para garantir que as tabelas do Zabbix foram criadas com êxito e têm as
permissões corretas, você pode verificar a lista de tabelas e sua propriedade
usando o comando `psql`:

- Listar as tabelas: Use o seguinte comando para listar todas as tabelas no
  esquema `zabbix_server`:

!!! info "Listar tabelas"

    ```sql
    sql zabbix=# \dt
    ```

Você verá uma lista de tabelas com seu esquema, nome, tipo e proprietário. Por
exemplo:

!!! info "Listar tabela com relações"

    ```sql
    zabbix=> \dt
                            List of relations
        Schema     |            Name            | Type  |   Owner
    ---------------+----------------------------+-------+------------
     zabbix_server | acknowledges               | table | zabbix-srv
     zabbix_server | actions                    | table | zabbix-srv
     zabbix_server | alerts                     | table | zabbix-srv
     zabbix_server | auditlog                   | table | zabbix-srv
     zabbix_server | autoreg_host               | table | zabbix-srv
     zabbix_server | changelog                  | table | zabbix-srv
     zabbix_server | conditions                 | table | zabbix-srv
    ...
    ...
    ...
     zabbix_server | valuemap                   | table | zabbix-srv
     zabbix_server | valuemap_mapping           | table | zabbix-srv
     zabbix_server | widget                     | table | zabbix-srv
     zabbix_server | widget_field               | table | zabbix-srv
    (203 rows)
    ```

- Verificar permissões: Confirme se o usuário zabbix-srv é o proprietário das
  tabelas e se tem as permissões necessárias. Você pode verificar as permissões
  de tabelas específicas usando o comando \dp:

!!! informações ""

    ```sql
    sql zabbix=# \dp zabbix_server.*
    ```

    ```sql
                                                         Access privileges
        Schema     |            Name            |   Type   |         Access privileges          | Column privileges | Policies
    ---------------+----------------------------+----------+------------------------------------+-------------------+----------
     zabbix_server | acknowledges               | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | actions                    | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | alerts                     | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
                   |                            |          | "zabbix-web"=arwd/"zabbix-srv"     |                   |
     zabbix_server | auditlog                   | table    | "zabbix-srv"=arwdDxtm/"zabbix-srv"+|                   |
    ```

Isso exibirá os privilégios de acesso de todas as tabelas no esquema
`zabbix_server`. Certifique-se de que `zabbix-srv` tenha os privilégios
necessários.

Se tudo estiver correto, suas tabelas foram criadas corretamente e o usuário
`zabbix-srv` tem a propriedade e as permissões adequadas. Se precisar ajustar
alguma permissão, você poderá fazê-lo usando os comandos GRANT, conforme
necessário.

???+ nota

    If you prefer not to set the search path manually each time you log in as the
    `zabbix-srv` user, you can configure PostgreSQL to automatically use the desired
    search path. Run the following SQL command to set the default search path for
    the `zabbix-srv` role:

    sql zabbix=> ALTER ROLE "zabbix-srv" SET search_path = "$user", public, zabbix_server;

    This command ensures that every time the `zabbix-srv` user connects to the
    database, the `search_path` is automatically set to include `$user`, `public`, and `zabbix_server`.

Se estiver pronto, você poderá sair do banco de dados e retornar como usuário
root.

!!! info "Sair do banco de dados"

    ```sql
    zabbix=> \q
    ```

Se quisermos que o servidor Zabbix possa se conectar ao nosso banco de dados,
também precisaremos abrir a porta do firewall.

!!! informações ""

    Red Hat
    ``` yaml
    firewall-cmd --add-port=5432/tcp --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` yaml
    sudo ufw allow 5432/tcp
    ```

???+ nota

    Make sure your DB is listening on the correct IP and not on 127.0.0.1.
    You could add the following files to your config file. This would allow MariaDB
    to listen on all interfaces. Best to limit it only to the needed IP.

    /etc/mysql/mariadb.cnf

    [mariadb]
    log_error=/var/log/mysql/mariadb.err
    log_warnings=3
    bind-address = 0.0.0.0

Isso conclui nossa instalação do banco de dados PostgreSQL.

---

## Instalando o servidor Zabbix para MariaDB/Mysql

Antes de prosseguir com a instalação do servidor Zabbix, certifique-se de que o
servidor esteja configurado corretamente, conforme descrito na seção anterior
[Requisitos do sistema](../ch00-getting-started/Requirements.md)

Outro passo crítico nesta etapa, se você usa sistemas baseados no Red Hat, é
desabilitar o SELinux, que pode interferir na instalação e operação do Zabbix.
Voltaremos a falar sobre o SELinux no final deste capítulo, quando nossa
instalação estiver concluída.

Para verificar o status atual do SELinux, você pode usar o seguinte comando:
`sestatus``

!!! info "Status do Selinux"

    ```yaml
    sestatus
    ```
    ```yaml
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   enforcing
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Conforme mostrado, o sistema está atualmente no modo de aplicação. Para
desativar temporariamente o SELinux, você pode executar o seguinte comando:
`setenforce 0`

!!! info "Desativar o SeLinux"

    ```yaml
    setenforce 0
    sestatus
    ```
    ```
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Agora, como você pode ver, o modo foi alterado para permissivo. No entanto, essa
alteração não é persistente nas reinicializações. Para torná-la permanente, você
precisa modificar o arquivo de configuração do SELinux localizado em
`/etc/selinux/config`. Abra o arquivo e substitua enforcing por `permissive`.

Como alternativa, você pode obter o mesmo resultado mais facilmente executando o
seguinte comando:

!!! info "Desativar o SeLinux permanentemente"

    Red Hat
    ``` yaml
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Essa linha alterará o arquivo de configuração para você. Portanto, quando
executarmos `sestatus` novamente, veremos que estamos no modo `permissivo` e que
nosso arquivo de configuração também está no modo permissivo.

!!! info "Verificar novamente o status do selinux"

    ```yaml
    sestatus
    ```
    ```yaml
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          permissive
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

---

### Adicionando o repositório Zabbix

Na página de download do Zabbix
[https://www.zabbix.com/download](https://www.zabbix.com/download), selecione a
versão apropriada do Zabbix que você deseja instalar. Neste caso, usaremos o
Zabbix 8.0 LTS. Além disso, certifique-se de escolher a distribuição de sistema
operacional correta para seu ambiente, que será o Rocky Linux 9 ou o Ubuntu
24.04 em nosso caso.

Instalaremos o Zabbix Server juntamente com o NGINX como o servidor Web para o
front-end. Certifique-se de fazer o download dos pacotes relevantes para a
configuração escolhida.

![Download do
Zabbix](./basic-installation/ch01-basic-installation-zabbixdownload.png)

_1.2 Download do Zabbix_

Se você usa um sistema baseado no RHEL, como o Rocky, a primeira etapa é
desativar os pacotes Zabbix fornecidos pelo repositório EPEL, se ele estiver
instalado em seu sistema. Para fazer isso, edite o arquivo
`/etc/yum.repos.d/epel.repo` e adicione a seguinte instrução para desativar o
repositório EPEL por padrão:

!!! info "excluir pacotes"

    Red Hat
    ``` yaml
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ dica

    It's considered bad practice to keep the EPEL repository enabled all the time,
    as it may cause conflicts by unintentionally overwriting or installing unwanted
    packages. Instead, it's safer to enable the repository only when needed, by using
    the following command during installations: dnf install --enablerepo=epel <package-name>
    This ensures that EPEL is only enabled when explicitly required.

Em seguida, instalaremos o repositório Zabbix em nosso sistema operacional.
Depois de adicionar o repositório do Zabbix, é recomendável executar uma limpeza
do repositório para remover arquivos de cache antigos e garantir que os
metadados do repositório estejam atualizados. Você pode fazer isso executando:

!!! info "Adicionar o repositório zabbix"

    Red Hat
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

Isso atualizará os metadados do repositório e preparará o sistema para a
instalação do Zabbix.

???+ nota

    A repository in Linux is a configuration that allows you to access and install
    software packages. You can think of it like an "app store" where you find and
    download software from a trusted source, in this case, the Zabbix repository.
    Many repositories are available, but it's important to only add those you trust.
    The safest practice is to stick to the repositories provided by your operating
    system and only add additional ones when you're sure they are both trusted and necessary.

    For our installation, the Zabbix repository is provided by the vendor itself,
    making it a trusted source. Another popular and safe repository for
    Red Hat-based systems is EPEL (Extra Packages for Enterprise Linux), which is
    commonly used in enterprise environments.
    However, always exercise caution when adding new repositories to ensure
    system security and stability.

---

### Configuração do servidor Zabbix para MySQL/MariaDB

Agora que adicionamos o repositório Zabbix com o software necessário, estamos
prontos para instalar o servidor Zabbix e o servidor Web. Lembre-se de que o
servidor Web não precisa ser instalado na mesma máquina que o servidor Zabbix;
eles podem ser hospedados em sistemas separados, se desejado.

Para instalar o servidor Zabbix e os componentes do servidor Web para
MySQL/MariaDB, execute o seguinte comando:

!!! info "Instalar o servidor zabbix"

    Red Hat
    ``` yaml
    dnf install zabbix-server-mysql
    ```

    Ubuntu
    ``` yaml
    sudo apt install zabbix-server-mysql
    ```

Depois de instalar com sucesso os pacotes do Zabbix Server e do front-end,
precisamos configurar o Zabbix Server para se conectar ao banco de dados. Para
isso, é necessário modificar o arquivo de configuração do servidor Zabbix. Abra
o arquivo `/etc/zabbix/zabbix_server.conf` e atualize as seguintes linhas para
que correspondam à configuração do seu banco de dados:

!!! info "Editar configuração do servidor zabbix"

    Red Hat and Ubuntu
    ``` yaml
    sudo vi /etc/zabbix/zabbix_server.conf
    ```
    ``` yaml
    DBHost=<database-host>
    DBName=<database-name>
    DBUser=<database-user>
    DBPassword=<database-password>
    ```

Substitua `<database-host>`, `<database-name>`, `<database-user>` e
`<database-password>` pelos valores apropriados para sua configuração. Isso
garante que o servidor Zabbix possa se comunicar com seu banco de dados.

Certifique-se de que não há nenhum # (símbolo de comentário) na frente dos
parâmetros de configuração, pois o Zabbix tratará as linhas que começam com #
como comentários, ignorando-as durante a execução. Além disso, verifique se há
linhas de configuração duplicadas; se houver várias linhas com o mesmo
parâmetro, o Zabbix usará o valor da última ocorrência.

Para nossa instalação, a configuração será semelhante a esta:

!!! info "Exemplo de configuração"

    ```yaml
    DBHost=<ip or dns of your MariaDB server>
    DBName=zabbix
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=3306
    ```

In this example:

- DBHost refers to the host where your database is running (use localhost if
  it's on the same machine).
- DBName is the name of the Zabbix database.
- DBUser is the database user.
- DBPassword is the password for the database user.

Make sure the settings reflect your environment's database configuration.

???+ nota

    The Zabbix server configuration file offers an option to include additional
    configuration files for custom parameters. For a production environment, it's
    often best to avoid altering the original configuration file directly. Instead,
    you can create and include a separate configuration file for any additional or
    modified parameters. This approach ensures that your original configuration
    file remains untouched, which is particularly useful when performing upgrades
    or managing configurations with tools like Ansible, Puppet, or SaltStack.

To enable this feature, remove the # from the line:

!!! informações ""

    ```yaml
    # Include=/usr/local/etc/zabbix_server.conf.d/*.conf
    ```

Ensure the path `/usr/local/etc/zabbix_server.conf.d/` exists and create a
custom configuration file in this directory. This file should be readable by the
`zabbix` user. By doing so, you can add or modify parameters without modifying
the default configuration file, making system management and upgrades smoother.

With the Zabbix server configuration updated to connect to your database, you
can now start and enable the Zabbix server service. Run the following command to
enable the Zabbix server and ensure it starts automatically on boot:

???+ nota

    Before restarting the Zabbix server after modifying its configuration, it is
    considered best practice to validate the configuration to prevent potential
    issues. Running a configuration check ensures that any errors are detected
    beforehand, avoiding downtime caused by an invalid configuration. This can
    be accomplished using the following command: `zabbix-server -T`

!!! info "enable and start zabbix-server service"

    Red Hat and Ubuntu
    ``` yaml
    sudo systemctl enable zabbix-server --now
    ```

This command will start the Zabbix server service immediately and configure it
to launch on system startup. To verify that the Zabbix server is running
correctly, check the log file for any messages. You can view the latest entries
in the `Zabbix server` log file using:

!!! info "Check the log file"

    ```yaml
    tail /var/log/zabbix/zabbix_server.log
    ```

Look for messages indicating that the server has started successfully. If there
are any issues, the log file will provide details to help with troubleshooting.

!!! info "Exemplo de saída"

    ```yaml
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

If there was an error and the server was not able to connect to the database you
would see something like this in the server log file :

!!! info "Example log with errors"

    ```yaml
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

Let's check the Zabbix server service to see if it's enabled so that it survives
a reboot

!!! info "check status of zabbix-server service"

    ```yaml
    systemctl status zabbix-server
    ```
    ```
    zabbix-server.service - Zabbix Server
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

This concludes our chapter on installing and configuring the Zabbix server with
Mariadb.

---

## Installing the Zabbix server for PostgreSQL

Antes de prosseguir com a instalação do servidor Zabbix, certifique-se de que o
servidor esteja configurado corretamente, conforme descrito na seção anterior
[Requisitos do sistema](../ch00-getting-started/Requirements.md)

Outro passo crítico nesta etapa, se você usa sistemas baseados no Red Hat, é
desabilitar o SELinux, que pode interferir na instalação e operação do Zabbix.
Voltaremos a falar sobre o SELinux no final deste capítulo, quando nossa
instalação estiver concluída.

Para verificar o status atual do SELinux, você pode usar o seguinte comando:
`sestatus``

!!! info "check the selinux status"

    ```yaml
    sestatus

    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   enforcing
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Conforme mostrado, o sistema está atualmente no modo de aplicação. Para
desativar temporariamente o SELinux, você pode executar o seguinte comando:
`setenforce 0`

!!! info "change selinux to permissive"

    ``` yaml
    setenforce 0
    sestatus
    ```
    ```
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Agora, como você pode ver, o modo foi alterado para permissivo. No entanto, essa
alteração não é persistente nas reinicializações. Para torná-la permanente, você
precisa modificar o arquivo de configuração do SELinux localizado em
`/etc/selinux/config`. Abra o arquivo e substitua enforcing por `permissive`.

Como alternativa, você pode obter o mesmo resultado mais facilmente executando o
seguinte comando:

!!! info "Adapt selinux config permanently"

    Red Hat
    ``` yaml
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Essa linha alterará o arquivo de configuração para você. Portanto, quando
executarmos `sestatus` novamente, veremos que estamos no modo `permissivo` e que
nosso arquivo de configuração também está no modo permissivo.

!!! info "check if everything is disabled"

    ```yaml
    sestatus

    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          permissive
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

---

### Adicionando o repositório Zabbix

Na página de download do Zabbix
[https://www.zabbix.com/download](https://www.zabbix.com/download), selecione a
versão apropriada do Zabbix que você deseja instalar. Neste caso, usaremos o
Zabbix 8.0 LTS. Além disso, certifique-se de escolher a distribuição de sistema
operacional correta para seu ambiente, que será o Rocky Linux 9 ou o Ubuntu
24.04 em nosso caso.

Instalaremos o Zabbix Server juntamente com o NGINX como o servidor Web para o
front-end. Certifique-se de fazer o download dos pacotes relevantes para a
configuração escolhida.

![zabbix-download](ch01-basic-installation-zabbixdownload.png)

_1.3 Download do Zabbix_

Se você usa um sistema baseado no RHEL, como o Rocky, a primeira etapa é
desativar os pacotes Zabbix fornecidos pelo repositório EPEL, se ele estiver
instalado em seu sistema. Para fazer isso, edite o arquivo
`/etc/yum.repos.d/epel.repo` e adicione a seguinte instrução para desativar o
repositório EPEL por padrão:

!!! info "Adicionar exclusão ao epelrepo para o zabbix"

    Red Hat
    ``` yaml
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ dica

    It's considered bad practice to keep the EPEL repository enabled all the time,
    as it may cause conflicts by unintentionally overwriting or installing unwanted
    packages. Instead, it's safer to enable the repository only when needed, by using
    the following command during installations: dnf install --enablerepo=epel <package-name>
    This ensures that EPEL is only enabled when explicitly required.

Em seguida, instalaremos o repositório Zabbix em nosso sistema operacional.
Depois de adicionar o repositório do Zabbix, é recomendável executar uma limpeza
do repositório para remover arquivos de cache antigos e garantir que os
metadados do repositório estejam atualizados. Você pode fazer isso executando:

!!! info "add the repo"

    Red Hat
    ```yaml
    rpm -Uvh https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
    dnf clean all
    ```

    Ubuntu
    ``` yaml
    sudo wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
    sudo apt update
    ```

Isso atualizará os metadados do repositório e preparará o sistema para a
instalação do Zabbix.

???+ nota

    A repository in Linux is a configuration that allows you to access and install
    software packages. You can think of it like an "app store" where you find and
    download software from a trusted source, in this case, the Zabbix repository.
    Many repositories are available, but it's important to only add those you trust.
    The safest practice is to stick to the repositories provided by your operating
    system and only add additional ones when you're sure they are both trusted and
    necessary.

    For our installation, the Zabbix repository is provided by the vendor itself,
    making it a trusted source. Another popular and safe repository for
    Red Hat-based systems is EPEL (Extra Packages for Enterprise Linux), which is
    commonly used in enterprise environments.
    However, always exercise caution when adding new repositories to ensure
    system security and stability.

---

### Configuring the Zabbix server for PostgreSQL

We are ready to install both the Zabbix server and the web server. Keep in mind
that the web server doesn't need to be installed on the same machine as the
Zabbix server; they can be hosted on separate systems if desired.

To install the Zabbix server and the web server components for PostgreSQL, run
the following command:

!!! info "install zabbix server"

    Red Hat

    ```yaml
    dnf install zabbix-server-pgsql
    ```

    Ubuntu

    ```yaml
    sudo apt install zabbix-server-pgsql
    ```

After successfully installing the Zabbix server packages, we need to configure
the Zabbix server to connect to the database. This requires modifying the Zabbix
server configuration file. Open the `/etc/zabbix/zabbix_server.conf` file and
update the following lines to match your database configuration:

!!! info "Editar configuração do servidor zabbix"

    Red Hat and Ubuntu
    ```yaml
    #sudo vi /etc/zabbix/zabbix_server.conf
    ```

    ```yaml
    DBHost=<database-host>
    DBName=<database-name>
    DBSchema=<database-schema>
    DBUser=<database-user>
    DBPassword=<database-password>
    ```

Replace `database-host`, `database-name`, `database-user`,`database-schema` and
`database-password` with the appropriate values for your setup. This ensures
that the Zabbix server can communicate with your database.

Certifique-se de que não há nenhum # (símbolo de comentário) na frente dos
parâmetros de configuração, pois o Zabbix tratará as linhas que começam com #
como comentários, ignorando-as durante a execução. Além disso, verifique se há
linhas de configuração duplicadas; se houver várias linhas com o mesmo
parâmetro, o Zabbix usará o valor da última ocorrência.

Para nossa instalação, a configuração será semelhante a esta:

!!! info "Exemplo de configuração"

    ```yaml
    DBHost=<ip or dns of your PostgreSQL server>
    DBName=zabbix
    DBSchema=zabbix_server
    DBUser=zabbix-srv
    DBPassword=<your super secret password>
    DBPort=5432
    ```

In this example:

- DBHost refers to the host where your database is running (use localhost if
  it's on the same machine).
- DBName is the name of the Zabbix database.
- DBUser is the database user.
- DBPassword is the password for the database user.

Make sure the settings reflect your environment's database configuration.

???+ nota

    The Zabbix server configuration file offers an option to include additional
    configuration files for custom parameters. For a production environment, it's
    often best to avoid altering the original configuration file directly. Instead,
    you can create and include a separate configuration file for any additional or
    modified parameters. This approach ensures that your original configuration
    file remains untouched, which is particularly useful when performing upgrades
    or managing configurations with tools like Ansible, Puppet, or SaltStack.

To enable this feature, remove the # from the line:

!!! informações ""

    `# Include=/usr/local/etc/zabbix_server.conf.d/*.conf`

Ensure the path `/usr/local/etc/zabbix_server.conf.d/` exists and create a
custom configuration file in this directory. This file should be readable by the
`zabbix` user. By doing so, you can add or modify parameters without modifying
the default configuration file, making system management and upgrades smoother.

With the Zabbix server configuration updated to connect to your database, you
can now start and enable the Zabbix server service. Run the following command to
enable the Zabbix server and ensure it starts automatically on boot:

!!! info "enable zabbix server service and start"

    Red Hat
    ```yaml
    systemctl enable zabbix-server --now
    ```

    Ubuntu
    ```yaml
    sudo systemctl enable zabbix-server --now
    ```

This command will start the Zabbix server service immediately and configure it
to launch on system startup. To verify that the Zabbix server is running
correctly, check the log file for any messages. You can view the latest entries
in the `Zabbix server` log file using:

!!! info "check the zabbix log file"

    ```yaml
    tail /var/log/zabbix/zabbix_server.log
    ```

Look for messages indicating that the server has started successfully. If there
are any issues, the log file will provide details to help with troubleshooting.

!!! info "Example log output"

    ```yaml
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

If there was an error and the server was not able to connect to the database you
would see something like this in the server log file :

!!! info "Example of an error in the log"

    ```yaml
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

Let's check the Zabbix server service to see if it's enabled so that it survives
a reboot

!!! info "check server status"

    ```yaml
     systemctl status zabbix-server
    ```
    ```yaml
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

This concludes our chapter on installing and configuring the Zabbix server with
PostgreSQL.

---

## Instalando o front-end

Before configuring the front-end, you need to install the necessary packages. If
the Zabbix front-end is hosted on the same server as the Zabbix server, you can
install the packages on the same server as is in our case. It's also perfectly
possible to install the front-end on another server. In that case you only need
to specify the correct IP addresses and open the correct firewall ports.

---

### Installing the frontend with NGINX

!!! info "install frontend packages"

    Red Hat
    ```yaml
    # dnf install zabbix-nginx-conf zabbix-web-mysql
    or if you used PostgreSQL
    # dnf install zabbix-nginx-conf zabbix-web-pgsql
    ```

    Ubuntu
    ```yaml
    # sudo apt install zabbix-frontend-php php8.3-mysql zabbix-nginx-conf
    or if you use PostgreSQL
    # sudo apt install zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```

This command will install the front-end packages along with the required
dependencies for Nginx. If you are installing the front-end on a different
server, make sure to execute this command on that specific machine.

If you don't remember how to add the repository, have a look at the topic
[Adding the zabbix repository](#adding-the-zabbix-repository)

First thing we have to do is alter the Nginx configuration file so that we don't
use the standard config.

!!! info "edit nginx config for Red Hat"

    ```yaml
    vi /etc/nginx/nginx.conf
    ```

In this configuration file look for the following block that starts with :

!!! info "original config"

    ```yaml
    server {
    listen 80;
    listen [::]:80;
    server*name *;
    root /usr/share/nginx/html;

             # Load configuration files for the default server block.
             include /etc/nginx/default.d/*.conf;
    ```

Then, comment out the following server block within the configuration file:

!!! info "config after edit"

    ```yaml
    server {
    # listen 80;
    # listen [::]:80;
    # server*name *;
    # root /usr/share/nginx/html;
    ```

The Zabbix configuration file must now be modified to reflect the current
environment. Open the following file for editing:

!!! info "edit zabbix config for nginx"

    ```yaml
    vi /etc/nginx/conf.d/zabbix.conf
    ```

And alter the following lines:

!!! info "original config"

    ```yaml
    server {
    listen 8080;
    server_name example.com;

    root    /usr/share/zabbix;

    index   index.php;
    ```

Replace the first 2 lines with the correct port and domain for your front-end in
case you don't have a domain you can replace `servername` with `_;` like in the
example below:

!!! info "config after the edit"

    ```yaml
    server { # listen 8080; # server*name example.com;
    listen 80;
    server_name *;

             root    /usr/share/zabbix;

             index   index.php;
    ```

The web server and PHP-FPM service are now ready for activation and persistent
startup. Execute the following commands to enable and start them immediately:

!!! info "edit nginx config for ubuntu"

    ```yaml
    sudo vi /etc/zabbix/nginx.conf
    ```

replace the Following lines:

!!! info "original config"

    ```yaml
    server {
    #        listen          8080;
    #        server_name     example.com;
    ```

with :

!!! info "config after edit"

    ```yaml
    server {
    listen xxx.xxx.xxx.xxx:80;
    server_name "";
    ```

where xxx.xxx.xxx.xxx is your IP or DNS name.

???+ nota

    server_name is normally replaced with the fqdn name of your machine. If you
    have no fqdn you can keep it open like in this example.

!!! info "restart the front-end services"

    Red Hat
    ```yaml
    systemctl enable php-fpm --now
    systemctl enable nginx --now
    ```

    Ubuntu
    ```yaml
    sudo systemctl enable nginx php8.3-fpm
    sudo systemctl restart nginx php8.3-fpm
    ```

Let's verify if the service is properly started and enabled so that it survives
our reboot next time.

!!! info "check if the service is running"

    ```yaml
    systemctl status nginx
    ```
    ```
    ● nginx.service - The nginx HTTP and reverse proxy server
          Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: disabled)
         Drop-In: /usr/lib/systemd/system/nginx.service.d
                  └─php-fpm.conf
          Active: active (running) since Mon 2023-11-20 11:42:18 CET; 30min ago
        Main PID: 1206 (nginx)
           Tasks: 2 (limit: 12344)
          Memory: 4.8M
             CPU: 38ms
          CGroup: /system.slice/nginx.service
                  ├─1206 "nginx: master process /usr/sbin/nginx"
                  └─1207 "nginx: worker process"

    Nov 20 11:42:18 zabbix-srv systemd[1]: Starting The nginx HTTP and reverse proxy server...
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    Nov 20 11:42:18 zabbix-srv nginx[1204]: nginx: configuration file /etc/nginx/nginx.conf test is successful
    Nov 20 11:42:18 zabbix-srv systemd[1]: Started The nginx HTTP and reverse proxy server.
    ```

With the service operational and configured for automatic startup, the final
preparatory step involves adjusting the firewall to permit inbound HTTP traffic.
Execute the following commands:

!!! info "configurar o firewall"

    Red Hat

    ```yaml
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```yaml
    sudo ufw allow 80/tcp
    ```

Open your browser and go to the url or ip of your front-end :

!!! info "front-end configuration"

    ```yaml
    http://<ip or dns of the zabbix frontend server>/
    ```

If all goes well you should be greeted with a Zabbix welcome page. In case you
have an error check the configuration again or have a look at the nginx log
file:

!!! informações ""

    ```yaml
     /var/log/nginx/error.log
    ```

or run the following command :

!!! informações ""

    ```yaml
    journalctl -xe
    ```

This should help you in locating the errors you made.

Upon accessing the appropriate URL, a page resembling the one illustrated below
should appear:

![overview](ch01-basic-installation-setup.png){ align=left }

_1.4 Zabbix welcome_

The Zabbix frontend presents a limited array of available localizations, as
shown.

![overview language](ch01-basic-installation-setuplanguage.png){ align=left }

_!.5 Zabbix welcome language choice_

What if we want to install Chinese as language or another language from the
list? Run the next command to get a list of all locales available for your OS.

!!! info "install language packs"

    Red Hat
    ```yaml
    dnf list glibc-langpack-*
    ```

    Ubuntu
    ```yaml
    apt-cache search language-pack
    ```

Users on Ubuntu will probably notice following error `"Locale for language
"en_US" is not found on the web server."``

!!! info "This can be solved easy with the following commands."

    ```
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```

This will give you on Red Hat based systems a list like:

!!! informações ""

    ```yaml
    Installed Packages
    glibc-langpack-en.x86_64
    Available Packages
    glibc-langpack-aa.x86_64
    ---
    glibc-langpack-zu.x86_64
    ```

!!! info "on Ubuntu it will look like :"

    ```yaml
    language-pack-kab - translation updates for language Kabyle
    language-pack-kab-base - translations for language Kabyle
    language-pack-kn - translation updates for language Kannada
    language-pack-kn-base - translations for language Kannada
    ---
    language-pack-ko - translation updates for language Korean
    language-pack-ko-base - translations for language Korean
    language-pack-ku - translation updates for language Kurdish
    language-pack-ku-base - translations for language Kurdish
    language-pack-lt - translation updates for language Lithuanian
    ```

Let's search for our Chinese locale to see if it is available. As you can see
the code starts with zh.

!!! info "search for language pack"

    Red Hat
    ```yaml
    dnf list glibc-langpack-* | grep zh
    ```

    ```
    glibc-langpack-zh.x86_64
    glibc-langpack-lzh.x86_64
    ```

    Ubuntu
    ```
    sudo apt-cache search language-pack | grep -i zh
    ```

The command outputs two lines; however, given the identified language code,
'zh_CN,' only the first package requires installation.

!!! info "install the package"

    Red Hat
    ```yaml
    dnf install glibc-langpack-zh.x86_64
    ```

    Ubuntu
    ```yaml
    sudo apt install language-pack-zh-hans
    sudo systemctl restart nginx php8.3-fpm
    ```

When we return now to our front-end we are able to select the Chinese language,
after a reload of our browser.

![select language](ch01-basic-installation-selectlanguage.png){ align=left }

_1.6 Zabbix select language_

???+ nota

    If your preferred language is not available in the Zabbix front-end, don't
    worry it simply means that the translation is either incomplete or not yet
    available. Zabbix is an open-source project that relies on community contributions
    for translations, so you can help improve it by contributing your own translations.

Visit the translation page at
[https://translate.zabbix.com/](https://translate.zabbix.com/) to assist with
the translation efforts. Once your translation is complete and reviewed, it will
be included in the next minor patch version of Zabbix. Your contributions help
make Zabbix more accessible and improve the overall user experience for
everyone.

When you're satisfied with the available translations, click `Next`. You will
then be taken to a screen to verify that all prerequisites are satisfied. If any
prerequisites are not fulfilled, address those issues first. However, if
everything is in order, you should be able to proceed by clicking `Next`.

![pre-requisites](ch01-basic-installation-prerequisites.png){ align=left }

_1.7 Zabbix pre-requisites_

On the next page, you'll configure the database connection parameters:

1. `Select the Database Type`: Choose either MySQL or PostgreSQL depending on
   your setup.
2. `Enter the Database Host`: Provide the IP address or DNS name of your
   database server. Use port 3306 for MariaDB/MySQL or 5432 for PostgreSQL.
3. `Enter the Database Name`: Specify the name of your database. In our case, it
   is zabbix. If you are using PostgreSQL, you will also need to provide the
   schema name, which is zabbix_server in our case.
4. `Enter the Database User`: Input the database user created for the web
   front-end, remember in our basic installation guide we created 2 users
   zabbix-web and zabbix-srv. One for the frontend and the other one for our
   zabbix server so here we will use the user `zabbix-web`. Enter the
   corresponding password for this user.

Ensure that the `Database TLS encryption` option is not selected, and then click
`Next step` to proceed.

![dbconnection](ch01-basic-installation-dbconnection.png){ align=left }

_1.8 Zabbix connections_

You're almost finished with the setup! The final steps involve:

1. `Assigning an Instance Name`: Choose a descriptive name for your Zabbix
   instance.
2. `Selecting the Timezone`: Choose the timezone that matches your location or
   your preferred time zone for the Zabbix interface.
3. `Setting the Default Time Format`: Select the default time format you prefer
   to use.
4. **Encrypt connections from Web interface**: I marked this box but you should
   not. This box is to encrypt communications between Zabbix frontend and your
   browser. We will cover this later. Once these settings are configured, you
   can complete the setup and proceed with any final configuration steps as
   needed.

???+ nota

    It's a good practice to set your Zabbix server to the UTC timezone, especially
    when managing systems across multiple timezones. Using UTC helps ensure consistency
    in time-sensitive actions and events, as the server’s timezone is often used for
    calculating and displaying time-related information.

![settings](ch01-basic-installation-settings.png){ align=left }

_1.9 Zabbix summary_

After clicking `Next step` again, you'll be taken to a page confirming that the
configuration was successful. Click `Finish` to complete the setup process.

![settings](ch01-basic-installation-final.png){ align=left }

_1.10 Zabbix install_

We are now ready to login :

![settings](ch01-basic-installation-login.png)

_1.11 Zabbix login_

- Login : Admin
- Password : zabbix

This concludes our topic on setting up the Zabbix server. If you're interested
in securing your front-end, I recommend checking out the topic Securing Zabbix
for additional guidance and best practices.

???+ nota

    If you are not able to safe your configuration at the end make sure SeLinux
    is disabled. It is possible that it will block access to certain files or even
    the database.

## Conclusão

With this, we conclude our journey through setting up Zabbix and configuring it
with MySQL or PostgreSQL on RHEL-based systems and Ubuntu. We have walked
through the essential steps of preparing the environment, installing the
necessary components, and ensuring a fully functional Zabbix server. From
database selection to web frontend configuration with Nginx, each decision has
been aimed at creating a robust and efficient monitoring solution.

At this stage, your Zabbix instance is operational, providing the foundation for
advanced monitoring and alerting. In the upcoming chapters, we will delve into
fine-tuning Zabbix, optimizing performance, and exploring key features that
transform it into a powerful observability platform.

Now that your Zabbix environment is up and running, let’s take it to the next
level.

## Perguntas

1. Should I choose MySQL or PostgreSQL as the database back-end? Why?
2. What version of Zabbix should I install for compatibility and stability?
3. What port does my DB use ?
4. What Zabbix logs should I check for troubleshooting common issues?

## URLs úteis

- <https://www.postgresql.org/docs/current/ddl-priv.html>
- <https://www.zabbix.com/download>
- <https://www.zabbix.com/documentation/current/en/manual>
- <https://www.zabbix.com/documentation/current/en/manual/installation/requirements>
- <https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages>
