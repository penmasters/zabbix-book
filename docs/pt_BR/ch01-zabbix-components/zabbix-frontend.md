---
description: |
    Esta seção do livro "The Zabbix Book" intitulada "Instalando o frontend"
    fornece instruções passo a passo para instalar o frontend do Zabbix com NGINX
    em várias distribuições Linux. Ela abrange a instalação de pacotes necessários,
    configuração de SELinux e Systemd para PHP-FPM, e modificação da configuração
    do NGINX para servir o frontend do Zabbix na porta 80. Além disso, guia os usuários
    através da configuração inicial do frontend do Zabbix, incluindo a configuração de conexão
    com o banco de dados e configurações básicas como nome da instância,
    fuso horário e formato de tempo.
tags: [beginner]
---

# Instalando o frontend

Antes de configurar o frontend do Zabbix, certifique-se de que o sistema atende aos requisitos
e está preparado conforme descrito no capítulo anterior: [_Início rápido_](../ch00-getting-started/Requirements.md). Este servidor pode ser o mesmo onde os pacotes do Zabbix server foram instalados anteriormente,
ou pode ser uma máquina separada.

Execute todas as etapas subsequentes no servidor designado para o frontend.

---

## Instalando o frontend com NGINX

!!! info "instalar pacotes de frontend"

    Red Hat
    ```bash
    # List all available php modules and active php-8.2
    dnf module list php -y
    dnf module enable php:8.2
    # When using MySQL/MariaDB
    dnf install zabbix-nginx-conf zabbix-web-mysql
    # or when using PostgreSQL
    dnf install zabbix-nginx-conf zabbix-web-pgsql
    ```

    SUSE
    ```bash
    # When using MySQL/MariaDB
    zypper install zabbix-nginx-conf zabbix-web-mysql php8-openssl php8-xmlreader php8-xmlwriter
    # or when using PostgreSQL
    zypper install zabbix-nginx-conf zabbix-web-pgsql php8-openssl php8-xmlreader php8-xmlwriter
    ```

    ???+ note "Suse Linux Enterprise Server"

        No SUSE Linux Enterprise Server (SLES), certifique-se de que você está inscrito no repositório
        "SUSE Linux Enterprise Module Web and Scripting" para acessar os pacotes PHP 8 necessários
        para a instalação do frontend do Zabbix: (em versões do SLES < 16, o comando é "`SUSEConnect`"
        em vez de "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```

        A URL real para o módulo de web scripting pode ser diferente dependendo do pacote específico.
        Use o seguinte comando para determinar a correta.
        ```bash
        suseconnect --list-extensions
        ```


    Ubuntu
    ```bash
    # When using MySQL/MariaDB
    sudo apt install zabbix-frontend-php php8.3-mysql zabbix-nginx-conf
    # or when using PostgreSQL
    sudo apt install zabbix-frontend-php php8.3-pgsql zabbix-nginx-conf
    ```


Este comando instalará os pacotes de frontend junto com as dependências necessárias para NGINX.

A partir do SUSE 16, SELinux é o módulo de segurança padrão em vez de AppArmor.
Por padrão, PHP-FPM não está permitido pelo SELinux no SUSE para
- mapear memória exec necessária para a compilação JIT do PHP,
- conectar ao servidor Zabbix ou
- se conectar ao servidor de banco de dados por TCP.
Precisamos informar o SELinux para permitir tudo isso:

!!! info "SELinux: Permitir que PHP-FPM mapeie memória exec"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```

???+ tip

    Para solucionar problemas relacionados ao SELinux, é recomendado instalar o pacote `setroubleshoot`,
    que registra quaisquer negações do SELinux no log do sistema e fornece sugestões sobre como resolvê-las.

Dependendo das configurações padrão da sua distribuição Linux, PHP-FPM pode não ser
permitido pelo Systemd para escrever no diretório `/etc/zabbix/web` necessário para a configuração do frontend do Zabbix.
Para habilitar isso precisamos criar um arquivo drop-in:

!!! info "Systemd: Permitir que PHP-FPM escreva em /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```


    Isso abrirá um editor para criar o arquivo drop-in `/etc/systemd/system/php-fpm.service.d/override.conf`
    que substituirá ou estenderá o arquivo de serviço existente.

    Adicione as seguintes linhas ao arquivo:

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```


    Em seguida, saia do editor e recarregue a configuração do Systemd:

    ```bash
    systemctl daemon-reload
    ```


???+ note "Como o Systemd está impedindo PHP-FPM de escrever em /etc/zabbix/web?"

    Em muitas distribuições Linux modernas, o Systemd emprega uma característica de segurança conhecida como
    sandboxing para limitar as capacidades dos serviços. Isso é feito para aumentar a segurança ao limitar o acesso
    dos serviços apenas aos recursos que eles precisam para funcionar.
    Por padrão, PHP-FPM pode ser restrito de escrever em certos diretórios,
    incluindo `/etc/zabbix/web`, para prevenir potenciais vulnerabilidades de segurança.
    Isso é imposto através das diretrizes do Systemd `ProtectSystem` e `ReadWritePaths`,
    que controlam o acesso ao sistema de arquivos dos serviços.

???+ tip

    Normalmente, a permissão para escrever em `/etc/zabbix/web` é necessária apenas durante a configuração inicial
    do frontend do Zabbix. Após a conclusão da configuração, você pode remover o arquivo drop-in novamente para
    fortalecer ainda mais a segurança do seu sistema.

A primeira coisa que precisamos fazer é alterar o arquivo de configuração do NGINX para que não usemos
a configuração padrão e sirvamos o frontend do Zabbix na porta 80.

!!! info "Editar configuração do nginx para Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

Se você estiver no Ubuntu, não é necessário editar `nginx.conf`; basta executar `sudo unlink /etc/nginx/sites-enabled/default`

Neste arquivo de configuração procure pelo bloco que começa com `server {`:

!!! example "Configuração original"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```

    ???+ tip

        Este bloco pode ser diferente dependendo da sua distribuição e versão do NGINX.

Em seguida, comente as diretrizes `listen` e `server_name` para desativar a configuração padrão
do servidor HTTP. Você pode fazer isso adicionando um `#` no início de cada linha,
como no exemplo abaixo:

!!! example "Configuração após edição"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```


O arquivo de configuração do Zabbix agora deve ser modificado para assumir o serviço padrão
na porta 80 que acabamos de desativar.
Abra o seguinte arquivo para edição:

!!! info "Editar a configuração do Zabbix para nginx"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```


E altere as seguintes linhas:

!!! example "Configuração original"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```


Remova o `#` na frente das duas primeiras linhas e modifique-as com a porta e domínio corretos
para seu frontend.

???+ tip

    Se você não tiver um domínio, pode substituir `servername` por `_`
    como no exemplo abaixo:

!!! example "Configuração após a edição"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```


O servidor web e o serviço PHP-FPM agora estão prontos para ativação e inicialização persistente.
Execute os seguintes comandos para habilitar e iniciar imediatamente:

!!! info "Reiniciar os serviços do frontend"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```


    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```


Vamos verificar se o serviço está em execução corretamente e habilitado para que sobreviva ao nosso próximo reinício.

!!! info "Verificar se o serviço está rodando"

    ```bash
    sudo systemctl status nginx
    ```

???+ example "Saída de exemplo"

    ```shell-session
    localhost:~> sudo systemctl status nginx
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


Com o serviço em operação e configurado para inicialização automática, a última etapa preparatória envolve ajustar o firewall
para permitir tráfego HTTP entrante. Execute os seguintes comandos:

!!! info "Configurar o firewall"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```


    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```


Abra seu navegador e acesse a URL ou IP do seu frontend :

!!! info "Configuração do frontend"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```


Se tudo correr bem, você deve ser recebido por uma página de boas-vindas do Zabbix. Em caso de
erro, verifique a configuração novamente ou examine o arquivo de log do NGINX `/var/log/nginx/error.log`
ou execute o seguinte comando:

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```


Isso deve ajudá-lo a localizar os erros que cometeu.

Ao acessar a URL apropriada, uma página semelhante à ilustrada abaixo
deverá aparecer:

![visão geral](ch01.2-basic-installation-setup.png){ align=left }

_1.2 Zabbix boas-vindas_

!!! tip "Escolha o local de idioma apropriado"

    O locale `en_US` usa a notação de data americana e um relógio de 12 horas, enquanto
    `en_GB` usa uma notação de data internacional e um relógio de 24 horas.

O frontend do Zabbix apresenta um conjunto limitado de localizações disponíveis, como mostrado.

![visão geral idioma](ch01.3-basic-installation-setuplanguage.png){ align=left }

_1.3 Escolha da linguagem no boas-vindas do Zabbix_

E se quisermos instalar o chinês ou outra língua da lista?
Execute o próximo comando para obter uma lista de todos os locais disponíveis para seu SO.

!!! info "Instalar pacotes de idioma"

    Red Hat
    ```bash
    dnf list glibc-langpack-*
    ```


    SUSE
    ```bash
    localectl list-locales
    ```


    Ubuntu
    ```bash
    apt-cache search language-pack
    ```


Usuários do Ubuntu provavelmente notarão o seguinte erro `"Locale for language "en_US"
is not found on the web server."``

!!! info "Isso pode ser resolvido facilmente com os seguintes comandos."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```


Isso lhe dará uma lista como:

???+ example "Saída de exemplo"

    Red Hat
    ```
    Installed Packages
    glibc-langpack-en.x86_64
    Available Packages
    glibc-langpack-aa.x86_64
    ---
    glibc-langpack-zu.x86_64
    ```


    SUSE
    ```
    C.UTF-8
    aa_DJ.UTF-8
    af_ZA.UTF-8
    an_ES.UTF-8
    ---
    zh_SG.UTF-8
    zh_TW.UTF-8
    zu_ZA.UTF-8
    ```


    Ubuntu
    ```
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


Vamos procurar pelo nosso locale chinês para ver se está disponível. Como você pode ver,
o código começa com zh.

!!! info "Procurar por pacote de idioma"

    Red Hat
    ```shell-session
    ~# dnf list glibc-langpack-* | grep zh
    glibc-langpack-zh.x86_64
    glibc-langpack-lzh.x86_64
    ```


    SUSE
    ```shell-session
    ~> localectl list-locales | grep zh
    zh_CN.UTF-8
    zh_HK.UTF-8
    zh_SG.UTF-8
    zh_TW.UTF-8
    ```


    Ubuntu
    ```bash
    sudo apt-cache search language-pack | grep -i zh
    ```


Em RedHat e Ubuntu, o comando retorna duas linhas; no entanto, dado o código de idioma identificado,
'zh_CN', apenas o primeiro pacote precisa ser instalado.
no SUSE ou os locais `C.UTF-8` e `en_US.UTF-8` são instalados ou todos
os locais disponíveis são instalados, dependendo de se o pacote `glibc-locale` está instalado ou não.

!!! info "Instalar o pacote do locale"

    Red Hat
    ```bash
    dnf install glibc-langpack-zh.x86_64
    sudo systemctl restart nginx php-fpm
    ```


    SUSE
    ```bash
    zypper install glibc-locale
    sudo systemctl restart nginx php-fpm
    ```


    Ubuntu
    ```bash
    sudo apt install language-pack-zh-hans
    sudo systemctl restart nginx php8.3-fpm
    ```


Ao retornar agora ao nosso frontend, somos capazes de selecionar o idioma chinês,
após um recarregamento do navegador.

![selecionar idioma](ch01.4-basic-installation-selectlanguage.png){ align=left }

_1.4 Seleção de idioma no Zabbix_

???+ note

    Se seu idioma preferido não estiver disponível no frontend do Zabbix, não se preocupe,
    isso simplesmente significa que a tradução é ou incompleta ou ainda não está disponível.
    O Zabbix é um projeto open-source que depende de contribuições da comunidade para as traduções,
    então você pode ajudar melhorando com suas próprias traduções.

Visite a página de tradução em [https://translate.zabbix.com/](https://translate.zabbix.com/)
para auxiliar nos esforços de tradução. Uma vez que sua tradução esteja completa e revisada,
será incluída na próxima versão menor do Zabbix.
Suas contribuições ajudam a tornar o Zabbix mais acessível e melhoram a experiência geral
do usuário para todos.Quando você estiver satisfeito com as traduções disponíveis, clique em `Next`. Você será então levado a uma tela para verificar que todos os pré-requisitos estão atendidos. Se algum dos pré-requisitos não for cumprido, resolva esses problemas primeiro. No entanto, se tudo estiver em ordem, você deve ser capaz de prosseguir clicando em `Next`.

![pré-requisitos](ch01.5-basic-installation-prerequisites.png){ align=left }

_1.5 Pré-requisitos do Zabbix_

Na próxima página, você configurará os parâmetros de conexão com o banco de dados:

1. `Select the Database Type`: Escolha entre MySQL ou PostgreSQL dependendo da sua configuração.
2. `Enter the Database Host`: Forneça o endereço IP ou nome DNS do seu servidor de banco de dados. Use a porta 3306 para MariaDB/MySQL ou 5432 para PostgreSQL.
3. `Enter the Database Name`: Especifique o nome do seu banco de dados. No nosso caso, é zabbix. Se você estiver usando PostgreSQL, também precisará fornecer o nome do esquema, que no nosso caso é zabbix_server.
4. `Enther the Database Schema`: Somente para usuários de PostgreSQL, insira o nome do esquema criado para o servidor Zabbix, que no nosso caso é `zabbix_server`.
4. `Enter the Database User`: Insira o usuário do banco de dados criado para a interface web frontal, lembre-se que em nossa guia de instalação básica criamos 2 usuários `zabbix-web` e `zabbix-srv`.
   Um para a frente e o outro para nosso servidor Zabbix, então aqui usaremos o usuário `zabbix-web`. Insira a senha correspondente para este usuário.

Certifique-se de que a opção `Database TLS encryption` não está selecionada, e em seguida clique
em `Next step` para prosseguir.

![conexão-banco-de-dados](ch01.6-basic-installation-dbconnection.png){ align=left }

_1.6 Conexões do Zabbix_

Você está quase terminando a configuração! Os últimos passos envolvem:

1. `Assigning an Instance Name`: Escolha um nome descritivo para sua instância Zabbix.
2. `Selecting the Timezone`: Escolha o fuso horário que corresponde à sua localização ou ao seu fuso horário preferido para a interface do Zabbix.
3. `Setting the Default Time Format`: Selecione o formato de tempo padrão que você prefere usar.
4. **Criptografar conexões da interface web**: Marquei esta caixa, mas você não deve fazer isso. Esta caixa é para criptografar as comunicações entre a frente do Zabbix e seu navegador. Vamos abordar isso mais tarde.
   Uma vez que essas configurações estejam configuradas, você pode concluir a instalação e prosseguir com quaisquer etapas de configuração final conforme necessário.

???+ note

    É uma boa prática definir o servidor Zabbix para o fuso horário UTC, especialmente
    quando gerenciando sistemas em múltiplos fusos horários. Usar UTC ajuda a garantir consistência
    em ações e eventos sensíveis ao tempo, pois o fuso horário do servidor é frequentemente usado para
    calcular e exibir informações relacionadas ao tempo.

![configurações](ch01.7-basic-installation-settings.png){ align=left }

_1.7 Resumo do Zabbix_

Após clicar em `Next step` novamente, você será levado a uma página confirmando que a
configuração foi bem-sucedida. Clique em `Finish` para concluir o processo de instalação.

![configurações](ch01.8-basic-installation-final.png){ align=left }

_1.8 Instalar Zabbix_

Estamos agora prontos para fazer login:

![configurações](ch01.9-basic-installation-login.png)

_1.9 Login no Zabbix_

- Usuário: Admin
- Senha: zabbix

Isso conclui nosso tópico sobre a configuração do servidor Zabbix. Se você estiver interessado em
segurança da frente, recomendo verificar o tópico Segurança do Zabbix para
orientações adicionais e melhores práticas.

???+ tip

    Se você não conseguir salvar sua configuração no final, certifique-se de que executou as instruções relacionadas ao SELinux ou tenha o SELinux desativado.
    Também verifique se a pasta `/etc/zabbix/web` é gravável pelo usuário do webservice
    (geralmente `wwwrun` ou `www`)

---

## Conclusão

Com a instalação e configuração da frente de usuário Zabbix agora concluída,
você configurou com sucesso a interface do usuário para seu sistema de monitoramento Zabbix.
Este processo incluiu a instalação dos pacotes necessários, configuração de um servidor web e
um motor PHP, configuração da conexão com o banco de dados e personalização das configurações da frente.

Nesta etapa, sua instância do Zabbix está em funcionamento, fornecendo a base para
monitoramento avançado e alertas. Nos próximos capítulos, vamos nos aprofundar no
ajuste fino do Zabbix, otimização de desempenho e exploração das principais características que o transformam em uma plataforma poderosa de observabilidade.

Agora que seu ambiente Zabbix está funcionando, vamos levar isso ao próximo nível.

---

## Perguntas

- Por que é necessário comentar a seção padrão listen 80 no nginx.conf antes de editar zabbix.conf?
- Quais serviços do servidor web e gerenciador de processos PHP precisam ser habilitados e iniciados após ajustar as configurações?
- Durante o assistente de configuração da frente de banco de dados, por que você deve inserir o usuário do banco de dados zabbix-web em vez de zabbix-srv?
- Ao conectar um banco de dados PostgreSQL no assistente de configuração Zabbix, qual parâmetro adicional precisa ser fornecido em comparação com MySQL/MariaDB?

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)