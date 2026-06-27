---
description: |
    This section from The Zabbix Book titled "Installing a PostgreSQL database"
    guides you through installing PostgreSQL as an alternative database backend
    for Zabbix. It covers installation methods using OS vendor-provided packages
    or official PostgreSQL repositories, with specific commands for Red Hat, SUSE,
    and Ubuntu systems. The section also includes steps to start and secure the
    PostgreSQL server, create the Zabbix database and users, and configure
    firewall rules if necessary.
tags: [beginner]
---

# Instalação de um banco de dados PostgreSQL

Como alternativa ao MariaDB/MySQL, você pode optar por usar o PostgreSQL como
backend de banco de dados para o Zabbix. Assim como o MariaDB, o PostgreSQL pode
ser instalado usando os pacotes fornecidos pelo fornecedor do sistema
operacional ou os repositórios oficiais do PostgreSQL.

Se você já instalou o MariaDB na seção anterior, pode pular esta seção.

Até o momento, o PostgreSQL 13-18 é suportado pelo Zabbix. Verifique a
documentação do Zabbix para obter uma lista atualizada das versões suportadas
para sua versão do Zabbix. Normalmente, é uma boa ideia usar a versão mais
recente que é suportada pelo Zabbix.

Dica "Extensão do TimescaleDB"

    Zabbix also supports the extension TimescaleDB but due to its advanced nature, 
    we won't cover it in this chapter. Refer to [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    for detailed instructions on that topic. 

    Do note that if you want to use TimescaleDB RPM packages provided
    by Timescale, you will need to install PostgreSQL from the official
    PostgreSQL repositories instead of the OS vendor-provided packages.
    If you choose to install PostgreSQL from the OS vendor-provided packages,
    you will need to compile and install the TimescaleDB extension from source.

---

## Instalação do servidor e cliente PostgreSQL a partir de pacotes fornecidos pelo fornecedor do sistema operacional

Para instalar o servidor PostgreSQL padrão da distribuição, execute os seguintes
comandos:

!!! info "Instalar o servidor Postgres"

    Red Hat
    ``` bash
    dnf install postgresql-server postgresql-client	postgresql-contrib
    ```

    SUSE
    ``` bash
    zypper install postgresql-server postgresql postgresql-contrib
    ```

    Ubuntu
    ``` bash
    sudo apt install postgresql postgresql-client postgresql-contrib
    ```

Esse comando fará o download e instalará os pacotes do servidor e do cliente,
permitindo que você defina, configure e interaja com o banco de dados
PostgreSQL.

!!! aviso "A inicialização do banco de dados é necessária no Red Hat"

    Due to policies for Red Hat family distributions, the PostgreSQL service
    does not initialize an empty database required for PostgreSQL to function.
    So for Red Hat we need to initialize an empty database before continuing:

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```

    On SUSE and Ubuntu the OS provided SystemD service will automatically initialize
    an empty database on first startup.

Quando a instalação estiver concluída, prossiga para a seção [_Starting the
PostgreSQL Database_](#starting-the-postgresql-database).

---

## Instalando o PostgreSQL a partir dos repositórios oficiais do PostgreSQL

Se você preferir instalar o PostgreSQL a partir dos repositórios oficiais do
PostgreSQL em vez dos pacotes fornecidos pelo fornecedor do sistema operacional,
a primeira etapa é adicionar o repositório do PostgreSQL ao seu sistema.

---

### Adição do repositório PostgreSQL

Configure o repositório PostgreSQL com os seguintes comandos:

Consulte
[https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/)
para obter mais informações.

!!! info "Adicionar repositório PostgreSQL"

    Red Hat
    ```bash
    # Install the repository RPM:
    dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

    # Disable the built-in PostgreSQL module:
    dnf -qy module disable postgresql
    ```

    SUSE
    ```bash
    # Import the repository signing key:
    rpm --import https://zypp.postgresql.org/keys/PGDG-RPM-GPG-KEY-SLES16

    # Install the repository RPM:
    zypper install https://download.postgresql.org/pub/repos/zypp/reporpms/SLES-16-x86_64/pgdg-suse-repo-latest.noarch.rpm

    # Update the package lists:
    zypper refresh
    ```

    !!! warning "openSUSE Leap"

        Since the official PostgreSQL packages are specifically built for use on 
        SUSE Linux Enterprise Server (SLES), you will get an error trying to install the
        repository on openSUSE Leap. We can however safely ignore this problem by
        choosing to "break the package by ignoring some of its dependencies" as
        long as you match the SLES version with your openSUSE version:

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```

    ???+ note "Suse Linux Enterprise Server"

        On SUSE Linux Enterprise Server (SLES), ensure you are subscribed to the
        "SUSE Package Hub extension" repository to access necessary dependency
        packages required for the Official PostgreSQL installation. On SLES 15
        you will also need the "Desktop Applications Module":

        ```bash
        # On SLES 16
        suseconnect -p PackageHub/16.0/x86_64

        # On SLES 15
        SUSEConnect -p sle-module-desktop-applications/15.7/x86_64
        SUSEConnect -p PackageHub/15.7/x86_64
        ```

    Ubuntu
    ```bash
    # Import the repository signing key:
    sudo apt install curl ca-certificates
    sudo install -d /usr/share/postgresql-common/pgdg
    sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc

    # Create the repository configuration file:
    sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    # Update the package lists:
    sudo apt update
    ```

