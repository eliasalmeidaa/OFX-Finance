# Sistema de categorização automática de transações


def determinar_tipo_transacao(valor): #Retorna 'Entrada' se valor positivo, 'Saída' se negativo.

    if valor > 0:
        return 'Entrada'
    else:
        return 'Saída'


# Dicionário de categorias com palavras-chave
# Cada categoria tem uma lista de palavras que, se encontradas na descrição,
# atribuem essa categoria à transação

CATEGORIAS = {
    # ENTRADAS
    'Salário': ['salario', 'salário', 'pagamento salario', 'folha'],
    'Extras': ['bonus', 'bônus', 'comissao', 'comissão', 'adicional', 'extra'],
    'Rendimentos': ['rendimento', 'dividendo', 'juros sobre capital', 'renda'],
    
    # SAÍDAS - ESSENCIAIS
    'Moradia': ['aluguel', 'financiamento', 'condominio', 'condomínio', 'iptu'],
    'Contas Fixas': ['telefone', 'telsp', 'celul', 'celular', 'vivo', 'tim', 'claro', 'oi', 'streaming', 'luz', 'agua', 'água', 'gas', 'gás', 'internet', 'netflix', 'spotify', 'tv', 'fatura', 'boleto', 'assinatura'],
    'Transferências': ['transferência', 'transferencia', 'pix', 'ted', 'doc'],
    'Supermercado': ['supermercado', 'mercado', 'extra', 'pao de acucar', 'pão de açúcar', 'carrefour', 'atacadao', 'atacadão', 'shibata', 'rossi', 'açai atacadista', 'açaí atacadista', 'compras'],
    'Saúde': ['farmacia', 'farmácia', 'droga', 'consulta', 'medico', 'médico', 'plano de saude', 'plano de saúde', 'hospital', 'clinica', 'clínica'],
    'Transporte': ['uber', '99 taxi', '99 pop', '99 moto', 'cabify', 'combustivel', 'combustível', 'posto', 'estacionamento', 'pedagio', 'pedágio', 'onibus', 'ônibus', 'metro', 'metrô'],
    
    # SAÍDAS - VARIÁVEIS
    'Educação': ['curso', 'livro', 'faculdade', 'universidade', 'escola', 'material escolar', 'udemy', 'alura'],
    'Lazer e Entretenimento': ['restaurante', 'cinema', 'bar', 'show', 'ifood', 'rappi', 'pizza', 'hamburger', 'hambúrguer', 'cafe', 'ingresso', 'cinema', 'café'],
    'Viagens e Turismo': ['hotel', 'passagem', 'hospedagem', 'airbnb', 'booking', 'gol', 'latam', 'azul'],
    'Cuidados Pessoais': ['salao', 'salão', 'barbearia', 'vestuario', 'vestuário', 'roupa', 'calcado', 'calçado', 'cosmetico', 'cosmético'],
}


def categorizar_transacao(descricao): #  Recebe a descrição da transação e retorna a categoria correspondente.
    #Se não encontrar match, retorna 'Outros'.

    if not descricao:
        return 'Outros'
    
    # Converte para minúsculo para comparação 
    descricao_lower = descricao.lower()
    
    # Percorre cada categoria e suas palavras-chave
    for categoria, palavras_chave in CATEGORIAS.items():
        # a variável categoria recebe o nome da categoria 
        # e palavras_chave recebe a lista de palavras daquela categoria
        for palavra in palavras_chave:
            if palavra in descricao_lower:
                return categoria
    
    # Se não encontrou nenhuma palavra-chave
    return 'Outros'