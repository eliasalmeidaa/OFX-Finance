# Relatório Técnico — OFX Finance
### Unificação, Testes e Documentação do Projeto Final

---

## 1. Contexto do Projeto

O projeto OFX Finance foi desenvolvido como trabalho final de grupo na disciplina de Linguagem de Programação. Cada integrante desenvolveu um módulo separado da aplicação em seu próprio ambiente, resultando em quatro aplicações Flask independentes:

- **Elias** — autenticação de usuários (login e cadastro) + banco de dados MySQL
- **Gabriel** — frontend, dashboard com gráficos e visualização de dados
- **Guilherme** — orçamentos e metas financeiras
- **Evelyn** — importação de arquivos OFX

O objetivo desta etapa foi unificar todos os módulos em uma única aplicação funcional, sem reescrever o que já estava funcionando, apenas adaptando e conectando as partes.

---

## 2. Estado Inicial — Problemas Encontrados

Ao analisar os quatro projetos separados, os seguintes problemas foram identificados antes mesmo de qualquer modificação:

### 2.1 Bancos de dados diferentes
Cada integrante usou um banco diferente:
- Gabriel e Evelyn usavam **SQLite** (banco de arquivo local)
- Guilherme armazenava os dados **em memória** (listas Python — dados sumiam ao reiniciar)
- Elias usava **MySQL** com banco `fintrack`

**Decisão:** Usar o banco MySQL do Elias para todos os módulos, pois é o mais robusto e persistente.

### 2.2 Sintaxe incompatível entre SQLite e MySQL
A migração de SQLite para MySQL exigiu ajustes em várias queries:

| SQLite | MySQL |
|---|---|
| `?` (placeholder) | `%s` |
| `AUTOINCREMENT` | `AUTO_INCREMENT` |
| `INSERT OR IGNORE` | `INSERT IGNORE` |
| `INSERT OR REPLACE` | `REPLACE INTO` |
| `strftime('%Y-%m', data)` | `DATE_FORMAT(data, '%Y-%m')` |

### 2.3 Conflito de rotas
Gabriel e Evelyn tinham a rota `/` e `/upload` cada um. Ao unificar, seria impossível registrar dois blueprints com a mesma rota.

**Solução:** A página de importação foi movida para `/importar` e o upload para `/upload` exclusivo do blueprint de importação.

### 2.4 Dados de Guilherme em memória
Os orçamentos e metas eram armazenados em listas Python dentro do código, o que significa que qualquer reinicialização do servidor apagava todos os dados.

**Solução:** Criadas duas novas tabelas no banco MySQL — `orcamentos` e `metas` — com chave estrangeira para `usuarios`.

### 2.5 Emojis no terminal Windows
O arquivo `leitor_ofx.py` original tinha emojis (🔍📖✅) em instruções `print`. O terminal do Windows usa encoding CP1252, que não suporta esses caracteres, causando `UnicodeEncodeError` ao processar qualquer arquivo OFX.

**Solução:** Removidos todos os `print` com emojis do arquivo.

### 2.6 CSS com sintaxe inválida
O arquivo `upload.css` tinha uma regra CSS aninhada dentro de outra — prática que só funciona em pré-processadores como SASS, não em CSS puro:

```css
/* ERRADO */
.upload-area {
    ...
    img { width: 30px; }  /* CSS puro não aceita isso */
}

/* CORRETO */
.upload-area { ... }
.upload-area img { width: 30px; }
```

### 2.7 Caminhos relativos quebrados no HTML estático
A página de login (`static/index.html`) usava caminhos relativos para CSS e JS:
```html
<!-- QUEBRADO ao servir pelo Flask -->
<link rel="stylesheet" href="css/style.css">

<!-- CORRETO -->
<link rel="stylesheet" href="/static/css/style.css">
```

### 2.8 Encoding corrompido no PowerShell
Durante tentativas de substituição em massa de "FinTrack" por "OFX Finance" via PowerShell, o comando `Get-Content | Set-Content` corrompeu os caracteres portugueses (ç, ã, ô). O PowerShell 5.1 lê arquivos como Windows-1252 e salva como UTF-16, corrompendo acentuação.

