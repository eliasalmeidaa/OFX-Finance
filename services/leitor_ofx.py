# Leitura e extração de dados de arquivos OFX.
# OFX (Open Financial Exchange) é o formato padrão exportado
# por bancos brasileiros como Itaú, Bradesco, Nubank, etc.

from ofxparse import OfxParser


def ler_arquivo_ofx(caminho_arquivo):
    # Abre em modo binário ('rb') pois o OFX pode ter encoding variado entre bancos
    with open(caminho_arquivo, 'rb') as ofx_file:
        ofx = OfxParser.parse(ofx_file)
    return ofx


def extrair_transacoes(ofx):
    # Percorre todas as transações do extrato e converte para dicionários
    conta = ofx.account
    extrato = conta.statement
    transacoes = []

    for transaction in extrato.transactions:
        transacao = {
            # memo é a descrição principal; payee é o nome do estabelecimento — usa o que estiver disponível
            'descricao': transaction.memo or transaction.payee or "Sem descricao",
            'valor': float(transaction.amount),
            # Formato legível para exibição na tela (DD/MM/YYYY)
            'data': transaction.date.strftime('%d/%m/%Y') if transaction.date else 'N/A',
            # Formato padrão SQL para salvar no banco (YYYY-MM-DD)
            'data_transacao': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            # fitid é o ID único da transação dentro do arquivo OFX
            'fitid': getattr(transaction, 'fitid', None)
        }
        transacoes.append(transacao)

    return transacoes


def obter_info_conta(ofx):
    # Retorna informações básicas da conta bancária presente no extrato
    conta = ofx.account
    extrato = conta.statement
    return {
        'banco': conta.institution.organization if conta.institution else 'N/A',
        'conta': conta.account_id,
        'saldo': extrato.balance
    }
