Você está executando a Routine de resumo semanal do Focus.

Esta Routine dispara VÁRIAS vezes por semana (segunda a quarta, a cada 3 h),
porque o GitHub Action de download atrasa e às vezes só publica o boletim na
terça (feriado na segunda). Por isso ela é **idempotente**: cada execução
resume no máximo um boletim, e só se ainda não houver resumo dele.

Os arquivos `data/focus_AAAA-MM-DD.{pdf,txt}` são commitados em `main` pelo
Action. A data no nome é a da **sexta-feira** de referência do boletim (que é
publicado na segunda ou terça seguinte). Sua tarefa é ler o `.txt` mais
recente, gerar um resumo em HTML com a logo da Análise Macro e publicá-lo no
repositório.

## Passos

1. **Localize o `.txt` mais recente.** Liste `data/focus_*.txt` e pegue
   o de data mais alta. Se não houver nenhum, pare sem commitar o HTML.

2. **Já foi resumido?** Se `output/focus/focus_AAAA-MM-DD.html` (mesma data
   do `.txt`) já existir, pare sem fazer nada: o resumo dessa semana já foi
   publicado e enviado. Isso é o caso normal nas execuções após a primeira.

3. **Verifique frescor.** Extraia a data do nome e compare com hoje:
   - 0 a 5 dias: está fresco, siga.
   - 6 a 9 dias: siga, mas escreva `[REVISAR]` no início do assunto.
   - Mais de 9 dias: o boletim novo ainda não foi baixado pelo Action.
     Pare sem commitar (execuções seguintes tentarão de novo).

4. **Sanity check do texto.** Confirme: pelo menos 2 000 caracteres e
   presença das palavras `IPCA`, `Selic`, `PIB`. Se falhar, o layout do
   PDF pode ter mudado — pare sem commitar o HTML.

5. **Leia o texto** e escreva o conteúdo do resumo:
   - **Resumo executivo** em até 200 palavras, em prosa corrida.
     Comece pelas medianas das principais variáveis (IPCA do ano,
     Selic fim de ano, PIB, câmbio). Cite literalmente entre aspas
     quando houver número-chave.
   - **Três principais revisões da semana** em bullets no formato:
     `Variável (ano): anterior → atual. Hipótese: motivo.`
   - Nunca invente número. Se não houver hipótese sólida, escreva
     "sem hipótese clara — pode ser ruído amostral".

6. **Monte o HTML** em `output/focus/focus_AAAA-MM-DD.html`, com
   esta estrutura:
   - No topo, a logo da Análise Macro, carregada desta URL:
     `https://analisemacro.com.br/wp-content/uploads/dlm_uploads/2021/10/logo_am.png`
   - Um título `Focus — AAAA-MM-DD`.
   - O resumo executivo em parágrafo e as três revisões em lista.
   - Use as cores da marca: azul `#282f6b` nos títulos.

7. **Inspecione** o HTML gerado: a logo aparece, as medianas batem com
   o `.txt`, há ao menos uma citação literal entre aspas.

8. **Publique o HTML** fazendo commit e push para `main`:

   ```
   git add output/focus/focus_AAAA-MM-DD.html
   git commit -m "resumo: Focus AAAA-MM-DD"
   git push origin main
   ```

   Se o push for rejeitado (o Action de download pode ter commitado no
   meio-tempo), rode `git pull --rebase origin main` e tente de novo.

   Esse push dispara automaticamente o Action `.github/workflows/focus-enviar.yml`,
   que lê o HTML, monta o e-mail e envia via SMTP do Gmail. O remetente,
   o destinatário e a senha de app ficam nos Secrets do repositório
   (`FOCUS_SMTP_USER`, `FOCUS_SMTP_APP_PASSWORD`, `FOCUS_EMAIL_DEST`,
   `FOCUS_EMAIL_BCC`) — nunca neste arquivo nem no código.

## Falhas

Em qualquer cenário abaixo, pare sem commitar o HTML. O motivo aparece no
transcript da Routine. Como o push não ocorre, o Action de envio também
não dispara — nada é enviado. **Não envie notificação push** nesses casos:
como a Routine roda várias vezes por semana, execuções antecipadas são
normais. Quem alerta sobre falhas é o workflow `focus-verificar.yml`.

- Nenhum `.txt` em `data/` (Action não rodou).
- Resumo dessa data já existe (execução repetida — normal).
- `.txt` com mais de 9 dias (boletim novo ainda não baixado).
- Sanity check do texto falhou (mudança de layout do PDF).

Nunca invente número.
