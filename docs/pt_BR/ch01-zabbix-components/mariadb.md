---
description: |
    Esta seção do livro The Zabbix Book intitulada "Instalando um Banco de Dados MariaDB"
    guia você através da instalação do MariaDB como o banco de dados backend para o Zabbix.
    Ela abrange dois métodos de instalação: usando pacotes fornecidos pelo distribuidor
    ou os repositórios oficiais do MariaDB. A seção inclui etapas para iniciar e
    proteger o servidor MariaDB, criar um banco de dados Zabbix com usuários apropriados,
    e configurar as regras do firewall se necessário.
tags: [beginner]
---

# Instalando um Banco de Dados MariaDB

Nesta seção, instalaremos os pacotes do servidor e cliente do MariaDB. Isso fornecerá
os componentes necessários para executar e gerenciar o banco de dados MariaDB como seu backend
do Zabbix.

Se você preferir usar PostgreSQL como seu banco de dados backend, pode pular esta seção
e prosseguir para a seção [_Instalando o Banco de Dados PostgreSQL_](postgresql.md).

???+ tip "MySQL/Percona"
    Se você preferir usar MySQL ou Percona em vez do MariaDB, os passos
    de instalação e configuração são muito semelhantes. Geralmente, você substituirá
    `mariadb` por `mysql` nos nomes dos pacotes e comandos.

## Instalando o Servidor e Cliente do MariaDB a partir de Pacotes Fornecidos pelo Distribuidor

Para instalar o servidor e cliente padrão da distribuição MariaDB, execute o
seguinte comando:

!!! info "Instale a versão da distribuição do Mariadb"

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


