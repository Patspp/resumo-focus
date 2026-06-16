"""
Envia o resumo HTML do Boletim Focus por e-mail via SMTP do Gmail.

Variáveis de ambiente obrigatórias (exceto em --dry-run):
  FOCUS_SMTP_USER          remetente (ex.: voce@gmail.com)
  FOCUS_SMTP_APP_PASSWORD  senha de app gerada no Google
  FOCUS_EMAIL_DEST         destinatários separados por vírgula

Variável opcional:
  FOCUS_EMAIL_BCC          cópias ocultas separadas por vírgula
"""

import argparse
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

# Raiz do projeto: dois níveis acima deste arquivo (src/ → raiz)
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output" / "focus"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL direto


def achar_html_mais_recente() -> Path:
    """Retorna o focus_*.html mais recente em output/focus/."""
    htmls = sorted(OUTPUT_DIR.glob("focus_*.html"))
    if not htmls:
        raise FileNotFoundError(
            f"Nenhum arquivo focus_*.html encontrado em {OUTPUT_DIR}"
        )
    return htmls[-1]  # ordenação lexicográfica == ordenação por data


def extrair_data_do_nome(caminho: Path) -> str:
    """Extrai a data AAAA-MM-DD do nome do arquivo; retorna string vazia se não achar."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", caminho.name)
    return match.group(1) if match else ""


def montar_assunto(data: str) -> str:
    """Monta o assunto padrão com a data do boletim."""
    if data:
        return f"Resumo Focus — {data}"
    return "Resumo Focus"


def texto_de_fallback(data: str) -> str:
    """Texto simples exibido em clientes que não renderizam HTML."""
    if data:
        return (
            f"Resumo do Boletim Focus do Banco Central — {data}.\n\n"
            "Abra este e-mail em um cliente com suporte a HTML para ler o resumo completo."
        )
    return (
        "Resumo do Boletim Focus do Banco Central.\n\n"
        "Abra este e-mail em um cliente com suporte a HTML para ler o resumo completo."
    )


def montar_mensagem(
    remetente: str,
    destinatarios: list[str],
    assunto: str,
    html: str,
    data: str,
    bcc: list[str] | None = None,
) -> EmailMessage:
    """Constrói o EmailMessage com partes texto e HTML."""
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)

    # set_content define a parte texto-plano; add_alternative adiciona o HTML
    msg.set_content(texto_de_fallback(data))
    msg.add_alternative(html, subtype="html")
    return msg


def enviar(msg: EmailMessage, usuario: str, senha: str) -> None:
    """Abre conexão SSL com o Gmail e envia a mensagem."""
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.login(usuario, senha)
        smtp.send_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Envia o resumo HTML do Focus por e-mail via Gmail SMTP."
    )
    parser.add_argument(
        "--html",
        metavar="ARQUIVO",
        help="Caminho do HTML a enviar. Padrão: focus_*.html mais recente em output/focus/.",
    )
    parser.add_argument(
        "--dest",
        metavar="EMAILS",
        help="Destinatários separados por vírgula (sobrescreve FOCUS_EMAIL_DEST).",
    )
    parser.add_argument(
        "--assunto",
        metavar="TEXTO",
        help="Assunto do e-mail (sobrescreve o padrão derivado do nome do arquivo).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Monta o e-mail e exibe no terminal SEM enviar e sem exigir credenciais.",
    )
    args = parser.parse_args()

    # --- Localiza o HTML ---
    if args.html:
        caminho_html = Path(args.html)
        if not caminho_html.exists():
            sys.exit(f"Erro: arquivo não encontrado: {caminho_html}")
    else:
        try:
            caminho_html = achar_html_mais_recente()
        except FileNotFoundError as e:
            sys.exit(f"Erro: {e}")

    data = extrair_data_do_nome(caminho_html)
    html_conteudo = caminho_html.read_text(encoding="utf-8")

    # --- Assunto ---
    assunto = args.assunto or montar_assunto(data)

    # --- Destinatários ---
    dest_str = args.dest or os.environ.get("FOCUS_EMAIL_DEST", "")
    if not dest_str:
        if args.dry_run:
            dest_str = "destinatario@exemplo.com"  # placeholder para dry-run
        else:
            sys.exit(
                "Erro: informe destinatários via --dest ou variável FOCUS_EMAIL_DEST."
            )
    destinatarios = [e.strip() for e in dest_str.split(",") if e.strip()]

    bcc_str = os.environ.get("FOCUS_EMAIL_BCC", "")
    bcc = [e.strip() for e in bcc_str.split(",") if e.strip()] or None

    # --- Credenciais (não exigidas em dry-run) ---
    usuario = os.environ.get("FOCUS_SMTP_USER", "")
    senha = os.environ.get("FOCUS_SMTP_APP_PASSWORD", "")
    if not args.dry_run and (not usuario or not senha):
        sys.exit(
            "Erro: defina FOCUS_SMTP_USER e FOCUS_SMTP_APP_PASSWORD antes de enviar."
        )

    remetente = usuario or "nao-configurado@exemplo.com"

    # --- Monta mensagem ---
    msg = montar_mensagem(remetente, destinatarios, assunto, html_conteudo, data, bcc)

    if args.dry_run:
        # Exibe cabeçalhos e os primeiros 500 caracteres do HTML para conferência
        print("=== DRY-RUN: e-mail NÃO enviado ===")
        print(f"De:       {msg['From']}")
        print(f"Para:     {msg['To']}")
        if bcc:
            print(f"Bcc:      {msg['Bcc']}")
        print(f"Assunto:  {msg['Subject']}")
        print(f"Arquivo:  {caminho_html}")
        print(f"\n--- Início do HTML (500 chars) ---\n{html_conteudo[:500]}")
        return

    # --- Envia ---
    try:
        enviar(msg, usuario, senha)
        print(f"E-mail enviado com sucesso para: {', '.join(destinatarios)}")
    except smtplib.SMTPAuthenticationError:
        sys.exit(
            "Erro de autenticação. Verifique FOCUS_SMTP_USER e FOCUS_SMTP_APP_PASSWORD."
        )
    except smtplib.SMTPException as e:
        sys.exit(f"Erro SMTP: {e}")


if __name__ == "__main__":
    main()
