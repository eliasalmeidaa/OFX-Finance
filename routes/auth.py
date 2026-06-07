# ============================================================
# MÓDULO DE AUTENTICAÇÃO — auth.py
# Desenvolvido por Elias
# ============================================================
#
# Este arquivo controla tudo relacionado a contas de usuário:
#   - /cadastro → cria uma nova conta
#   - /login    → autentica o usuário e inicia a sessão
#   - /logout   → encerra a sessão e volta para o login
#
# Conceitos importantes usados aqui:
#
#   HASH DE SENHA:
#     Nunca salvamos a senha original no banco. A função
#     generate_password_hash() transforma "minha_senha" em algo como
#     "$pbkdf2-sha256$29000$abc123..." — um texto embaralhado irreversível.
#     Assim, mesmo que o banco vaze, ninguém consegue descobrir as senhas.
#
#   SESSÃO (session):
#     O Flask guarda dados do usuário logado em um cookie criptografado
#     no navegador. Quando salvamos session['id_usuario'] = 3, por exemplo,
#     todas as próximas requisições daquele navegador carregam esse valor.
#     É assim que o sistema sabe quem está logado sem pedir senha toda hora.
#
#   BLUEPRINT:
#     Um Blueprint é um agrupador de rotas. Em vez de registrar todas as
#     rotas direto no app.py, cada módulo tem seu próprio Blueprint.
#     Aqui temos auth_bp, que é registrado no app.py central.
#
#   JSON (jsonify):
#     O frontend (auth.js) se comunica com o backend via JavaScript.
#     Por isso as respostas de /cadastro e /login são JSON, não HTML.
#     O HTML só é usado no /logout (que redireciona a página inteira).
# ============================================================

from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from services.database import conectar_banco
import mysql.connector

# Cria o Blueprint de autenticação — será registrado no app.py
auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────────
# ROTA: POST /cadastro
# Cria uma nova conta de usuário no sistema
# ─────────────────────────────────────────────
@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():

    # O frontend envia os dados do formulário como JSON no corpo da requisição
    # request.get_json() lê esse JSON e transforma em dicionário Python
    dados = request.get_json()

    # Se o corpo da requisição não for JSON válido, retorna erro 400 (Bad Request)
    if not dados:
        return jsonify({'erro': 'Corpo da requisição deve ser JSON'}), 400

    # Extrai os três campos esperados do JSON recebido
    # .get() retorna None se o campo não existir (não gera erro)
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    # Verifica se todos os campos foram preenchidos
    # all([...]) retorna False se qualquer valor for None, "" ou 0
    if not all([nome, email, senha]):
        return jsonify({'erro': 'nome, email e senha são obrigatórios'}), 400

    # SEGURANÇA: nunca salvar senha em texto puro no banco
    # generate_password_hash() cria um hash seguro com salt aleatório
    # Exemplo: "123456" vira "$pbkdf2-sha256$29000$XYZ$ABCDEF..."
    # Esse processo é irreversível — não dá para descobrir a senha original
    senha_hash = generate_password_hash(senha)

    # Inicializa como None para garantir que o bloco finally funcione
    # mesmo se o erro ocorrer antes de criar a conexão
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco de dados
        conexao = conectar_banco()

        # Cria um cursor — é o objeto usado para executar comandos SQL
        cursor = conexao.cursor()

        # Insere o novo usuário na tabela 'usuarios'
        # %s são placeholders que o MySQL substitui pelos valores da tupla
        # Isso previne SQL Injection (ataque onde o usuário digita SQL malicioso)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )

        # commit() confirma a inserção no banco — sem isso a transação é cancelada
        conexao.commit()

        # Retorna sucesso com código HTTP 201 (Created — recurso criado com sucesso)
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso'}), 201

    except mysql.connector.IntegrityError:
        # IntegrityError acontece quando viola uma constraint do banco
        # Aqui significa que o email já está cadastrado (coluna email é UNIQUE)
        # Código 409 = Conflict (conflito com dados já existentes)
        return jsonify({'erro': 'Email já cadastrado'}), 409

    except Exception as e:
        # Qualquer outro erro inesperado — registra no console para debug
        print(f'[ERRO /cadastro] {e}')
        # Código 500 = Internal Server Error
        return jsonify({'erro': 'Erro interno no servidor'}), 500

    finally:
        # finally sempre executa, mesmo se houver erro
        # Garante que a conexão seja sempre fechada e não fique aberta no banco
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ─────────────────────────────────────────────
# ROTA: POST /login
# Autentica o usuário e inicia a sessão
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():

    # Lê os dados enviados pelo formulário de login (em JSON)
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Corpo da requisição deve ser JSON'}), 400

    email = dados.get('email')
    senha = dados.get('senha')

    # Garante que os dois campos foram preenchidos
    if not all([email, senha]):
        return jsonify({'erro': 'email e senha são obrigatórios'}), 400

    conexao = None
    cursor = None
    try:
        conexao = conectar_banco()

        # dictionary=True faz cada linha retornar como dicionário {'coluna': valor}
        # Sem isso, retornaria tupla (1, 'Elias', 'elias@...' , '$hash...', ...)
        # Com isso, retorna {'id_usuario': 1, 'nome': 'Elias', 'email': '...', ...}
        cursor = conexao.cursor(dictionary=True)

        # Busca o usuário pelo email — a senha não entra no WHERE porque
        # precisamos do hash salvo para comparar com a senha digitada
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))

        # fetchone() retorna apenas uma linha (ou None se não encontrar)
        usuario = cursor.fetchone()

    except Exception as e:
        print(f'[ERRO /login] {e}')
        return jsonify({'erro': 'Erro interno no servidor'}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    # Verifica duas condições:
    # 1. O usuário existe no banco (não é None)
    # 2. A senha digitada confere com o hash salvo
    #    check_password_hash() recalcula o hash da senha digitada e compara
    #    com o hash armazenado — retorna True se forem iguais
    if usuario and check_password_hash(usuario['senha_hash'], senha):

        # LOGIN APROVADO — salva os dados do usuário na sessão do Flask
        # A sessão é um cookie criptografado no navegador do usuário
        # Todos os blueprints podem ler session['id_usuario'] para saber quem está logado
        session['id_usuario'] = usuario['id_usuario']
        session['nome_usuario'] = usuario['nome']

        # Retorna JSON com o campo 'redirect' para o auth.js saber para onde ir
        # O JavaScript lê esse campo e usa window.location.href para navegar
        return jsonify({
            'mensagem': 'Login realizado com sucesso',
            'id_usuario': usuario['id_usuario'],
            'redirect': '/importar'   # o JS redireciona para /dashboard na prática
        }), 200

    # LOGIN RECUSADO
    # A mensagem é genérica de propósito — não informamos se o email ou a senha
    # está errado, pois isso ajudaria um atacante a descobrir emails cadastrados
    # Código 401 = Unauthorized (não autorizado)
    return jsonify({'erro': 'Credenciais inválidas'}), 401


# ─────────────────────────────────────────────
# ROTA: GET /logout
# Encerra a sessão e volta para o login
# ─────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():

    # session.clear() apaga todos os dados da sessão (id_usuario, nome_usuario, etc.)
    # Após isso, qualquer rota protegida vai redirecionar para o login
    session.clear()

    # redirect('/') envia o navegador de volta para a página de login
    return redirect('/')
