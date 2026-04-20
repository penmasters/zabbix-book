---
description: |
    This section from The Zabbix Book titled "Installing a MariaDB Database"
    guides you through installing MariaDB as the database backend for Zabbix.
    It covers two installation methods: using OS vendor-provided packages or the
    official MariaDB repositories. The section includes steps to start and 
    secure the MariaDB server, create a Zabbix database with appropriate users,
    and configure firewall rules if necessary. 
tags: [beginner]
---

# Instalação de um banco de dados MariaDB

Nesta seção, instalaremos os pacotes MariaDB server e -client. Isso fornecerá os
componentes necessários para executar e gerenciar o MariaDB como backend do
banco de dados do Zabbix.

Se preferir usar o PostgreSQL como backend do banco de dados, pule esta seção e
vá para a seção [_Installing the PostgreSQL Database_](postgresql.md).

Dica "MySQL/Percona" Se você preferir usar o MySQL ou o Percona em vez do
MariaDB, as etapas de instalação e configuração são muito semelhantes. Em geral,
você substituiria `mariadb` por `mysql` nos nomes e comandos dos pacotes.

## Instalação do servidor e cliente MariaDB a partir de pacotes fornecidos pelo fornecedor do sistema operacional

Para instalar o servidor e o cliente MariaDB padrão da distribuição, execute o
seguinte comando:

!!! info "Instalar a versão de distribuição do Mariadb"

    Red Hat
    ```bash
    dnf install mariadb-server
    ```

    SUSE
    ``` bash
    zypper install mariadb mariadb-client
    ```

    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```

Esse comando fará o download e instalará os pacotes do servidor e do cliente,
permitindo que você defina, configure e interaja com o banco de dados MariaDB.
Quando a instalação estiver concluída, você poderá prosseguir para a seção
[_Starting the MariaDB database_](#starting-the-mariadb-database).

---

## Instalando o servidor e o cliente MariaDB a partir dos repositórios oficiais do MariaDB

Se você preferir instalar o MariaDB a partir dos repositórios oficiais do
MariaDB em vez dos pacotes fornecidos pelo fornecedor do sistema operacional, a
primeira etapa é adicionar o repositório do MariaDB ao seu sistema.

---

### Adicionando o repositório MariaDB
Para criar o arquivo de repositório do MariaDB, execute o seguinte comando em
seu terminal:

!!! info "Definir o repositório do MariaDB"

    Red Hat
    ``` bash
    vi /etc/yum.repos.d/mariadb.repo
    ```

    SUSE
    ``` bash
    sudo vi /etc/zypp/repos.d/mariadb.repo
    ```

    Ubuntu
    ``` bash
    sudo apt install apt-transport-https curl
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp'

    sudo vi /etc/apt/sources.list.d/mariadb.sources
    ```

Isso abrirá um editor de texto no qual você poderá inserir os detalhes de
configuração do repositório. Depois que o repositório estiver configurado, você
poderá prosseguir com a instalação do MariaDB usando o gerenciador de pacotes.

A configuração mais recente pode ser encontrada aqui:
[https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Aqui está um exemplo de configuração para repositórios do MariaDB 11.4:

!!! exemplo "Configuração do repositório Mariadb"

    Red Hat
    ```ini
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

    SUSE
    ```ini
    # MariaDB 11.4 openSUSE repository list - created 2025-12-29 14:34 UTC
    # https://mariadb.org/download/
    [mariadb]
    name = MariaDB
    # rpm.mariadb.org is a dynamic mirror if your preferred mirror goes offline. See https://mariadb.org/mirrorbits/ for details.
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    # baseurl = https://rpm.mariadb.org/11.4/opensuse/$releasever/$basearch
    baseurl = https://mirror.bouwhuis.network/mariadb/yum/11.4/opensuse/$releasever/$basearch
    # gpgkey = https://rpm.mariadb.org/RPM-GPG-KEY-MariaDB
    gpgkey = https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    gpgcheck = 1
    ```

    Ubuntu
    ```  yaml
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

Depois de salvar o arquivo, verifique se tudo está configurado corretamente e se
a versão do MariaDB de sua preferência é compatível com a versão do Zabbix para
evitar possíveis problemas de integração.

---

### Instalação do servidor e do cliente MariaDB

Com o repositório do MariaDB configurado, você está pronto para instalar o
servidor MariaDB e os pacotes do cliente. Isso fornecerá os componentes
necessários para executar e gerenciar seu banco de dados.

Para instalar o servidor e o cliente MariaDB, execute o seguinte comando:

!!! info "Instale o MariaDB a partir do repositório oficial"

    Red Hat
    ```bash
    dnf install MariaDB-server
    ```

    SUSE
    ```bash
    sudo rpm --import https://mirror.bouwhuis.network/mariadb/yum/RPM-GPG-KEY-MariaDB
    sudo zypper install MariaDB-server MariaDB-client
    ```


    Ubuntu
    ```bash
    sudo apt install mariadb-server
    ```

Esse comando fará o download e instalará os pacotes do servidor e do cliente,
permitindo que você defina, configure e interaja com o banco de dados MariaDB.
Quando a instalação estiver concluída, você poderá prosseguir para a seção
[_Starting the MariaDB database_](#starting-the-mariadb-database).

---

## Iniciando o banco de dados MariaDB

Agora que o MariaDB está instalado, precisamos habilitar o serviço para iniciar
automaticamente na inicialização do sistema operacional, assim como iniciá-lo
imediatamente. Utilize o seguinte comando para realizar isso:

!!! info "Habilitar o serviço MariaDB"

    ```bash
    sudo systemctl enable mariadb --now
    ```

Esse comando habilitará e iniciará o serviço MariaDB e, como essa será a
primeira vez que o serviço é iniciado, ele inicializará o diretório do banco de
dados. Com o serviço MariaDB instalado e em execução, você pode verificar se a
instalação foi bem-sucedida verificando a versão do MariaDB usando o seguinte
comando:

!!! info "Verificar versão do Mariadb"

    ```bash
    mariadb -V
    ```

A saída esperada deve ser similar a esta:

???+ exemplo "Exemplo de versão do MariaDB"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb  Ver 15.1 Distrib 10.11.14-MariaDB, for Linux (x86_64) using  EditLine wrapper
    ```

