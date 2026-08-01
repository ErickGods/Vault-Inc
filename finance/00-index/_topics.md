---
house: finance
type: topic-index
updated: 2026-07-29
---

# Casa Finance — Índice de Temas Transversais

Alguns problemas não moram em um domínio. Tributação do investidor pessoa física é tratada em
seis dos dez domínios desta casa — a isenção mensal está em investimentos, o come-cotas em
fundos, o withholding americano em mercados, o DARF em finanças pessoais. Para essas perguntas,
escolher um domínio em `_house.md` é escolher errado por construção: qualquer escolha perde
material que está em outro lugar.

Use este arquivo quando a pergunta for sobre **uma preocupação**, não sobre um território.
A coluna **Onde começar** nomeia a nota que trata o tema de forma mais direta: abra só ela e
pare, se responder. A coluna **Também tratado em** existe para o caso de não responder — é a
divulgação honesta de que o tema é distribuído, não uma lista de leitura obrigatória.

Se a pergunta for sobre um território (fundamentos, investimentos, análise, contabilidade,
mercados, psicologia), volte para `_house.md` e desça pelo domínio.

## Temas

| Tema | Onde começar | Também tratado em |
|---|---|---|
| Tributação do investidor PF | [[tax-optimization-br]] | [[stocks-fundamentals]] (isenção de R$ 20k e DARF), [[tesouro-direto]] e [[cdb-lci-lca]] (tabela regressiva, isenção de LCI/LCA), [[fundos-de-investimento]] (come-cotas), [[etfs]] (sem a isenção de R$ 20k), [[fiis-real-estate]] (as 3 condições da isenção), [[crypto-assets]] (isenção de R$ 35k), [[private-equity]] (FIP-IE), [[us-markets-overview]] (withholding de 30%, estate tax), [[capital-allocation]], [[acronyms-br]] |
| Custo que corrói retorno | [[compound-interest]] (2% a.a. ≈ 45% do patrimônio em 30 anos) | [[fundos-de-investimento]] (administração e performance), [[etfs]] (taxa e tracking error), [[private-equity]] (2/20 sobre hurdle), [[how-markets-work]] e [[b3-structure]] (spread e custos de corretagem), [[insurance-planning]] (carregamento de PGBL/VGBL), [[capital-allocation]] |
| Sensibilidade a juros e marcação a mercado | [[interest-rate-cycles]] | [[tesouro-direto]] (IPCA+ longo oscilando 10-20%), [[yield-curve]], [[bonds-international]] (TLT −31% em 2022), [[fiis-real-estate]], [[valuation-dcf]] (taxa de desconto), [[growth-vs-value]] (o regime que favorece cada estilo), [[market-cycles]], [[inflation]], [[fire-movement]] |
| Câmbio e exposição em dólar | [[bonds-international]] | [[futures]] (WDO como hedge), [[commodities]] (o real como moeda de commodity), [[us-markets-overview]], [[diversification]], [[interest-rate-cycles]] (carry trade) |
| Liquidez | [[how-markets-work]] | [[b3-structure]], [[fiis-real-estate]] (critério de R$ 500k/dia), [[private-equity]] (capital travado 7-12 anos), [[cdb-lci-lca]] (carência de 90 dias), [[graham-net-net]], [[emergency-fund]] |
| Vieses distorcendo decisão | [[cognitive-biases]] | o catálogo mora em psicologia, mas as manifestações moram fora: [[growth-vs-value]] (style drift), [[crypto-assets]] (FOMO), [[market-cycles]] (sentimento como sinal contrário), [[market-participants]] (manada e fluxo), [[graham-net-net]] (Mr. Market), [[investment-checklist]] (checklist como contramedida) |
| Concentração do mercado brasileiro | [[brazilian-market-b3]] (top 10 = ~55% do IBOV) | [[b3-structure]], [[market-participants]], [[diversification]] (o Brasil é ~0,5% do market cap mundial), [[capital-allocation]] (15-25% internacional), [[valuation-dcf]] (prêmio de risco-país) |
| Risco regulatório e ativo com prazo | [[moats]] | [[investment-checklist]] (bloco Brasil: processo na CVM, risco político em setor regulado), [[brazilian-market-b3]] (segmento de listagem e tag along na troca de controle), [[valuation-dcf]] (valor terminal de ativo com vida finita não é perpetuidade), [[private-equity]] (controlador com janela de saída) |
| Desconto barato vs value trap | [[growth-vs-value]] | [[valuation-multiples]] (múltiplo baixo contra a banda setorial, não contra o peer), [[moats]] (moat que morre transforma desconto em armadilha), [[red-flags-accounting]] (o desconto pode estar precificando o que a contabilidade esconde) |
| Correlação que sobe na crise | [[diversification]] | [[ray-dalio-machine]] (risk parity falhou em 2022), [[capital-allocation]], [[bonds-international]] (a face inversa: descorrelação que sobrevive) |

## Critério de inclusão

Um tema entra aqui quando é tratado **em mais de um domínio** — não quando aparece em muitas
notas. O teste é: existe uma escolha de domínio em `_house.md` que responde a pergunta sozinha?
Se existe, o tema pertence ao índice daquele domínio e não a este arquivo. Índice de temas que
cresce sem esse filtro vira um segundo índice de tudo, e volta a custar o contexto que os três
saltos economizam.

Contagem de notas não é o teste; dispersão entre domínios é. Três exemplos do que foi
**rejeitado** por esse critério, apesar de aparecerem em várias notas:

- **Lucro não é caixa** — aparece em cinco notas, mas contabilidade responde sozinha.
- **Margem de segurança e métodos de valuation** — aparece em toda a casa, mas o domínio de
  análise responde sozinho.
- **Alavancagem** — parece transversal e não é: são **dois conceitos distintos colados por uma
  palavra**. Alavancagem corporativa (DL/EBITDA, estrutura de capital) mora em contabilidade;
  alavancagem do investidor (margem, multiplicador de contrato) mora em derivativos. Uma linha
  única aqui mandaria o agente para a nota errada metade das vezes. Se um dia entrar, entra
  como duas linhas com hubs distintos.
