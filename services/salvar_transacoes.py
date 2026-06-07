from models.categoria import Categoria
from models.importacao import Importacao
from models.transacao import Transacao
from services.database import conectar_banco


def salvar_importacao_db(nome_arquivo, data_importacao, mes_referencia, id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        id_importacao = Importacao.criar(cursor, id_usuario, nome_arquivo, data_importacao, mes_referencia)
        conexao.commit()
        return id_importacao
    finally:
        cursor.close()
        conexao.close()


def salvar_categoria_db(nome_categoria):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        id_categoria = Categoria.buscar_por_nome(cursor, nome_categoria)
        if id_categoria is None:
            id_categoria = Categoria.criar(cursor, nome_categoria)
            conexao.commit()
        return id_categoria
    finally:
        cursor.close()
        conexao.close()


def salvar_transacao_db(id_importacao, id_categoria, descricao, valor, data_transacao, tipo, fitid):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        Transacao.criar(cursor, id_importacao, id_categoria, descricao, valor, data_transacao, tipo, fitid)
        conexao.commit()
    except Exception as e:
        print(f'[ERRO salvar_transacao] {e}')
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()