Para garantir que o serviço do MariaDB esteja sendo funcionando corretamente,
você pode verificar o status com o seguinte comando:

!!! info "Obter status do mariadb"

    ```bash
    sudo systemctl status mariadb
    ```

Você deverá ver um resultado semelhante a este, indicando que o serviço MariaDB
está ativo e em execução:

???+ exemplo "Exemplo de status do serviço Mariadb"

    ```shell-session
    localhost:~ $ sudo systemctl status mariadb
    ● mariadb.service - MariaDB database server
         Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: disabled)
         Active: active (running) since Wed 2025-12-03 00:16:04 CET; 5s ago
           Docs: man:mysqld(8)
                 https://mariadb.com/kb/en/library/systemd/
        Process: 11148 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper install (code=exited, status=0/SUCCESS)
        Process: 11155 ExecStartPre=/usr/lib/mysql/mysql-systemd-helper upgrade (code=exited, status=0/SUCCESS)
       Main PID: 11162 (mysqld)
         Status: "Taking your SQL requests now..."
          Tasks: 18 (limit: 4670)
            CPU: 340ms
         CGroup: /system.slice/mariadb.service
                 └─11162 /usr/sbin/mysqld --defaults-file=/etc/my.cnf --user=mysql --socket=/run/mysql/mysql.sock

    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Plugin 'FEEDBACK' is disabled.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Loading buffer pool(s) from /var/lib/mysql/ib_buffer_pool
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] Server socket created on IP: '127.0.0.1', port: '3306'.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] /usr/sbin/mysqld: ready for connections.
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Version: '10.11.14-MariaDB'  socket: '/run/mysql/mysql.sock'  port: 3306  MariaDB package
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Buffer pool(s) load completed at 251203  0:16:04
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Started MariaDB database server.
    ```

