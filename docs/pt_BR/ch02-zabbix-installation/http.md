---
description: |
    This section from The Zabbix Book, titled "HTTP Authentication," explains how
    to secure Zabbix frontend access using web server authentication methods. It
    covers setup with Apache or Nginx, integration with Zabbix, and how HTTP auth
    adds an extra protection layer to your monitoring environment.
tags: [advanced]
---

# HTTP

A autenticação HTTP é um dos métodos de autenticação externa fornecidos pelo
Zabbix e pode ser usada para proteger adicionalmente sua WebUI do Zabbix com o
mecanismo de autenticação básica no nível do servidor HTTP.

Basic HTTP authentication protects Website (Zabbix WebUI) resources with a
username and password. When a user attempts to access Zabbix WebUI, the browser
pops up a dialog asking for credentials before sending anything over to Zabbix
WebUI php code.

Um servidor HTTP tem um arquivo com credenciais que é usado para autenticar
usuários.

Primeiro, vamos ver como podemos configurar a autenticação básica no servidor
HTTP.

???+ aviso

    The examples below provide just minimum set of options to configure
    basic authentication. Please refer to respective HTTP server documentation
    for more details

## Autenticação básica

Para ativar a autenticação básica, primeiro precisamos de um "arquivo de senha"
que contenha todos os nomes de usuário e senhas que têm permissão para acessar o
frontend.

!!! aviso "Importante"

    Usernames configured for basic authentication in HTTP server
    must exist in Zabbix. But only passwords configured in HTTP server are used
    for users authentication.

Para criar esse arquivo, precisamos do comando `htpasswd`. Execute os comandos a
seguir para garantir que temos esse utilitário:

!!! info "Instalar o utilitário htpasswd"

    Red Hat
    ```bash
    dnf install httpd-utils
    ```

    SUSE
    ```bash
    zypper install apache2-utils
    ```

    Ubuntu
    ```bash
    sudo apt install apache2-utils
    ``` 

Em seguida, criaremos o arquivo necessário e o usuário `Administrador` nele:

!!! informações

    NGINX
    ```bash
    sudo htpasswd -c /etc/nginx/httpauth Admin
    ```

    Apache on Red Hat
    ```bash
    sudo htpasswd -c /etc/httpd/.htpasswd Admin
    ```

    Apache on SUSE / Ubuntu
    ```bash
    sudo htpasswd -c /etc/apache2/.htpasswd Admin
    ```

Esse comando solicitará que você insira a senha desejada para o usuário
`Administrador` e, em seguida, criará o arquivo de senha especificado com o nome
de usuário e a senha criptografada.

Para qualquer usuário adicional, podemos usar o mesmo comando, mas sem a opção
`-c`, pois o arquivo já está criado:

???+ exemplo "Adicionar usuários adicionais"

    ```shell-session
    localhost:~> sudo htpasswd /etc/nginx/httpauth user1
    New password: 
    Re-type new password: 
    Adding password for user user1
    ```

O que adicionará `user1` ao arquivo `/etc/nginx/httpauth`. Substitua esse
caminho pelo caminho desse arquivo em sua distribuição/servidor da Web.

No final, o arquivo de senha deve se parecer com algo como:

???+ exemplo "Exemplo de arquivo de senha"

    ```shell-session
    localhost:~> sudo cat /etc/nginx/httpauth
    Admin:$1$8T6SbR/N$rgANUPGvFh7H.R1Mffexh.
    user1:$1$GXoDIOCA$u/n1kkDeFwcI4KhyHkY6p/
    ```

Agora que temos um arquivo de senha, podemos continuar a configurar o navegador
da Web para realmente executar a autenticação básica, usando esse arquivo.

### Configurar o arquivo de autenticação no Nginx

Localize o bloco `/ {` no arquivo de configuração do Nginx que define a WebUI do
Zabbix (se você seguiu as etapas de instalação descritas nos capítulos
anteriores, ele deve estar em `/etc/nginx/conf.d/zabbix.conf`) e adicione essas
duas linhas:

!!! informações

    ```
        location / {
            ...
            auth_basic "Basic Auth Protected Site";
            auth_basic_user_file /etc/nginx/httpauth;
        }
    ```

Não se esqueça de reiniciar o serviço Nginx depois de fazer essa alteração.

## Configurar o arquivo de autenticação no Apache HTTPD

Localize `<Directory "/usr/share/zabbix">` bloco no arquivo de configuração
HTTPD do Apache que define sua Zabbix WebUI (no meu caso é
`/etc/zabbix/apache.conf`) e adicione estas linhas:

???+ nota

    By default configuration has `Require all granted`, remove this line.

???+ exemplo

    RedHat:
    ```
        <Directory "/usr/share/zabbix">
            ...
            AuthType Basic
            AuthName "Restricted Content"
            AuthUserFile /etc/httpd/.htpasswd
            Require valid-user
        </Directory>
    ```

    Ubuntu / SUSE
    ```
        <Directory "/usr/share/zabbix">
            ...
            AuthType Basic
            AuthName "Restricted Content"
            AuthUserFile /etc/apache2/.htpasswd
            Require valid-user
        </Directory>
    ```

