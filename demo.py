"""Pipeline completo: baixa o PDF do Focus e extrai o texto."""

import argparse
import sys
import webbrowser
from pathlib import Path

# Adiciona src/ ao path para importar os módulos do projeto
sys.path.insert(0, str(Path(__file__).parent / "src"))

from baixar_focus import baixar
from extrair_texto import extrair


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa o Focus do BCB e extrai o texto em sequência."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrão após a extração.",
    )
    args = parser.parse_args()

    pasta_data = Path(__file__).parent / "data"

    # Passo 1: download do PDF
    data_pub, pdf_path = baixar(pasta_data)
    tamanho_kb = pdf_path.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {pdf_path.name} ({tamanho_kb:.1f} KB)")

    # Passo 2: extração do texto
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraído: {txt_path}")

    # Abre o .txt no navegador, se solicitado
    if args.abrir:
        webbrowser.open(txt_path.as_uri())


if __name__ == "__main__":
    main()