Isso confirma que seu servidor MariaDB está funcionando e pronto para outras
configurações.

---

## Protegendo o banco de dados MariaDB

Para aumentar a segurança do seu servidor MariaDB, é essencial remover bancos de
dados de teste desnecessários, usuários anônimos e definir uma senha de raiz.
Isso pode ser feito usando o script mariadb-secure-installation, que fornece um
guia passo a passo para proteger seu banco de dados.

Execute o seguinte comando:

!!! info "Configuração segura do Mariadb"

    ```bash
    sudo mariadb-secure-installation
    ```

O script mariadb-secure-installation o guiará por várias etapas importantes:

1. Defina uma senha de root, caso ainda não tenha sido definida.
2. Remover usuários anônimos.
3. Não permitir logins de raiz remotos.
4. Remova o banco de dados de teste.
5. Recarregue as tabelas de privilégios para garantir que as alterações tenham
   efeito.

Depois de concluída, sua instância do MariaDB estará significativamente mais
segura.

!!! exemplo "mariadb-secure-installation example output" (saída de exemplo da
instalação segura do mariadb)

    ```shell-session
    localhost:~ $ sudo mariadb-secure-installation
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

Agora você está pronto para configurar o banco de dados para o Zabbix.

---

## Criação da instância do banco de dados Zabbix

Com o MariaDB configurado e protegido, podemos prosseguir com a criação do banco
de dados para o Zabbix. Esse banco de dados armazenará todos os dados
necessários relacionados ao seu servidor Zabbix, incluindo informações de
configuração e dados de monitoramento.

Siga estas etapas para criar o banco de dados do Zabbix:

Faça login no shell do MariaDB como usuário root: Será solicitado que você
digite a senha de root que definiu durante o processo de instalação do
mariadb-secure-installation.

!!! info "Entre no Mariadb como usuário root"

    ```bash
    mariadb -uroot -p
    ```

Quando estiver conectado ao shell do MariaDB, execute o seguinte comando para
criar um banco de dados para o Zabbix:

!!! info "Criar o banco de dados"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```

Nota "O que é utf8mb4"

     utf8mb4 is a proper implementation of UTF-8 in MySQL/MariaDB, supporting all
     Unicode characters, including emojis. The older utf8 charset in MySQL/MariaDB
     only supports up to three bytes per character and is not a true UTF-8 implementation,
     which is why utf8mb4 is recommended.

Esse comando cria um novo banco de dados chamado `zabbix`com o conjunto de
caracteres UTF-8, que é necessário para o Zabbix.

Crie um usuário dedicado para o Zabbix e conceda os privilégios necessários: Em
seguida, é necessário criar um usuário que o Zabbix usará para acessar o banco
de dados. Substitua a `<senha>` por uma senha forte de sua escolha.

!!! info "Criar usuários e conceder privilégios"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```

    - Replace `<zabbix server ip>` with the actual IP address of your server
      where the Zabbix server  will be installed.
    - Replace `<zabbix frontend ip>` with the actual IP address of your server
      where the Zabbix frontend will be installed.

    If both components are installed on the same server, use the same IP address.

    ???+ tip

        If your Zabbix server, frontend and database are on the same machine, you can replace
        `<zabbix server ip>` and `<zabbix frontend ip>` with `localhost` or `127.0.0.1`.

Isso cria novos usuários `zabbix-web` e `zabbix-srv`, concede a eles acesso ao
banco de dados do Zabbix e garante que os privilégios sejam aplicados
imediatamente.

Neste ponto, seu banco de dados do Zabbix está pronto, mas antes que ele possa
realmente ser usado pelo Zabbix, ainda precisamos preencher o banco de dados com
as tabelas necessárias e os dados iniciais, mas isso será abordado na próxima
seção, quando instalarmos o servidor Zabbix.

Se você pretende instalar o Zabbix Server em uma máquina diferente da que
hospeda o banco de dados, será necessário abrir o firewall do host para permitir
conexões de entrada com o servidor de banco de dados. Por padrão, o MariaDB
escuta na porta 3306.

!!! info "Adicionar regras de firewall"

    Red Hat / SUSE
    ``` bash
    firewall-cmd --add-service=mysql --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ``` bash
    sudo ufw allow 3306/tcp
    ```

