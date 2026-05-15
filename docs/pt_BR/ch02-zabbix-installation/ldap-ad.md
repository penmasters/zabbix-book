---
description: |
    This section from The Zabbix Book, titled "LDAP/AD Authentication," explains
    how to integrate Zabbix with LDAP or Active Directory for centralized user
    management. It covers connection setup, binding options, and login verification,
    making user authentication more secure and easier to maintain.
tags: [expert]
---

# LDAP / AD

Como qualquer sistema moderno, o Zabbix pode realizar a autenticação de usuários
usando o Lightweight Directory Access Protocol (LDAP). Em teoria, o LDAP é um
protocolo aberto muito bem definido que deve ser independente do fornecedor, mas
sua complexidade relativa desempenha um papel importante em cada implementação
de servidor LDAP. O Zabbix é conhecido por trabalhar bem com o Microsoft Active
Directory e o servidor OpenLDAP.

A autenticação LDAP pode ser configurada em dois modos:

- Autenticação de usuários
- Autenticação de usuários com provisionamento de usuários

## Modo de autenticação de usuários

O processo de autenticação de usuários segue este diagrama.

![Autenticação de usuários LDAP](ch02.3-ldap-auth-diagram.png){ align=center }

_2.3 Autenticação de usuários LDAP_

Conforme mostrado no diagrama, um usuário que tenta fazer login deve ser
pré-criado no Zabbix para poder fazer login usando o LDAP. Os registros de
usuário do banco de dados não têm nenhum campo "dizendo" que o usuário será
autenticado via LDAP, apenas as senhas dos usuários armazenadas no banco de
dados são ignoradas; em vez disso, o Zabbix vai até um servidor LDAP para
verificar se o usuário está autenticado:

- existe um usuário com um determinado nome de usuário
- o usuário forneceu a senha correta

nenhum outro atributo configurado para o usuário no lado do servidor LDAP é
levado em consideração.

Portanto, quando o Zabbix é usado por muitos usuários e grupos, o gerenciamento
de usuários se torna uma tarefa não muito trivial à medida que novas pessoas
entram em equipes diferentes (ou saem). Esse problema é resolvido pelo
"provisionamento de usuários" e abordaremos esse tópico um pouco mais tarde. Por
enquanto, vamos dar uma olhada em como configurar a autenticação LDAP.

## Configurar LDAP

Nesta seção, usaremos um servidor LDAP de demonstração personalizado com dados
pré-carregados. Você pode configurar esse ambiente de demonstração para
verificar as possibilidades de autenticação LDAP do Zabbix. Ou você pode pular a
configuração do ambiente de demonstração se quiser apenas conectar sua instância
do Zabbix ao seu servidor LDAP ou AD existente.

### Configurar o servidor LDAP de demonstração local

Acreditamos que é melhor aprender esse tópico por meio de exemplos, portanto,
usaremos nosso próprio servidor LDAP, que pode ser ativado em um contêiner para
fins de demonstração. Primeiro, precisamos garantir que temos um mecanismo de
contêiner instalado.

!!! info "Instalar o mecanismo de contêiner do Podman"

Red Hat
  ```bash
  dnf install podman
  ```

SUSE
  ```bash
  zypper install podman
  ```

Ubuntu
  ```bash
  sudo apt install podman
  ```

???+ nota "O que é Podman"?

Podman is a container engine designed as a drop-in replacement for Docker, but
with a daemonless architecture. This means it runs containers directly under the
user’s control, improving security and simplicity. Podman is fully compatible
with Docker’s CLI and supports rootless containers, making it ideal for
development, testing, and production environments where security and isolation
are priorities.

???+ tip

Se você quiser usar o Docker em vez do Podman, basta substituir todas as
ocorrências de `podman` nas instruções a seguir por `docker`.

Agora podemos iniciar os contêineres. Inicie um servidor OpenLDAP em um
contêiner:

!!! info "Inicie um servidor OpenLDAP em um contêiner com dados pré-carregados"

  ```bash
  podman run -p 3389:389 -p 6636:636 --name openldap-server --detach bgmot42/openldap-server:0.1.1
  ```

Para simplificar, todos os usuários (incluindo `ldap_search`) nesse servidor
LDAP de teste têm a palavra `e a senha` como suas senhas.

Os usuários `user1` e `user2` são membros do grupo LDAP `zabbix-admins`. Usuário
`user3` é membro do grupo LDAP `zabbix-users`.

