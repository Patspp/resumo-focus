# Projeto Boletim Focus – BCB

## Objetivo

Baixar o Boletim Focus do Banco Central do Brasil toda segunda-feira, extrair o texto do PDF e gerar um resumo executivo em markdown.

## Fonte dos dados

- Página oficial: https://www.bcb.gov.br/publicacoes/focus
- Padrão de URL do PDF: `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - Exemplo: `https://www.bcb.gov.br/content/focus/focus/R20240101.pdf`

## Convenções de nomenclatura

- Todos os arquivos são nomeados com a **data de publicação** do boletim no formato `focus_AAAA-MM-DD`.
  - PDF baixado: `data/focus_AAAA-MM-DD.pdf`
  - Texto extraído: `data/focus_AAAA-MM-DD.txt`
  - Resumo gerado: `output/focus/focus_AAAA-MM-DD.md`

## Estrutura de pastas

```
Projeto_Boletim/
├── src/                  # Código-fonte principal
├── tests/                # Testes automatizados
├── data/                 # PDFs e textos extraídos (baixados do BCB)
├── output/
│   └── focus/            # Resumos executivos em markdown
└── .github/
    └── workflows/        # GitHub Actions (agendamento semanal)
```

## Regras de negócio

1. **Nunca inventar números.** Toda mediana ou projeção citada no resumo deve estar textualmente presente no PDF extraído. Nunca interpolar, estimar ou completar valores ausentes.

2. **Feriados na segunda-feira.** O BCB publica na segunda-feira. Quando segunda é feriado, a publicação ocorre na terça-feira. A lógica de download deve retroceder dia a dia (segunda → terça → quarta…) até encontrar um PDF válido na URL, com um limite razoável de tentativas (ex.: 5 dias).

3. **Idempotência.** Se o PDF do dia já existir em `data/`, o download deve ser pulado sem erro.

4. **Encoding.** Salvar textos extraídos sempre em UTF-8.

## Fluxo esperado

```
download_focus.py   →  data/focus_AAAA-MM-DD.pdf
extract_text.py     →  data/focus_AAAA-MM-DD.txt
summarize_focus.py  →  output/focus/focus_AAAA-MM-DD.md
```

## Agendamento

O GitHub Actions (cron) atrasa por horas e às vezes pula execuções; o BCB publica na terça quando a segunda é feriado. Por isso tudo roda **várias vezes, de segunda a quarta**, e cada etapa é idempotente:

- `focus-download.yml`: 12h15, 15h15, 18h15 e 21h15 UTC (seg–qua). Sem PDF novo, não commita.
- Routine `resumo-focus` (claude.ai): 12h45, 15h45, 18h45 e 21h45 UTC (seg–qua). Resume o `.txt` mais recente só se ainda não houver `output/focus/focus_AAAA-MM-DD.html`. Prompt em `routine-prompt.md`.
- `focus-enviar.yml`: dispara no push do HTML e envia o e-mail.
- `focus-verificar.yml` (vigia): terça 23h30 UTC e quinta 12h UTC. Falha e envia alerta por e-mail se o boletim mais recente não foi baixado, extraído e resumido.
