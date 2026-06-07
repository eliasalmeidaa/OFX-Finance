# Funções responsáveis por persistir os dados do OFX no banco de dados.
# Cada função abre sua própria conexão e a fecha ao final (padrão seguro para Flask).

from models.categoria import Categoria
from models.importacao import Importacao
from models.transacao import Transacao
from services.database import conectar_banco


def salvar_importacao_db(nome_arquivo, data_importacao, mes_referencia, id_usuario):
    # Registra o arquivo OFX como uma importação vinculada ao usuário
    # Retorna o ID gerado para ser usado ao salvar as transações
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
    # Busca a categoria pelo nome; se não existir, cria uma nova
    # Garante que não haverá categorias duplicadas no banco
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
    # Salva uma transação individual no banco
    # Em caso de erro (ex: fitid duplicado), faz rollback para não deixar dados inconsistentes
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
