class Transacao:
    @staticmethod
    def criar(cursor, id_importacao, id_categoria, descricao, valor,
              data_transacao, tipo, fitid):
        cursor.execute('''
            INSERT INTO transacoes
            (id_importacao, id_categoria, descricao, valor,
             data_transacao, tipo, fitid)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (id_importacao, id_categoria, descricao, valor,
              data_transacao, tipo, fitid))
