import mysql.connector
from config import Config


def conectar_banco():
    params = dict(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
    if Config.DB_SSL:
        params['ssl_disabled'] = False
        params['ssl_verify_cert'] = False
        params['ssl_verify_identity'] = False
    return mysql.connector.connect(**params)


def criar_tabelas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Tabela de usuários (Elias)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL
        )
    ''')

    # Tabela de categorias (Gabriel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nome_categoria VARCHAR(255) NOT NULL UNIQUE
        )
    ''')

    # Tabela de importações OFX (Gabriel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS importacoes (
            id_importacao INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            nome_arquivo VARCHAR(255) NOT NULL,
            data_importacao DATE NOT NULL,
            mes_referencia VARCHAR(7),
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')

    # Tabela de transações (Gabriel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id_transacao INT AUTO_INCREMENT PRIMARY KEY,
            id_importacao INT NOT NULL,
            id_categoria INT,
            descricao TEXT,
            valor DECIMAL(10,2) NOT NULL,
            data_transacao DATE,
            tipo VARCHAR(10) NOT NULL,
            fitid VARCHAR(255),
            FOREIGN KEY (id_importacao) REFERENCES importacoes(id_importacao),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    ''')

    # Tabela de configurações chave/valor por usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave VARCHAR(255) NOT NULL,
            valor TEXT NOT NULL,
            id_usuario INT NOT NULL DEFAULT 1,
            PRIMARY KEY (chave, id_usuario)
        )
    ''')

    # Tabela de orçamentos mensais (Guilherme - antes era em memória)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id_orcamento INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            mes INT NOT NULL,
            ano INT NOT NULL,
            valor_previsto DECIMAL(10,2) NOT NULL,
            data_criacao DATE NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')

    # Tabela de metas financeiras (Guilherme - antes era em memória)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metas (
            id_meta INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Em andamento',
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')

    conexao.commit()
    cursor.close()
    conexao.close()


def inicializar_categorias(categorias_dict):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    categorias_padrao = list(categorias_dict.keys()) + ['Outros']

    for nome in categorias_padrao:
        cursor.execute(
            'INSERT IGNORE INTO categorias (nome_categoria) VALUES (%s)',
            (nome,)
        )

    conexao.commit()
    cursor.close()
    conexao.close()
