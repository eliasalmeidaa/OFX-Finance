from flask import Blueprint, request, redirect, flash, render_template, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import Config
from services.leitor_ofx import ler_arquivo_ofx, extrair_transacoes, obter_info_conta
from services.categorizador import categorizar_transacao, determinar_tipo_transacao, CATEGORIAS
from services.salvar_transacoes import salvar_importacao_db, salvar_categoria_db, salvar_transacao_db
from services.database import conectar_banco

importacao_bp = Blueprint('importacao', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@importacao_bp.route('/importar')
def index():
    if 'id_usuario' not in session:
        return redirect('/')
    id_usuario = session['id_usuario']
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute('''
        SELECT i.id_importacao, i.nome_arquivo, i.data_importacao, i.mes_referencia,
               COUNT(t.id_transacao) AS total_transacoes
        FROM importacoes i
        LEFT JOIN transacoes t ON t.id_importacao = i.id_importacao
        WHERE i.id_usuario = %s
        GROUP BY i.id_importacao
        ORDER BY i.data_importacao DESC
        LIMIT 10
    ''', (id_usuario,))
    importacoes = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('index.html', importacoes=importacoes)


@importacao_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('Nenhum arquivo foi enviado.', 'erro')
        return redirect('/importar')

    file = request.files['file']
    if file.filename == '':
        return redirect('/importar')

    filename = secure_filename(file.filename)

    if not allowed_file(filename):
        flash(f'O arquivo "{filename}" não é um OFX válido.', 'erro')
        return redirect('/importar')

    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    id_usuario = session.get('id_usuario', 1)

    try:
        ofx = ler_arquivo_ofx(filepath)
        info_conta = obter_info_conta(ofx)
        transacoes = extrair_transacoes(ofx)

        data_importacao = datetime.now().strftime('%Y-%m-%d')
        mes_referencia = datetime.now().strftime('%Y-%m')

        id_importacao = salvar_importacao_db(
            nome_arquivo=filename,
            data_importacao=data_importacao,
            mes_referencia=mes_referencia,
            id_usuario=id_usuario
        )

        for transacao in transacoes:
            descricao = transacao['descricao']
            valor = transacao['valor']
            tipo = determinar_tipo_transacao(valor)
            categoria_nome = categorizar_transacao(descricao)

            id_categoria = salvar_categoria_db(categoria_nome)
            salvar_transacao_db(
                id_importacao=id_importacao,
                id_categoria=id_categoria,
                descricao=descricao,
                valor=valor,
                data_transacao=transacao['data_transacao'],
                tipo=tipo,
                fitid=transacao['fitid']
            )

        flash(f'Arquivo "{filename}" processado com sucesso!', 'sucesso')

    except Exception as e:
        print(f'[ERRO upload] {e}')
        flash('Erro ao processar o arquivo.', 'erro')

    return redirect('/importar')