**Solução:** Todos os arquivos afetados foram reescritos diretamente pela ferramenta de escrita, que preserva UTF-8 corretamente.

---

## 3. Processo de Unificação

### 3.1 Estrutura adotada — Flask Blueprints

A arquitetura escolhida foi o uso de **Blueprints do Flask**, que permite separar as rotas em módulos independentes e registrá-los em um único `app.py`:

```python
app.register_blueprint(auth_bp)       # /login /cadastro /logout
app.register_blueprint(importacao_bp) # /importar /upload
app.register_blueprint(dashboard_bp)  # /dashboard
app.register_blueprint(orcamento_bp)  # /orcamentos
app.register_blueprint(metas_bp)      # /metas
```

Isso permitiu manter o código de cada integrante em seu próprio arquivo, apenas adaptando as incompatibilidades.

### 3.2 Isolamento de dados por usuário

Um problema crítico descoberto durante os testes: o dashboard mostrava os dados de **todos os usuários** misturados. As queries não filtravam por `id_usuario`.

Como a tabela `transacoes` não tem `id_usuario` diretamente (ela pertence a uma `importacao`, que pertence a um `usuario`), o filtro correto exige um JOIN:

```sql
-- ANTES (dados de todos)
SELECT SUM(valor) FROM transacoes WHERE tipo = 'Entrada'

-- DEPOIS (dados só do usuário logado)
SELECT SUM(t.valor) FROM transacoes t
JOIN importacoes i ON t.id_importacao = i.id_importacao
WHERE t.tipo = 'Entrada' AND i.id_usuario = %s
```

Esse ajuste foi aplicado em todas as funções do `dados_dashboard.py`.

### 3.3 Tabela `configuracoes` por usuário

A tabela de configurações (usada para salvar o orçamento mensal do dashboard) não tinha coluna `id_usuario`, o que fazia todos os usuários compartilharem o mesmo valor de orçamento.

**Solução:** Adicionada coluna `id_usuario` e atualizada a chave primária para `(chave, id_usuario)`:

```sql
ALTER TABLE configuracoes ADD COLUMN id_usuario INT NOT NULL DEFAULT 1;
ALTER TABLE configuracoes DROP PRIMARY KEY;
ALTER TABLE configuracoes ADD PRIMARY KEY (chave, id_usuario);
```

### 3.4 Proteção de rotas

Inicialmente, qualquer pessoa podia acessar `/dashboard`, `/importar`, `/orcamentos` e `/metas` sem estar logada. O sistema usava `session.get('id_usuario', 1)` como fallback, o que fazia a aplicação funcionar como se fosse sempre o usuário de ID 1.

**Solução:** Adicionada verificação de sessão em todas as rotas protegidas:

```python
if 'id_usuario' not in session:
    return redirect('/')
```

### 3.5 Rota de logout

O logout original retornava um JSON `{"mensagem": "Logout realizado"}` — comportamento adequado para uma API, mas que deixava o usuário numa tela preta no navegador.

**Solução:** Alterado para redirecionar para a página de login:

```python
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
```

---

## 4. Melhorias de Interface

### 4.1 Identidade visual — OFX Finance
O nome "FinTrack" (nome original de alguns módulos) foi substituído por "OFX Finance" em todos os templates, títulos de página e elementos visuais.

### 4.2 Header padronizado
Cada módulo tinha seu próprio estilo de cabeçalho — alguns com fundo preto, outros sem logo. Foi criado um header único e consistente em todas as páginas:
- Fundo branco com sombra sutil
- Logo "OFX **Finance**" com destaque em azul
- Navegação com botões transparentes e hover azul
- Botão de ação principal em azul sólido
- Ícone de logout (seta saindo de porta) no canto direito, fica vermelho ao passar o mouse

### 4.3 Página de importação com conteúdo
A página `/importar` estava completamente vazia no corpo. Foram adicionados:
- **Estado vazio:** ícone e mensagem orientando o usuário quando nenhum extrato foi importado
- **Tabela de histórico:** lista os últimos 10 extratos importados com nome do arquivo, data, mês de referência e quantidade de transações

