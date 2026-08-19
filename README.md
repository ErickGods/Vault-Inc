# Vault Inc

### Uma casa de análises financeiras onde a equipe inteira é de agentes de IA.

Research de ações, gestão de patrimônio, análise de crédito, estratégia quantitativa — o trabalho
que uma boutique de investimentos faz. Na Vault Inc, quem faz esse trabalho são **agentes**
construídos sobre o [Claude Code](https://claude.com/claude-code): cada um é um especialista, com
uma função, organizados numa estrutura que imita uma casa de análise de verdade.

Este repositório é o **cérebro da empresa** — o conhecimento, os agentes e as rotinas que eles
seguem. As entregas para cliente ficam em um repositório privado; aqui está o que faz a máquina
funcionar.

---

## Veja funcionando

**Você pede: "inicie a cobertura da Vale."** O que acontece:

1. O **equity-research-analyst** assume e puxa da base só o conhecimento que a tarefa exige.
2. Faz o **valuation por dois métodos** — fluxo de caixa e múltiplos — e explica por que divergem.
3. Monta o **cenário bear** com a perda máxima, não só o caso otimista.
4. O **compliance-officer** confere disclosure e suitability — e pode **vetar** a entrega.
5. Sai um relatório com recomendação, preço-alvo, margem de segurança e riscos nomeados.

Do jeito que um analista de verdade faria: as mesmas etapas, na mesma ordem, sem pular nenhuma.

---

## Por que não é "só um chatbot financeiro"

A diferença entre a Vault Inc e perguntar a um modelo "essa ação está barata?" é a **disciplina** —
escrita em regras que os agentes **não podem contornar**:

- **O compliance pode vetar qualquer entrega** — e o veto não se negocia.
- **Nenhum backtest sem critério de rejeição escrito _antes_ do teste.** Backtest sem hipótese
  produz racionalização, não resultado.
- **Nenhum valuation sem cenário bear e matriz de sensibilidade.** "Quanto posso perder?" é uma
  pergunta obrigatória, não opcional.
- Afirmação sobre **uma população de empresas** nunca vira fato sobre uma empresa só — vai para a
  prova estatística.

É research com o rigor que se cobra de gente, aplicado a uma equipe que não dorme e não pula etapa.

---

## As três casas

A empresa é organizada como uma casa de análise real: três **casas**, cada uma com um mandato e uma
equipe de agentes especialistas.

| Casa | O que faz | A equipe |
|---|---|---|
| 🏛️ **finance** | Fala com o cliente: research de empresas, carteiras e crédito. Toda entrega é uma decisão de alocar capital. | equity-research · private-banker · credit-research · macro-strategist · pe-analyst · compliance |
| 📊 **quant** | Testa se uma ideia de mercado funciona de verdade — e transforma a que sobrevive em código. | quant-researcher · quant-developer · risk-quant · market-data-quant |
| 🔧 **tech** | Constrói o que roda: software, infraestrutura e dados. | backend · frontend · data-engineer · devops · ml-engineer · e mais |

**Uma regra separa as duas primeiras:** afirmação sobre **uma empresa** é finance; sobre **uma
população de empresas** é quant. *"O ROIC desta empresa foi 18%"* é finance. *"Empresas com ROIC de
18% superam o índice"* é quant.

---

## Como a máquina funciona por dentro

Duas peças fazem os agentes trabalharem com consistência:

**A base de conhecimento** é o que cada agente sabe. Em vez de ler o repositório inteiro, o agente
desce por índices — parte do mapa da casa, escolhe o assunto, abre **só** as notas que a tarefa
pede. É o que deixa a base crescer sem deixar os agentes mais lentos.

**As skills** são as rotinas críticas da casa, com passos numerados e uma seção `Nunca`. Elas
garantem que trabalho sensível saia sempre com o mesmo padrão:

`equity-initiation` · `dcf-valuation` · `hypothesis-test` · `backtest-protocol`

---

## Explore

- **Só quero ler** — abra a pasta no [Obsidian](https://obsidian.md) e navegue pelo `_house.md` de
  cada casa.
- **Quero colocar os agentes para trabalhar** — abra o repositório no Claude Code. Os 20 agentes e
  as skills são reconhecidos sozinhos; comece pelo [`CLAUDE.md`](CLAUDE.md) e peça uma tarefa.

Conteúdo em **português**, com termos técnicos em inglês. Cobre mercado brasileiro (B3, Tesouro
Direto, CDB/LCI/LCA, JCP, tributação PF) e americano.

---

## Estado

As três casas estão **montadas e funcionando** — índices completos e agentes prontos.
**finance** e **quant** já foram testadas com agentes reais executando tarefas de verdade; **tech**
tem conhecimento e agentes prontos, e passa pelo mesmo teste em seguida.

---

## Licença

[MIT](LICENSE) · Construído por [Vault Inc](https://github.com/ErickGods)
