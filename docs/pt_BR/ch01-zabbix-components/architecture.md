---
description: |
    Esta seção do livro The Zabbix Book intitulada "Arquitetura do Zabbix" explica a
    estrutura modular de uma configuração do Zabbix. Ela destaca os papéis de cada componente
    e suas interdependências, enquanto fornece uma introdução sobre como realizaremos a
    instalação dos componentes nas próximas seções.
tags: [beginner]
---

# Arquitetura do Zabbix

Neste capítulo, vamos caminhar pelo processo de instalação do servidor Zabbix.
Existem muitas maneiras diferentes de configurar um servidor Zabbix. Vamos abordar as
configurações mais comuns com MariaDB e PostgreSQL em distribuições baseadas em RHEL,
SLES e Ubuntu.

Antes de começar a instalação, é importante entender a arquitetura do Zabbix.
O servidor Zabbix é estruturado de forma modular, composto por três componentes principais,
que discutiremos em detalhes.

- O servidor Zabbix
- O servidor web Zabbix
- O banco de dados Zabbix

!!! abstract "Criação dos usuários do DB"

    Em nossa configuração criaremos 2 usuários do DB `zabbix-web` e `zabbix-srv`.
    O usuário zabbix-web será usado para o front-end se conectar ao nosso banco de dados Zabbix.
    O usuário zabbix-srv será usado pelo nosso servidor Zabbix para se conectar ao banco de dados.
    Isso nos permite limitar as permissões para cada usuário apenas ao que é estritamente
    necessário.


![overview](ch01.1-basic-installation-zabbixserver.png){ align=left }

_1.1 Instalação básica do Zabbix_
split installation

Todos esses componentes podem ser instalados em um único servidor ou distribuídos
em três servidores separados. O núcleo do sistema é o servidor Zabbix, frequentemente
chamado de "cérebro". Este componente é responsável por processar cálculos de gatilhos e enviar alertas.
O banco de dados serve como armazenamento para a configuração do servidor Zabbix e todos os dados que ele coleta.
O servidor web fornece a interface do usuário (front-end) para interagir com o sistema. É importante notar
que a API do Zabbix faz parte do componente front-end, não do próprio servidor Zabbix.

Esses componentes devem funcionar juntos de forma perfeita, como ilustrado no diagrama acima.
O servidor Zabbix deve ler configurações e armazenar dados de monitoramento no banco de dados,
enquanto o front-end precisa ter acesso para ler e escrever dados de configuração. Além disso,
o front-end deve ser capaz de verificar o status do servidor Zabbix e recuperar informações adicionais necessárias
para garantir um funcionamento suave.

Para nossa configuração, usaremos duas máquinas virtuais (VMs): uma VM hospedará tanto o servidor Zabbix quanto o front-end web Zabbix,
enquanto a segunda VM hospedará o banco de dados Zabbix.

???+ note

    É perfeitamente possível instalar todos os componentes em uma única VM ou cada componente
    em uma VM separada.
    A razão pela qual dividimos o DB no nosso exemplo é porque o banco de dados provavelmente será
    a primeira parte que causará problemas de desempenho. Também é o componente
    que precisa de atenção extra quando o dividimos dos outros componentes,
    por isso escolhemos neste exemplo dividir o banco de dados
    do resto da configuração.

Vamos abordar os seguintes tópicos:

- Instalar nosso Banco de Dados baseado em MariaDB.
- Instalar nosso Banco de Dados baseado em PostgreSQL.
- Instalar o servidor Zabbix.
- Instalar o front-end.