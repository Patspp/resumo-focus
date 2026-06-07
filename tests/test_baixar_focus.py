"""Testes para src/baixar_focus.py."""

import datetime
import sys
from pathlib import Path

import pytest

# Adiciona src/ ao path para importar os módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from baixar_focus import baixar, ultima_segunda


# ---------------------------------------------------------------------------
# Testes puros (sem rede) — ultima_segunda()
# ---------------------------------------------------------------------------

def test_ultima_segunda_quinta():
    """A última segunda de uma quinta-feira é 3 dias antes."""
    quinta = datetime.date(2026, 6, 4)      # quinta-feira
    assert ultima_segunda(quinta) == datetime.date(2026, 6, 1)


def test_ultima_segunda_terca():
    """A última segunda de uma terça-feira é 1 dia antes."""
    terca = datetime.date(2026, 6, 2)       # terça-feira
    assert ultima_segunda(terca) == datetime.date(2026, 6, 1)


def test_ultima_segunda_quando_hoje_e_segunda():
    """Se hoje é segunda, deve retornar a segunda da semana passada (7 dias antes)."""
    segunda = datetime.date(2026, 6, 1)     # segunda-feira
    assert ultima_segunda(segunda) == datetime.date(2026, 5, 25)


def test_ultima_segunda_domingo():
    """A última segunda de um domingo é 6 dias antes."""
    domingo = datetime.date(2026, 5, 31)    # domingo
    assert ultima_segunda(domingo) == datetime.date(2026, 5, 25)


def test_ultima_segunda_varredura_60_dias():
    """Para qualquer dia nos próximos 60 dias, o retorno é sempre uma
    segunda-feira estritamente anterior à data fornecida."""
    hoje = datetime.date.today()
    for delta in range(60):
        data = hoje + datetime.timedelta(days=delta)
        resultado = ultima_segunda(data)
        # O resultado deve ser uma segunda-feira (weekday == 0)
        assert resultado.weekday() == 0, (
            f"{data} → {resultado} não é segunda-feira"
        )
        # O resultado deve ser estritamente anterior à data dada
        assert resultado < data, (
            f"{data} → {resultado} não é estritamente anterior"
        )


# ---------------------------------------------------------------------------
# Teste de rede — baixar()
# ---------------------------------------------------------------------------

@pytest.mark.network
def test_baixar_download_real(tmp_path):
    """Faz o download real do Focus e valida o arquivo recebido."""
    data_pub, caminho = baixar(tmp_path)

    # Arquivo deve ter sido criado no disco
    assert caminho.exists(), "O arquivo PDF não foi criado"

    # Deve começar com a assinatura de PDF
    assert caminho.read_bytes()[:4] == b"%PDF", "O arquivo não parece um PDF válido"

    # Deve ter mais de 50 KB (boletins reais têm centenas de KB)
    tamanho_kb = caminho.stat().st_size / 1024
    assert tamanho_kb > 50, f"Arquivo muito pequeno: {tamanho_kb:.1f} KB"

    # Nome do arquivo deve bater com a data de publicação retornada
    nome_esperado = f"focus_{data_pub.isoformat()}.pdf"
    assert caminho.name == nome_esperado, (
        f"Nome incorreto: {caminho.name!r} ≠ {nome_esperado!r}"
    )

    # Data de publicação deve estar dentro de uma janela razoável:
    # não no futuro e não mais de 14 dias no passado
    hoje = datetime.date.today()
    assert data_pub <= hoje, "Data de publicação está no futuro"
    assert (hoje - data_pub).days <= 14, (
        f"Data de publicação muito antiga: {data_pub} ({(hoje - data_pub).days} dias atrás)"
    )
