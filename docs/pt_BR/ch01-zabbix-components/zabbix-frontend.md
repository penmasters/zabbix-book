---
description: |
    This section from The Zabbix Book titled "Installing the frontend" provides
    step-by-step instructions for installing the Zabbix frontend with NGINX on
    various Linux distributions. It covers the installation of necessary packages,
    configuration of SELinux and SystemD for PHP-FPM, and modification of the
    NGINX configuration to serve the Zabbix frontend on port 80. Additionally, 
    it guides users through the initial setup of the Zabbix frontend, including
    database connection configuration and basic settings such as instance name,
    timezone, and time format.
tags: [beginner]
---

# Instalando o front-end

Antes de configurar o front-end do Zabbix, certifique-se de que o sistema atenda
aos requisitos e esteja preparado conforme descrito no capítulo anterior:
[_Getting started_](../ch00-getting-started/Requirements.md). Esse servidor pode
ser o mesmo em que os pacotes do Zabbix Server foram instalados anteriormente ou
pode ser uma máquina separada.

Execute todas as etapas subsequentes no servidor designado para o frontend.

---

## Instalando o front-end com o NGINX

!!! info "instalar pacotes de front-end"

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

        On SUSE Linux Enterprise Server (SLES), ensure you are subscribed to the
        "SUSE Linux Enterprise Module Web and Scripting" repository to access
        the necessary PHP 8 packages required for the Zabbix frontend installation:
        (on SLES versions < 16, the command is "`SUSEConnect`" instead of "`suseconnect`")

        ```bash
        suseconnect -p sle-module-web-scripting/16/x86_64
        ```
        The actual URL for web scripting module may be different depending on particular service pack. Use the following command to determine the right one.
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

Esse comando instalará os pacotes de front-end junto com as dependências
necessárias para o Nginx.

A partir do SUSE 16, o SELinux é agora o módulo de segurança padrão em vez do
AppArmor. Por padrão, o PHP-FPM não é permitido pelo SELinux no SUSE para
- mapear a memória executiva necessária para a compilação JIT do PHP,
- conectar-se ao servidor Zabbix ou
- conectar-se ao servidor de banco de dados via TCP. Precisamos informar ao
  SELinux para permitir tudo isso:

!!! info "SELinux: Permitir que o PHP-FPM mapeie a memória executiva"

    ```bash
    setsebool -P httpd_execmem 1
    setsebool -P httpd_can_connect_zabbix 1
    setsebool -P httpd_can_network_connect_db 1
    ```
???+ dica

    To troubleshoot SELinux issues, it is recommended to install the `setroubleshoot`
    package which will log any SELinux denials in the system log and provide
    suggestions on how to resolve them.

Dependendo dos padrões de sua distribuição Linux, o PHP-FPM pode, por padrão,
não ser autorizado pelo SystemD a gravar no diretório `/etc/zabbix/web`
necessário para a configuração do front-end do Zabbix. Para habilitar isso,
precisamos criar um arquivo drop-in que permita isso:

!!! info "SystemD: Permitir que o PHP-FPM escreva em /etc/zabbix/web"

    ```bash
    systemctl edit php-fpm
    ```

    This will open an editor to create a drop-in file `/etc/systemd/system/php-fpm.service.d/override.conf`
    which will override or extend the existing service file.

    Add the following lines to the file:

    ```ini
    [Service]
    ReadWritePaths=/etc/zabbix/web
    ```

    Then exit the editor and reload the SystemD configuration:

    ```bash
    systemctl daemon-reload
    ```

Nota "Como o SystemD está impedindo que o PHP-FPM escreva em /etc/zabbix/web?"

    On many modern Linux distributions, SystemD employs a security feature known as
    sandboxing to restrict the capabilities of services. This is done to enhance
    security by limiting the access of services to only the resources they need to function.
    By default, PHP-FPM may be restricted from writing to certain directories,
    including `/etc/zabbix/web`, to prevent potential security vulnerabilities.
    This is enforced through SystemD's `ProtectSystem` and `ReadWritePaths` directives, which
    control the file system access of services.

