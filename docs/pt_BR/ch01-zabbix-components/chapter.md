# Componentes do Zabbix, funções básicas e instalação

Nesta seção, expandimos o conhecimento fundamental da seção "Getting Started" para fornecer uma guia abrangente tanto para iniciantes que estão instalando o Zabbix pela primeira vez quanto para usuários avançados que buscam otimizar sua configuração. Não apenas cobriremos os passos essenciais para uma instalação básica, mas também entraremos nos detalhes mais finos da arquitetura do Zabbix, componentes e práticas recomendadas.

Começaremos caminhando pelo processo de instalação, garantindo que você tenha uma base sólida para construir. A partir daí, passaremos pelos componentes principais do Zabbix, o que cada um faz, como eles interagem e por que são cruciais para sua solução de monitoramento.
Você aprenderá sobre subprocessos, seus papéis e como contribuem para a eficiência e confiabilidade do Zabbix.

Além disso, exploraremos escolhas arquiteturais boas que podem fazer ou quebrar sua configuração de monitoramento. Seja gerenciando uma pequena rede ou uma infraestrutura em escala grande, tomar decisões de design corretas desde o início renderá dividendos na escalabilidade, desempenho e manutenção.

Este capítulo é projetado para atender a um amplo espectro de leitores.
Se você está simplesmente procurando colocar o Zabbix no ar, encontrará instruções claras e passo a passo. Para aqueles que querem mergulhar mais fundo, forneceremos insights detalhados sobre como o Zabbix funciona por trás das cortinas, ajudando-o a tomar decisões informadas que se alinhem com suas necessidades e planos de crescimento futuro.

Ao final deste capítulo, você não apenas terá uma instalação do Zabbix funcionando, mas também um entendimento abrangente de seus componentes e arquitetura, permitindo-lhe aproveitar o Zabbix ao máximo, independentemente da complexidade do seu ambiente.

Vamos embarcar nesta jornada detalhada no Zabbix e equipar-nos com o conhecimento para tanto iniciar quanto otimizar uma poderosa solução de monitoramento.

???+ note

    "A partir da versão 7.0, o Zabbix migrou sua licença do GPLv2 para AGPLv3.
    Esta é uma mudança significativa que os usuários e contribuidores devem ter em mente. A adoção
    do AGPLv3 está projetada para fechar a 'brecha da nuvem', garantindo que qualquer entidade
    oferecendo o Zabbix como um serviço hospedado deve contribuir suas modificações de volta à
    comunidade. Embora isso proteja a integridade do projeto e garanta sustentabilidade a longo prazo,
    é uma mudança que as organizações devem revisar para garantir conformidade com suas políticas internas de software livre."