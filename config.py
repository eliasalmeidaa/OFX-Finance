# Configurações centrais da aplicação.
# Todas as variáveis sensíveis (senha do banco, chave secreta) são lidas
# do arquivo .env para não ficarem expostas no código-fonte.

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente do Python
load_dotenv()

class Config:
    # Chave usada para criptografar os cookies de sessão do Flask
    # Se não encontrar no .env, usa um valor padrão (apenas para desenvolvimento local)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave_secreta_123')

    # Usa /tmp no Linux (Render) e 'uploads' localmente no Windows
    UPLOAD_FOLDER = '/tmp/uploads' if os.name == 'posix' else 'uploads'

    # Apenas arquivos com extensão .ofx são aceitos no upload
    ALLOWED_EXTENSIONS = {'ofx'}

    # Credenciais do banco de dados MySQL (lidas do .env)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'fintrack')

    # SSL é obrigatório quando o banco está hospedado online (ex: Aiven)
    DB_SSL = os.environ.get('DB_SSL', 'false').lower() == 'true'

    @staticmethod
    def init_app(app):
        # Garante que a pasta de uploads existe antes de o servidor iniciar
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
