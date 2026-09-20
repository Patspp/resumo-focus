"""Testes para src/verificar_pipeline.py."""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verificar_pipeline import avaliar


def _montar(tmp_path, pdf=True, txt=True, html=True, data="2026-09-18"):
    d, o = tmp_path / "data", tmp_path / "output"
    d.mkdir()
    o.mkdir()
    if pdf:
        (d / f"focus_{data}.pdf").write_bytes(b"%PDF")
    if txt:
        (d / f"focus_{data}.txt").write_text("x", encoding="utf-8")
    if html:
        (o / f"focus_{data}.html").write_text("x", encoding="utf-8")
    return d, o


def test_tudo_certo(tmp_path):
    d, o = _montar(tmp_path)
    assert avaliar(datetime.date(2026, 9, 22), d, o) == []


def test_sem_pdf_nenhum(tmp_path):
    d, o = _montar(tmp_path, pdf=False, txt=False, html=False)
    assert avaliar(datetime.date(2026, 9, 22), d, o)


def test_pdf_desatualizado(tmp_path):
    """Terça 09-22 com o PDF mais recente de 09-04 (feriado perdido)."""
    d, o = _montar(tmp_path, data="2026-09-04")
    problemas = avaliar(datetime.date(2026, 9, 22), d, o)
    assert len(problemas) == 1 and "não foi baixado" in problemas[0]


def test_txt_ausente(tmp_path):
    d, o = _montar(tmp_path, txt=False, html=False)
    problemas = avaliar(datetime.date(2026, 9, 22), d, o)
    assert "não foi extraído" in problemas[0]


def test_resumo_ausente(tmp_path):
    d, o = _montar(tmp_path, html=False)
    problemas = avaliar(datetime.date(2026, 9, 22), d, o)
    assert "NÃO foi gerado" in problemas[0]


def test_limite_de_idade_quinta(tmp_path):
    """Quinta-feira (6 dias após a sexta) ainda é aceitável."""
    d, o = _montar(tmp_path)
    assert avaliar(datetime.date(2026, 9, 24), d, o) == []
