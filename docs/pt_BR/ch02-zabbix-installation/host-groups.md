---
description: |
    This chapter from The Zabbix Book, titled "Host Groups," explains how to organize
    and manage monitored hosts effectively in Zabbix. It covers the creation of
    host groups, their role in permission management, and how they simplify large
    environments by structuring hosts for better visibility and control.
tags: [beginner]
---

# Grupos de hospedagem

No Zabbix, os **grupos de hosts** servem como um mecanismo fundamental para
organizar as entidades monitoradas. Eles permitem que você categorize
logicamente os hosts para facilitar o gerenciamento, simplificar as permissões e
agilizar a configuração, o que é especialmente útil em ambientes maiores.

Exemplos comuns incluem:

- Agrupamento de todos os servidores **Linux**.
- Separação de **servidores de banco de dados** (por exemplo, PostgreSQL,
  MySQL).
- Organização de hosts por **equipe**, **local**, ou **função**.

Os grupos de hosts não servem apenas para estruturar os hosts monitorados, eles
também desempenham um papel importante na atribuição de modelos, na configuração
de permissões de usuário e na filtragem de hosts em painéis ou mapas.

## Acesso a grupos de hosts

Você pode gerenciar grupos de hosts navegando até:

**Menu → Coleta de dados → Grupos de hosts**

![Captura de tela do menu Grupos de hosts](ch02-host-grouops.png)

_2.19 Menu Grupos de hosts_

Nesse menu, em `Coleta de dados`, você verá duas seções distintas:

- **Grupos de hosts**: Grupos que contêm hosts.
- **Grupos de modelos**: Uma adição mais recente, criada especificamente para
  organizar modelos.

???+ info "Migrando de uma versão anterior do Zabbix"

    In previous versions, templates and hosts were often placed in the same groups.
    This led to confusion, particularly for new users, as templates don't technically
    belong to host groups in Zabbix. As of recent versions (starting from Zabbix
    6.x), template groups are separated out for better clarity.

## Entendendo a visão geral dos grupos de hosts

Ao abrir o menu **Host groups**, você verá uma lista de grupos predefinidos.
Cada entrada de grupo inclui:

- **Nome do grupo** (por exemplo, `Servidores Linux`)
- **Número de hosts** no grupo (exibido como um número na frente)
- **Nomes de host** atualmente atribuídos a esse grupo

Ao clicar no nome de um host, você será levado diretamente à tela de
configuração do host, o que proporciona uma maneira conveniente de gerenciar as
configurações sem precisar navegar por vários menus.

## Criação de um grupo de hosts

Há duas maneiras principais de criar grupos de hosts:

### 1. Durante a criação do host

Ao adicionar um novo host:

1. Acesse **Coleta de dados → Hosts**.
2. Clique em **Create host** (canto superior direito).
3. No campo **Host groups**, selecione um grupo existente ou digite um novo nome
   para criar um na hora.

### 2. Na página Grupos de hosts

1. Navegue até **Data collection → Host groups**.
2. Clique em **Create host group** no canto superior direito.
3. Digite um **nome de grupo** e clique em **Add**.

![Criar novo grupo de hosts](ch02-new-host-group.png)

_2.20 Criar novos grupos de hosts_

## Grupos de hosts aninhados

O Zabbix suporta **grupos de hosts aninhados** usando barras (`/`) nos nomes dos
grupos. Isso permite que você represente hierarquias como:

- `Europa/Bélgica`
- `Europa/França`
- `Centros de dados/EUA/Chicago`

Esses nomes de grupos aninhados são **apenas nomes** O Zabbix não exige que as
pastas pai (por exemplo, `Europa`) existam fisicamente como grupos separados, a
menos que você os crie explicitamente.

???+ aviso

    - You cannot escape the `/` character.
    - Group names **cannot** contain leading/trailing slashes or multiple consecutive
      slashes.
    - `/` is reserved for nesting and cannot be used in regular group names.

## Applying Permissions and Tag Filters to Nested Groups

Once you've created nested groups, the **Host group overview** screen provides
an option to apply permissions and tag filters to all subgroups:

1. Click on a parent group (e.g., `Europe`).
2. A box appears: **Apply permissions and tag filters to all subgroups**.
3. Enabling this will cascade any rights assigned to the parent group down to
   its subgroups.

![Apply subgroup permissions](ch02-sub-groups.png)

_2.21 subgroup permissions_

This is especially useful for user groups. For example:

- If **Brian** is in a user group with access to `Europe/Belgium`, enabling this
  option allows Brian to see all hosts in subgroups like `Europe/Belgium/Gent`
  or `Europe/Belgium/Brussels`, including their tags and data.

## Best Practices

- Use a consistent naming convention: `Location/Function`, `Team/Environment`,
  etc.
- Assign hosts to **multiple groups** if they logically belong in more than one.
- Avoid overly deep nesting keep it readable and manageable.
- Regularly review group usage and clean up unused or outdated groups.

???+ tip

    You can even try adding **emojis** to group names for a fun visual touch! 🎉
    For example: `🌍 Europe/🇧🇪 Belgium` or `📦 Containers/Docker`.

## Conclusão

Host groups are a key organizational tool in Zabbix. With the introduction of
**template groups**, clearer group separation, and support for **nested
structures**, modern versions of Zabbix offer great flexibility for tailoring
your monitoring setup to your organization's structure and workflows.

## Perguntas

- What are host groups used for in Zabbix?
- Can you assign a host to more than one group?
- How are nested groups created in Zabbix?
- What happens when you apply permissions to subgroups?
- Why are slashes (/) special in host group names?
- Can a parent group exist only logically (i.e., not created in Zabbix)?

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual/config/hosts/host_groups](https://www.zabbix.com/documentation/current/en/manual/config/hosts/host_groups)