---

### Instalando o servidor e o cliente PostgreSQL

Com os repositórios do PostgreSQL configurados, agora você está pronto para
instalar o servidor PostgreSQL e os pacotes do cliente. Isso fornecerá os
componentes necessários para executar e gerenciar seu banco de dados.

!!! info "Instale o PostgreSQL a partir dos repositórios oficiais"

    Red Hat
    ```bash
    # Install Postgres server:
    dnf install postgresql17 postgresql17-server postgresql17-contrib
    ```

    SUSE
    ```bash
    zypper install postgresql17 postgresql17-server postgresql17-contrib
    ```

    Ubuntu
    ```bash
    sudo apt install postgresql-17 postgresql-client-17
    ```

Esse comando fará o download e instalará os pacotes do servidor e do cliente,
permitindo que você defina, configure e interaja com o banco de dados
PostgreSQL.

Em seguida, antes de iniciarmos o servidor PostgreSQL, precisamos inicializar um
novo banco de dados vazio:

!!! info "Inicializar banco de dados PostgreSQL vazio"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```

Quando a instalação estiver concluída, prossiga para a seção [Iniciando o banco
de dados PostgreSQL](#starting-the-postgresql-database).

---

## Iniciando o banco de dados PostgreSQL

Agora que o PostgreSQL está instalado, precisamos habilitar o serviço para
iniciar automaticamente na inicialização, bem como iniciá-lo imediatamente. Use
o seguinte comando para fazer isso:

!!! info "Habilitar e iniciar o serviço PostgreSQL"

    for OS-provided packages
    ```bash
    sudo systemctl enable postgresql --now
    ```

    for official PostgreSQL packages:
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```

Esse comando habilitará e iniciará o serviço do PostgreSQL. Com o serviço
instalado e em execução, você pode verificar se a instalação foi bem-sucedida
verificando a versão do PostgreSQL usando o seguinte comando:

!!! info "Verificar versão do PostgreSQL"

    ```bash
    psql -V
    ```

A saída esperada deve ser similar a esta:

