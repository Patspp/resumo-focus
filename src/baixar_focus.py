"""Baixa o PDF mais recente do Boletim Focus do Banco Central do Brasil."""

import datetime
from pathlib import Path

import requests

URL_TEMPLATE = "https://www.bcb.gov.br/content/focus/focus/R{data}.pdf"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
MAX_TENTATIVAS = 7


def ultima_segunda(hoje: datetime.date) -> datetime.date:
    """Retorna a segunda-feira mais recente, incluindo hoje se for segunda."""
    return hoje - datetime.timedelta(days=hoje.weekday())


def baixar(dest: Path | str) -> tuple[datetime.date, Path]:
    """Baixa o PDF do Focus mais recente para a pasta `dest`.

    Parte da última segunda-feira e recua dia a dia até encontrar
    um PDF válido (máximo de MAX_TENTATIVAS tentativas, cobrindo feriados).

    Retorna uma tupla (data_da_publicacao, caminho_do_arquivo).
    Levanta RuntimeError se nenhuma tentativa for bem-sucedida.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    data_candidata = ultima_segunda(datetime.date.today())
    sessao = requests.Session()
    sessao.headers["User-Agent"] = USER_AGENT

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        url = URL_TEMPLATE.format(data=data_candidata.strftime("%Y%m%d"))
        nome_arquivo = f"focus_{data_candidata.isoformat()}.pdf"
        caminho = dest / nome_arquivo

        # Se o arquivo já existe localmente, não baixa de novo
        if caminho.exists():
            print(f"Arquivo já existe, pulando download: {caminho}")
            return data_candidata, caminho

        print(f"Tentativa {tentativa}/{MAX_TENTATIVAS}: {url}")
        resposta = sessao.get(url, timeout=30)

        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            caminho.write_bytes(resposta.content)
            return data_candidata, caminho

        # PDF não encontrado nesta data; recua um dia
        data_candidata -= datetime.timedelta(days=1)

    raise RuntimeError(
        f"Nenhum PDF do Focus encontrado após {MAX_TENTATIVAS} tentativas."
    )


def main() -> None:
    pasta_data = Path(__file__).parent.parent / "data"
    data_pub, caminho = baixar(pasta_data)
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"\nPublicação: {data_pub.isoformat()}")
    print(f"Arquivo:    {caminho}")
    print(f"Tamanho:    {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
