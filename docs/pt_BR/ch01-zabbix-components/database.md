---
description: |
  Esta seção do livro The Zabbix Book intitulada "Escolhas de banco de dados" ajuda você a selecionar o backend e os pacotes de banco de dados adequados para sua instalação do Zabbix.
tags: [beginner]
---

# Escolhas de Banco de Dados

## Escolhendo um Backend de Banco de Dados para o Zabbix

Uma decisão crítica ao gerenciar instalações do Zabbix é a escolha do backend de banco de dados. O Zabbix suporta várias opções de banco de dados: MySQL/Percona, MariaDB, PostgreSQL (incluindo TimescaleDB) e Oracle (até o Zabbix 7.0).

???+ warning "Depreciação do Oracle Database"

    A versão 7.0 do Zabbix marca a última versão que oferece suporte ao Oracle Database.
    Consequentemente, sistemas executando o Zabbix 7.0 ou qualquer versão anterior devem realizar uma migração de banco de dados para PostgreSQL, MySQL ou um fork compatível como MariaDB antes de atualizar para uma versão posterior do Zabbix. Esta migração é um passo obrigatório para garantir a funcionalidade contínua e a compatibilidade com futuras versões do Zabbix.

Todos os bancos de dados suportados desempenham-se semelhantemente sob cargas típicas do Zabbix, e o Zabbix trata todos igualmente em termos de funcionalidades. Portanto, a escolha depende principalmente da familiaridade com um sistema de banco de dados específico por parte você ou sua equipe.
Uma exceção notável é o TimescaleDB, uma extensão PostgreSQL otimizada para dados de séries temporais. Isso torna-o especialmente bem adequado para aplicações de monitoramento como o Zabbix, que lidam com grandes volumes de dados com marcação temporal.

Em ambientes em grande escala com coleta de dados de alta frequência, o TimescaleDB pode oferecer benefícios significativos de desempenho, incluindo velocidades de consulta melhoradas e compressão embutida para reduzir as necessidades de armazenamento. No entanto, essas vantagens vêm com uma complexidade adicional durante a instalação e algumas restrições na retenção de dados históricos.

???+ tip "Instalação do TimescaleDB"

    Dada sua natureza avançada, o TimescaleDB não é essencial para a maioria dos usuários do Zabbix.
    Como tal, sua instalação está além do escopo deste capítulo. Se você planeja usar o TimescaleDB, consulte [Particionamento do PostgreSQL com TimescaleDB](../ch13-advanced-security/partitioning-postgresql-database.md) para orientações detalhadas após a instalação do PostgreSQL.

---

## Escolhendo a Fonte de Instalação do Banco de Dados

Neste capítulo focaremos na instalação do MariaDB e do PostgreSQL, já que eles são os bancos de dados mais comumente usados com o Zabbix. Para instalações do MySQL ou Percona, exceto pelos comandos de instalação de pacotes, os passos são muito semelhantes ao MariaDB.

Ao instalar o MariaDB ou PostgreSQL, você deve determinar a fonte da qual deseja instalar o servidor de banco de dados. Duas opções principais estão disponíveis:

1. **Pacotes fornecidos pelo fornecedor do sistema operacional**

:   Esses pacotes são incluídos nos repositórios de software de quase todas as distribuições Linux e são mantidos pelo fornecedor da distribuição.

    **Vantagens:**

    - **Instalação simplificada:** Os pacotes estão disponíveis via o gerenciador de pacotes da distribuição.
    - **Suporte do fornecedor:** Para distribuições empresariais (por exemplo, RHEL, SLES), assinaturas ativas incluem suporte oficial.
    - **Compatibilidade:** Integração garantida com outros pacotes e dependências do sistema.
      - **Otimizações específicas da distribuição:** Inclui configurações personalizadas (por exemplo, logrotate, bash completion,...).
      - **Manutenção a longo prazo:** Correções de segurança e bugs são retroportados pelo fornecedor durante o ciclo de vida de suporte da distribuição.

    **Desvantagens:**

      - **Travamento na versão:** Atualizações major das distribuições podem introduzir automaticamente novas versões do banco de dados, potencialmente exigindo verificações de compatibilidade com o Zabbix.
      - **Modificações do fornecedor:** Configurações padrão, diretórios de log e caminhos de dados podem ser alterados para se alinhar com os padrões específicos da distribuição.

2. **Repositórios oficiais MariaDB/PostgreSQL**

:   Esses repositórios oferecem pacotes diretamente do MariaDB/PostgreSQL e fornecem acesso às últimas versões estáveis.

    **Vantagens:**

    - **Versões atualizadas:** Acesso imediato a recursos mais recentes, patches de segurança e correções de bugs. No entanto, certifique-se de que o Zabbix é compatível com a versão escolhida.
    - **Suporte empresarial:** Opção para adquirir MariaDB Enterprise ou Enterprise DB respectivamente, que incluem suporte profissional e recursos adicionais.

    **Desvantagens:**

    - **Gerenciamento manual de versões:** Os usuários devem monitorar proativamente e atualizar para novas versões principais para garantir cobertura contínua de segurança e correções de bugs.

???+ warning "Compatibilidade da versão do banco de dados"

    Seja que você planeje usar os pacotes fornecidos pelo provedor do sistema operacional ou os pacotes oficiais do fornecedor do banco de dados, certifique-se de que a versão do banco de dados é compatível com sua versão do Zabbix para evitar possíveis problemas de integração.
    Verifique o [https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software](https://www.zabbix.com/documentation/current/en/manual/installation/requirements#required-software) para as versões mais recentes suportadas.

Antes de instalar o software do banco de dados, certifique-se de que o servidor atende aos requisitos de configuração e está preparado conforme descrito no capítulo anterior: [_Getting started_](../ch00-getting-started/Requirements.md).

---

## Conclusão

Discutimos os vários backends de banco de dados suportados pelo Zabbix. Também examinamos as vantagens e desvantagens do uso de pacotes fornecidos pelo provedor versus repositórios oficiais para a instalação do MariaDB e PostgreSQL.

Com esse conhecimento, você está agora pronto para proceder com a instalação do backend de banco de dados escolhido. Nos capítulos seguintes, guiaremos você através do processo de instalação do MariaDB ou PostgreSQL, garantindo que sua instância Zabbix esteja equipada com um sistema de banco de dados robusto e eficiente.

Agora que você tem uma compreensão clara das opções de banco de dados disponíveis, vamos prosseguir para a instalação do backend de banco de dados preferido.

---

## Perguntas

1. Devo escolher MySQL ou PostgreSQL como o backend de banco de dados? Por quê?
2. Devo usar os pacotes fornecidos pelo provedor do sistema operacional, ou devo instalar pacotes oficiais do fornecedor do banco de dados? Por quê?

---

## URLs Úteis

- [https://mariadb.org](https://mariadb.org)
- [https://mariadb.com](https://mariadb.com)
- [https://www.mysql.com](https://www.mysql.com)
- [https://www.percona.com](https://www.percona.com)
- [https://www.postgresql.org](https://www.postgresql.org)
- [https://www.tigerdata.com/timescaledb](https://www.tigerdata.com/timescaledb)
- [https://www.enterprisedb.com](https://www.enterprisedb.com)
- [https://www.zabbix.com/documentation/current/en/manual/installation/requirements](https://www.zabbix.com/documentation/current/en/manual/installation/requirements)
