class Categoria:
    @staticmethod
    def buscar_por_nome(cursor, nome_categoria):
        cursor.execute(
            'SELECT id_categoria FROM categorias WHERE nome_categoria = %s',
            (nome_categoria,)
        )
        resultado = cursor.fetchone()
        return resultado['id_categoria'] if resultado else None

    @staticmethod
    def criar(cursor, nome_categoria):
        cursor.execute(
            'INSERT INTO categorias (nome_categoria) VALUES (%s)',
            (nome_categoria,)
        )
        return cursor.lastrowid
