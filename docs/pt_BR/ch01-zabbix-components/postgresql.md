---
description: |
    Esta seção do livro The Zabbix Book intitulada "Instalando um banco de dados PostgreSQL"
    guia você através da instalação do PostgreSQL como uma alternativa ao backend de banco de dados
    para o Zabbix. Ela abrange métodos de instalação usando pacotes fornecidos pelo distribuidor
    operacional ou repositórios oficiais do PostgreSQL, com comandos específicos para sistemas Red Hat,
    SUSE e Ubuntu. A seção também inclui etapas para iniciar e proteger o servidor PostgreSQL,
    criar o banco de dados Zabbix e usuários, e configurar as regras de firewall se necessário.
tags: [beginner]
---

# Instalando um banco de dados PostgreSQL

Além do MariaDB/MySQL, você pode optar por usar o PostgreSQL como backend de banco de dados para o Zabbix.
Assim como no caso do MariaDB, o PostgreSQL pode ser instalado usando pacotes fornecidos pelo distribuidor
operacional ou repositórios oficiais do PostgreSQL.

Se você já tiver instalado o MariaDB na seção anterior, pode pular esta seção.

Até a data de escrita, as versões 13-18 do PostgreSQL são suportadas pelo Zabbix. Consulte a documentação
do Zabbix para obter uma lista atualizada das versões suportadas para sua versão do Zabbix. Geralmente é
uma boa ideia usar a última versão que seja compatível com o Zabbix.

???+ tip "Extensão TimescaleDB"

    O Zabbix também suporta a extensão TimescaleDB, mas devido à sua natureza avançada,
    não abordaremos isso neste capítulo. Consulte [_Partitioning PostgreSQL with TimescaleDB_](../ch13-advanced-security/partitioning-postgresql-database.md)
    para instruções detalhadas sobre esse tópico.

    Observe que, se você deseja usar os pacotes RPM da TimescaleDB fornecidos
    pela Timescale, será necessário instalar o PostgreSQL a partir dos repositórios oficiais
    do PostgreSQL em vez dos pacotes fornecidos pelo distribuidor operacional. Se optar por
    instalar o PostgreSQL a partir dos pacotes fornecidos pelo distribuidor operacional,
    você precisará compilar e instalar a extensão TimescaleDB a partir da fonte.

    Nota extra: A TimescaleDB não fornece pacotes para SUSE Linux Enterprise
    Server (SLES) ou openSUSE Leap. Em vez disso, o Suse fornece a extensão TimescaleDB
    em seus próprios repositórios. Mas para que isso funcione, você precisará instalar
    o PostgreSQL a partir dos pacotes fornecidos pelo distribuidor operacional em vez dos repositórios oficiais
    do PostgreSQL.

---

## Instalando o servidor e cliente PostgreSQL a partir de pacotes fornecidos pelo distribuidor

Para instalar o servidor padrão do PostgreSQL da distribuição, execute os seguintes
comandos:

!!! info "Instale o servidor Postgres"

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


Este comando baixará e instalará tanto os pacotes do servidor quanto do cliente, permitindo-lhe configurar,
configurar e interagir com seu banco de dados PostgreSQL.

!!! warning "Inicialização do banco de dados é necessária no Red Hat"

    Devido às políticas para distribuições da família Red Hat, o serviço PostgreSQL
    não inicializa um banco de dados vazio necessário para que o PostgreSQL funcione.
    Portanto, precisamos inicializar um banco de dados vazio antes de continuar:

    Red Hat
    ```bash
    postgresql-setup --initdb --unit postgresql
    ```


    Em SUSE e Ubuntu, o serviço Systemd fornecido pelo sistema operacional inicia automaticamente
    um banco de dados vazio na primeira inicialização.