???+ dica Dica: use o phpLdapAdmin como uma GUI LDAP

    To visually see LDAP server data (and add your own configuration like users
    and groups) you can start this standard container:

    ```bash
    podman run -p 8081:80 -p 4443:443 --name phpldapadmin --hostname phpldapadmin\
      --link openldap-server:ldap-host --env PHPLDAPADMIN_LDAP_HOSTS=ldap-host\
      --detach osixia/phpldapadmin:0.9.0
    ```
    Now you can access this LDAP server via https://<ip_address>:4443 (or any
    other port you configure to access this Docker container), click Login,
    enter “cn=admin,dc=example,dc=org” in Login DN field and “password” in
    Password field, click Authenticate. You should see the following structure
    of the LDAP server (picture shows ‘zabbix-admins’ group configuration):

    ![LDAP server data](ch02.4-ldap-ldap-server-data.png){ align=center }

    _2.4 LDAP server data_

### Configurar a autenticação LDAP do Zabbix

Vamos definir as configurações do servidor LDAP no Zabbix. No menu do Zabbix,
selecione `Users | Authentication | LDAP settings` e, em seguida, marque a caixa
de seleção `Enable LDAP authentication` e clique em `Add` em `Servers` (altere o
endereço IP do servidor LDAP e o número da porta de acordo com a sua
configuração):

![Configurações do servidor LDAP no
Zabbix](ch02.5-ldap-server-settings-in-zabbix.png){ align=center }

_2.5 Configurações do servidor LDAP no Zabbix_

O diagrama a seguir pode ajudá-lo a entender como configurar o servidor LDAP no
Zabbix com base na estrutura de dados do seu servidor LDAP:

![Servidor LDAP para Zabbix](ch02.6-ldap-server-to-zabbix.png){ align=center }

_2.6 Servidor LDAP para Zabbix_

"Especial" _Distinguished Name_ (DN) _cn=ldap_search,dc=example,dc=org_ é usado
para pesquisa, ou seja, o Zabbix usa esse DN para se conectar ao servidor LDAP
e, é claro, quando você se conecta ao servidor LDAP, precisa ser autenticado - é
por isso que você precisa fornecer _Bind password_. Esse DN deve ter acesso a
uma subárvore na hierarquia de dados LDAP onde todos os seus usuários estão
configurados. No nosso caso, todos os usuários configurados "sob"
_ou=Users,dc=example,dc=org_, esse DN é chamado de DN de base e usado pelo
Zabbix como, por assim dizer, "ponto de partida" para iniciar a pesquisa.

Aviso "Ligação LDAP anônima"

    Technically it is possible to bind to the LDAP server anonymously, without
    providing a password but this is a huge breach in security as the whole
    users sub-tree becomes available for anonymous (unauthenticated) search,
    i.e. effectively exposed to any LDAP client that can connect to LDAP server
    over TCP. The LDAP server we deployed previously in Docker container does
    not provide this functionality.

Clique no botão `Test` e digite `user1` e `password` nos respectivos campos. O
teste deve ser bem-sucedido, confirmando que o Zabbix pode autenticar usuários
no servidor LDAP.

???+ tip

    We can add multiple LDAP servers and use them for different `User groups`.

Para testar o login de usuários reais usando a autenticação LDAP, precisamos
criar grupos de usuários e usuários no Zabbix. No menu do Zabbix, selecione
`Usuários | Grupos de usuários`. Certifique-se de que o grupo `Zabbix
administrators` existe (precisaremos dele mais tarde) e crie um novo grupo
`Zabbix users` clicando no botão `Create user group`. Digite "Zabbix users" no
campo `Group name`, selecione "LDAP" no menu suspenso `Frontend access` que fará
com que o Zabbix autentique os usuários pertencentes a esse grupo no servidor
LDAP e no menu suspenso `LDAP server` selecione o servidor LDAP que configuramos
anteriormente "Test LDAP server". Clique no botão `Add` para criar esse grupo de
usuários:

![Adicionar grupo de usuários no
zabbix](ch02.7-ldap-add-user-group-in-zabbix.png){ align=center }

_2.7 Adicionar grupo de usuários no zabbix_

Agora precisamos criar nosso usuário de teste. No menu do Zabbix, selecione
`Users | Users` e clique no botão `Create user`. Em seguida, digite "user3" no
campo `Username`. Selecione "Zabbix users" no campo `Groups`. O que você digitar
nos campos `Password` e `Password (mais uma vez)` não importa, pois o Zabbix não
tentará usar essa senha; em vez disso, ele irá para o servidor LDAP para
autenticar esse usuário, já que ele é membro do grupo de usuários que tem o
método de autenticação `LDAP`, apenas certifique-se de digitar a mesma cadeia de
caracteres nesses dois campos e de que ela atenda à política de força da senha
definida em `Users | Authentication`.

![Adicionar usuário no Zabbix](ch02.8-ldap-add-user-in-zabbix.png){ align=center
}

_2.8 Adicionar usuário no Zabbix_

Em seguida, clique nEm seguida, clique na guia `Permissions (Permissões)` e
selecione "User role" (Função do usuário) no campo `Role (Função)`:a guia
`Permissions (Permissões)` e selecione "User role" (Função do usuário) no campo
`Role (Função)`:

