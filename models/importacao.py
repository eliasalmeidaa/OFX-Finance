class Importacao:
    @staticmethod
    def criar(cursor, id_usuario, nome_arquivo, data_importacao, mes_referencia):
        cursor.execute('''
            INSERT INTO importacoes
            (id_usuario, nome_arquivo, data_importacao, mes_referencia)
            VALUES (%s, %s, %s, %s)
        ''', (id_usuario, nome_arquivo, data_importacao, mes_referencia))
        return cursor.lastrowid