???+ exemplo "Exemplo de versão do PostgreSQL"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```

Para garantir que o serviço PostgreSQL esteja sendo executado corretamente, você
pode verificar seu status com o seguinte comando:

!!! info "Obter status do PostgreSQL"

    for OS-provided packages
    ```bash
    sudo systemctl status postgresql
    ```

    for official PostgreSQL packages:
    ```bash
    sudo systemctl status postgresql-17
    ```

Você deverá ver um resultado semelhante a este, indicando que o serviço
PostgreSQL está ativo e em execução:

???+ exemplo "Exemplo de status do serviço PostgreSQL"

    ```shell-session
    localhost:~ $ sudo systemctl status postgresql-17
    ● postgresql-17.service - PostgreSQL 17 database server
        Loaded: loaded (/usr/lib/systemd/system/postgresql-17.service; enabled; preset: disabled)
        Active: active (running) since Mon 2025-12-29 17:24:07 CET; 6s ago
    Invocation: 43ba47dfee5b415db223e3452c3cfacc
        Docs: https://www.postgresql.org/docs/17/static/
        Process: 11131 ExecStartPre=/usr/pgsql-17/bin/postgresql-17-check-db-dir ${PGDATA} (code=exited, status=0/SUCCESS)
    Main PID: 11137 (postgres)
        Tasks: 7 (limit: 4672)
            CPU: 471ms
        CGroup: /system.slice/postgresql-17.service
                ├─11137 /usr/pgsql-17/bin/postgres -D /var/lib/pgsql/17/data/
                ├─11138 "postgres: logger "
                ├─11139 "postgres: checkpointer "
                ├─11140 "postgres: background writer "
                ├─11142 "postgres: walwriter "
                ├─11143 "postgres: autovacuum launcher "
                └─11144 "postgres: logical replication launcher "

    Dec 29 17:24:07 localhost.localdomain systemd[1]: Starting PostgreSQL 17 database server...
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] LOG:  redirecting log output to logging co>
    Dec 29 17:24:07 localhost.localdomain postgres[11137]: 2025-12-29 17:24:07.650 CET [11137] HINT:  Future log output will appear in di>
    Dec 29 17:24:07 localhost.localdomain systemd[1]: Started PostgreSQL 17 database server.
    ```

Isso confirma que seu servidor PostgreSQL está funcionando e pronto para outras
configurações.

---

## Protegendo o banco de dados PostgreSQL

O PostgreSQL lida com as permissões de acesso de forma diferente do MySQL e do
MariaDB. O PostgreSQL se baseia em um arquivo chamado `pg_hba.conf` para
gerenciar quem pode acessar o banco de dados, de onde e qual método de
criptografia é permitido para autenticação.

???+ nota "Sobre o pg_hba.conf"

    Client authentication in PostgreSQL is configured through the `pg_hba.conf`
    file, where "HBA" stands for Host-Based Authentication. This file specifies
    which users can access the database, from which hosts, and how they are authenticated.
    For further details, you can refer to the official PostgreSQL documentation."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Adicione as seguintes linhas, a ordem aqui é importante.

!!! info "Editar o arquivo pg_hba"

    Red Hat / SUSE
    ``` bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/pg_hba.conf

    # for official packages
    vi /var/lib/pgsql/17/data/pg_hba.conf
    ```

    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/pg_hba.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/pg_hba.conf
    ```

!!! aviso "Localização do arquivo pg_hba"

    If you don't find the `pg_hba.conf` and `postgres.conf` files in the above 
    mentioned location you can ask PostgreSQL itself for the location using
    this command (provided that PostgreSQL is currently running):

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```

O arquivo pg_hba resultante deve ser semelhante a :

!!! exemplo "Exemplo de Pg_hba"

    ```
    # "local" is for Unix domain socket connections only
    local    zabbix     zabbix-srv                                 scram-sha-256
    local    all        all                                        peer
    # IPv4 local connections
    host     zabbix         zabbix-srv      <ip from zabbix server/24>     scram-sha-256
    host     zabbix         zabbix-web      <ip from zabbix frontend/24>   scram-sha-256
    host     all            all             127.0.0.1/32                   scram-sha-256
    # IPv6 local connections:
    host    zabbix          zabbix-srv      ::1/128                 scram-sha-256
    host    zabbix          zabbix-web      ::1/128                 scram-sha-256
    host    all             all             ::1/128                 ident
    ```

!!! aviso "Certifique-se de manter a ordem das entradas"

    The order of the entries in the `pg_hba.conf` file is crucial, as PostgreSQL
    processes these rules sequentially. Ensure that the specific rules for the
    `zabbix-srv` and `zabbix-web` users are placed before any broader rules like
    the default `all` user rules that could potentially override them.

Depois de alterarmos o arquivo `pg_hba.conf`, não se esqueça de reiniciar o
Postgres, caso contrário as configurações não serão aplicadas. Mas antes de
reiniciarmos, vamos também editar o arquivo `postgresql.conf` e permitir que
nosso banco de dados escute em nossa interface de rede as conexões de entrada do
servidor Zabbix. Por padrão, o PostgreSQL só permite conexões de um soquete
unix.

!!! info "Editar arquivo postgresql.conf"

    Red Hat / SUSE
    ```bash
    # for OS-provided packages
    vi /var/lib/pgsql/data/postgresql.conf

    # for official packages
    vi /var/lib/pgsql/17/data/postgresql.conf
    ```

    Ubuntu
    ``` bash
    # for OS-provided packages
    sudo vi /etc/postgresql/current/main/postgresql.conf

    # for official packages
    sudo vi /etc/postgresql/17/main/postgresql.conf
    ```

Localize a seguinte linha:

!!! info ""

    ```ini
    #listen_addresses = 'localhost'
    ```

e substituí-la por:

!!! info ""

    ```ini
    listen_addresses = '*'
    ```

???+ nota

    This will enable PostgreSQL to accept connections from any network interface,
    not just the local machine. In production it's probably a good idea to limit
    who can connect to the DB.

Depois de fazer essa alteração, reinicie o serviço PostgreSQL para aplicar as
novas configurações:

!!! info "restart the DB server" (reinicie o servidor de banco de dados)

    for OS-provided packages
    ``` bash
    sudo systemctl restart postgresql
    ```

    for official packages
    ```bash
    sudo systemctl restart postgresql-17
    ```

???+ dica

    If the service fails to restart, review the `pg_hba.conf` file for any syntax errors,
    as incorrect entries here may prevent PostgreSQL from starting.

---

## Criação da instância do banco de dados Zabbix

Com os pacotes necessários instalados, agora você está pronto para criar o banco
de dados e os usuários do Zabbix para o servidor e o frontend.

Os pacotes do PostgreSQL criam automaticamente um usuário Linux padrão
`postgres` durante a instalação, que tem privilégios administrativos na
instância do PostgreSQL. Para administrar o banco de dados, você precisará
executar comandos como o usuário `postgres`.

Primeiro, crie o usuário do banco de dados do servidor Zabbix (também chamado de
"função" no PostgreSQL):

!!! info "criar usuários do servidor"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```

