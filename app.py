# Arquivo principal da aplicação OFX Finance.
# Responsável por criar e configurar o app Flask,
# registrar todos os blueprints e inicializar o banco de dados.

import traceback
from flask import Flask, send_from_directory
from config import Config
from services.database import criar_tabelas, inicializar_categorias
from services.categorizador import CATEGORIAS
from routes.auth import auth_bp
from routes.importacao import importacao_bp
from routes.dashboard import dashboard_bp
from routes.orcamento import orcamento_bp
from routes.metas import metas_bp


def create_app():
    # Cria a instância do Flask apontando a pasta 'static' para arquivos públicos (CSS, JS, imagens)
    app = Flask(__name__, static_url_path='/static', static_folder='static')

    # Chave secreta usada para assinar os cookies de sessão (login do usuário)
    app.secret_key = Config.SECRET_KEY

    # Pasta onde os arquivos OFX enviados pelo usuário serão salvos temporariamente
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

    # Cria a pasta de uploads se não existir
    Config.init_app(app)

    # Cria todas as tabelas no banco MySQL (não recria se já existirem)
    criar_tabelas()

    # Insere as categorias padrão no banco (ex: Salário, Moradia, Transporte...)
    inicializar_categorias(CATEGORIAS)

    # Registra os blueprints — cada blueprint é um módulo com suas rotas
    app.register_blueprint(auth_bp)        # Elias: /cadastro /login /logout
    app.register_blueprint(importacao_bp)  # Gabriel: /importar /upload
    app.register_blueprint(dashboard_bp)   # Evelyn: /dashboard
    app.register_blueprint(orcamento_bp)   # Guilherme: /orcamentos
    app.register_blueprint(metas_bp)       # Guilherme: /metas

    # Rota raiz ('/') serve a página de login (arquivo HTML estático do Elias)
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    # Loga o traceback completo de qualquer erro 500 nos logs do Render
    @app.errorhandler(500)
    def erro_interno(e):
        print(f'[500 TRACEBACK]\n{traceback.format_exc()}')
        return 'Internal Server Error', 500

    return app


# Cria o app para ser usado pelo servidor Flask
app = create_app()

if __name__ == '__main__':
    # Inicia o servidor em modo debug na porta 5000
    # debug=True recarrega automaticamente ao salvar arquivos
    app.run(debug=True, port=5000)