Uma vez que a instalação é concluída, você pode prosseguir para a seção [_Iniciando o banco de dados PostgreSQL_](#iniciando-o-banco-de-dados-postgresql).

---

## Instalando o PostgreSQL dos repositórios oficiais do PostgreSQL

Se preferir instalar o PostgreSQL a partir dos repositórios oficiais do PostgreSQL em vez
dos pacotes fornecidos pelo distribuidor operacional, a primeira etapa é adicionar o repositório
PostgreSQL ao seu sistema.

---

### Adicionando o repositório PostgreSQL

Configure o repositório PostgreSQL com os seguintes comandos:

Consulte [https://www.postgresql.org/download/linux/](https://www.postgresql.org/download/linux/)
para mais informações.

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

        Como os pacotes oficiais do PostgreSQL são especificamente construídos para uso em
        SUSE Linux Enterprise Server (SLES), você receberá um erro ao tentar instalar o
        repositório no openSUSE Leap. No entanto, podemos ignorar esse problema de forma segura escolhendo "quebrar o pacote ignorando algumas de suas dependências" desde que a versão do SLES corresponda à sua versão do openSUSE:

        ```
        Problem: 1: nothing provides 'sles-release' needed by the to be installed pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 1: do not install pgdg-suse-repo-42.0-48PGDG.noarch
         Solution 2: break pgdg-suse-repo-42.0-48PGDG.noarch by ignoring some of its dependencies

        Choose from above solutions by number or cancel [1/2/c/d/?] (c): 2
        ```


    ???+ note "Suse Linux Enterprise Server"

        No SUSE Linux Enterprise Server (SLES), certifique-se de estar inscrito no repositório
        "SUSE Package Hub extension" para acessar os pacotes necessários como dependências do
        Instalação oficial do PostgreSQL. No SLES 15, você também precisará do módulo "Desktop Applications":

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

### Instalando o servidor e cliente PostgreSQL

Com os repositórios PostgreSQL configurados, está pronto para instalar os pacotes do servidor
e cliente PostgreSQL. Isso fornecerá os componentes necessários para executar e gerenciar seu banco de dados.

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


Este comando baixará e instalará tanto os pacotes do servidor quanto do cliente, permitindo-lhe configurar,
configurar e interagir com seu banco de dados PostgreSQL.

Em seguida, antes de podermos iniciar o servidor PostgreSQL precisamos inicializar um novo
banco de dados vazio:

!!! info "Inicialize um banco de dados PostgreSQL vazio"

    ```
    sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
    ```


Uma vez que a instalação é concluída, você pode prosseguir para a seção [Iniciando o banco de dados PostgreSQL](#iniciando-o-banco-de-dados-postgresql).

---

## Iniciando o banco de dados PostgreSQL

Agora que o PostgreSQL está instalado, precisamos habilitar o serviço para iniciar automaticamente
ao ligar e iniciá-lo imediatamente. Use o seguinte comando para realizar isso:

!!! info "Habilitar e iniciar o serviço PostgreSQL"

    para pacotes fornecidos pelo distribuidor operacional
    ```bash
    sudo systemctl enable postgresql --now
    ```


    para pacotes oficiais do PostgreSQL:
    ```bash
    sudo systemctl enable postgresql-17 --now
    ```


Este comando habilitará e iniciará o serviço PostgreSQL.
Com o serviço agora em execução, você pode verificar que a instalação
foi bem-sucedida verificando a versão do PostgreSQL usando o seguinte comando:

!!! info "Verificar a versão do PostgreSQL"

    ```bash
    psql -V
    ```


A saída esperada deve ser semelhante a esta:

???+ example "Exemplo de versão PostgreSQL"

    ```shell-session
    localhost:~ $ psql -V
    psql (PostgreSQL) 17.7
    ```


Para garantir que o serviço PostgreSQL está funcionando corretamente, você pode verificar seu status
com o seguinte comando:

!!! info "Obter status do PostgreSQL"

    para pacotes fornecidos pelo distribuidor operacional
    ```bash
    sudo systemctl status postgresql
    ```


    para pacotes oficiais do PostgreSQL:
    ```bash
    sudo systemctl status postgresql-17
    ```


Você deve ver uma saída semelhante a esta, indicando que o serviço PostgreSQL está ativo e em execução:

???+ example "Exemplo de status do serviço PostgreSQL"

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


Isso confirma que seu servidor PostgreSQL está funcionando e pronto para configurações adicionais.

---

## Protegendo o banco de dados PostgreSQL

O PostgreSQL lida com permissões de acesso de forma diferente em relação ao MySQL e MariaDB.
O PostgreSQL depende de um arquivo chamado `pg_hba.conf` para gerenciar quem pode acessar o banco de dados,
de onde, e qual método de criptografia é permitido para autenticação.

???+ note "Sobre pg_hba.conf"

    A autenticação do cliente no PostgreSQL é configurada através do arquivo `pg_hba.conf`,
    onde "HBA" significa Autenticação Baseada em Host. Este arquivo especifica
    quais usuários podem acessar o banco de dados, de quais hosts e como eles são autenticados.
    Para mais detalhes, você pode consultar a documentação oficial do PostgreSQL."
    [https://www.postgresql.org/docs/current/auth-pg-hba-conf.html](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

Adicione as seguintes linhas, a ordem aqui é importante.

!!! info "Edite o arquivo pg_hba"

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


!!! warning "Localização do arquivo pg_hba"

    Se você não encontrar os arquivos `pg_hba.conf` e `postgres.conf` na localização mencionada acima,
    pode pedir ao PostgreSQL em si pela localização usando
    o seguinte comando (desde que o PostgreSQL esteja atualmente rodando):

    ```bash
    sudo -u postgres psql -t -c 'show hba_file';
    ```


O arquivo pg_hba resultante deve parecer com:

!!! example "Exemplo de pg_hba"

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


!!! warning "Certifique-se de manter a ordem das entradas"

    A ordem das entradas no `pg_hba.conf` é crucial, pois o PostgreSQL
    processa essas regras sequencialmente. Certifique-se de que as regras específicas para os
    usuários `zabbix-srv` e `zabbix-web` estejam antes de quaisquer regras mais amplas como
    a regra padrão do usuário `all` que poderiam potencialmente anulá-las.

Após alterar o arquivo `pg_hba.conf`, não se esqueça de reiniciar o PostgreSQL para aplicar as novas configurações.
Mas antes de reiniciar, também edite o arquivo `postgresql.conf`
e permita que nosso banco de dados escute em nossa interface de rede para conexões entrantes
do servidor Zabbix. O PostgreSQL por padrão só permite conexões a partir de um socket unix.

!!! info "Edite o arquivo postgresql.conf"

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


e substitua-a por:

!!! info ""

    ```ini
    listen_addresses = '*'
    ```


???+ note

    Isso permitirá que o PostgreSQL aceite conexões de qualquer interface de rede,
    não apenas do próprio computador. Em produção, é provavelmente uma boa ideia limitar
    quem pode se conectar ao banco de dados.

Após fazer essa alteração, reinicie o serviço PostgreSQL para aplicar as novas configurações:

!!! info "Reiniciar o servidor DB"

    para pacotes fornecidos pelo distribuidor operacional
    ``` bash
    sudo systemctl restart postgresql
    ```


    para pacotes oficiais
    ```bash
    sudo systemctl restart postgresql-17
    ```


???+ tip

    Se o serviço não conseguir reiniciar, revise o arquivo `pg_hba.conf` para erros de sintaxe,
    pois entradas incorretas aqui podem impedir que o PostgreSQL inicie.

---

## Criando a instância do banco de dados Zabbix

Com os pacotes necessários instalados, você está pronto para criar o banco de dados
do Zabbix e usuários tanto para o servidor quanto para o frontend.The PostgreSQL packages automaticamente criam um usuário padrão `postgres` durante a instalação, que possui privilégios administrativos na instância do PostgreSQL. Para administrar o banco de dados, você precisará executar comandos como o usuário `postgres`.

Primeiro, crie o usuário do servidor Zabbix (também conhecido como "role" no PostgreSQL):

!!! info "Criar usuários do servidor"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-srv
    Enter password for new role: <server-password>
    Enter it again: <server-password>
    ```


Em seguida, crie o usuário da interface frontal, que será usado para se conectar ao banco de dados:

!!! info "Criar usuário da frente"

    ```bash
    sudo -u postgres createuser --pwprompt zabbix-web
    Enter password for new role: <frontend-password>
    Enter it again: <frontend-password>
    ```


Agora com os usuários criados, a próxima etapa é criar o banco de dados do Zabbix. Execute o seguinte comando para criar o banco de dados `zabbix` com o proprietário definido como
`zabbix-srv` e a codificação de caracteres configurada para `Unicode` conforme exigido pelo Zabbix:

!!! info "Criar DB"

    ``` bash
    sudo -u postgres createdb -E Unicode -T template0 -O zabbix-srv zabbix
    ```


???+ note "O que é esse 'template0'?"

    No PostgreSQL, `template0` é um modelo de banco de dados padrão que serve como uma cópia limpa do sistema de banco de dados. Ao criar um novo banco de dados usando `template0`,
    garante que o novo banco de dados comece com um estado limpo, sem nenhum
    objeto ou configurações pré-existentes presentes em outros modelos.
    Isso é particularmente útil quando você deseja criar um banco de dados com configurações específicas ou extensões sem herdar elementos indesejados de outros modelos.

Uma vez que o banco de dados foi criado, você deve verificar a conexão e garantir que
a sessão do usuário correta esteja ativa. Para fazer isso, conecte-se ao banco de dados zabbix usando
o usuário `zabbix-srv`:

!!! info "Conectar como usuário zabbix-srv"

    ```bash
    psql -d zabbix -U zabbix-srv
    ```


Depois de se conectar, execute a seguinte consulta SQL para confirmar que tanto o `session_user`
quanto o `current_user` estão configurados como `zabbix-srv`:

!!! info ""

    ```psql
    zabbix=> SELECT session_user, current_user;
     session_user | current_user
    --------------+--------------
     zabbix-srv   | zabbix-srv
    (1 row)
    ```


Se a saída corresponder, você está conectado ao banco de dados com o usuário correto.

O PostgreSQL difere significativamente do MySQL ou MariaDB em vários aspectos,
e uma das principais características que o destaca é seu uso de esquemas. Diferentemente do MySQL,
onde os bancos de dados são mais autônomos, o sistema de esquema do PostgreSQL fornece um ambiente estruturado e multiusuário dentro de um único banco de dados.

Os esquemas atuam como contêineres lógicos dentro de um banco de dados, permitindo que múltiplos usuários ou
aplicações acessem e gerenciem dados independentemente sem conflitos. Esta característica é especialmente valiosa em ambientes onde vários usuários ou aplicações precisam interagir com o mesmo servidor de banco de dados simultaneamente. Cada usuário ou aplicação pode ter seu próprio esquema, prevenindo interferências acidentais entre os dados de outros.

???+ note

    O PostgreSQL vem com um esquema padrão, geralmente chamado `public`, mas em
    geral, é uma boa prática criar esquemas personalizados para organizar e separar
    objetos do banco de dados, especialmente em ambientes complexos ou multiusuários.

    Para mais informações detalhadas, recomendo verificar o guia completo neste URI, [https://hevodata.com/learn/postgresql-schema/#schema](https://hevodata.com/learn/postgresql-schema/#schema)
    que explica os benefícios e casos de uso para esquemas no PostgreSQL.

Para finalizar a configuração inicial do banco de dados para o Zabbix, precisamos configurar permissões de esquema
para ambos os usuários `zabbix-srv` e `zabbix-web`.

Primeiro, criaremos um esquema personalizado chamado `zabbix_server` e atribuiremos a propriedade ao
usuário `zabbix-srv`:

!!! info "Criar o esquema do banco de dados"

    ```psql
    zabbix=> CREATE SCHEMA zabbix_server AUTHORIZATION "zabbix-srv";
    ```


Em seguida, definimos o `search path` como `zabbix_server` para que ele seja padrão
para a sessão atual:

!!! info "Definir caminho de pesquisa"

    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


???+ tip

    Se você preferir não definir o caminho de pesquisa manualmente cada vez que se conectar como o
    usuário `zabbix-srv`, pode configurar o PostgreSQL para usar automaticamente o caminho desejado.
    Execute a seguinte consulta SQL para definir o caminho padrão de pesquisa para
    o papel `zabbix-srv`:

    ```sql
    zabbix=> ALTER ROLE "zabbix-srv" SET search_path = zabbix_server;
    ```


    Esta consulta garante que toda vez que o usuário `zabbix-srv` se conectar ao banco de dados,
    o `search_path` será automaticamente definido como `zabbix_server`.

Para confirmar a configuração do esquema, você pode listar os esquemas existentes:

!!! example "Verificar acesso ao esquema"

    ```psql
    zabbix=> \dn
              List of schemas
         Name      |       Owner
    ---------------+-------------------
     public        | pg_database_owner
     zabbix_server | zabbix-srv
    (2 rows)
    ```


Neste ponto, o usuário `zabbix-srv` tem acesso completo ao esquema, mas o usuário `zabbix-web`
ainda precisa de permissões apropriadas para se conectar e interagir com o banco de dados.
Primeiro, concedemos privilégios `USAGE` no esquema para permitir que o usuário `zabbix-web` conecte:

!!! info "Conceder acesso ao esquema para o usuário zabbix-web"

    ```psql
    zabbix=> GRANT USAGE ON SCHEMA zabbix_server TO "zabbix-web";
    ```


Agora, o usuário `zabbix-web` tem acesso apropriado para interagir com o esquema
enquanto mantém a segurança limitando as permissões às operações essenciais.

Se você estiver pronto, pode sair do banco de dados e retornar ao shell linux.

!!! info "Sair da interface do banco de dados"

    ```psql
    zabbix=> \q
    ```


Neste ponto, o banco de dados Zabbix está pronto, mas antes que ele possa ser usado pelo
Zabbix, ainda precisamos preencher o banco de dados com as tabelas e os dados iniciais necessários,
mas isso será abordado na próxima seção quando instalarmos o servidor do Zabbix.

Se você pretende instalar o servidor do Zabbix em uma máquina diferente da que hospeda
o banco de dados, precisará abrir a firewall do host para permitir conexões entrantes ao servidor de banco de dados. Por padrão, o PostgreSQL escuta na porta 5432.

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

Durante a instalação do software do banco de dados anteriormente, criamos os
usuários necessários, banco de dados e esquema para o Zabbix, no entanto, o Zabbix espera que certas tabelas,
esquemas, imagens e outros elementos estejam presentes no banco de dados.
Para configurar corretamente o banco de dados, precisamos preenchê-lo com o esquema necessário.

Primeiro precisamos instalar os scripts SQL do Zabbix que contêm os scripts de importação necessários para o banco de dados.

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


Em seguida, você precisa preparar o esquema do banco de dados: descompacte os arquivos de esquema necessários
executando o seguinte comando:

!!! info "Descompactar o patch DB"

    Red Hat / SUSE
    ``` bash
    gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


    Ubuntu
    ``` bash
    sudo gzip -d /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz
    ```


???+ note

    O Zabbix parece gostar de mudar as localizações dos scripts para preencher o
    DB em cada versão ou até mesmo entre versões. Se você encontrar um erro, verifique a
    documentação do Zabbix, há uma boa chance de que algumas localizações foram
    alteradas.

Isso extrairá o esquema do banco de dados necessário para o servidor do Zabbix.

Agora executaremos o arquivo SQL para preencher o banco de dados. Abra um `psql` shell:

!!! info "Abrir psql shell"

    ``` bash
    psql -d zabbix -U zabbix-srv
    ```


???+ warning "Certifique-se de que a search_path correta está configurada"

    Certifique-se de ter seguido os passos anteriores conforme descrito em [Criando o banco de dados do Zabbix com PostgreSQL](postgresql.md#criando-a-instância-do-banco-de-dados-zabbix)
    cuidadosamente para garantir que você tenha definido a `search_path` correta.

    Se você não definiu a `search_path` padrão para o usuário `zabbix-srv`,
    certifique-se de configurá-la manualmente na sessão atual antes de continuar:
    ```psql
    zabbix=> SET search_path TO "zabbix_server";
    ```


Carregue o esquema do banco de dados no banco de dados usando os seguintes comandos:

!!! info "Carregar o esquema do banco de dados para db zabbix"

    ```psql
    zabbix=> \i /usr/share/zabbix/sql-scripts/postgresql/server.sql
    ```


???+ warning

    Dependendo das especificações da sua máquina ou VM, este processo pode levar de alguns
    segundos a vários minutos. Por favor seja paciente e evite cancelar a operação.

Monitore o progresso conforme o script é executado. Você verá uma saída semelhante à:

!!! example "Exemplo de saída"

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


Uma vez que o script termine e você retorne ao prompt `zabbix=>`, o banco de dados
deverá ser preenchido com todas as tabelas, esquemas,
imagens e outros elementos necessários para o Zabbix.

No entanto, `zabbix-web` ainda não pode realizar operações nas tabelas ou sequências.
Para permitir interação básica de dados sem conceder muitos privilégios, conceda os seguintes direitos:

- Para as tabelas: SELECT, INSERT, UPDATE e DELETE.
- Para as sequências: SELECT e UPDATE.

!!! info "Conceder permissões no esquema para o usuário zabbix-web"

    ```psql
    zabbix=> GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA zabbix_server
    TO "zabbix-web";
    zabbix=> GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA zabbix_server TO "zabbix-web";
    ```


Verifique se os direitos estão corretos no esquema :

!!! example "Exemplo de direitos do esquema"

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


???+ note

    Se você encontrar o seguinte erro durante a importação SQL:
    `vbnet psql:/usr/share/zabbix/sql-scripts/postgresql/server.sql:7: ERROR: no
        schema has been selected to create in` It indicates that the `search_path` configuração
    pode não ter sido aplicada corretamente. Esta configuração é crucial porque especifica
    o esquema onde as tabelas e outros objetos devem ser criados. Ao configurar corretamente a search path,
    você garante que o script SQL criará tabelas e outros objetos no esquema pretendido.

Para garantir que as tabelas do Zabbix foram criadas com sucesso e têm os privilégios
corretos, você pode verificar a lista de tabelas e sua propriedade usando o `psql` comando:

- Listar Tabelas: Use o seguinte comando para listar todas as tabelas no esquema `zabbix_server`:

!!! info "Listar tabelas"

    ```psql
    zabbix=# \dt
    ```


Você deve ver uma lista de tabelas com seu esquema, nome, tipo e proprietário.
Por exemplo:

???+ example "Listar tabela com relações"

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


- Verificar Permissões: Confirme que o usuário zabbix-srv é proprietário das tabelas e tem
  as permissões necessárias. Você pode verificar permissões para tabelas específicas usando
  o comando \dp:

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


Isso exibirá as permissões de acesso para todas as tabelas no esquema `zabbix_server`.
Certifique-se de que o usuário `zabbix-srv` tenha os privilégios necessários.Se tudo parece correto, suas tabelas foram criadas corretamente e o usuário `zabbix-srv` tem as permissões apropriadas. Se você precisar ajustar alguma permissão, pode fazer isso usando os comandos GRANT conforme necessário.

Isso conclui nossa instalação do banco de dados PostgreSQL.

---

## Conclusão

Com a instalação e configuração do PostgreSQL como o backend de banco de dados para
o Zabbix completa, você agora tem um sistema de banco de dados poderoso e eficiente
pronto para atender às suas necessidades de monitoramento. Cobrimos a instalação do
PostgreSQL tanto a partir de pacotes fornecidos pelo provedor quanto de repositórios oficiais,
segurança do banco de dados, criação dos bancos de dados e usuários necessários para o Zabbix,
e preenchimento do banco de dados com o esquema e os dados iniciais exigidos.

Seu ambiente Zabbix está agora pronto para as próximas etapas de configuração.

---

## Perguntas

1. Qual versão do PostgreSQL eu devo instalar para compatibilidade e estabilidade?
2. Em qual porta meu banco de dados utiliza?
3. Quais usuários de banco de dados criei e por quê?

---

## URLs Úteis

- [https://yum.postgresql.org](https://yum.postgresql.org)
- [https://zypp.postgresql.org/howtozypp/](https://zypp.postgresql.org/howtozypp/)
- [https://wiki.postgresql.org/wiki/Apt](https://wiki.postgresql.org/wiki/Apt)
- [https://en.opensuse.org/SDB:PostgreSQL](https://en.opensuse.org/SDB:PostgreSQL)
- [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)
- [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)