### 4.4 Fluxo de autenticação melhorado
- Após **cadastro**: mensagem de sucesso e redirecionamento automático para a aba de login
- Após **login**: redirecionamento direto para o dashboard
- Links "Não tem conta? Cadastre-se" e "Já tem conta? Entrar" adicionados entre as abas

---

## 5. Testes Realizados

Ao final do desenvolvimento, foi criado um script de testes automatizados (`run_tests.py`) que testa a aplicação via HTTP, simulando o comportamento real de um usuário no navegador.

### 5.1 Resultado final: 45/45 testes passaram

| # | Teste | Resultado |
|---|---|---|
| 1-3 | Página de login carrega, contém formulário e título | ✅ |
| 4-5 | Cadastro cria usuário e retorna JSON correto | ✅ |
| 6-7 | Login válido retorna 200 com campo redirect | ✅ |
| 8-9 | Dashboard acessível com sessão e exibe cards | ✅ |
| 10-13 | Rotas protegidas redirecionam para / sem login | ✅ |
| 14-15 | Página de importação carrega com botão | ✅ |
| 16-18 | Upload OFX processa e extrato aparece na lista | ✅ |
| 19-20 | Dashboard mostra dados do extrato importado | ✅ |
| 21-26 | Orçamentos: criar, listar, editar | ✅ |
| 27-34 | Metas: criar, listar, editar, concluir | ✅ |
| 35-37 | Isolamento: usuário 2 não vê dados do usuário 1 | ✅ |
| 38-39 | Logout redireciona e bloqueia acesso (302) | ✅ |
| PROBE-A | Login com senha errada retorna 401 | ✅ |
| PROBE-B | Cadastro com campos vazios retorna 400 | ✅ |
| PROBE-C | Email duplicado retorna 409 | ✅ |
| PROBE-D | Upload de arquivo não-OFX sem erro 500 | ✅ |
| PROBE-E | Orçamento com valor negativo é rejeitado | ✅ |
| PROBE-F | Campo `min=0` no HTML protege contra valores negativos | ✅ |

---

## 6. Aprendizados Técnicos

### Flask Blueprints
Permitem dividir uma aplicação Flask em módulos independentes. Cada blueprint tem suas próprias rotas, e todos são registrados em um `app.py` central. Ideal para projetos em equipe onde cada pessoa desenvolve um módulo.

### MySQL vs SQLite
SQLite é excelente para desenvolvimento individual por não precisar de instalação, mas MySQL é necessário quando há múltiplos usuários simultâneos ou quando o projeto será implantado em servidor. A migração exige atenção às diferenças de sintaxe nas queries.

### Sessions no Flask
A sessão Flask é baseada em cookies criptografados. Quando o servidor é reiniciado, todos os cookies de sessão são invalidados (pois dependem da `SECRET_KEY` para descriptografar). Por isso é fundamental ter proteção de rotas — sem ela, um usuário com sessão expirada continua acessando dados sem saber de qual usuário são.

### Isolamento de dados
Em qualquer aplicação multi-usuário, todas as queries devem filtrar por `id_usuario`. Um erro comum é esquecer tabelas intermediárias — neste projeto, `transacoes` não tem `id_usuario` diretamente, mas pertence a `importacoes` que pertence a `usuarios`. O JOIN é obrigatório.

### Encoding no Windows
O Windows usa CP1252 por padrão no terminal e PowerShell 5.1 tem comportamento inconsistente com UTF-8. Ao manipular arquivos com caracteres portugueses programaticamente, é necessário garantir que a leitura e escrita usem o mesmo encoding (preferencialmente UTF-8 explícito).

### Testes automatizados via HTTP
Testar uma aplicação web via `requests.Session()` em Python permite simular sessões de usuário reais, incluindo cookies, redirecionamentos e autenticação. É mais confiável do que testar funções isoladas porque testa o fluxo completo — rota → lógica → banco → resposta.

---

## 7. Arquivos Sensíveis

O arquivo `.env` contém as credenciais do banco de dados e **não foi versionado** (está no `.gitignore`). Cada desenvolvedor deve criar o seu próprio com as credenciais do MySQL local:

```
SECRET_KEY=chave_secreta_123
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=fintrack
```

---

*Relatório gerado ao final do desenvolvimento do projeto OFX Finance — Junho de 2026.*
