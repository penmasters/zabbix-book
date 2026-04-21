---
description: |
    This chapter from The Zabbix Book, titled "Proxies as Containers," explains
    how to deploy Zabbix proxies using container technologies like Docker or Podman.
    It covers installation, configuration, and networking considerations, showing
    how containerized proxies simplify scaling and management in modern monitoring
    environments.
tags: [expert]
---

# Execução de proxies como contêineres

Conforme discutido na seção anterior, os proxies Zabbix oferecem uma solução
leve e eficiente para o monitoramento distribuído. Aproveitando o SQLite como
banco de dados backend, eles são inerentemente flexíveis e portáteis, o que os
torna adequados para implantação em ambientes de contêineres. Este capítulo
fornece um guia passo a passo sobre a implementação de um proxy Zabbix em um
contêiner, descrevendo as opções de configuração e as práticas recomendadas para
otimizar o desempenho e a manutenção.

---

## Configuração de contêineres

Para essa configuração, você precisará de uma máquina virtual (VM) com o Podman
instalado para implantar o contêiner de proxy do Zabbix. Esse contêiner será
então configurado para se comunicar com o servidor Zabbix.

Consulte o capítulo [_Preparando o sistema para o
Zabbix_](../ch00-getting-started/preparation.md#preparing-the-system-for-running-containers-using-podman)
para obter instruções sobre como preparar o sistema para executar contêineres
usando o Podman.

---

### Adicionar o proxy ao front-end do zabbix

![Adicionar o proxy](ch03-container-proxy-new.png)

_3.9 Adicionar proxy ao frontend_

Para manter a configuração simples, implantaremos um proxy Zabbix ativo. Nesse
caso, apenas dois parâmetros precisam ser configurados: o nome do host do proxy
(conforme definido no front-end do Zabbix) e o endereço IP do proxy para
comunicação com o servidor Zabbix.

---

### Preparar a configuração do proxy

A próxima etapa é criar um arquivo de unidade `.container` para a nossa
configuração do Quadlet. Esse arquivo deve ser colocado no diretório
`~/.config/containers/systemd/`. Por exemplo, criaremos um arquivo chamado
`zabbix-proxy-sqlite.container`, que definirá a configuração para executar o
contêiner do proxy Zabbix no SystemD usando o Podman.

Verifique se você está conectado como usuário `podman`.

!!! info "Mudar para o usuário podman"

    ```bash
    sudo -u podman -i
    ```


Exemplo "Criação de um arquivo de unidade do systemd .container"

    ```bash
    vi ~/.config/containers/systemd/zabbix-proxy-sqlite.container
    ```

    ```ini
    [Unit]
    Description=ZabbixProxy

    [Container]
    Image=docker.io/zabbix/zabbix-proxy-sqlite3:7.0-centos-latest
    ContainerName=ZabbixProxySqlite-Quadlet
    AutoUpdate=registry
    EnvironmentFile=ZabbixProxy.env
    PublishPort=10051:10051

    [Service]
    Restart=always

    [Install]
    WantedBy=default.target
    ```

A imagem do contêiner para o proxy do Zabbix usando o SQLite pode ser obtida no
Docker Hub. Especificamente, usaremos a imagem com a tag 7.0-centos-latest, que
é mantida pelo projeto oficial do Zabbix. Essa imagem pode ser encontrada em:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3/tags?name=centos](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3/tags?name=centos)

Uma lista completa das tags de imagem disponíveis, incluindo diferentes versões
e bases de sistemas operacionais, está disponível na página principal da imagem:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)

Para nossos propósitos, a tag 7.0-centos-latest fornece uma imagem de contêiner
baseada no CentOS que é adequada para ambientes LTS e inclui todos os
componentes necessários para executar o proxy Zabbix com SQLite.

Além do arquivo de unidade `.container`, também precisamos criar um arquivo de
ambiente que defina as variáveis de configuração do contêiner. Esse arquivo deve
residir no mesmo diretório que o arquivo `.container`:
`~/.config/containers/systemd/` e deve ser nomeado `ZabbixProxy.env`, conforme
referenciado em nossa configuração `.container`.

