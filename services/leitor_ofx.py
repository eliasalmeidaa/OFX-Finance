# Leitura e extração de dados de arquivos OFX.
# Suporta formato OFXSGML (OFX 1.x) sem depender de lxml/BeautifulSoup,
# evitando crashes de bibliotecas C em ambientes de produção (Python 3.14+).

import re
from datetime import datetime


def _parse_ofx_bytes(data):
    """Lê bytes OFX e retorna lista de transações + info de conta."""
    for enc in ('utf-8', 'latin-1', 'cp1252', 'ascii'):
        try:
            text = data.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            pass
    else:
        text = data.decode('latin-1', errors='replace')

    def tag(name, content):
        m = re.search(rf'<{name}>\s*([^<\r\n]+)', content, re.IGNORECASE)
        return m.group(1).strip() if m else ''

    # Info da conta
    banco = tag('ORG', text) or tag('FID', text) or 'N/A'
    conta = tag('ACCTID', text) or 'N/A'
    saldo_str = tag('BALAMT', text)
    try:
        saldo = float(saldo_str)
    except ValueError:
        saldo = 0.0

    # Extrai todas as transações
    transacoes = []
    blocos = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', text, re.DOTALL | re.IGNORECASE)
    for bloco in blocos:
        fitid   = tag('FITID', bloco)
        memo    = tag('MEMO', bloco) or tag('NAME', bloco) or 'Sem descricao'
        amt_str = tag('TRNAMT', bloco)
        dt_str  = tag('DTPOSTED', bloco) or tag('DTUSER', bloco)

        try:
            valor = float(amt_str)
        except ValueError:
            continue

        # Converte data YYYYMMDD[HHMMSS] → date
        dt_raw = dt_str[:8] if dt_str else ''
        try:
            data_obj = datetime.strptime(dt_raw, '%Y%m%d').date()
            data_sql = data_obj.strftime('%Y-%m-%d')
        except ValueError:
            data_sql = None

        transacoes.append({
            'descricao':      memo,
            'valor':          valor,
            'data_transacao': data_sql,
            'fitid':          fitid or None,
        })

    return transacoes, banco, conta, saldo


class _ContaInfo:
    def __init__(self, banco, conta_id, saldo):
        self.institution = type('Inst', (), {'organization': banco})()
        self.account_id = conta_id
        self.statement = type('Stmt', (), {'balance': saldo, 'transactions': []})()


class _OFXResult:
    def __init__(self, transacoes, banco, conta_id, saldo):
        self.account = _ContaInfo(banco, conta_id, saldo)
        self._transacoes = transacoes

    def get_transacoes(self):
        return self._transacoes


def ler_arquivo_ofx(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        data = f.read()
    transacoes, banco, conta, saldo = _parse_ofx_bytes(data)
    return _OFXResult(transacoes, banco, conta, saldo)


def ler_arquivo_ofx_stream(stream):
    data = stream.read()
    transacoes, banco, conta, saldo = _parse_ofx_bytes(data)
    return _OFXResult(transacoes, banco, conta, saldo)


def extrair_transacoes(ofx):
    return ofx.get_transacoes()


def obter_info_conta(ofx):
    conta = ofx.account
    return {
        'banco': conta.institution.organization,
        'conta': conta.account_id,
        'saldo': conta.statement.balance,
    }