Este comando baixará e instalará os pacotes do servidor e cliente, permitindo que você
configure, configure e interaja com seu banco de dados MariaDB. Uma vez concluída a
instalação, você pode prosseguir para a seção [_Iniciando o Banco de Dados MariaDB_](#iniciando-o-banco-de-dados-mariadb).

---

## Instalando o Servidor e Cliente do MariaDB a partir dos Repositórios Oficiais do MariaDB

Se preferir instalar o MariaDB a partir dos repositórios oficiais do MariaDB em vez
dos pacotes fornecidos pelo distribuidor, a primeira etapa é adicionar o repositório
MariaDB ao seu sistema.

---

### Adicionando o Repositório MariaDB

Para criar o arquivo de repositório MariaDB, execute o seguinte comando no terminal:

!!! info "Defina o repositório do MariaDB"

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


Isso abrirá um editor de texto onde você pode inserir os detalhes da configuração do repositório.
Uma vez configurado o repositório, você poderá prosseguir com a instalação do MariaDB
usando seu gerenciador de pacotes.

A última configuração pode ser encontrada aqui: [https://mariadb.org/download/?t=repo-config](https://mariadb.org/download/?t=repo-config)

Aqui está um exemplo de configuração para os repositórios MariaDB 11.4:

!!! example "Configuração do repositório Mariadb"

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


Após salvar o arquivo, certifique-se de que tudo está configurado corretamente e que a versão
preferida do MariaDB é compatível com sua versão do Zabbix para evitar possíveis problemas
de integração.

---

### Instalando o Servidor e Cliente do MariaDB

Com o repositório MariaDB configurado, você agora está pronto para instalar os pacotes
do servidor e cliente do MariaDB. Isso fornecerá os componentes necessários para executar
e gerenciar seu banco de dados.

Para instalar o servidor e cliente do MariaDB, execute o seguinte comando:

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


Este comando baixará e instalará os pacotes do servidor e cliente, permitindo que você
configure, configure e interaja com seu banco de dados MariaDB. Uma vez concluída a
instalação, você pode prosseguir para a seção [_Iniciando o Banco de Dados MariaDB_](#iniciando-o-banco-de-dados-mariadb).

---

## Iniciando o Banco de Dados MariaDB

Agora que o MariaDB está instalado, precisamos habilitar o serviço para iniciar automaticamente
ao ligar e iniciá-lo imediatamente. Use o seguinte comando para fazer isso:

!!! info "Habilitar o serviço do MariaDB"

    ```bash
    sudo systemctl enable mariadb --now
    ```


Este comando habilitará e iniciará o serviço do MariaDB, e como será a primeira vez que
o serviço é iniciado, ele inicializará o diretório de banco de dados.
Com o serviço MariaDB agora em execução, você pode verificar se a instalação foi bem-sucedida
verificando a versão do MariaDB usando o seguinte comando:

!!! info "Verifique a versão do Mariadb"

    ```bash
    mariadb -V
    ```


A saída esperada deve ser semelhante a esta:

???+ example "Exemplo de versão do MariaDB"

    ```shell-session
    localhost:~ $ mariadb -V
    mariadb from 11.4.13-MariaDB, client 15.2 for Linux (aarch64) using  EditLine wrapper
    ```


Para garantir que o serviço MariaDB está funcionando corretamente, você pode verificar seu status
com o seguinte comando:

!!! info "Obter status do mariadb"

    ```bash
    sudo systemctl status mariadb
    ```


Você deve ver uma saída semelhante a esta, indicando que o serviço MariaDB é ativo e em execução:

???+ example "Exemplo de status do serviço Mariadb"

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
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Version: '11.4.13-MariaDB'  socket: '/run/mysql/mysql.sock'  port: 3306  MariaDB package
    Dec 03 00:16:04 localhost.localdomain systemd[1]: [Note] InnoDB: Buffer pool(s) load completed at 251203  0:16:04
    Dec 03 00:16:04 localhost.localdomain systemd[1]: Started MariaDB database server.
    ```


Isso confirma que seu servidor MariaDB está funcionando e pronto para configurações adicionais.

---

## Segurança do Banco de Dados MariaDB

Para aumentar a segurança do seu servidor MariaDB, é essencial remover bancos de dados de teste
não necessários, usuários anônimos e definir uma senha root. Isso pode ser feito usando o script
mariadb-secure-installation, que fornece um guia passo a passo para proteger seu banco de dados.

Execute o seguinte comando:

!!! info "Configurar MariaDB com segurança"

    ```bash
    sudo mariadb-secure-installation
    ```


O script mariadb-secure-installation levará você por vários passos importantes:

1. Defina uma senha root se ainda não estiver definida.
2. Remova usuários anônimos.
3. Desabilite o login remoto do root.
4. Remova o banco de dados de teste.
5. Recarregue as tabelas de privilégios para garantir que as alterações entrem em vigor.

Uma vez concluído, sua instância MariaDB será significativamente mais segura.

!!! example "Exemplo de saída do mariadb-secure-installation"

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


Agora você está pronto para configurar o banco de dados para Zabbix.

---

## Criando a Instância do Banco de Dados Zabbix

Com o MariaDB agora configurado e seguro, podemos prosseguir com a criação do banco de dados
para o Zabbix. Este banco de dados armazenará todos os dados necessários relacionados ao seu servidor Zabbix,
incluindo informações de configuração e dados de monitoramento.

Siga estas etapas para criar o banco de dados do Zabbix:

Conecte-se à interface do MariaDB como usuário root:
Será solicitado que você insira a senha root definida durante o processo mariadb-secure-installation.

!!! info "Entre no Mariadb como usuário root"

    ```bash
    mariadb -uroot -p
    ```


Uma vez conectado à interface do MariaDB, execute o seguinte comando para criar um
banco de dados para Zabbix:

!!! info "Crie o banco de dados"

    ```mysql
    MariaDB [(none)]> CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
    ```


???+ note "O que é utf8mb4"

     O utf8mb4 é uma implementação adequada do UTF-8 no MySQL/MariaDB, suportando todos
     os caracteres Unicode, incluindo emojis. A antiga codificação de caracteres utf8 no MySQL/MariaDB
     só suporta até três bytes por caractere e não é uma verdadeira implementação de UTF-8,
     por isso o utf8mb4 é recomendado.

Este comando cria um novo banco de dados chamado `zabbix` com o conjunto de caracteres UTF-8,
que é necessário para o Zabbix.

Crie um usuário dedicado para o Zabbix e conceda os privilégios necessários: Em seguida, você
precisa criar um usuário que o Zabbix usará para acessar o banco de dados. Substitua `<password>`
por uma senha forte da sua escolha.

!!! info "Crie usuários e conceda privilégios"

    ```mysql
    MariaDB [(none)]> CREATE USER 'zabbix-web'@'<zabbix frontend ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> CREATE USER 'zabbix-srv'@'<zabbix server ip>' IDENTIFIED BY '<password>';
    MariaDB [(none)]> GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix-srv'@'<zabbix server ip>';
    MariaDB [(none)]> GRANT SELECT, UPDATE, DELETE, INSERT ON zabbix.* TO 'zabbix-web'@'<zabbix server ip>';
    MariaDB [(none)]> FLUSH PRIVILEGES;
    ```


    - Substitua `<zabbix server ip>` pelo endereço IP real do seu servidor
      onde o servidor Zabbix será instalado.
    - Substitua `<zabbix frontend ip>` pelo endereço IP real do seu servidor
      onde a interface frontal do Zabbix será instalada.

    Se ambos os componentes forem instalados no mesmo servidor, use o mesmo endereço IP.

    ???+ tip

        Se seu servidor Zabbix, frontend e banco de dados estiverem na mesma máquina,
        você pode substituir `<zabbix server ip>` e `<zabbix frontend ip>` por `localhost` ou `127.0.0.1`.

Isso cria novos usuários `zabbix-web` e `zabbix-srv`, concede a eles acesso ao
banco de dados do Zabbix e garante que os privilégios sejam aplicados imediatamente.

Neste ponto, seu banco de dados Zabbix está pronto, mas antes que ele possa ser realmente usado pelo
Zabbix, ainda precisamos preencher o banco de dados com as tabelas necessárias e os dados iniciais,
mas isso será abordado na próxima seção quando instalarmos o servidor do Zabbix.

Se você pretende instalar o servidor do Zabbix em uma máquina diferente daquela que hospeda
o banco de dados, precisará abrir o firewall do host para permitir conexões entrantes ao servidor
do banco de dados. Por padrão, o MariaDB escuta na porta 3306.

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

## Preenchendo o Banco de Dados Zabbix

Durante a instalação do software de banco de dados anteriormente, criamos os
usuários e banco de dados necessários para o Zabbix, no entanto, o Zabbix espera que certas tabelas,
esquemas, imagens e outros elementos estejam presentes no banco de dados.
Para configurar corretamente o banco de dados, precisamos preenchê-lo com o esquema necessário.

Primeiro precisamos instalar os scripts SQL do Zabbix que contêm os scripts de importação
necessários para o banco de dados.

!!! info "Instale os scripts SQL"

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


???+ warning

    Ao usar uma versão recente do MySQL ou MariaDB como o backend de banco de dados para
    Zabbix, você pode encontrar problemas relacionados à criação de gatilhos durante
    o processo de importação do esquema. Isso é particularmente relevante se o registro binário
    estiver habilitado no seu servidor de banco de dados. (O registro binário geralmente está habilitado por padrão)
    Para resolver isso, você precisa definir a opção `log_bin_trust_function_creators` para `1`
    no arquivo de configuração do MySQL/MariaDB ou temporariamente em tempo de execução.
    Isso permite que usuários não-root criem funções armazenadas e gatilhos sem exigir
    privilégios `SUPER`, que são restritos quando o registro binário está habilitado.

    Normalmente não precisaremos dessa configuração após a importação inicial do esquema do Zabbix,
    então desabilitaremos novamente depois que a importação for concluída.

    !!! info "Ativar temporariamente privilégios adicionais para usuários não root"

        ```bash
        mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 1;"
        ```


Agora vamos fazer o upload dos dados do zabbix (estrutura de banco, imagens,
usuário, ...) para isso usamos o usuário `zabbix-srv` e fazemos
o upload em nosso DB `zabbix`.

!!! info "Popule o banco de dados"

    ``` bash
    sudo zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uroot -p zabbix
    ```


!!! warning

    Dependendo da velocidade do seu hardware ou máquina virtual, o processo pode
    levar de alguns segundos a vários minutos sem nenhum feedback visual após
    entrar com a senha root.

    Por favor seja paciente e evite cancelar a operação; apenas aguarde a
    reaparição da prompt linux.

???+ note

    O Zabbix parece gostar de mudar as localizações do script para popular o DB
    em cada versão ou até mesmo entre versões. Se você encontrar um erro, dê uma
    olhada na documentação do Zabbix, há uma boa chance que alguma localização foi
    alterada.

Uma vez concluída a importação do esquema do Zabbix, você não precisará mais da
parâmetro global `log_bin_trust_function_creators`. É uma boa prática removê-lo por razões de
segurança.

Para reverter o parâmetro global para 0, use o seguinte comando no shell MySQL/MariaDB:

!!! info "Desabilitar a função log_bin_trust novamente"

    ```bash
    mariadb -uroot -p -e "SET GLOBAL log_bin_trust_function_creators = 0;"
    ```


Este comando desabilitará a configuração, garantindo que a postura de segurança dos
servidores permaneça robusta.

Isso conclui nossa instalação do MariaDB. Você pode agora prosseguir para [Preparando o servidor Zabbix](preparation.md).

---

## Conclusão

Com a instalação e configuração bem-sucedida do MariaDB como backend de banco de
dados para o Zabbix, você agora tem uma base robusta para sua solução de monitoramento.
Cobrimos a instalação do MariaDB tanto de pacotes fornecidos pelo provedor quanto
de repositórios oficiais, segurando o banco de dados, criando os usuários necessários
do Zabbix e populando o banco com o esquema e dados iniciais exigidos.

Seu ambiente Zabbix está agora pronto para as próximas etapas de configuração e setup.

---

## Perguntas

1. Qual versão do MariaDB eu devo instalar para compatibilidade e estabilidade?
2. Em qual porta meu banco de dados está usando?
3. Quais usuários de banco de dados criei e por quê?

---

## URLs Úteis

- [https://mariadb.org/download/](https://mariadb.org/download/)
- [https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines](https://mariadb.com/docs/server/server-usage/stored-routines/binary-logging-of-stored-routines)