???+ dica

    Normally write access to `/etc/zabbix/web` is only needed during the initial setup
    of the Zabbix frontend. After the setup is complete you can remove the drop-in
    file again to further harden the security of your system.

A primeira coisa que precisamos fazer é alterar o arquivo de configuração do
Nginx para que não usemos a configuração padrão e sirvamos o frontend do Zabbix
na porta 80.

!!! info "editar configuração do nginx para Red Hat"

    ```bash
    vi /etc/nginx/nginx.conf
    ```

Nesse arquivo de configuração, procure o seguinte bloco que começa com `server
{`:

!!! exemplo "Configuração original"

    ```nginx
    server {
        listen 80;
        listen [::]:80;
        server_name *;
    ...
    ```
    ???+ tip

        This block may be different depending on your distribution and Nginx version.


Em seguida, comente as diretivas any `listen` e `server_name` para desativar a
configuração padrão do servidor http. Você pode fazer isso adicionando `#` no
início de cada linha, como no exemplo abaixo:

!!! exemplo "Configurar após editar"

    ```nginx
    server {
        #listen 80;
        #listen [::]:80;
        #server_name *;
    ...
    ```

Agora, o arquivo de configuração do Zabbix deve ser modificado para assumir o
serviço padrão na porta 80 que acabamos de desativar. Abra o arquivo a seguir
para edição:

!!! info "editar configuração do zabbix para nginx"

    ```bash
    sudo vi /etc/nginx/conf.d/zabbix.conf
    ```

E altere as seguintes linhas:

!!! exemplo "Configuração original"

    ```nginx
    server {
    #       listen          8080;
    #       server_name     example.com;

            root    /usr/share/zabbix;

            index   index.php;
    ...
    ```

Remova o `#` na frente das duas primeiras linhas e modifique-as com a porta e o
domínio corretos para seu front-end.

???+ dica

    In case you don't have a domain you can replace `servername` with `_` 
    like in the example below:

!!! exemplo "Configuração após a edição"

    ```nginx
    server {
            listen          80;
            server_name     _;

             root    /usr/share/zabbix;

             index   index.php;
    ```

O servidor Web e o serviço PHP-FPM agora estão prontos para ativação e
inicialização persistente. Execute os comandos a seguir para ativá-los e
iniciá-los imediatamente:

!!! info "reinicie os serviços de front-end"

    Red Hat / SUSE
    ```bash
    systemctl enable nginx php-fpm --now
    ```

    Ubuntu
    ```bash
    sudo systemctl enable nginx php8.3-fpm --now
    ```

Vamos verificar se o serviço foi iniciado e ativado corretamente para que ele
sobreviva à nossa reinicialização na próxima vez.

!!! info "verifique se o serviço está em execução"

    ```bash
    sudo systemctl status nginx
    ```
???+ example "Exemplo de saída"

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

Com o serviço operacional e configurado para inicialização automática, a etapa
preparatória final envolve o ajuste do firewall para permitir o tráfego HTTP de
entrada. Execute os seguintes comandos:

!!! info "configurar o firewall"

    Red Hat / SUSE
    ```bash
    firewall-cmd --add-service=http --permanent
    firewall-cmd --reload
    ```

    Ubuntu
    ```bash
    sudo ufw allow 80/tcp
    ```

Abra seu navegador e acesse a url ou o ip de seu front-end:

!!! info "configuração de front-end"

    ```
    http://<ip or dns of the zabbix frontend server>/
    ```

Se tudo correr bem, você deverá ser recebido com uma página de boas-vindas do
Zabbix. Caso ocorra algum erro, verifique novamente a configuração ou dê uma
olhada no arquivo de registro do nginx `/var/log/nginx/error.log` ou execute o
seguinte comando :