---

## Preencher o banco de dados do Zabbix

Durante a instalação do software de banco de dados anteriormente, criamos os
usuários e o banco de dados necessários para o Zabbix; no entanto, o Zabbix
espera que determinadas tabelas, esquemas, imagens e outros elementos estejam
presentes no banco de dados. Para configurar o banco de dados corretamente,
precisamos preenchê-lo com o esquema necessário.

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

???+ aviso

    When using a recent version of MySQL or MariaDB as the database backend for 
    Zabbix, you may encounter issues related to the creation of triggers during
    the schema import process. This is particularly relevant if binary logging
    is enabled on your database server. (Binary logging is often enabled by default)
    To address this, you need to set the `log_bin_trust_function_creators` option to `1`
    in the MySQL/MariaDB configuration file or temporarily at runtime.
    This allows non-root users to create stored functions and triggers without requiring
    `SUPER` privileges, which are restricted when binary logging is enabled.

    Normally we won't need the setting after the initial import of the Zabbix schema is done,
    so we will disable it again after the import is complete.

    !!! info "Activate temporarily extra privileges for non root users"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```

Agora vamos fazer o upload dos dados do zabbix (estrutura do banco de dados,
imagens, usuário, ...) para isso, usamos o usuário `zabbix-srv` e fazemos o
upload de tudo em nosso banco de dados `zabbix`.

!!! info "Populate the database" (Preencher o banco de dados)

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```

!!! aviso

    Depending on the speed of your hardware or virtual machine, the process may
    take anywhere from a few seconds to several minutes without any visual feedback
    after entering the root password.

    Please be patient and avoid cancelling the operation; just wait for the linux 
    prompt to reappear.

???+ Nota

    Zabbix seems to like to change the locations of the script to populate the
    DB every version or even in between versions. If you encounter an error take a
    look at the Zabbix documentation, there is a good chance that some location was
    changed.

Quando a importação do esquema do Zabbix estiver concluída, você não precisará
mais do parâmetro global `log_bin_trust_function_creators`. É uma boa prática
removê-lo por motivos de segurança.

Para reverter o parâmetro global de volta para 0, use o seguinte comando no
shell do MySQL/MariaDB:

!!! info "Desativar a função log_bin_trust novamente"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```

Esse comando desativará a configuração, garantindo que a postura de segurança
dos servidores permaneça robusta.

Isso conclui nossa instalação do MariaDB. Agora você pode prosseguir para
[Preparando o servidor Zabbix](preparation.md).

---

## Conclusão

Com a instalação e a configuração bem-sucedidas do MariaDB como backend do banco
de dados para o Zabbix, agora você tem uma base robusta para sua solução de
monitoramento. Cobrimos a instalação do MariaDB a partir dos pacotes fornecidos
pelo fornecedor e dos repositórios oficiais, protegendo o banco de dados,
criando o banco de dados e os usuários necessários do Zabbix e preenchendo o
banco de dados com o esquema necessário e os dados iniciais.

Seu ambiente Zabbix agora está pronto para os próximos estágios de instalação e
configuração.

---

## Perguntas

1. Qual versão do MariaDB devo instalar para obter compatibilidade e
   estabilidade?
2. Qual é a porta usada pelo meu banco de dados?
3. Quais usuários do banco de dados eu criei e por quê?

---

## URLs úteis

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)
