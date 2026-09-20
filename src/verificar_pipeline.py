"""
Vigia do pipeline semanal do Focus.

Confere se o boletim mais recente foi baixado, extraído e resumido. Se algo
estiver faltando, sai com código 1 (o GitHub avisa por e-mail que o workflow
falhou) e, havendo credenciais, envia também um alerta por SMTP.

Variáveis de ambiente (todas opcionais; sem elas só imprime e sai com 1):
  FOCUS_SMTP_USER          remetente do alerta
  FOCUS_SMTP_APP_PASSWORD  senha de app do Gmail
  FOCUS_ALERT_DEST         destino do alerta (padrão: o próprio FOCUS_SMTP_USER)
"""

import datetime
import os
import re
import sys
from email.message import EmailMessage
from pathlib import Path

from enviar_email import enviar

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output" / "focus"

# O boletim leva a data da sexta e sai na segunda (terça, se segunda for
# feriado). Até a quinta seguinte, o mais recente tem no máximo 6 dias.
MAX_IDADE_PDF_DIAS = 6


def _data_do_arquivo(caminho: Path) -> datetime.date:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", caminho.name)
    return datetime.date.fromisoformat(m.group(1))


def avaliar(hoje: datetime.date, data_dir: Path, output_dir: Path) -> list[str]:
    """Retorna a lista de problemas encontrados (vazia = tudo certo)."""
    pdfs = sorted(data_dir.glob("focus_*.pdf"))
    if not pdfs:
        return ["Nenhum PDF do Focus em data/ — o download nunca funcionou."]

    ultimo = pdfs[-1]
    data = _data_do_arquivo(ultimo)
    idade = (hoje - data).days
    if idade > MAX_IDADE_PDF_DIAS:
        return [
            f"PDF do boletim desta semana não foi baixado: o mais recente é "
            f"{data} ({idade} dias atrás). Veja o workflow 'Focus – Download e Extração'."
        ]

    problemas = []
    if not ultimo.with_suffix(".txt").exists():
        problemas.append(f"PDF {data} baixado, mas o .txt não foi extraído.")
    elif not (output_dir / f"focus_{data}.html").exists():
        problemas.append(
            f"Resumo do Focus {data} NÃO foi gerado/enviado. A Routine "
            "'resumo-focus' não commitou o HTML — veja as sessões dela em claude.ai/code."
        )
    return problemas


def alertar(problemas: list[str]) -> None:
    """Envia o alerta por e-mail, se houver credenciais."""
    usuario = os.environ.get("FOCUS_SMTP_USER", "")
    senha = os.environ.get("FOCUS_SMTP_APP_PASSWORD", "")
    destino = os.environ.get("FOCUS_ALERT_DEST", "") or usuario
    if not (usuario and senha and destino):
        print("Sem credenciais SMTP: alerta não enviado por e-mail.")
        return
    msg = EmailMessage()
    msg["Subject"] = "⚠ Pipeline Focus com problema"
    msg["From"] = usuario
    msg["To"] = destino
    msg.set_content(
        "O vigia do pipeline do Boletim Focus encontrou problemas:\n\n- "
        + "\n- ".join(problemas)
        + "\n\nOs destinatários do resumo podem não ter recebido o e-mail desta semana."
    )
    try:
        enviar(msg, usuario, senha)
        print(f"Alerta enviado para {destino}.")
    except Exception as e:  # o alerta não pode mascarar o problema original
        print(f"Falha ao enviar alerta por e-mail: {e}")


def main() -> None:
    problemas = avaliar(datetime.date.today(), DATA_DIR, OUTPUT_DIR)
    if not problemas:
        print("OK: boletim mais recente baixado, extraído e resumido.")
        return
    for p in problemas:
        print(f"PROBLEMA: {p}")
    alertar(problemas)
    sys.exit(1)


if __name__ == "__main__":
    main()