Esse arquivo de ambiente nos permite substituir as configurações padrão do
contêiner especificando as variáveis de ambiente usadas durante o tempo de
execução do contêiner. A lista de variáveis suportadas e suas funções estão
claramente documentadas na página do Docker Hub do contêiner:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)

Essas variáveis permitem configurar parâmetros importantes, como o modo de
proxy, o endereço do servidor, o nome do host, as configurações do banco de
dados e as opções de registro, fornecendo uma maneira flexível e declarativa de
adaptar o comportamento do proxy ao seu ambiente.

Vamos criar o arquivo `~/.config/containers/systemd/ZabbixProxy.env` e adicionar
o seguinte conteúdo.

!!! info "~/.config/containers/systemd/ZabbixProxy.env"

    ```ini
    # Zabbix proxy hostname as it appears in the Zabbix frontend
    ZBX_HOSTNAME=ProxyA

    # IP address or DNS name of the Zabbix server
    ZBX_SERVER_HOST=<DNS or IP>

    # Proxy mode: 0 = active, 1 = passive
    ZBX_PROXYMODE=0
    ```

Com a nossa configuração concluída, a etapa final é recarregar o daemon do
usuário systemd para que ele reconheça a nova unidade Quadlet. Isso pode ser
feito usando o seguinte comando:

!!! info "Recarregar o daemon do usuário SystemD"

    ``` bash
    systemctl --user daemon-reload
    ```

Se tudo estiver configurado corretamente, o systemd gerará automaticamente uma
unidade de serviço para o contêiner com base no arquivo `.container`. Você pode
verificar se a unidade foi registrada verificando a saída de `systemctl --user
list-unit-files`:

???+ exemplo "Verifique se a nova unidade está registrada corretamente"

    ```shell-session
    podman@localhost:~> systemctl --user list-unit-files | grep zabbix
    zabbix-proxy-sqlite.service             generated -
    ```

Agora, você pode iniciar o contêiner usando o comando `systemctl --user start`.
Para iniciar o contêiner, use o seguinte comando (substituindo o nome do serviço
se tiver usado um diferente):

???+ exemplo "Iniciar o contêiner do Zabbix Proxy"

    ```bash
    systemctl --user start zabbix-proxy-sqlite.service
    ```

Esse comando pode levar alguns minutos, pois ele fará o download do contêiner do
Zabbix Proxy necessário a partir do registro do docker.

Para verificar se o contêiner foi iniciado corretamente, você pode inspecionar
os contêineres em execução com:

???+ exemplo "Inspecionar contêineres em execução"

    ```shell-session
    podman@localhost:~> podman ps
    CONTAINER ID  IMAGE                                                   COMMAND               CREATED       STATUS       PORTS                     NAMES
    b5716f8f379d  docker.io/zabbix/zabbix-proxy-sqlite3:7.0-centos-latest /usr/sbin/zabbix_...  2 hours ago   Up 2 hours   0.0.0.0:10051->10051/tcp  ZabbixProxySqlite-Quadlet
    ```

Anote o ID do contêiner `` - neste exemplo, é `b5716f8f379d`. Em seguida, é
possível recuperar os logs do contêiner usando:

???+ Informação "Recuperar registros de contêineres"

    ```bash
    podman logs b5716f8f379d
    ```
    Where `b5716f8f379d` is the `CONTAINER ID` of your container

    On some distributions, you can also view the logs directly through SystemD:
    ```bash
    journalctl --user -u zabbix-proxy-sqlite.service
    ```

Esse comando retornará os registros de inicialização e de tempo de execução do
contêiner, que são úteis para solucionar problemas e verificar se o proxy do
Zabbix foi iniciado corretamente.

---

## Atualizando nossos contêineres

Em algum momento, você pode estar se perguntando: Como faço para atualizar meus
contêineres do Zabbix? Felizmente, as atualizações de contêineres são um
processo simples que pode ser realizado manualmente ou por meio de automação,
dependendo da sua estratégia de implantação.

