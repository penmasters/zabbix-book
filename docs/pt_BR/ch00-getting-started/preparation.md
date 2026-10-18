---
description: |
    Esta seção do Zabbix Book, intitulada "Preparando o sistema para o Zabbix",
    descreve as etapas preliminares necessárias antes da instalação de qualquer
    componente do Zabbix. Ela inclui instruções para adicionar o repositório
    oficial do Zabbix e preparar o sistema para executar containers com o Podman.
tags: [beginner]
---

# Preparando o sistema para o Zabbix

Antes de instalar qualquer componente do Zabbix, precisamos garantir que o(s)
servidor(es) atenda(m) aos requisitos de configuração descritos na seção
anterior: [Requisitos de sistema](Requirements.md).

Se você pretende instalar o banco de dados, o servidor e/ou o frontend do Zabbix
em máquinas separadas, prepare cada servidor individualmente conforme as
instruções apresentadas aqui. Os servidores que hospedarão um proxy Zabbix
também devem ser preparados da mesma maneira.

---

## Desabilitando o SELinux no RHEL

Ao usar um sistema baseado em Red Hat em um ambiente de teste ou laboratório,
você pode desabilitar o SELinux (temporariamente) para evitar que ele interfira
na instalação e na configuração inicial do Zabbix.

Não desabilite o SELinux em sistemas de produção. Em ambientes de produção, o
SELinux deve permanecer habilitado e no modo enforcing. Consulte a seção sobre
configuração do SELinux no capítulo de configuração avançada e segurança para
obter instruções sobre as políticas necessárias para o Zabbix.

Para verificar o estado atual do SELinux, use o comando `sestatus`.

!!! info "Estado do SELinux"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   enforcing
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

Como mostrado, o sistema está no modo enforcing. Para colocar o SELinux
temporariamente no modo permissive, execute `setenforce 0`.