Em seguida, crie o usuário front-end do Zabbix, que será usado para se conectar
ao banco de dados:

!!! info "Criar usuário de front-end"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```

Agora, com os usuários criados, a próxima etapa é criar o banco de dados do
Zabbix. Execute o seguinte comando para criar o banco de dados `zabbix` com o
proprietário definido como `zabbix-srv` e a codificação de caracteres definida
como `Unicode`, conforme exigido pelo Zabbix:

!!! info "Criar banco de dados"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```

???+ nota "O que é esse 'template0'?"

    In PostgreSQL, `template0` is a default database template that serves as a pristine
    copy of the database system. When creating a new database using `template0`,
    it ensures that the new database starts with a clean slate, without any
    pre-existing objects or configurations that might be present in other templates.
    This is particularly useful when you want to create a database with specific
    settings or extensions without inheriting any unwanted elements from other templates.

Depois que o banco de dados for criado, verifique a conexão e certifique-se de
que a sessão correta do usuário esteja ativa. Para fazer isso, faça login no
banco de dados zabbix usando o usuário `zabbix-srv`:

!!! info "Faça login como usuário zabbix-srv"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```

Depois de fazer login, execute a seguinte consulta SQL para confirmar que tanto
o `session_user` quanto o `current_user` estão definidos como `zabbix-srv`:

!!! info ""

    ```psql
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

    PostgreSQL comes with a default schema, typically called `public`, but in
    general, it's a best practice to create custom schemas to better organize and separate
    database objects, especially in complex or multi-user environments.

    For more in-depth information, I recommend checking out the detailed guide at
    this URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    which explains the benefits and use cases for schemas in PostgreSQL.

Para finalizar a configuração inicial do banco de dados do Zabbix, precisamos
configurar as permissões do esquema para os usuários `zabbix-srv` e
`zabbix-web`.

Primeiro, criamos um esquema personalizado chamado `zabbix_server` e atribuímos
a propriedade ao usuário `zabbix-srv`:

!!! info "create the db schema" (criar o esquema do banco de dados)

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```

Em seguida, definimos o `caminho de pesquisa` para `zabbix_server` schema para
que seja o padrão da sessão atual:

!!! info "Definir caminho de pesquisa"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```

???+ dica

    If you prefer not to set the search path manually each time you log in as the
    `zabbix-srv` user, you can configure PostgreSQL to automatically use the desired
    search path. Run the following SQL command to set the default search path for
    the `zabbix-srv` role:

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```

    This command ensures that every time the `zabbix-srv` user connects to the
    database, the `search_path` is automatically set to `zabbix_server`.


Para confirmar a configuração do esquema, você pode listar os esquemas
existentes:

!!! exemplo "Verificar acesso ao esquema"

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
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```

Agora, o usuário `zabbix-web` tem acesso adequado para interagir com o esquema,
mantendo a segurança ao limitar as permissões às operações essenciais.

Se estiver pronto, você poderá sair do banco de dados e retornar ao shell do
Linux.

!!! info "Sair do shell do banco de dados"

    ```psql
    zabbix=> \q
    ```

Neste ponto, seu banco de dados do Zabbix está pronto, mas antes que ele possa
realmente ser usado pelo Zabbix, ainda precisamos preencher o banco de dados com
as tabelas necessárias e os dados iniciais, mas isso será abordado na próxima
seção, quando instalarmos o servidor Zabbix.

