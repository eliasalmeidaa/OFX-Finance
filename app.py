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
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    app.secret_key = Config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    Config.init_app(app)

    # Cria todas as tabelas no banco MySQL do Elias
    criar_tabelas()
    inicializar_categorias(CATEGORIAS)

    # Blueprints de cada integrante
    app.register_blueprint(auth_bp)        # Elias (auth + banco mySQL)
    app.register_blueprint(importacao_bp)  # Gabriel (upload OFX)
    app.register_blueprint(dashboard_bp)   # Gabriel (dashboard)
    app.register_blueprint(orcamento_bp)   # Guilherme (orçamentos)
    app.register_blueprint(metas_bp)       # Guilherme (metas)

    # Página de login do Elias servida como arquivo estático
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
