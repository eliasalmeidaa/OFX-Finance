from ofxparse import OfxParser


def ler_arquivo_ofx(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as ofx_file:
        ofx = OfxParser.parse(ofx_file)
    return ofx


def extrair_transacoes(ofx):
    conta = ofx.account
    extrato = conta.statement
    transacoes = []

    for transaction in extrato.transactions:
        transacao = {
            'descricao': transaction.memo or transaction.payee or "Sem descricao",
            'valor': float(transaction.amount),
            'data': transaction.date.strftime('%d/%m/%Y') if transaction.date else 'N/A',
            'data_transacao': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            'fitid': getattr(transaction, 'fitid', None)
        }
        transacoes.append(transacao)

    return transacoes


def obter_info_conta(ofx):
    conta = ofx.account
    extrato = conta.statement

    return {
        'banco': conta.institution.organization if conta.institution else 'N/A',
        'conta': conta.account_id,
        'saldo': extrato.balance
    }