Se você pretende instalar o Zabbix Server em uma máquina diferente da que
hospeda o banco de dados, será necessário abrir o firewall do host para permitir
conexões de entrada com o servidor de banco de dados. Por padrão, o PostgreSQL
escuta na porta 5432.

!!! info "Adicionar regras de firewall"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=postgresql --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 5432/tcp
    ```
---

## Preencher o banco de dados do Zabbix

Durante a instalação do software de banco de dados anteriormente, criamos os
usuários, o banco de dados e o esquema necessários para o Zabbix. No entanto, o
Zabbix espera que determinadas tabelas, esquemas, imagens e outros elementos
estejam presentes no banco de dados. Para configurar o banco de dados
corretamente, precisamos preenchê-lo com o esquema necessário.

Primeiro, precisamos instalar os scripts SQL do Zabbix que contêm os scripts de
importação necessários para o banco de dados.

!!! info "Instalar scripts SQL"

    Red Hat
    ``` bash
    dnf install zabbix-sql-scripts
    ```

    SUSE
    ``` bash
    zypper install zabbix-sql-scripts
    ```

    Ubuntu
    ``` bash
    sudo apt install zabbix-sql-scripts
    ```

Em seguida, você precisa preparar o esquema do banco de dados: descompacte os
arquivos de esquema necessários executando o seguinte comando:

!!! info "Descompacte o patch do DB"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```

???+ nota

    Zabbix seems to like to change the locations of the script to populate the
    DB every version or even in between versions. If you encounter an error take a
    look at the Zabbix documentation, there is a good chance that some location was
    changed.

Isso extrairá o esquema do banco de dados necessário para o servidor Zabbix.

Agora, executaremos o arquivo SQL para preencher o banco de dados. Abra um shell
`psql`:

!!! info "Abrir o shell psql"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```

???+ aviso "Certifique-se de que o search_path correto esteja definido"

    Make sure you performed previous steps as outlined in [Creating the Zabbix database instance with PostgreSQL](postgresql.md#creating-the-zabbix-database-instance)
    carefully so that you have set the correct `search_path`.

    If you did not set the default `search_path` for the `zabbix-srv` user,
    ensure you set it manually in the current session before proceeding:
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```

Faça o upload do esquema do banco de dados para o banco de dados usando os
seguintes comandos:

!!! info "carregar o esquema do banco de dados para o banco de dados zabbix"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```

???+ aviso

    Depending on your hardware or VM performance, this process can take anywhere
    from a few seconds to several minutes. Please be patient and avoid cancelling
    the operation.

Monitore o progresso à medida que o script é executado. Você verá uma saída
semelhante a:

!!! exemplo "Exemplo de saída"

    ```psql
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

!!! info "Conceder direitos sobre o esquema ao usuário zabbix-web"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```

Verifique se os direitos estão corretos no esquema:

!!! exemplo "Exemplo de direitos de esquema"

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
        schema has been selected to create in` It indicates that the `search_path` setting
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

    ```psql
    zabbix=# \dt
    ```

Você verá uma lista de tabelas com seu esquema, nome, tipo e proprietário. Por
exemplo:

???+ exemplo "Tabela de listas com relações"

    ```psql
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

!!! info "Verificar permissões de tabela"

    ```psql
    zabbix=> \dp zabbix_server.*
    ```

???+ example "Exemplo de saída"

    ```psql
    zabbix=> \dp zabbix_server.*
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

Isso conclui nossa instalação do banco de dados PostgreSQL.

---

## Conclusão

Com a instalação e a configuração do PostgreSQL como backend do banco de dados
para o Zabbix concluídas, agora você tem um sistema de banco de dados poderoso e
eficiente pronto para suas necessidades de monitoramento. Cobrimos a instalação
do PostgreSQL a partir dos pacotes fornecidos pelo fornecedor e dos repositórios
oficiais, protegendo o banco de dados, criando o banco de dados e os usuários
necessários do Zabbix e preenchendo o banco de dados com o esquema necessário e
os dados iniciais.

Seu ambiente Zabbix agora está pronto para os próximos estágios de instalação e
configuração.

---

## Perguntas

1. Qual versão do PostgreSQL devo instalar para garantir a compatibilidade e a
   estabilidade?
2. Qual é a porta usada pelo meu banco de dados?
3. Quais usuários do banco de dados eu criei e por quê?

---

## URLs úteis

- [https://yum.postgresql.org](ttps://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)