Ao longo deste livro, usamos a tag de imagem `7.0-centos-latest`, que sempre
extrai a imagem mais atualizada do Zabbix 7.0 baseada no CentOS disponível no
momento. Essa abordagem garante que você esteja executando as últimas correções
e melhorias sem especificar uma versão exata.

Como alternativa, você pode optar por tags específicas de versão, como
`centos-7.0.13`, que permitem manter um controle rigoroso sobre a versão
implantada. Isso pode ser útil em ambientes em que a consistência e a
reprodutibilidade são essenciais.

Nas seções a seguir, exploraremos as duas abordagens: usar a tag `latest` para
atualizações automatizadas e especificar versões fixas para ambientes
controlados.

---

### Atualização manual

Se você estiver executando seu contêiner Zabbix usando uma **tag flutuante** ,
como `:latest` ou `:trunk-centos`, a atualização é um processo simples e
eficiente. Essas tags sempre apontam para a imagem mais recente disponível no
repositório.

???+ info "Para atualizar:"

    ```bash
    # Pull the latest image using Podman.
    podman pull zabbix/zabbix-proxy-sqlite3:7.0-centos-latest
    # Restart the systemd service associated with the container.
    systemctl --user restart zabbix-proxy-sqlite.service
    ```

Graças à nossa integração com o Quadlet, o systemd cuidará do resto
automaticamente: O contêiner em execução no momento será interrompido. Uma nova
instância de contêiner será iniciada usando a imagem recém-obtida. Todas as
opções de configuração definidas no arquivo `.container` associado serão
reaplicadas. Essa abordagem permite atualizações rápidas com o mínimo de esforço
e, ao mesmo tempo, preserva o gerenciamento consistente da configuração por meio
do systemd.

---

### Atualização ao usar uma tag de imagem fixa

Se o seu contêiner estiver configurado para usar uma tag de imagem fixa ****
(por exemplo, `7.0.13-centos`) em vez de uma tag flutuante como `:latest` ou
`:trunk`, o processo de atualização envolve uma etapa adicional: **atualizar
manualmente a tag no arquivo `.container`**.

Por exemplo, se você estiver executando um contêiner Quadlet em nível de usuário
e seu arquivo de configuração estiver localizado em
`~/.config/containers/systemd/zabbix-proxy-sqlite.container`:

???+ exemplo "Atualizando manualmente a tag"

    You'll need to edit this file 
    ```bash
    vi ~/.config/containers/systemd/zabbix-proxy-sqlite.container
    ```

    and update the `Image=` line. For instance, change:

    ```ini
    Image=docker.io/zabbix/zabbix-proxy-sqlite3:7.0.13-centos
    ```

    to:

    ```ini
    Image=docker.io/zabbix/zabbix-proxy-sqlite3:7.0.14-centos
    ```

    Once the file has been updated, apply the changes by running:

    ```bash
    systemctl --user daemon-reload
    systemctl --user restart zabbix-proxy-sqlite.service
    ```

    This tells systemd to reload the modified unit file and restart the container with
    the updated image. Since you're using a fixed tag, this upgrade process gives you
    full control over when and how new versions are introduced.

---

### Atualizando automaticamente

Ao usar tags flutuantes como `:latest` ou `:trunk-centos` para suas imagens de
contêiner do Zabbix, o Podman Quadlet suporta atualizações automatizadas
combinando-as com a diretiva `AutoUpdate=registry` no seu arquivo `.container`.

Essa configuração garante que o seu contêiner seja atualizado automaticamente
sempre que uma nova imagem estiver disponível no registro remoto, sem a
necessidade de intervenção manual.

---

#### Exemplo de configuração

???+ exemplo ".arquivo de contêiner"

    ```ini
    [Container]
    Image=docker.io/zabbix/zabbix-proxy-sqlite3:trunk-centos
    AutoUpdate=registry
    ...
    ```

    In this example, the `Image` points to the `trunk-centos` tag, and `AutoUpdate=registry`
    tells Podman to periodically check the container registry for updates to this tag.

