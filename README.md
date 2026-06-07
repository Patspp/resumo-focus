# Boletim Focus – BCB

Pipeline que baixa o Boletim Focus do Banco Central do Brasil toda segunda-feira, extrai o texto do PDF e — numa automação agendada — gera um resumo executivo em markdown.

> **Divisão de responsabilidades:** os scripts Python cuidam exclusivamente de baixar o PDF e extrair o texto. O resumo executivo é gerado por um agente que lê o texto extraído e produz o arquivo markdown em `output/focus/`.

---

## Estrutura

```
Projeto_Boletim/
├── src/
│   ├── baixar_focus.py     # Download do PDF com retrocesso de datas (cobre feriados)
│   └── extrair_texto.py    # Extração do texto do PDF com pdfplumber
├── tests/
│   └── test_baixar_focus.py
├── data/                   # PDFs e .txt extraídos (gerados em execução, não versionados)
├── output/
│   └── focus/              # Resumos executivos em markdown (gerados pelo agente)
├── .github/
│   └── workflows/          # GitHub Actions — agendamento semanal do download
├── demo.py                 # Roda o pipeline completo localmente
├── requirements.txt
├── pytest.ini
└── CLAUDE.md               # Briefing do projeto para o agente
```

---

## Como rodar localmente

**1. Instale as dependências:**

```bash
python -m pip install -r requirements.txt
```

**2. Rode o pipeline completo:**

```bash
python demo.py --abrir
```

A flag `--abrir` abre o `.txt` gerado no navegador padrão ao final da extração. Sem ela, o pipeline roda normalmente e imprime os caminhos no terminal.

---

## Testes

**Apenas testes offline** (rápido, sem acesso à internet):

```bash
pytest -m "not network"
```

**Todos os testes**, incluindo o download real do PDF do BCB:

```bash
pytest
```

Os testes marcados com `@pytest.mark.network` fazem chamadas reais à internet e dependem de o BCB ter publicado o boletim da semana.

---

## Pipeline em duas etapas

O resumo é gerado em dois estágios separados por design:

**Etapa 1 — GitHub Actions (download + extração)**

O workflow roda toda segunda-feira e executa `baixar_focus.py` e `extrair_texto.py`. Isso é necessário porque o BCB bloqueia requisições originadas de IPs de provedores de cloud — o download precisa sair de uma máquina real (o runner do GitHub Actions usa IPs residenciais/compartilhados que passam pelo filtro).

**Etapa 2 — Agente (resumo executivo)**

Com o `.txt` disponível em `data/`, a automação aciona um agente que lê o texto extraído e gera o resumo em `output/focus/focus_AAAA-MM-DD.md`. O agente nunca inventa números: toda mediana ou projeção citada no resumo deve estar presente no texto original.
