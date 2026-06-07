from flask import Blueprint, request, redirect, render_template, flash, session
from services.database import conectar_banco

metas_bp = Blueprint('metas', __name__)


@metas_bp.route('/metas')
def listar_metas():
    if 'id_usuario' not in session:
        return redirect('/')
    id_usuario = session['id_usuario']
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


@metas_bp.route('/metas/criar', methods=['GET', 'POST'])
def criar_meta():
    if request.method == 'POST':
        descricao = request.form['descricao'].strip()
        valor = float(request.form['valor'])

        if valor < 0:
            flash('O valor da meta não pode ser negativo.', 'erro')
            return redirect('/metas/criar')

        id_usuario = session.get('id_usuario', 1)
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

    return render_template('metas/criar.html')


@metas_bp.route('/metas/editar/<int:id_meta>', methods=['GET', 'POST'])
def editar_meta(id_meta):
    id_usuario = session.get('id_usuario', 1)
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM metas WHERE id_meta = %s AND id_usuario = %s',
        (id_meta, id_usuario)
    )
    meta = cursor.fetchone()
    cursor.close()
    conexao.close()

    if not meta:
        flash('Meta não encontrada.', 'erro')
        return redirect('/metas')

    if request.method == 'POST':
        descricao = request.form['descricao'].strip()
        valor = float(request.form['valor'])

        if valor < 0:
            flash('O valor da meta não pode ser negativo.', 'erro')
            return redirect(f'/metas/editar/{id_meta}')

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

    return render_template('metas/editar.html', meta=meta)


@metas_bp.route('/metas/concluir/<int:id_meta>')
def concluir_meta(id_meta):
    id_usuario = session.get('id_usuario', 1)
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
