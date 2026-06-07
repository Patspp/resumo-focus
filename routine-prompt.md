# Roteiro semanal — Resumo do Boletim Focus

Este arquivo é o roteiro executado por uma automação agendada toda semana.
Siga os passos em ordem. Em caso de parada antecipada, não gere nenhum arquivo de saída.

---

## Passo 1 — Localizar o texto extraído

Procure o arquivo mais recente que corresponda ao padrão `data/focus_*.txt`.

- Se **não houver nenhum arquivo**, pare imediatamente sem fazer nada.
  O pipeline de download pode não ter rodado ainda esta semana.

---

## Passo 2 — Verificar o frescor do arquivo

Extraia a data do nome do arquivo (formato `focus_AAAA-MM-DD.txt`) e calcule
quantos dias se passaram desde a data de publicação até hoje.

| Faixa | Ação |
|---|---|
| 0 a 3 dias | Prosseguir normalmente. |
| 4 a 7 dias | Prosseguir, mas adicionar no topo do resumo gerado: `> **Atenção:** boletim com X dias — pode haver uma edição mais recente.` |
| Mais de 7 dias | Parar. O boletim está desatualizado demais para gerar um resumo confiável. |

---

## Passo 3 — Sanity check do conteúdo

Leia o arquivo `.txt` e verifique:

1. O texto tem **pelo menos 2 000 caracteres**. Se não tiver, o PDF pode ter
   sido mal extraído ou o layout do BCB mudou — pare.
2. O texto contém as três palavras-chave obrigatórias (busca case-insensitive):
   - `IPCA`
   - `Selic`
   - `PIB`

   Se qualquer uma estiver ausente, o layout provavelmente mudou e o resumo
   seria incompleto — pare e registre quais palavras estão faltando.

---

## Passo 4 — Gerar o resumo executivo

Leia o texto completo e produza um documento markdown com as duas seções abaixo.

**Regra absoluta:** nunca invente nem interpole números. Toda mediana,
projeção ou variação percentual citada deve estar textualmente presente
no arquivo `.txt`. Se um valor não aparecer no texto, escreva
"não divulgado nesta edição" em vez de estimar.

### Seção A — Resumo executivo (até 200 palavras)

- Comece pelas **medianas principais** da edição: IPCA (ano corrente e
  próximo), Selic (fim de ano), PIB (ano corrente) e câmbio (fim de ano),
  nessa ordem, se disponíveis.
- Em seguida, destaque em até dois parágrafos o que mais mudou em relação
  à edição anterior, conforme indicado no próprio texto do boletim.
- Mantenha linguagem direta e factual. Evite adjetivos avaliativos
  ("surpreendente", "preocupante") que não estejam no texto.

### Seção B — Três principais revisões da semana

Liste as três revisões de expectativa mais relevantes da edição (para cima
ou para baixo), cada uma no formato:

```
**[Indicador]:** de X% para Y% [ano de referência]
*Hipótese de motivo:* [uma frase explicando o possível fator, baseada no
contexto do próprio texto. Se o texto não oferecer pistas, escreva
"motivo não identificado no texto".]
```

Ordene da revisão de maior magnitude (em pontos percentuais absolutos)
para a de menor.

---

## Passo 5 — Salvar o resultado

Salve o markdown gerado em:

```
output/focus/focus_AAAA-MM-DD.md
```

onde `AAAA-MM-DD` é a data extraída do nome do arquivo `.txt` de origem.

O arquivo deve começar com o cabeçalho:

```markdown
# Focus BCB — AAAA-MM-DD

> Fonte: `data/focus_AAAA-MM-DD.txt`
```

seguido das seções A e B do Passo 4.
