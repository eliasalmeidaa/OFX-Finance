from services.database import conectar_banco


def obter_resumo(id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(t.valor), 0) AS total
            FROM transacoes t
            JOIN importacoes i ON t.id_importacao = i.id_importacao
            WHERE t.tipo = 'Entrada' AND i.id_usuario = %s
        """, (id_usuario,))
        receita = float(cursor.fetchone()['total'])

        cursor.execute("""
            SELECT COALESCE(SUM(ABS(t.valor)), 0) AS total
            FROM transacoes t
            JOIN importacoes i ON t.id_importacao = i.id_importacao
            WHERE t.tipo = 'Saída' AND i.id_usuario = %s
        """, (id_usuario,))
        despesa = float(cursor.fetchone()['total'])

        return {'receita': receita, 'despesa': despesa, 'saldo': receita - despesa}
    finally:
        cursor.close()
        conexao.close()


def gastos_por_categoria(id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.nome_categoria AS categoria, COALESCE(SUM(ABS(t.valor)), 0) AS total
            FROM transacoes t
            JOIN importacoes i ON t.id_importacao = i.id_importacao
            JOIN categorias c ON t.id_categoria = c.id_categoria
            WHERE t.tipo = 'Saída' AND i.id_usuario = %s
            GROUP BY c.nome_categoria
            HAVING total > 0
            ORDER BY total DESC
        """, (id_usuario,))
        return [{'categoria': r['categoria'], 'total': float(r['total'])} for r in cursor.fetchall()]
    finally:
        cursor.close()
        conexao.close()


def evolucao_saldo(id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT t.data_transacao, SUM(t.valor) AS total_dia
            FROM transacoes t
            JOIN importacoes i ON t.id_importacao = i.id_importacao
            WHERE t.data_transacao IS NOT NULL AND i.id_usuario = %s
            GROUP BY t.data_transacao
            ORDER BY t.data_transacao
        """, (id_usuario,))
        datas, saldos, acumulado = [], [], 0.0
        for row in cursor.fetchall():
            acumulado += float(row['total_dia'])
            datas.append(str(row['data_transacao']))
            saldos.append(round(acumulado, 2))
        return {'datas': datas, 'saldos': saldos}
    finally:
        cursor.close()
        conexao.close()


def receitas_vs_despesas_mensal(id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DATE_FORMAT(t.data_transacao, '%Y-%m') AS mes, t.tipo, SUM(ABS(t.valor)) AS total
            FROM transacoes t
            JOIN importacoes i ON t.id_importacao = i.id_importacao
            WHERE t.data_transacao IS NOT NULL AND i.id_usuario = %s
            GROUP BY mes, t.tipo
            ORDER BY mes
        """, (id_usuario,))
        rows = cursor.fetchall()
        meses = sorted({r['mes'] for r in rows if r['mes']})
        receitas, despesas = [], []
        for mes in meses:
            receitas.append(next(
                (float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Entrada'),
                0.0
            ))
            despesas.append(next(
                (float(r['total']) for r in rows if r['mes'] == mes and r['tipo'] == 'Saída'),
                0.0
            ))
        return {'meses': meses, 'receitas': receitas, 'despesas': despesas}
    finally:
        cursor.close()
        conexao.close()


def obter_orcamento(id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT valor FROM configuracoes WHERE chave = 'orcamento_mensal' AND id_usuario = %s",
            (id_usuario,)
        )
        row = cursor.fetchone()
        return float(row['valor']) if row else 0.0
    finally:
        cursor.close()
        conexao.close()


def definir_orcamento(valor, id_usuario):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "REPLACE INTO configuracoes (chave, valor, id_usuario) VALUES ('orcamento_mensal', %s, %s)",
            (str(valor), id_usuario)
        )
        conexao.commit()
    finally:
        cursor.close()
        conexao.close()
