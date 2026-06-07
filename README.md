# OFX Finance

Aplicação web para gestão financeira pessoal desenvolvida em Python/Flask. Permite importar extratos bancários no formato OFX, visualizar gastos em dashboards interativos, definir orçamentos mensais e acompanhar metas financeiras.

## Funcionalidades

- **Autenticação** — cadastro e login com senha criptografada, sessões isoladas por usuário
- **Importação OFX** — upload de extratos bancários com categorização automática das transações
- **Dashboard** — gráficos de gastos por categoria, receitas x despesas, evolução do saldo e gauge de orçamento
- **Orçamentos** — definição de limite de gastos por mês/ano
- **Metas** — criação e acompanhamento de metas financeiras com status de conclusão

## Tecnologias

- Python 3 + Flask
- MySQL (mysql-connector-python)
- Plotly.js (gráficos)
- HTML/CSS puro (sem frameworks)
- ofxparse (leitura de arquivos OFX)

## Estrutura

```
app_unificado/
├── app.py                  # Inicialização e registro dos blueprints
├── config.py               # Configurações (lê do .env)
├── routes/                 # Blueprints Flask
│   ├── auth.py             # /cadastro /login /logout
│   ├── importacao.py       # /importar /upload
│   ├── dashboard.py        # /dashboard
│   ├── orcamento.py        # /orcamentos
│   └── metas.py            # /metas
├── services/               # Lógica de negócio
│   ├── database.py         # Conexão MySQL e criação de tabelas
│   ├── dados_dashboard.py  # Queries do dashboard
│   ├── leitor_ofx.py       # Parser de arquivos OFX
│   ├── categorizador.py    # Categorização automática
│   ├── salvar_transacoes.py
│   └── graficos.py
├── templates/              # HTML (Jinja2)
├── static/                 # CSS, JS, imagens
└── teste_extrato.ofx       # Arquivo OFX de exemplo
```

## Como rodar

### 1. Pré-requisitos

- Python 3.10+
- MySQL rodando localmente com um banco chamado `fintrack`

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto. As credenciais do banco compartilhado serão enviadas pelo Elias no grupo:

```
SECRET_KEY=chave_secreta_123
DB_HOST=<host enviado pelo Elias>
DB_PORT=<porta enviada pelo Elias>
DB_USER=avnadmin
DB_PASSWORD=<senha enviada pelo Elias>
DB_NAME=defaultdb
DB_SSL=true
```

> O banco está hospedado online (Aiven) e é compartilhado por todos os integrantes. Não precisa instalar MySQL localmente.

### 4. Rodar a aplicação

```bash
python app.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

As tabelas são criadas automaticamente na primeira execução.

## Teste rápido

Use o arquivo `teste_extrato.ofx` incluído no repositório para testar a importação. Ele contém 15 transações fictícias de maio/2026 com categorias variadas (salário, aluguel, supermercado, transporte, etc).

## Integrantes

| Nome | Módulo |
|---|---|
| Elias | Autenticação + banco de dados e Frontend |
| Gabriel | Dashboard + gráficos e frontend|
| Guilherme | Orçamentos e metas |
| Evelyn | Importação OFX + categorização |
