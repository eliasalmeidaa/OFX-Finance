# Rotas de importação de arquivos OFX.
# Desenvolvido por Gabriel. Recebe o arquivo enviado pelo usuário,
# lê as transações, categoriza cada uma e salva tudo no banco.

from flask import Blueprint, request, redirect, flash, render_template, session
from werkzeug.utils import secure_filename
import os
import traceback
from datetime import datetime
from config import Config
from services.leitor_ofx import ler_arquivo_ofx, ler_arquivo_ofx_stream, extrair_transacoes, obter_info_conta
from services.categorizador import categorizar_transacao, determinar_tipo_transacao, CATEGORIAS
from services.salvar_transacoes import salvar_importacao_db, salvar_categoria_db, salvar_transacao_db
from services.database import conectar_banco

importacao_bp = Blueprint('importacao', __name__)


def allowed_file(filename):
    # Verifica se a extensão do arquivo está na lista de extensões permitidas (.ofx)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@importacao_bp.route('/importar')
def index():
    # Rota protegida — redireciona para login se o usuário não estiver autenticado
    if 'id_usuario' not in session:
        return redirect('/')

    id_usuario = session['id_usuario']

    # Busca os últimos 10 extratos importados pelo usuário para exibir na tabela
    # LEFT JOIN com transacoes para contar quantas transações cada importação gerou
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
    except Exception as e:
        print(f'[ERRO /importar] {traceback.format_exc()}')
        importacoes = []

    return render_template('index.html', importacoes=importacoes)


@importacao_bp.route('/upload', methods=['POST'])
def upload():
    # Verifica se o formulário enviou algum arquivo
    if 'file' not in request.files:
        flash('Nenhum arquivo foi enviado.', 'erro')
        return redirect('/importar')

    file = request.files['file']

    # Nome vazio significa que o usuário não selecionou nenhum arquivo
    if file.filename == '':
        return redirect('/importar')

    # secure_filename remove caracteres perigosos do nome do arquivo
    filename = secure_filename(file.filename)

    # Rejeita arquivos que não sejam .ofx
    if not allowed_file(filename):
        flash(f'O arquivo "{filename}" não é um OFX válido.', 'erro')
        return redirect('/importar')

    id_usuario = session.get('id_usuario', 1)

    try:
        # Lê o OFX diretamente do stream — sem salvar em disco (evita problemas de permissão no servidor)
        ofx = ler_arquivo_ofx_stream(file.stream)
        info_conta = obter_info_conta(ofx)

        # Extrai as transações do extrato como lista de dicionários
        transacoes = extrair_transacoes(ofx)

        data_importacao = datetime.now().strftime('%Y-%m-%d')
        mes_referencia = datetime.now().strftime('%Y-%m')

        # Registra a importação no banco e obtém o ID gerado
        id_importacao = salvar_importacao_db(
            nome_arquivo=filename,
            data_importacao=data_importacao,
            mes_referencia=mes_referencia,
            id_usuario=id_usuario
        )

        # Processa e salva cada transação individualmente
        for transacao in transacoes:
            descricao = transacao['descricao']
            valor = transacao['valor']

            # Define se é Entrada (valor positivo) ou Saída (valor negativo)
            tipo = determinar_tipo_transacao(valor)

            # Tenta identificar a categoria com base nas palavras da descrição
            categoria_nome = categorizar_transacao(descricao)

            # Busca ou cria a categoria no banco e obtém o ID
            id_categoria = salvar_categoria_db(categoria_nome)

            # Salva a transação vinculada à importação e à categoria
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
        print(f'[ERRO upload] {traceback.format_exc()}')
        flash(f'Erro ao processar o arquivo: {e}', 'erro')

    return redirect('/importar')
