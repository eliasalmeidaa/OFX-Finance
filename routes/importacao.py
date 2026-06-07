# Rotas de importação de arquivos OFX.
# Desenvolvido por Gabriel. Recebe o arquivo enviado pelo usuário,
# lê as transações, categoriza cada uma e salva tudo no banco.

from flask import Blueprint, request, redirect, flash, render_template, session
from werkzeug.utils import secure_filename
import os
import io
import traceback
from datetime import datetime
from config import Config
from services.leitor_ofx import ler_arquivo_ofx_stream, extrair_transacoes, obter_info_conta
from services.categorizador import categorizar_transacao, determinar_tipo_transacao
from services.database import conectar_banco
from models.importacao import Importacao
from models.categoria import Categoria
from models.transacao import Transacao

importacao_bp = Blueprint('importacao', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@importacao_bp.route('/importar')
def index():
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    try:
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
    except Exception:
        print(f'[ERRO /importar] {traceback.format_exc()}')
        importacoes = []

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

    id_usuario = session.get('id_usuario', 1)

    try:
        # Lê o arquivo em memória e parseia o OFX
        ofx = ler_arquivo_ofx_stream(io.BytesIO(file.read()))
        transacoes = extrair_transacoes(ofx)

        data_importacao = datetime.now().strftime('%Y-%m-%d')
        mes_referencia = datetime.now().strftime('%Y-%m')

        # Usa UMA única conexão para todo o processo — evita timeout por excesso de conexões no Aiven
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        try:
            # Registra a importação
            id_importacao = Importacao.criar(cursor, id_usuario, filename, data_importacao, mes_referencia)

            # Salva cada transação reutilizando a mesma conexão
            for transacao in transacoes:
                descricao = transacao['descricao']
                valor = transacao['valor']
                tipo = determinar_tipo_transacao(valor)
                categoria_nome = categorizar_transacao(descricao)

                # Busca ou cria categoria
                id_categoria = Categoria.buscar_por_nome(cursor, categoria_nome)
                if id_categoria is None:
                    id_categoria = Categoria.criar(cursor, categoria_nome)

                # Salva transação (ignora duplicatas por fitid)
                try:
                    Transacao.criar(cursor, id_importacao, id_categoria, descricao,
                                    valor, transacao['data_transacao'], tipo, transacao['fitid'])
                except Exception:
                    pass  # fitid duplicado — ignora

            conexao.commit()
            flash(f'Arquivo "{filename}" importado com sucesso! ({len(transacoes)} transações)', 'sucesso')

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    except Exception as e:
        print(f'[ERRO upload] {traceback.format_exc()}')
        flash(f'Erro ao processar o arquivo: {e}', 'erro')

    return redirect('/importar')
