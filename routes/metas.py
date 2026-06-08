# ============================================================
# MÓDULO DE METAS — metas.py
# Desenvolvido por Guilherme
# ============================================================
#
# Gerencia as metas financeiras do usuário logado.
# Uma meta representa um objetivo de economia ou investimento
# com um valor-alvo e um status (Em andamento / Concluída).
#
# Rotas disponíveis:
#   GET  /metas                   → lista todas as metas do usuário
#   GET  /metas/criar             → exibe formulário de criação
#   POST /metas/criar             → salva nova meta no banco
#   GET  /metas/editar/<id>       → exibe formulário de edição
#   POST /metas/editar/<id>       → atualiza meta existente
#   GET  /metas/concluir/<id>     → marca a meta como concluída
# ============================================================

from flask import Blueprint, request, redirect, render_template, flash, session
from services.database import conectar_banco

# Blueprint agrupa todas as rotas deste módulo sob o prefixo /metas
metas_bp = Blueprint('metas', __name__)


# ─────────────────────────────────────────────
# ROTA: GET /metas
# Lista as metas do usuário logado
# ─────────────────────────────────────────────
@metas_bp.route('/metas')
def listar_metas():
    # Rota protegida — redireciona para login se não autenticado
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    # Busca todas as metas do usuário, da mais recente para a mais antiga
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM metas WHERE id_usuario = %s ORDER BY id_meta DESC',
        (id_usuario,)
    )
    metas = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('metas/listar.html', metas=metas)


# ─────────────────────────────────────────────
# ROTA: GET/POST /metas/criar
# Exibe e processa o formulário de nova meta
# ─────────────────────────────────────────────
@metas_bp.route('/metas/criar', methods=['GET', 'POST'])
def criar_meta():
    if request.method == 'POST':
        # Lê os dados do formulário; strip() remove espaços desnecessários
        descricao = request.form['descricao'].strip()
        valor = float(request.form['valor'])

        # Validação: valor da meta não pode ser negativo
        if valor < 0:
            flash('O valor da meta não pode ser negativo.', 'erro')
            return redirect('/metas/criar')

        id_usuario = session.get('id_usuario', 1)

        # Insere a nova meta com status inicial "Em andamento"
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            'INSERT INTO metas (id_usuario, descricao, valor, status) VALUES (%s, %s, %s, %s)',
            (id_usuario, descricao, valor, 'Em andamento')
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Meta criada com sucesso!', 'sucesso')
        return redirect('/metas')

    # GET: apenas exibe o formulário vazio
    return render_template('metas/criar.html')


# ─────────────────────────────────────────────
# ROTA: GET/POST /metas/editar/<id>
# Exibe e processa o formulário de edição de meta
# ─────────────────────────────────────────────
@metas_bp.route('/metas/editar/<int:id_meta>', methods=['GET', 'POST'])
def editar_meta(id_meta):
    id_usuario = session.get('id_usuario', 1)

    # Busca a meta filtrando pelo id_usuario — evita que um usuário
    # edite a meta de outro acessando a URL diretamente
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM metas WHERE id_meta = %s AND id_usuario = %s',
        (id_meta, id_usuario)
    )
    meta = cursor.fetchone()
    cursor.close()
    conexao.close()

    # Se não encontrou (ou pertence a outro usuário), redireciona
    if not meta:
        flash('Meta não encontrada.', 'erro')
        return redirect('/metas')

    if request.method == 'POST':
        descricao = request.form['descricao'].strip()
        valor = float(request.form['valor'])

        # Validação: valor não pode ser negativo
        if valor < 0:
            flash('O valor da meta não pode ser negativo.', 'erro')
            return redirect(f'/metas/editar/{id_meta}')

        # Atualiza a descrição e o valor da meta
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            'UPDATE metas SET descricao=%s, valor=%s WHERE id_meta=%s',
            (descricao, valor, id_meta)
        )
        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Meta atualizada com sucesso!', 'sucesso')
        return redirect('/metas')

    # GET: exibe formulário preenchido com os dados atuais
    return render_template('metas/editar.html', meta=meta)


# ─────────────────────────────────────────────
# ROTA: GET /metas/concluir/<id>
# Marca uma meta como concluída
# ─────────────────────────────────────────────
@metas_bp.route('/metas/concluir/<int:id_meta>')
def concluir_meta(id_meta):
    id_usuario = session.get('id_usuario', 1)

    # Atualiza o status para 'Concluída', garantindo que só o dono pode concluir
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        'UPDATE metas SET status=%s WHERE id_meta=%s AND id_usuario=%s',
        ('Concluída', id_meta, id_usuario)
    )
    conexao.commit()
    cursor.close()
    conexao.close()

    flash('Meta concluída!', 'sucesso')
    return redirect('/metas')
