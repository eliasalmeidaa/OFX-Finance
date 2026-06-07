# Conexão com o banco de dados MySQL e criação das tabelas.
# Todas as tabelas são criadas automaticamente na primeira execução —
# não é necessário rodar nenhum SQL manualmente.

import mysql.connector
from config import Config


def conectar_banco():
    # Monta os parâmetros de conexão a partir das configurações do .env
    params = dict(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )

    # SSL é obrigatório para bancos hospedados online (ex: Aiven)
    # ssl_verify_cert=False aceita o certificado sem validar a cadeia de CA
    if Config.DB_SSL:
        params['ssl_disabled'] = False
        params['ssl_verify_cert'] = False
        params['ssl_verify_identity'] = False

    return mysql.connector.connect(**params)


def criar_tabelas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Tabela de usuários — armazena as contas cadastradas no sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de categorias — ex: Salário, Moradia, Transporte
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nome_categoria VARCHAR(255) NOT NULL UNIQUE
        )
    ''')

    # Tabela de importações — registra cada arquivo OFX enviado por um usuário
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

    # Tabela de transações — cada linha do extrato OFX vira uma transação aqui
    # fitid é o ID único da transação no arquivo OFX, usado para evitar duplicatas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id_transacao INT AUTO_INCREMENT PRIMARY KEY,
            id_importacao INT NOT NULL,
            id_categoria INT,
            descricao TEXT,
            valor DECIMAL(10,2) NOT NULL,
            data_transacao DATE,
            tipo VARCHAR(10),
            fitid VARCHAR(255),
            FOREIGN KEY (id_importacao) REFERENCES importacoes(id_importacao),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    ''')

    # Tabela de configurações por usuário — armazena o orçamento mensal do dashboard
    # Chave primária composta (chave + id_usuario) para que cada usuário tenha seu próprio valor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave VARCHAR(255) NOT NULL,
            valor TEXT NOT NULL,
            id_usuario INT NOT NULL DEFAULT 1,
            PRIMARY KEY (chave, id_usuario)
        )
    ''')

    # Tabela de orçamentos mensais — limites de gasto definidos por mês/ano
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id_orcamento INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            mes INT NOT NULL,
            ano INT NOT NULL,
            valor_previsto DECIMAL(10,2) NOT NULL,
            data_criacao DATE,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')

    # Tabela de metas financeiras — objetivos de economia ou investimento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metas (
            id_meta INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            descricao VARCHAR(255) NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'Em andamento',
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')

    conexao.commit()
    cursor.close()
    conexao.close()


def inicializar_categorias(categorias_dict):
    # Insere as categorias padrão definidas em categorizador.py
    # INSERT IGNORE ignora silenciosamente se a categoria já existir (evita erros na segunda execução)
    conexao = conectar_banco()
    cursor = conexao.cursor()
    for nome in categorias_dict:
        cursor.execute(
            "INSERT IGNORE INTO categorias (nome_categoria) VALUES (%s)",
            (nome,)
        )
    # Categorias extras que não estão no dicionário principal de palavras-chave
    cursor.execute("INSERT IGNORE INTO categorias (nome_categoria) VALUES ('Outros')")
    conexao.commit()
    cursor.close()
    conexao.close()