Não se esqueça de reiniciar o serviço apache2 ou httpd depois de fazer essa
alteração.

## Configuração do Zabbix para autenticação HTTP

Quando tivermos um servidor WEB configurado com autenticação básica, é hora de
configurar o servidor Zabbix. No menu do Zabbix, selecione `Users |
Authentication | HTTP settings` e marque a caixa de seleção `Enable HTTP
authentication`. Clique em `Update` e confirme as alterações clicando no botão
`OK`.

![Autenticação de usuários HTTP](ch02.1-http-auth-settings.png){ align=center }

_2.1 Autenticação de usuários HTTP_

`Remover nome de domínio` campo deve ter uma lista separada por vírgulas de
domínios que o Zabbix removerá do nome de usuário fornecido, por exemplo, se um
usuário digitar "test@myzabbix" ou "myzabbix\test" e tivermos "myzabbix" nesse
campo, o usuário será conectado com o nome de usuário "test".

Desmarque a caixa de seleção `Case-sensitive login` para que o Zabbix não dê
atenção às letras maiúsculas e minúsculas nos nomes de usuário, por exemplo,
"tEst" e "test" se tornarão nomes de usuário igualmente legítimos, mesmo que no
Zabbix tenhamos apenas o usuário "test" configurado.

Observe que `Formulário de login padrão` está definido como "Formulário de login
do Zabbix". Agora, se você sair, verá o link "Sign in with HTTP" abaixo dos
campos Nome de usuário e Senha. Se você clicar no link, será automaticamente
conectado à WebUI do Zabbix com o mesmo nome de usuário usado anteriormente. Ou
você pode digitar um nome de usuário e uma senha diferentes e fazer o login
normalmente na Zabbix WebUI como um usuário diferente.

![Login de autenticação de usuários HTTP](ch02.2-http-auth-login.png){
align=center }

_2.2 Formulário de login de autenticação de usuários HTTP_

Se você selecionar "HTTP login form" em `Default login form` drop-down, você não
verá o formulário de login padrão do Zabbix quando tentar sair. Na verdade, você
não poderá fazer o logout a menos que sua sessão de autenticação expire. A única
maneira de se desconectar é limpar os cookies em seu navegador. Em seguida, você
terá que passar pelo procedimento de autenticação básica do servidor Web
novamente.

---

## Conclusão

A configuração da autenticação no nível HTTP adiciona uma camada crítica de
controle de acesso à interface do usuário da Web do Zabbix, aproveitando os
mecanismos de autenticação nativos do servidor da Web. Seja usando o Nginx ou o
Apache, essa abordagem garante que as credenciais dos usuários sejam solicitadas
antes mesmo de chegarem ao Zabbix, protegendo-os efetivamente contra o acesso
não autorizado no ponto de entrada HTTP. As principais considerações incluem a
garantia de que os nomes de usuário usados na autenticação HTTP já estejam
definidos no próprio Zabbix; somente a senha do servidor Web é importante para
as verificações de credenciais e a configuração correta das configurações de
autenticação HTTP do Zabbix (como a remoção do domínio e as opções de
diferenciação de maiúsculas e minúsculas). Ao coordenar as configurações de
autenticação do servidor Web com a configuração interna do Zabbix, é possível
obter fluxos de trabalho de login de usuário seguros e contínuos que combinam a
usabilidade do front-end com medidas de proteção robustas.

---

## Perguntas

- Qual é a vantagem da autenticação HTTP (baseada no servidor da Web) em
  comparação com o mecanismo de autenticação interna do Zabbix? (Considere a
  proteção na camada do servidor Web antes mesmo de o usuário chegar à interface
  do usuário do Zabbix).

- Por que é essencial que um usuário exista no Zabbix mesmo quando a
  autenticação HTTP está ativada e por que a senha do Zabbix se torna
  irrelevante nesse caso?

- Quais são as opções de configuração no front-end do Zabbix em "Administração →
  Autenticação" para autenticação HTTP e como cada uma delas pode afetar o
  comportamento de login? Os exemplos incluem ativar/desativar a sensibilidade a
  maiúsculas e minúsculas, a remoção de domínio e a escolha do formulário de
  login.

- Suponha que você desative os logins com distinção entre maiúsculas e
  minúsculas e mantenha as contas "Admin" e "admin" no Zabbix. Como a
  autenticação HTTP se comportará e que resultado você deve esperar?

- Imagine a solução de um problema de falha de login ao usar a autenticação
  HTTP: Que medidas você tomaria para garantir que a autenticação do servidor
  Web esteja configurada corretamente antes de examinar as configurações do
  Zabbix?

- Do ponto de vista da segurança, quando a autenticação HTTP por si só seria
  insuficiente e quais outros métodos de autenticação (por exemplo, LDAP, SAML,
  MFA) você poderia colocar em camadas para aumentar a segurança?

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/http)