![Adicionar usuário no Zabbix -
permissões](ch02.9-ldap-add-user-in-zabbix-permissions.png){ align=center }

_2.9 Adicionar usuário no Zabbix - permissões_

Clique no botão `Add` para criar o usuário.

Estamos prontos para testar a autenticação do nosso servidor LDAP! Clique em
`Sign out` no menu do Zabbix e faça login com "user3" como nome de usuário e
"password" como `Password`, se você seguiu cuidadosamente as etapas acima,
deverá fazer login com sucesso com permissões de função de usuário.

Clique em `. Saia do site` novamente e faça login como administrador para
continuar.

## Provisionamento de usuários Just-in-Time

Agora vamos falar sobre um recurso muito legal que o Zabbix oferece -
"Provisionamento de usuário Just-in-Time (JIT) disponível desde o Zabbix 6.4.

Esta imagem ilustra em alto nível como isso funciona: ![LDAP JIT
explained](ch02.10-ldap-jit-explained.png){ align=center }

_2.10 Explicação do LDAP JIT_

Aqui, quando o Zabbix obtém um nome de usuário e senha do formulário de login do
Zabbix, ele vai até o servidor LDAP e obtém todas as informações disponíveis
para esse usuário, incluindo sua associação a grupos LDAP e endereço de e-mail.
Obviamente, ele obtém tudo isso somente se o nome de usuário e a senha corretos
(do ponto de vista do servidor LDAP) tiverem sido fornecidos. Em seguida, o
Zabbix passa pelo mapeamento pré-configurado que define os usuários de qual
`grupo LDAP ` vai para qual `grupo de usuários Zabbix ` . Se pelo menos uma
correspondência for encontrada, um `usuário do Zabbix ` será criado no banco de
dados do Zabbix, pertencente a um grupo de `usuários do Zabbix` e com uma
`função de usuário do Zabbix ` , de acordo com a "correspondência" configurada.
Até agora parece bem simples, certo? Agora vamos entrar em detalhes sobre como
tudo isso deve ser configurado.

Em `Users | Authentication`, precisamos fazer duas coisas:

- Defina `Autenticação padrão` para _LDAP_. Quando o JIT está desativado, o tipo
  de autenticação é definido com base no grupo de usuários __ ao qual o usuário
  que tenta fazer o login pertence. No caso do JIT, o usuário ainda não existe
  no Zabbix e, portanto, obviamente não pertence a nenhum grupo de usuários __ ,
  portanto, o método de autenticação _Padrão_ é usado e queremos que seja
  _LDAP_.