---

#### Como funciona o processo de atualização automática

Uma vez configurado, as etapas a seguir são tratadas automaticamente:

1. **Verificação de imagem** O serviço systemd `podman-auto-update` é acionado
   por um cronômetro (geralmente diário). Ele compara o resumo da imagem atual
   com o resumo da imagem remota para a mesma tag.

2. **Atualização de imagem** Se uma nova versão for detectada:

   - A imagem atualizada é extraída do registro.
   - O contêiner em execução no momento é interrompido e removido.
   - Um novo contêiner é criado a partir da imagem atualizada.

3. **Reutilização de configuração** O novo contêiner é iniciado usando
   exatamente a mesma configuração definida no arquivo `.container`, incluindo
   variáveis de ambiente, montagens de volume, portas e rede.

Essa abordagem fornece uma maneira limpa e repetível de manter o proxy do Zabbix
(ou outros componentes) atualizado sem a intervenção direta do usuário.

---

#### Ativação do cronômetro de atualização automática

Para garantir que as atualizações sejam aplicadas regularmente, você deve ativar
o temporizador de atualização automática do Podman.

!!! info "Para serviços em todo o sistema"

    ```bash
    sudo systemctl enable --now podman-auto-update.timer
    ```

!!! info "Para serviços de nível de usuário"

    ```bash
    systemctl --user enable --now podman-auto-update.timer
    ```

Isso ativa um cronômetro do systemd que invoca periodicamente
`podman-auto-update.service`.

---

### Quando usar essa abordagem

`AutoUpdate=registry` é particularmente útil nos seguintes cenários:

- **Ambientes de desenvolvimento ou preparação**, nos quais a execução da versão
  mais recente é benéfica.
- **Componentes não críticos do Zabbix**, como proxies de teste ou implantações
  de laboratório.
- **Quando você prefere uma estratégia de atualização sem intervenção**, e a
  estabilidade da imagem é confiável.

???+ aviso

    This setup is not recommended for production environments without a proper rollback
    plan. Floating tags like `:latest` or `:trunk-centos` can introduce breaking
    changes unexpectedly. For production use, fixed version tags (e.g. `7.0.13-centos`)
    are generally recommended since they offer greater stability and control.

---

## Conclusão

Neste capítulo, implantamos um proxy ativo Zabbix usando Podman e SystemD
Quadlets. Configuramos o SELinux, ativamos a permanência do usuário e criamos os
arquivos `.container` e `.env` para definir o comportamento do proxy. O uso do
Podman no modo sem raiz garante maior segurança e integração do sistema. O
gerenciamento do SystemD torna o contêiner fácil de controlar e monitorar. Essa
configuração oferece uma abordagem leve, flexível e segura para a implantação de
proxies Zabbix. É ideal para ambientes modernos, especialmente quando se usa
contêineres ou virtualização. Com o proxy em execução, você está pronto para
estender o monitoramento do Zabbix a locais remotos com eficiência.

---

## Perguntas

- Quais são as principais vantagens de usar o Podman em vez do Docker para
  executar contêineres em sistemas baseados no Red Hat?
- Por que o comando `loginctl enable-linger` é importante ao usar o SystemD com
  contêineres Podman sem raiz?
- Qual é a finalidade do arquivo `.env` no contexto de um contêiner gerenciado
  pelo Quadlet?
- Como as políticas do SELinux afetam a execução do contêiner do Podman e como
  você pode configurá-las corretamente?
- Como verificar se o contêiner do proxy Zabbix foi iniciado com sucesso?
- Qual é a diferença entre um proxy Zabbix ativo e passivo?

---

## URLs úteis

- [https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)
- [https://podman.io/](https://podman.io/)
- [https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
- [https://blog.zabbix.com/podman-container-monitoring-with-prometheus-exporter-part-1/30513/](https://blog.zabbix.com/podman-container-monitoring-with-prometheus-exporter-part-1/30513/)
