# Casa Tech — Vault Inc

## Mandato

A casa tech faz engenharia de software, infraestrutura e dados. É a casa que **constrói**: o que
sai daqui roda, é deployado, é monitorado e alguém é chamado quando quebra às três da manhã.

Toda entrega desta casa é código em produção, infraestrutura provisionada ou pipeline de dados
em operação — ou a decisão técnica que sustenta uma delas.

## Como alcançar o conhecimento

Carregue `tech/00-index/_house.md` primeiro. Ele lista os oito domínios, o que cada um cobre e
em que pasta as notas moram. Escolha o domínio, carregue o índice dele, e leia **apenas** as
notas que a tarefa exige. Três saltos, e nunca varrer o vault com Glob às cegas.

Atenção a um detalhe desta casa: **cinco dos oito domínios têm subpastas**. Para eles o
`_house.md` dá só a raiz do domínio, e o caminho exato mora no **título da seção** dentro do
índice do domínio. Parar no `_house.md` produz um caminho que não existe.

Se a pergunta for sobre uma **preocupação** e não sobre um território — custo de inferência,
custo de infraestrutura, segredos, idempotência, evolução de schema, cache, observabilidade,
gerenciado contra self-hosted — pule para `tech/00-index/_topics.md`, que nomeia a nota por onde
começar em cada tema.

Chegar a uma nota pelo campo `Related` de outra nota é legítimo **para aquela nota específica**.
Mas necessidade **territorial** — "o que esta casa sabe sobre mensageria?", "quais notas cobrem
orquestração?" — exige abrir o índice do domínio. `Related` mostra o que está **linkado**; o
índice mostra o que **existe**. Confiar em `Related` para varrer um território produz um
levantamento incompleto que parece completo, e num projeto isso vira decisão de arquitetura
tomada sem saber que a casa já tinha a resposta.

## Padrões obrigatórios

- **Decisão arquitetural vira ADR.** Os quatro critérios estão em `adr-guide`: difícil de
  reverter, cruza times, trade-off não óbvio, equipe futura vai perguntar. ADR escrito depois
  para justificar o que já foi feito não conta, e ADR parado em `proposed` há meses é pior que
  ADR nenhum.
- **Nenhuma escolha de tecnologia sem o que se perde declarado.** Toda nota desta casa carrega
  uma seção de gotchas justamente porque o custo aparece depois. Recomendar stack sem nomear a
  restrição que ela impõe é vender folheto.
- **Cite as notas do vault que sustentam a decisão.** Wikilink para a nota, não paráfrase de
  memória. Se a decisão depende de algo que o vault não cobre, isso é um buraco a declarar.
- **UI/UX antes de frontend.** Especificação de interface precede implementação; o inverso
  produz retrabalho, não velocidade.
- **Conflito técnico entre agentes escala para o `lead-engineer`.** Nenhum agente escreve fora
  do próprio escopo sem passar por ali.
- **Linguagem:** português profissional; inglês técnico preservado para termos consagrados
  (`deploy`, `commit`, `pipeline`, `throughput`, `trade-off`).

## Fronteira com a casa quant

`market-data-quant` cuida da **correção financeira** do dado — point-in-time, ajuste de
proventos, sobrevivência, splits, corporate actions. **Especifica.**

`data-engineer` (tech) cuida do **transporte** — ingestão, orquestração, storage, SLA, custo.
**Constrói.**

A regra prática: se a pergunta é "esse número está certo?", é quant. Se é "esse número chega a
tempo, íntegro e por um custo aceitável?", é tech. Um pipeline impecável servindo série com
viés de sobrevivência é falha da casa quant; uma especificação correta servida com seis horas de
atraso é falha desta.

Quando a fronteira ficar ambígua, **abra um Cross-Desk Request em vez de decidir sozinho.**

Ver `quant/00-index/_house.md` e `quant/CLAUDE.md` para o que aquela casa cobre.

## Entregáveis

Vão para o **repositório privado `Vault-Inc-Workspace`, nunca para este**:

- Código de projeto: `projects/<projeto>/`
- ADRs: `decisions/ADR-<n>-<titulo>.md`
- Specs de UI/UX e de API: `specs/ui-ux/`, `specs/api/`
- Reports de QA e de segurança: `reports/qa/<projeto>-<YYYY-MM-DD>.md`,
  `reports/security/<projeto>-<YYYY-MM-DD>.md`
- Cross-Desk Requests: `cross-desk/<YYYY-MM-DD>-<from>-<to>.md`

Conhecimento durável que sair de um projeto **sobe para este vault** como nota nova, e o índice
do domínio ganha uma linha — uma linha, e zero edições em qualquer prompt de agente. É esse
passo que impede a casa de reaprender a cada projeto o que já custou caro uma vez.
