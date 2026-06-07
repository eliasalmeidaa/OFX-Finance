# Este arquivo cria os gráficos do dashboard usando a biblioteca Plotly.
# Cada função recebe dados do banco e retorna uma string HTML pronta para
# ser injetada diretamente no template dashboard.html.

import plotly.graph_objects as Caio  # alias não-convencional mantido por convenção do projeto

# Mensagem padrão exibida no lugar do gráfico quando não há dados no banco
SEM_DADOS = '<p class="sem-dados">Nenhuma transação importada ainda.</p>'


def grafico_pizza(dados_categorias):
    """Gráfico de rosca (donut) com os gastos divididos por categoria."""

    # Se a lista de categorias estiver vazia, exibe a mensagem padrão no lugar do gráfico
    if not dados_categorias:
        return SEM_DADOS

    # Separa os dados em duas listas: nomes das categorias e seus valores totais
    categorias = []
    valores = []
    for auxiliar in dados_categorias:
        categorias.append(auxiliar['categoria'])
        valores.append(auxiliar['total'])

    # Cria o gráfico de pizza com os dados separados acima
    # labels = fatias com nome, values = tamanho de cada fatia
    # hole=0.4 transforma o pie em donut; 0 = pizza sólida, 1 = anel invisível
    fig = Caio.Figure(Caio.Pie(labels=categorias, values=valores, hole=0.4))

    # Define a altura do gráfico em pixels
    fig.update_layout(height=500)

    # Converte o gráfico para HTML puro para ser injetado no template
    # full_html=False: não gera <html><body>, só o <div> do gráfico
    # include_plotlyjs=False: não embute a biblioteca Plotly no HTML gerado —
    # ela já é carregada via CDN no <head> do dashboard.html
    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_barras(dados_mensais):
    """Gráfico de barras agrupadas comparando receitas e despesas por mês."""

    # Se não houver lista de meses, não há dados para exibir
    if not dados_mensais.get('meses'):
        return SEM_DADOS

    # Cria o gráfico com duas séries de barras: uma para receitas (verde) e outra para despesas (vermelho)
    # x = eixo horizontal (meses), y = eixo vertical (valores em R$)
    fig = Caio.Figure([
        Caio.Bar(name='Receitas', x=dados_mensais['meses'], y=dados_mensais['receitas'], marker_color='#22c55e'),
        Caio.Bar(name='Despesas', x=dados_mensais['meses'], y=dados_mensais['despesas'], marker_color='#ef4444'),
    ])

    # barmode='group' coloca as barras lado a lado (em vez de empilhadas)
    fig.update_layout(height=500, barmode='group')

    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_linha(dados_saldo):
    """Gráfico de linha mostrando a evolução do saldo ao longo do tempo."""

    # Se não houver datas, não há dados para exibir
    if not dados_saldo.get('datas'):
        return SEM_DADOS

    # Scatter com mode='lines+markers' desenha a linha e os pontos em cada data
    fig = Caio.Figure(Caio.Scatter(
        x=dados_saldo['datas'],    # eixo X: datas das transações
        y=dados_saldo['saldos'],   # eixo Y: saldo acumulado em cada data
        mode='lines+markers',      # exibe tanto a linha quanto os pontos
        fill='tozeroy',            # preenche a área entre a linha e o eixo Y=0
    ))

    # Altura menor porque este gráfico ocupa a seção mais larga da tela
    fig.update_layout(height=320)

    return fig.to_html(full_html=False, include_plotlyjs=False)


def grafico_gauge(despesa_total, orcamento):
    """Gauge (velocímetro) que mostra o quanto do orçamento mensal já foi gasto."""

    # Define o valor máximo da escala do gauge
    # Multiplica por 1.5 para que o ponteiro nunca fique no limite máximo do arco
    # O mínimo de 100 evita escala zerada quando não há dados
    maximo = max(orcamento * 1.5, despesa_total * 1.5, 100)

    fig = Caio.Figure(Caio.Indicator(
        mode='gauge+number',       # exibe o arco do gauge + o número atual
        value=despesa_total,       # valor do ponteiro: total gasto no mês
        number=dict(prefix='R$ '), # formata o número exibido com prefixo monetário
        gauge=dict(
            axis=dict(range=[0, maximo]),   # escala do arco: de 0 até o máximo calculado
            bar=dict(color='#0055ff'),       # cor da barra que indica o valor atual
            threshold=dict(
                # linha vertical que marca o limite do orçamento no gauge
                line=dict(color='black', width=3),
                value=orcamento,  # posição da linha = valor do orçamento definido
            ),
        ),
    ))

    # Altura menor pois o gauge divide espaço com o formulário de orçamento
    fig.update_layout(height=250)

    return fig.to_html(full_html=False, include_plotlyjs=False)
