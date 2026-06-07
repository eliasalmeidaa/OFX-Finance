from flask import Blueprint, request, redirect, render_template, flash, session
from datetime import datetime, date
from services.database import conectar_banco

orcamento_bp = Blueprint('orcamento', __name__)


@orcamento_bp.route('/orcamentos')
def historico():
    if 'id_usuario' not in session:
        return redirect('/')
    id_usuario = session['id_usuario']
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


@orcamento_bp.route('/orcamentos/criar', methods=['GET', 'POST'])
def criar_orcamento():
    if request.method == 'POST':
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        valor_previsto = float(request.form['valor'])
        agora = datetime.now()

        if valor_previsto < 0:
            flash('O valor previsto não pode ser negativo.', 'erro')
            return redirect('/orcamentos/criar')

        if ano < agora.year or (ano == agora.year and mes < agora.month):
            flash('Não é possível criar orçamento para mês/ano passado.', 'erro')
            return redirect('/orcamentos/criar')

        id_usuario = session.get('id_usuario', 1)
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

    return render_template('orcamento/criar.html')


@orcamento_bp.route('/orcamentos/editar/<int:id_orcamento>', methods=['GET', 'POST'])
def editar_orcamento(id_orcamento):
    id_usuario = session.get('id_usuario', 1)
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM orcamentos WHERE id_orcamento = %s AND id_usuario = %s',
        (id_orcamento, id_usuario)
    )
    orcamento = cursor.fetchone()
    cursor.close()
    conexao.close()

    if not orcamento:
        flash('Orçamento não encontrado.', 'erro')
        return redirect('/orcamentos')

    if request.method == 'POST':
        mes = int(request.form['mes'])
        ano = int(request.form['ano'])
        valor_previsto = float(request.form['valor'])
        agora = datetime.now()

        if valor_previsto < 0:
            flash('O valor previsto não pode ser negativo.', 'erro')
            return redirect(f'/orcamentos/editar/{id_orcamento}')

        if ano < agora.year or (ano == agora.year and mes < agora.month):
            flash('Não é possível definir mês/ano passado.', 'erro')
            return redirect(f'/orcamentos/editar/{id_orcamento}')

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

    return render_template('orcamento/editar.html', orcamento=orcamento)