- Forneça `Grupo de usuários desprovisionados`. Esse grupo deve ser literalmente
  _desativado_, caso contrário você não poderá selecioná-lo aqui. Este é o grupo
  de usuários do Zabbix onde todos os usuários _desprovisionados_ serão
  colocados para que efetivamente sejam desabilitados de acessar o Zabbix.

  ![Default authentication](ch02.11-ldap-default-authentication.png){
  align=center }

  _2.11 Default authentication_

  Click `Update` button`.

- Enable JIT provisioning check-box which obviously needs to be checked for this
  feature to work. It's done in our _Test LDAP server_ configuration - select
  `Users | Authentication | LDAP settings` and click on our server in `Servers`
  section. After enabling this check-box we'll see some other fields related to
  JIT to be filled in and what we put in there depends on the method we choose
  to perform JIT.

### Group configuration method “memberOf”

All users in our LDAP server have _memberOf_ attribute which defines what LDAP
groups every user belongs to, e.g. if we perform a LDAP query for _user1_ user
we’ll get that its _memberOf_ attribute has this value:

**memberOf**: cn=**zabbix-admins**,ou=Group,dc=example,dc=org

Note, that your real LDAP server can have totally different LDAP attribute that
provides users’ group membership, and of course, you can easily configure what
attribute to use when searching for user’s LDAP groups by putting it into `User
group membership attribute` field:

![LDAP groups mapping](ch02.12-ldap-groups-mapping.png){ align=center }

_2.12 LDAP groups mapping_

In the picture above we are telling Zabbix to use _memberOf_ attribute to
extract DN defining user’s group membership (in this case it is
_cn=zabbix-admins,out=Group,dc=example,dc=org_) and take only _cn_ attribute
from that DN (in this case it is _zabbix-admins_) to use in searching for a
match in User group mapping rules. Then we define as many mapping rules as we
want. In the picture above we have two rules:

- All users belonging to _zabbix-users_ LDAP group will be created in Zabbix as
  members of _Zabbix users group_ with _User_ role
- All users belonging to _zabbix-admins_ LDAP group will be created in Zabbix as
  members of _Zabbix administrators_ group with _Super admin_ role

### Group configuration method “groupOfNames”

There is another method of finding users’ group membership called “groupOfNames”
it is not as efficient as “memberOf” method but can provide much more
flexibility if needed. Here Zabbix is not querying LDAP server for a user
instead it is searching for LDAP groups based on a given criterion (filter).
It’s easier to explain with pictures depicting an example:

![LDAP server group of names](ch02.13-ldap-group-of-names.png){ align=center }

_2.13 LDAP server groupOfNames_

Firstly we define LDAP “sub-tree” where Zabbix will be searching for LDAP groups
– note _ou=Group,dc=example,dc=org_ in Group base DN field. Then in the field
`Group name attribute` field we what attribute to use when we search in mapping
rules (in this case we take _cn_, i.e. only _zabbix-admins_ from full DN
_cn=zabbix-admins,ou=Group,dc=example,dc=org_). Each LDAP group in our LDAP
server has _member_ attribute that has all users that belong to this LDAP group
(look at the right picture) so we put _member_ in `Group member attribute`
field. Each user’s DN will help us construct `Group filter` field. Now pay
attention: `Reference attribute` field defines what LDAP user’s attribute Zabbix
will use in the `Group filter`, i.e. _%{ref}_ will be replaced with the value of
this attribute (here we are talking about the user’s attributes – we already
authenticated this user, i.e. got all its attributes from LDAP server). To sum
up what I've said above Zabbix:

1. Authenticates the user with entered Username and Password against LDAP server
   getting all user’s LDAP attributes
2. Uses `Reference attribute` and `Group filter` fields to construct a filter
   (when user1 logs in the filter will be
   (_member=uid=user1,ou=Users,dc=example, dc=org_)
3. Performs LDAP query to get all LDAP groups with member attribute (configured
   in `Group member attribute` field) containing constructed in step 2) filter
4. Goes through all LDAP groups received in step 3) and picks `cn` attribute
   (configured in `Group name attribute` field) and finds a match in User group
   mapping rules

Looks a bit complicated but all you really need to know is the structure of your
LDAP data.

### Ready to test

Now when you login with _user1_ or _user2_ username then these users will be
created by Zabbix and put into _Zabbix administrators_ user group, when you
login with _user3_ username then this user will be created by Zabbix and put
into _Zabbix users_ user group:

![Test user1](ch02.14-ldap-jit-test-user1.png){ align=center }

_2.14 Test user1_

![Test user3](ch02.15-ldap-jit-test-user3.png){ align=center }

_2.15 Test user3_

---

## Conclusão

Integrating Zabbix with LDAP—or specifically, Active Directory elevates your
system's authentication capabilities by leveraging existing organizational
credentials. It allows users to log in using familiar domain credentials, while
Zabbix offloads the password verification process to a trusted external
directory. Notably, even when configuring LDAP authentication, corresponding
user accounts must still exist within Zabbix though their internal passwords
become irrelevant once external authentication is active.

Particularly powerful is the Just-In-Time (JIT) provisioning feature: this
enables Zabbix to dynamically create user accounts upon first successful LDAP
login streamlining onboarding and reducing manual administration. Beyond that,
JIT supports ongoing synchronization updating user roles, group memberships, or
even user removals in Zabbix to mirror changes in LDAP—either when a user logs
in or during configured provisioning intervals.

Important configuration details such as case sensitivity, authentication binding
methods, search filters, and group mapping need careful attention to ensure
reliable and secure operation. And while LDAP offers seamless integration,
Zabbix still maintains control over roles, permissions, and access behavior
through its own user and user group models Zabbix.

In sum, LDAP/AD authentication offers a scalable, secure, and enterprise-aligned
approach to centralizing identity management in Zabbix. With flexible
provisioning and synchronization, organizations can reduce administrative load
while reinforcing consistency across their access control and authentication
strategy.

## Perguntas

- What are the main benefits of integrating Zabbix authentication with LDAP or
  Active Directory compared to using only internal Zabbix accounts?

- Why must a user still exist in Zabbix even when LDAP authentication is
  enabled, and what role does the internal password play in that case?

- How does Just-In-Time (JIT) provisioning simplify user management in Zabbix,
  and what potential risks or caveats should an administrator consider when
  enabling it?

- What is the difference between user authentication and user authorization in
  the context of LDAP integration with Zabbix? (Hint: Authentication verifies
  credentials, while authorization determines permissions inside Zabbix.)

- Imagine an administrator incorrectly configures the LDAP search filter. What
  issues might users encounter when attempting to log in, and how could you
  troubleshoot the problem?

- How could LDAP group mappings be used to streamline permission assignment in
  Zabbix? Can you think of an example from your own environment?

- If an organization disables a user account in Active Directory, how does JIT
  provisioning ensure that Zabbix access is also updated? What would happen if
  JIT was not enabled?

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/ldap](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/authentication/ldap)