!!! info "Colocar o SELinux temporariamente no modo permissive"

    ```console
    ~# setenforce 0
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          enforcing
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

O modo agora é permissive. No entanto, essa alteração não persiste após uma
reinicialização. Para torná-la permanente, edite o arquivo de configuração
`/etc/selinux/config` e substitua `enforcing` por `permissive`.

Você também pode obter o mesmo resultado com o seguinte comando:

!!! info "Configurar o SELinux permanentemente no modo permissive"

    Red Hat
    ``` bash
    sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    ```

Essa linha altera o arquivo de configuração. Ao executar `sestatus` novamente,
o modo atual e o modo definido no arquivo de configuração serão permissive.

!!! info "Verificar novamente o estado do SELinux"

    ```console
    ~# sestatus
    SELinux status:                 enabled
    SELinuxfs mount:                /sys/fs/selinux
    SELinux root directory:         /etc/selinux
    Loaded policy name:             targeted
    Current mode:                   permissive
    Mode from config file:          permissive
    Policy MLS status:              enabled
    Policy deny_unknown status:     allowed
    Memory protection checking:     actual (secure)
    Max kernel policy version:      33
    ```

---

## Instalando o repositório do Zabbix

Na página de download do Zabbix
[https://www.zabbix.com/download](https://www.zabbix.com/download), selecione a
versão do Zabbix que deseja instalar. Neste caso, usaremos o Zabbix 8.0 LTS.
Escolha também a distribuição correta: Rocky Linux 9, openSUSE Leap 16 ou
Ubuntu 24.04 em nossos exemplos.

Instalaremos o servidor Zabbix com o NGINX como servidor web do frontend. Baixe
os pacotes correspondentes à configuração escolhida.

![Zabbix Download](./getting-started/ch00.1-getting-started-zabbixdownload.png)

_0.1 Download do Zabbix_

---

### Observações específicas para Red Hat

Se você usa um sistema baseado em RHEL, como o Rocky Linux, primeiro exclua os
pacotes do Zabbix fornecidos pelo repositório EPEL, caso ele esteja instalado.
Edite `/etc/yum.repos.d/epel.repo` e adicione a seguinte diretiva para excluir
esses pacotes por padrão:

!!! info "Excluir pacotes"

    Red Hat
    ``` ini
    [epel]
    ...
    excludepkgs=zabbix*
    ```

???+ tip

    Não é recomendável manter o repositório EPEL sempre habilitado, pois isso
    pode causar conflitos ao substituir pacotes ou instalar pacotes indesejados.
    É mais seguro habilitá-lo apenas quando necessário com o comando
    `dnf install --enablerepo=epel <package-name>`. Assim, o EPEL só será usado
    quando for solicitado explicitamente.

---

### Observações específicas para openSUSE

No openSUSE, os pacotes do Zabbix também estão disponíveis no repositório padrão
`repo-oss`. Diferentemente dos sistemas baseados em RHEL, o openSUSE não oferece
uma forma integrada de excluir pacotes específicos de um repositório. Entretanto,
os pacotes do Zabbix nos repositórios padrão geralmente estão uma ou duas versões
LTS atrás das versões atuais. Portanto, é improvável que interfiram na instalação,
a menos que já estejam instalados.

Na próxima etapa, configuraremos os repositórios oficiais do Zabbix. Desde que
você escolha uma versão do repositório do Zabbix mais recente do que os pacotes
disponíveis no `repo-oss`, o zypper instalará automaticamente a versão mais nova.

???+ tip

    Se você já instalou pacotes do Zabbix dos repositórios padrão, recomendamos:

    - removê-los antes de continuar; ou
    - atualizá-los depois de adicionar os novos repositórios do Zabbix, usando a
      opção `--allow-vendor-change` do zypper.

???+ note "SUSE Linux Enterprise Server (SLES)"

    No SLES, os pacotes do Zabbix não estão incluídos nos repositórios padrão.
    Portanto, você pode adicionar o repositório oficial do Zabbix sem se preocupar
    com conflitos com pacotes existentes.

---

### Adicionando o repositório do Zabbix

Agora instalaremos o repositório do Zabbix no sistema operacional. Depois de
adicioná-lo, recomendamos limpar o cache dos repositórios para remover arquivos
antigos e atualizar os metadados:

!!! info "Adicionar o repositório do Zabbix"

    Red Hat
    ``` bash
    rpm -Uvh https://repo.zabbix.com/zabbix/8.0/release/rocky/9/noarch/zabbix-release-latest-8.0.el9.noarch.rpm
    dnf clean all
    ```

    SUSE
    ``` bash
    rpm -Uvh --nosignature https://repo.zabbix.com/zabbix/8.0/release/sles/16/noarch/zabbix-release-latest-8.0.sles16.noarch.rpm
    zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'

    # Set the repository to auto-refresh to ensure it's always up to date
    zypper modifyrepo --refresh 'Zabbix Official Repository'
    ```

    Ubuntu
    ``` bash
    sudo wget https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo dpkg -i zabbix-release_latest_8.0+ubuntu24.04_all.deb
    sudo apt update
    ```

Esses comandos atualizam os metadados dos repositórios e preparam o sistema para
a instalação do Zabbix.

???+ note "O que é um repositório?"

    No Linux, um repositório é uma configuração que permite acessar e instalar
    pacotes de software. Ele pode ser comparado a uma loja de aplicativos onde
    você encontra e baixa software de uma fonte confiável, neste caso, o
    repositório do Zabbix. Há muitos repositórios disponíveis, mas é importante
    adicionar apenas aqueles em que você confia. A prática mais segura é usar os
    repositórios fornecidos pelo sistema operacional e adicionar outros somente
    quando tiver certeza de que são confiáveis e necessários.

    Em nossa instalação, o repositório do Zabbix é fornecido pelo próprio
    fabricante e, portanto, é uma fonte confiável. Outro repositório popular e
    seguro para sistemas baseados em Red Hat é o EPEL (Extra Packages for
    Enterprise Linux), muito usado em ambientes corporativos. Mesmo assim, tenha
    cuidado ao adicionar novos repositórios para preservar a segurança e a
    estabilidade do sistema.

---

## Preparando o sistema para executar containers com o Podman

Se você pretende executar componentes do Zabbix em containers com o Podman,
verifique se o Podman está instalado e configurado corretamente. As instruções
a seguir mostram como instalá-lo em diferentes sistemas operacionais.

Você pode ignorar esta seção se não pretende executar componentes do Zabbix em
containers no sistema atual.

???+ note "Por que usar o Podman?"

    O Podman é uma ferramenta popular de containerização que permite executar e
    gerenciar containers sem exigir um daemon como o Docker. Ele é o mecanismo
    de containers recomendado na maioria das distribuições modernas e oferece
    várias vantagens em relação ao Docker.

    Primeiro, o Podman melhora a segurança com suporte a containers rootless,
    executados em contas de usuário sem privilégios. Segundo, ele se integra ao
    SELinux, permitindo controle de acesso robusto e aplicação de políticas.
    Terceiro, o Podman funciona nativamente com o systemd, facilitando o
    gerenciamento do ciclo de vida dos containers por meio de unidades systemd
    e Quadlets.

### Instalando o Podman

Para executar containers com o Podman, primeiro instale o Podman e as ferramentas
adicionais necessárias para gerenciá-los com o systemd.

!!! info "Instalar o Podman e as ferramentas necessárias"

    Red Hat
    ```bash
    dnf install podman policycoreutils-python-utils
    ```

    SUSE
    ```bash
    zypper install podman policycoreutils-python-utils
    ```

    Ubuntu
    ```bash
    sudo apt install podman
    ```

### Configurando o Podman para gerenciamento de containers por usuário

Em seguida, crie um usuário `podman` que executará o(s) container(s). Você pode
usar outro nome, como `zabbix-proxy` para um usuário que executará apenas um
proxy Zabbix em um container.

!!! info "Criar e inicializar o usuário do Podman"

    ```bash
    sudo useradd --comment "User for running container workloads" podman
    sudo -i -u podman
    mkdir -p ~/.local/share/containers
    mkdir -p ~/.config/containers/systemd/
    exit
    ```

Quando o SELinux estiver habilitado no sistema, execute o seguinte comando como
`root`.

!!! info "SELinux: definir o mapeamento de contexto dos arquivos"

    ```bash
    semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
    ```

Esse comando adiciona um mapeamento de contexto de arquivos do SELinux criando
uma equivalência (`-e`) entre o diretório de armazenamento padrão dos containers,
`/var/lib/containers`, e o armazenamento do Podman do usuário,
`/home/podman/.local/share/containers`. Assim, o SELinux trata os arquivos no
armazenamento do usuário da mesma forma que os arquivos no armazenamento padrão
do sistema e aplica as permissões corretas de sua política.

!!! info "SELinux: aplicar o mapeamento de contexto dos arquivos"

    ```bash
    restorecon -R -v /home/podman/.local/share/containers
    ```

Depois de definir os novos contextos do SELinux, esse comando aplica
recursivamente (`-R`) os contextos de segurança corretos aos arquivos do
diretório. A opção `-v` habilita a saída detalhada e mostra as alterações. Isso
garante que todos os arquivos no armazenamento dos containers tenham os rótulos
SELinux definidos pelo comando `semanage` anterior.

!!! info "Habilitar a persistência dos processos do usuário"

    ```bash
    loginctl enable-linger podman
    ```

Esse comando habilita o “linger” para o usuário `podman`. Os serviços do usuário,
como containers gerenciados pelo systemd, podem continuar em execução mesmo sem
uma sessão ativa. Assim, proxies em containers e outros serviços permanecem
ativos depois de um logout ou da reinicialização do sistema.

Como etapa final da configuração do Podman, informe ao systemd onde ficam os
arquivos de execução específicos do usuário:

!!! info "Definir XDG_RUNTIME_DIR para o usuário do Podman"

    ```bash
    sudo -u podman -i
    echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile && \
        source ~/.bash_profile
    ```

Essa linha define corretamente a variável de ambiente `XDG_RUNTIME_DIR` para o
usuário `podman` e a carrega na sessão atual e nas próximas sessões. A variável
aponta para os arquivos de execução específicos do usuário, incluindo o
barramento da sessão systemd. Ela é essencial para que `systemctl --user`
funcione corretamente com containers gerenciados pelo Podman.

O sistema agora está preparado para executar componentes do Zabbix em containers
com o Podman.

???+ warning "Problema conhecido ao aguardar network-online.target"

    Se a inicialização dos containers levar cerca de 90 segundos antes de falhar
    e você encontrar linhas semelhantes a estas no log do sistema (`journalctl`):

    ```
    systemd[1601]: Starting Wait for system level network-online.target as user....
    sh[3128]: inactive
    sh[3130]: inactive
    sh[3132]: inactive
    sh[3134]: inactive
    sh[3136]: inactive
    ...
    ...
    sh[3604]: inactive
    sh[3606]: inactive
    systemd[1601]: podman-user-wait-network-online.service: start operation timed out. Terminating.
    systemd[1601]: podman-user-wait-network-online.service: Main process exited, code=killed, status=15/TERM
    systemd[1601]: podman-user-wait-network-online.service: Failed with result 'timeout'.
    systemd[1601]: Failed to start Wait for system level network-online.target as user..
    ```

    você está enfrentando um problema conhecido com o Quadlet:
    [https://github.com/containers/podman/issues/24796](https://github.com/containers/podman/issues/24796).

    Isso ocorre porque o serviço Quadlet gerado pelo systemd contém uma
    dependência da unidade especial `network-online.target`, que normalmente
    indica que a rede do sistema está totalmente operacional. Em determinadas
    distribuições Linux ou configurações de rede, os componentes de rede podem
    não informar corretamente ao systemd que a rede está “online”. Com isso,
    `network-online.target` nunca é ativado e o Podman aguarda até que o tempo
    limite expire, pois considera que a rede ainda não está disponível.

    Como solução alternativa, crie um serviço fictício que acionará
    `network-online.target`:

    ```bash
    vi /etc/systemd/system/podman-network-online-dummy.service
    ```
    ```ini
    [Unit]
    Description=This is a dummy service to activate network-online.target
    After=network-online.target
    Wants=network-online.target

    [Service]
    ExecStart=/usr/bin/echo Activating network-online.target

    [Install]
    WantedBy=multi-user.target
    ```
    ```bash
    systemctl daemon-reload
    systemctl enable --now podman-network-online-dummy.service
    ```

---

## Conclusão

Com a preparação do sistema para o Zabbix concluída, o ambiente está configurado
para a instalação dos componentes do Zabbix. Adicionamos o repositório oficial
do Zabbix e preparamos o sistema para instalar o servidor Zabbix, o banco de
dados e o frontend. Se necessário, também preparamos o sistema para executar
containers com o Podman.

O sistema está pronto para as próximas etapas. No capítulo seguinte, abordaremos
a instalação dos componentes do Zabbix e a configuração do servidor Zabbix, do
banco de dados e do frontend.

---

## Perguntas

- Por que é importante usar o repositório oficial do Zabbix em vez dos pacotes
  fornecidos pela sua distribuição Linux?

- Por que o SELinux deve permanecer habilitado em ambientes de produção e quais
  são as implicações de colocá-lo no modo permissive?

---

## URLs úteis

- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
