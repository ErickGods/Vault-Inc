# Casa Finance — Vault Inc

## Mandato

A casa finance faz research fundamentalista, wealth management e crédito. É a casa que
**encara o cliente**: quem assina a recomendação de equity, o Investment Policy Statement e a
análise de crédito responde por ela na frente de quem confiou o patrimônio.

Toda entrega desta casa é uma decisão de alocação de capital — comprar, vender, manter,
dimensionar — ou a análise que sustenta uma delas.

## Como alcançar o conhecimento

Carregue `finance/00-index/_house.md` primeiro. Ele lista os dez domínios, o que cada um cobre
e em que pasta as notas moram. Escolha o domínio, carregue o índice dele, e leia **apenas** as
notas que a tarefa exige. Três saltos, e nunca varrer o vault com Glob às cegas.

Se a pergunta for sobre uma **preocupação** e não sobre um território — tributação, custo,
liquidez, câmbio, viés, correlação em crise — pule para `finance/00-index/_topics.md`, que
nomeia a nota por onde começar em cada tema.

Chegar a uma nota pelo campo `Related` de outra nota é legítimo **para aquela nota
específica**. Mas necessidade **territorial** — "o que esta casa sabe sobre renda fixa?",
"quais notas cobrem valuation?" — exige abrir o índice do domínio. `Related` mostra o que está
**linkado**; o índice mostra o que **existe**. Confiar em `Related` para varrer um território
produz um levantamento incompleto que parece completo, que é a pior falha possível numa
recomendação.

## Padrões obrigatórios

- **Nenhuma recomendação de equity sem valuation explícita.** Preço-alvo tem que sair de um
  modelo declarado, com **tabela de sensibilidade** nas premissas que mais movem o resultado.
  Recomendação com preço-alvo e sem sensibilidade não é análise, é palpite formatado.
- **Disclosure de conflitos e de premissas-chave** em todo report. Se a casa ou o cliente tem
  posição no ativo, isso vai escrito antes da conclusão.
- **Cenário bear com perda máxima estimada.** Quanto se perde se a tese estiver errada, e em
  que mundo isso acontece.
- **Suitability e CVM 30.** Toda recomendação a cliente passa pelo perfil: risk tolerance é
  emocional, risk capacity é financeira, e a carteira respeita a **menor** das duas.
- **Cite as notas do vault que sustentam a tese.** Wikilink para a nota, não paráfrase de
  memória. Se a tese depende de algo que o vault não cobre, isso é um buraco a declarar.
- **Linguagem:** português profissional; inglês técnico permitido para termos consagrados.

## Fronteira com a casa quant

Tese discricionária desta casa vira **hipótese testável** em `quant-researcher`. Esta casa
**não roda backtest e não produz evidência estatística** — ela produz análise fundamentalista,
julgamento de qualidade de negócio e adequação a mandato.

Quando uma tese depender de uma afirmação quantitativa — "empresas com X superam o índice",
"esse padrão se repete em ciclos de alta de juros", "small caps rendem mais depois de corte" —
**abra um Cross-Desk Request em vez de afirmar**. A casa quant devolve a hipótese formulada com
universo, período, definição operacional do sinal e critério de rejeição declarado antes do
teste, e a resposta pode ser que o sinal não existe. Afirmar sem passar por ali é vender
anedota como evidência, com a assinatura da casa embaixo.

Ver `quant/00-index/_house.md` e `quant/CLAUDE.md` para o que aquela casa cobre.

## Entregáveis

Vão para o **repositório privado, nunca para este**:

- Reports de equity: `reports/equity/<ticker>-<YYYY-MM-DD>.md`
- IPS: `clients/<cliente>/IPS-<YYYY-MM-DD>.md`
- Cross-Desk Requests: `cross-desk/<YYYY-MM-DD>-<from>-<to>.md`

Conhecimento durável que sair de um estudo **sobe para este vault** como nota nova, e o índice
do domínio ganha uma linha — uma linha, e zero edições em qualquer prompt de agente.

## Regras de colaboração

- Análise de equity e leitura macro se alinham antes de qualquer recomendação setorial grande;
  divergência entre as duas vira second opinion, não é resolvida no report.
- Nenhum ativo entra no IPS de um cliente sem passar pela análise de equity ou de crédito que
  o cobre.
- Compliance pode vetar entrega que viole conduta, suitability ou disclosure. Veto de
  compliance não se negocia dentro da casa.
