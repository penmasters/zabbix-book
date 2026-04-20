---
description: |
    This section from The Zabbix Book titled "Zabbix architecture" explains the 
    modular structure of a Zabbix setup. It highlights the roles of each component
    and their interdependencies, while providing an introduction to how we will 
    perform the installation of the components in next sections.
tags: [beginner]
---

# Arquitetura do Zabbix

Neste capítulo, examinaremos o processo de instalação do servidor Zabbix. Há
muitas maneiras diferentes de configurar um servidor Zabbix. Abordaremos as
configurações mais comuns com MariaDB e PostgreSQL em distribuições baseadas em
RHEL e SLES e no Ubuntu.

Antes de iniciar a instalação, é importante entender a arquitetura do Zabbix. O
Zabbix Server é estruturado de forma modular, composto por três componentes
principais, que discutiremos em detalhes.

- O Zabbix Server
- O servidor web Zabbix (Frontend)
- O banco de dados do Zabbix

!!! resumo "Criação de usuários do banco de dados"

    In our setup we will create 2 DB users `zabbix-web` and `zabbix-srv`. The 
    zabbix-web user will be used for the frontend to connect to our zabbix database.
    The zabbix-srv user will be used by our zabbix server to connect to the database.
    This allows us to limit the permissions for every user to only what is strictly
    needed.


![visualização](ch01-basic-installation-zabbixserver.png){ align=left }

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

Nota

    It is perfectly possible to install all components on one single VM or every component
    on a separate VM.
    The reason why we split the DB in our example is because the database will probably be
    the first component giving you performance headaches. It is also the component
    that needs some extra attention when we split it from the other components,
    so for this reason we have chosen in this example to split the database 
    from the rest of the setup.

Abordaremos os seguintes tópicos:

- Instale nosso banco de dados baseado no MariaDB.
- Instale nosso banco de dados baseado no PostgreSQL.
- Instalando o Zabbix Server.
- Instale o front-end.