!!! info ""

    ```bash
    journalctl -xeu nginx
    ```

Isso deve ajudá-lo a localizar os erros que você cometeu.

Ao acessar o URL apropriado, deverá aparecer uma página semelhante à ilustrada
abaixo:

![overview](ch01-basic-installation-setup.png){ align=left }

_1.4 Boas-vindas ao Zabbix_

O front-end do Zabbix apresenta um conjunto limitado de localizações
disponíveis, conforme mostrado.

![overview language](ch01-basic-installation-setuplanguage.png){ align=left }

_!.5 Escolha do idioma de boas-vindas do Zabbix_

E se quisermos instalar o chinês como idioma ou outro idioma da lista? Execute o
comando a seguir para obter uma lista de todas as localidades disponíveis para
seu sistema operacional.

!!! info "Instalar pacotes de idiomas"

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

Os usuários do Ubuntu provavelmente notarão o seguinte erro `"Locale for
language "en_US" is not found on the web server."``

!!! info "Isso pode ser resolvido facilmente com os seguintes comandos."

    ```bash
    sudo locale-gen en_US.UTF-8
    sudo update-locale
    sudo systemctl restart nginx php8.3-fpm
    ```

Isso lhe dará uma lista como:

???+ example "Exemplo de saída"

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

Vamos procurar nossa localidade chinesa para ver se ela está disponível. Como
você pode ver, o código começa com zh.

!!! info "search for language pack" (procurar pacote de idiomas)

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

No RedHat e no Ubuntu, o comando gera duas linhas; no entanto, dado o código de
idioma identificado, 'zh_CN', somente o primeiro pacote requer instalação. No
SUSE, somente os locais `C.UTF-8` e `en_US.UTF-8` são instalados ou todos os
locais disponíveis são instalados, dependendo se o pacote `glibc-locale` está
instalado ou não.

!!! info "Instalar o pacote de localidade"

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

Quando retornamos ao nosso front-end, podemos selecionar o idioma chinês, depois
de recarregar o navegador.

![selecione o idioma](ch01-basic-installation-selectlanguage.png){ align=left }

_1.6 Zabbix selecionar idioma_

???+ Nota

    If your preferred language is not available in the Zabbix front-end, don't
    worry, it simply means that the translation is either incomplete or not yet
    available. Zabbix is an open-source project that relies on community contributions
    for translations, so you can help improve it by contributing your own translations.

Visite a página de tradução em
[https://translate.zabbix.com/](https://translate.zabbix.com/) para ajudar nos
esforços de tradução. Assim que sua tradução for concluída e revisada, ela será
incluída na próxima versão de correção menor do Zabbix. Suas contribuições
ajudam a tornar o Zabbix mais acessível e melhoram a experiência geral do
usuário para todos.

Quando estiver satisfeito com as traduções disponíveis, clique em `Next`. Você
será levado a uma tela para verificar se todos os pré-requisitos foram
atendidos. Se algum pré-requisito não for atendido, resolva esses problemas
primeiro. Entretanto, se tudo estiver em ordem, você poderá prosseguir clicando
em `Next`.

![pré-requisitos](ch01-basic-installation-prerequisites.png){ align=left }

_1.7 Pré-requisitos do Zabbix_

Na próxima página, você configurará os parâmetros de conexão do banco de dados:

1. `Selecione o tipo de banco de dados`: Escolha MySQL ou PostgreSQL, dependendo
   de sua configuração.
2. `Digite o host do banco de dados`: Forneça o endereço IP ou o nome DNS do seu
   servidor de banco de dados. Use a porta 3306 para MariaDB/MySQL ou 5432 para
   PostgreSQL.
3. `Digite o nome do banco de dados`: Especifique o nome do seu banco de dados.
   No nosso caso, é zabbix. Se estiver usando o PostgreSQL, também será
   necessário fornecer o nome do esquema, que, no nosso caso, é zabbix_server.
4. `Digite o Esquema do Banco de Dados`: Somente para usuários do PostgreSQL,
   digite o nome do esquema criado para o servidor Zabbix, que é `zabbix_server`
   no nosso caso.
4. `Digite o usuário do banco de dados`: Insira o usuário do banco de dados
   criado para o front-end da Web, lembre-se de que em nosso guia de instalação
   básica criamos dois usuários `zabbix-web` e `zabbix-srv`. Um para o front-end
   e o outro para o nosso servidor zabbix, portanto, aqui usaremos o usuário
   `zabbix-web`. Digite a senha correspondente para esse usuário.

Certifique-se de que a opção `Database TLS encryption` não esteja selecionada e
clique em `Next step` para prosseguir.

![dbconnection](ch01-basic-installation-dbconnection.png){ align=left }

_1.8 Conexões do Zabbix_

Você está quase terminando a configuração! As etapas finais envolvem:

1. `Atribuição de um nome de instância`: Escolha um nome descritivo para sua
   instância do Zabbix.
2. `Selecionando o fuso horário`: Escolha o fuso horário que corresponde à sua
   localização ou o fuso horário preferido para a interface do Zabbix.
3. `Definição do formato de hora padrão`: Selecione o formato de hora padrão que
   você prefere usar.
4. **Criptografar conexões da interface da Web**: Eu marquei esta caixa, mas
   você não deveria. Essa caixa serve para criptografar as comunicações entre o
   front-end do Zabbix e seu navegador. Falaremos sobre isso mais tarde. Quando
   essas configurações estiverem definidas, você poderá concluir a instalação e
   prosseguir com as etapas finais de configuração, conforme necessário.

???+ Nota

    It's a good practice to set your Zabbix server to the UTC timezone, especially
    when managing systems across multiple timezones. Using UTC helps ensure consistency
    in time-sensitive actions and events, as the server’s timezone is often used for
    calculating and displaying time-related information.

![configurações](ch01-basic-installation-settings.png){ align=left }

_1.9 Resumo do Zabbix_

Depois de clicar novamente em `Next step`, você será levado a uma página que
confirma que a configuração foi bem-sucedida. Clique em `Finish` para concluir o
processo de configuração.

![configurações](ch01-basic-installation-final.png){ align=left }

_1.10 Instalação do Zabbix_

Agora estamos prontos para fazer o login:

![configurações](ch01-basic-installation-login.png)

_1.11 Login do Zabbix_

- Login : Administrador
- Senha : zabbix

Isso conclui nosso tópico sobre a configuração do servidor Zabbix. Se você
estiver interessado em proteger seu front-end, recomendo que consulte o tópico
Protegendo o Zabbix para obter orientações adicionais e práticas recomendadas.

???+ dica

    If you are not able to save your configuration at the end, make sure you
    executed the SELinux related instructions or have SELinux disabled.
    Also check if the `/etc/zabbix/web` directory is writable by the webservice
    user (usually `wwwrun` or `www`)

---

## Conclusão

Com a instalação e a configuração do front-end do Zabbix concluídas, você
configurou com êxito a interface do usuário para o seu sistema de monitoramento
Zabbix. Esse processo incluiu a instalação dos pacotes necessários, a
configuração de um servidor Web e de um mecanismo PHP, a configuração da conexão
com o banco de dados e a personalização das configurações do frontend.

Nesta etapa, sua instância do Zabbix está operacional, fornecendo a base para o
monitoramento e os alertas avançados. Nos próximos capítulos, vamos nos
aprofundar no ajuste fino do Zabbix, otimizando o desempenho e explorando os
principais recursos que o transformam em uma poderosa plataforma de
observabilidade.

Agora que seu ambiente Zabbix está instalado e funcionando, vamos levá-lo para o
próximo nível.

---

## Perguntas

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual](https://www.zabbix.com/documentation/current/en/manual)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](ttps://www.zabbix.com/documentation/current/en/manual/installation/requirements)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
