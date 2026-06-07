"""Extrai o texto de um PDF do Boletim Focus e salva como .txt."""

import argparse
import sys
from pathlib import Path

import pdfplumber


def extrair(pdf_path: Path | str) -> Path:
    """Extrai o texto de todas as páginas do PDF e salva num arquivo .txt.

    O .txt é salvo no mesmo diretório do PDF, com o mesmo nome
    e extensão trocada. Retorna o caminho do arquivo gerado.
    """
    pdf_path = Path(pdf_path)
    txt_path = pdf_path.with_suffix(".txt")

    paginas = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            paginas.append(texto)

    # Separa páginas com linha em branco para facilitar leitura posterior
    conteudo = "\n\n".join(paginas)
    txt_path.write_text(conteudo, encoding="utf-8")

    return txt_path


def _pdf_mais_recente(pasta: Path) -> Path | None:
    """Retorna o focus_*.pdf mais recente da pasta, ou None se não houver."""
    pdfs = sorted(pasta.glob("focus_*.pdf"))
    return pdfs[-1] if pdfs else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai texto de um PDF do Focus e salva como .txt"
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        help="Caminho do PDF a extrair (opcional; padrão: mais recente em data/)",
    )
    args = parser.parse_args()

    if args.pdf:
        pdf_path = args.pdf
    else:
        # Procura o PDF mais recente na pasta data/ do projeto
        pasta_data = Path(__file__).parent.parent / "data"
        pdf_path = _pdf_mais_recente(pasta_data)

        if pdf_path is None:
            print(
                "Nenhum PDF encontrado em data/. "
                "Execute primeiro: python src/baixar_focus.py",
                file=sys.stderr,
            )
            sys.exit(1)

    print(f"Extraindo texto de: {pdf_path}")
    txt_path = extrair(pdf_path)
    tamanho_kb = txt_path.stat().st_size / 1024
    print(f"Texto salvo em:     {txt_path}")
    print(f"Tamanho:            {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
