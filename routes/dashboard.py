# Rotas do dashboard financeiro.
# Desenvolvido por Evelyn. Exibe gráficos e resumo financeiro
# com dados filtrados exclusivamente pelo usuário logado.

from flask import Blueprint, render_template, request, redirect, flash, session
from services.dados_dashboard import (
    obter_resumo, gastos_por_categoria, evolucao_saldo,
    receitas_vs_despesas_mensal, obter_orcamento, definir_orcamento,
)
from services.graficos import grafico_pizza, grafico_barras, grafico_linha, grafico_gauge

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    # Rota protegida — redireciona para login se não autenticado
    if 'id_usuario' not in session:
        return redirect('/')

    uid = session['id_usuario']

    # Busca o resumo financeiro (receita total, despesa total, saldo)
    resumo = obter_resumo(uid)

    # Busca o orçamento mensal definido pelo usuário (padrão 0 se não configurado)
    orcamento = obter_orcamento(uid)

    # Calcula a porcentagem do orçamento já gasta no mês
    perc_orcamento = round(resumo['despesa'] / orcamento * 100, 1) if orcamento > 0 else 0.0

    return render_template(
        'dashboard.html',
        resumo=resumo,
        orcamento=orcamento,
        perc_orcamento=perc_orcamento,
        # Cada função retorna uma string HTML com o gráfico Plotly pronto para injetar no template
        chart_pizza=grafico_pizza(gastos_por_categoria(uid)),
        chart_barras=grafico_barras(receitas_vs_despesas_mensal(uid)),
        chart_linha=grafico_linha(evolucao_saldo(uid)),
        chart_gauge=grafico_gauge(resumo['despesa'], orcamento),
    )


@dashboard_bp.route('/dashboard/orcamento', methods=['POST'])
def atualizar_orcamento():
    # Rota protegida — redireciona para login se não autenticado
    if 'id_usuario' not in session:
        return redirect('/')

    try:
        valor = float(request.form.get('orcamento', 0))
        if valor < 0:
            raise ValueError
        # Salva o novo orçamento vinculado ao usuário logado
        definir_orcamento(valor, session['id_usuario'])
        flash('Orçamento atualizado com sucesso!', 'sucesso')
    except (ValueError, TypeError):
        flash('Valor de orçamento inválido.', 'erro')

    return redirect('/dashboard')
