# Rotas de autenticação: cadastro, login e logout.
# Desenvolvido por Elias. Usa hash de senha para segurança
# e sessões Flask para manter o usuário logado.

from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from services.database import conectar_banco
import mysql.connector

# Blueprint agrupa todas as rotas de autenticação
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    # Recebe os dados do formulário em formato JSON
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição deve ser JSON'}), 400

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    # Todos os campos são obrigatórios
    if not all([nome, email, senha]):
        return jsonify({'erro': 'nome, email e senha são obrigatórios'}), 400

    # Nunca salvar senha em texto puro — gera um hash seguro
    senha_hash = generate_password_hash(senha)

    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        conexao.commit()
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso'}), 201

    except mysql.connector.IntegrityError:
        # Email duplicado — a coluna email tem constraint UNIQUE no banco
        return jsonify({'erro': 'Email já cadastrado'}), 409

    except Exception as e:
        print(f'[ERRO /cadastro] {e}')
        return jsonify({'erro': 'Erro interno no servidor'}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição deve ser JSON'}), 400

    email = dados.get('email')
    senha = dados.get('senha')

    if not all([email, senha]):
        return jsonify({'erro': 'email e senha são obrigatórios'}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()
        # dictionary=True faz o cursor retornar dicionários (coluna: valor)
        # em vez de tuplas, facilitando o acesso por nome da coluna
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

    except Exception as e:
        print(f'[ERRO /login] {e}')
        return jsonify({'erro': 'Erro interno no servidor'}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    # Verifica se o usuário existe e se a senha confere com o hash salvo
    if usuario and check_password_hash(usuario['senha_hash'], senha):
        # Salva o ID e nome do usuário na sessão para identificá-lo nas próximas requisições
        session['id_usuario'] = usuario['id_usuario']
        session['nome_usuario'] = usuario['nome']

        # Retorna o campo 'redirect' para o JavaScript saber para onde navegar
        return jsonify({
            'mensagem': 'Login realizado com sucesso',
            'id_usuario': usuario['id_usuario'],
            'redirect': '/importar'
        }), 200

    # Resposta genérica — não informa se o email ou a senha está errado por segurança
    return jsonify({'erro': 'Credenciais inválidas'}), 401


@auth_bp.route('/logout')
def logout():
    # Remove todos os dados da sessão, deslogando o usuário
    session.clear()
    # Redireciona para a página de login
    return redirect('/')
