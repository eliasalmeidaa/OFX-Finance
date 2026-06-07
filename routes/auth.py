from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from services.database import conectar_banco
import mysql.connector

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição deve ser JSON'}), 400

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not all([nome, email, senha]):
        return jsonify({'erro': 'nome, email e senha são obrigatórios'}), 400

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

    if usuario and check_password_hash(usuario['senha_hash'], senha):
        session['id_usuario'] = usuario['id_usuario']
        session['nome_usuario'] = usuario['nome']
        # redirect sinalizado ao JS via campo 'redirect'
        return jsonify({
            'mensagem': 'Login realizado com sucesso',
            'id_usuario': usuario['id_usuario'],
            'redirect': '/importar'
        }), 200

    return jsonify({'erro': 'Credenciais inválidas'}), 401


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
