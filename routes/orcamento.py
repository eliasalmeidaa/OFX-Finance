# ============================================================
# MÓDULO DE ORÇAMENTOS — orcamento.py
# Desenvolvido por Guilherme
# ============================================================
#
# Gerencia os orçamentos mensais do usuário logado.
# Um orçamento define quanto o usuário planeja gastar em um mês/ano.
#
# Rotas disponíveis:
#   GET  /orcamentos              → lista todos os orçamentos do usuário
#   GET  /orcamentos/criar        → exibe formulário de criação
#   POST /orcamentos/criar        → salva novo orçamento no banco
#   GET  /orcamentos/editar/<id>  → exibe formulário de edição
#   POST /orcamentos/editar/<id>  → atualiza orçamento existente
# ============================================================

from flask import Blueprint, request, redirect, render_template, flash, session
from datetime import datetime, date
from services.database import conectar_banco

# Blueprint agrupa todas as rotas deste módulo sob o prefixo /orcamentos
orcamento_bp = Blueprint('orcamento', __name__)


# ─────────────────────────────────────────────
# ROTA: GET /orcamentos
# Lista os orçamentos do usuário logado
# ─────────────────────────────────────────────
@orcamento_bp.route('/orcamentos')
def historico():
    # Rota protegida — redireciona para login se não autenticado
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    # Busca todos os orçamentos do usuário, ordenados do mais recente para o mais antigo
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM orcamentos WHERE id_usuario = %s ORDER BY ano DESC, mes DESC',
        (id_usuario,)
    )
    orcamentos = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('orcamento/historico.html', orcamentos=orcamentos)


# ─────────────────────────────────────────────
# ROTA: GET/POST /orcamentos/criar
# Exibe e processa o formulário de novo orçamento
# ─────────────────────────────────────────────
@orcamento_bp.route('/orcamentos/criar', methods=['GET', 'POST'])
def criar_orcamento():
    if request.method == 'POST':
        # Lê os dados enviados pelo formulário HTML
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        valor_previsto = float(request.form['valor'])
        agora = datetime.now()

        # Validação: valor não pode ser negativo
        if valor_previsto < 0:
            flash('O valor previsto não pode ser negativo.', 'erro')
            return redirect('/orcamentos/criar')

        # Validação: não permite criar orçamento para mês/ano já passado
        if ano < agora.year or (ano == agora.year and mes < agora.month):
            flash('Não é possível criar orçamento para mês/ano passado.', 'erro')
            return redirect('/orcamentos/criar')

        id_usuario = session.get('id_usuario', 1)

        # Insere o novo orçamento vinculado ao usuário logado
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            '''INSERT INTO orcamentos (id_usuario, mes, ano, valor_previsto, data_criacao)
               VALUES (%s, %s, %s, %s, %s)''',
            (id_usuario, mes, ano, valor_previsto, date.today())
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Orçamento criado com sucesso!', 'sucesso')
        return redirect('/orcamentos')

    # GET: apenas exibe o formulário vazio
    return render_template('orcamento/criar.html')


# ─────────────────────────────────────────────
# ROTA: GET/POST /orcamentos/editar/<id>
# Exibe e processa o formulário de edição
# ─────────────────────────────────────────────
@orcamento_bp.route('/orcamentos/editar/<int:id_orcamento>', methods=['GET', 'POST'])
def editar_orcamento(id_orcamento):
    id_usuario = session.get('id_usuario', 1)

    # Busca o orçamento filtrando também pelo id_usuario — evita que um usuário
    # edite o orçamento de outro usuário acessando a URL diretamente
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM orcamentos WHERE id_orcamento = %s AND id_usuario = %s',
        (id_orcamento, id_usuario)
    )
    orcamento = cursor.fetchone()
    cursor.close()
    conexao.close()

    # Se não encontrou (ou pertence a outro usuário), redireciona
    if not orcamento:
        flash('Orçamento não encontrado.', 'erro')
        return redirect('/orcamentos')

    if request.method == 'POST':
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        valor_previsto = float(request.form['valor'])
        agora = datetime.now()

        # Mesmas validações do criar
        if valor_previsto < 0:
            flash('O valor previsto não pode ser negativo.', 'erro')
            return redirect(f'/orcamentos/editar/{id_orcamento}')

        if ano < agora.year or (ano == agora.year and mes < agora.month):
            flash('Não é possível definir mês/ano passado.', 'erro')
            return redirect(f'/orcamentos/editar/{id_orcamento}')

        # Atualiza os campos do orçamento
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            'UPDATE orcamentos SET mes=%s, ano=%s, valor_previsto=%s WHERE id_orcamento=%s',
            (mes, ano, valor_previsto, id_orcamento)
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Orçamento atualizado com sucesso!', 'sucesso')
        return redirect('/orcamentos')

    # GET: exibe o formulário preenchido com os dados atuais
    return render_template('orcamento/editar.html', orcamento=orcamento)
