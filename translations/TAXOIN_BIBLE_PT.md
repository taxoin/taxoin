# TAXOIN BIBLE (Bíblia do Taxoin)

## Prova de Contribuição (Proof of Contribution) — A Verdade do Serviço

> SIGNED NOT_FOR_COMPACTION. Especificação canônica do protocolo Taxoin.

---

## Prólogo

No início, existia a prova de trabalho. Mineradores queimavam eletricidade
para computar hashes, e a rede os recompensava com moedas. O trabalho era
útil para a segurança, mas inútil para a humanidade.

Taxoin foi criado para resolver um problema fundamental:

> **Substituir o cálculo inútil por contribuição útil.**

Não "uma CPU, um voto" (Nakamoto, 2008).
Mas **um humano, uma contribuição, um valor.**

---

## Parte I: O Que é um Taxoin?

### I.1 Definição

Um **Taxoin (Ⓣ)** é uma unidade de **contribuição comprovada** à rede Taxoin.
Não pode ser minerado, cunhado ou criado do nada.

Cada Ⓣ em circulação entrou na rede por um dos dois portões:

| Portão | Mecanismo | Fornecimento Máximo |
|------|-----------|------------|
| **Gênese (Genesis)** | Prova de Humanidade (Proof of Personhood) — um humano, uma gênese | 21.000.000 Ⓣ (420.000 pessoas × 50Ⓣ) |
| **Serviço (Service)** | Prova de Contribuição (Proof of Contribution) — fornecer um serviço real | Ilimitado (limitado pela atividade econômica real) |

### I.2 Princípio Fundamental

> **Não existe Taxoin sem uma contribuição correspondente.**

Esta é a lei fundamental. Cada moeda é lastreada por:
- Um ser humano único (gênese), ou
- Um serviço verificado prestado (contribuição)

Não há minerador extraindo moedas da eletricidade. Não há staker
ganhando renda passiva. Há apenas **trabalho que alguém valorizou
o suficiente para pagar.**

### I.3 Não-Princípios (O Que Taxoin NÃO é)

| ❌ Não é isto | ✅ Mas é isto |
|------------|------------|
| Ativo de investimento | Meio de troca por serviços |
| Reserva de valor | Unidade de contribuição |
| Recompensa de mineração | Pagamento por serviço |
| Renda passiva | Renda de trabalho ativo |
| Token especulativo | Prova de trabalho realizado |

---

## Parte II: Gênese (Genesis) — Prova de Humanidade (Proof of Personhood)

### II.1 O Problema de Inicialização

Uma economia de serviços não pode começar do zero:
- Ninguém tem moedas para pagar por serviços
- Ninguém pode ganhar moedas sem fornecer serviços
- Impasse

### II.2 Solução: Um Humano, Uma Gênese

Taxoin distribui moedas de gênese não para "mineradores" ou "investidores"
mas para **seres humanos únicos** verificados pelo conjunto de validadores.

```
PARÂMETROS GLOBAIS:
  GENESIS_REWARD     = 50 Ⓣ  (por pessoa única)
  MAX_GENESIS_SUPPLY = 21.000.000 Ⓣ
  MAX_PARTICIPANTS   = 420.000  (21M / 50)
```

### II.3 A Cerimônia de Gênese

```
  ┌──────────────────────────────────────────────────────────────┐
  │             CERIMÔNIA DE GÊNESE (GENESIS CEREMONY)           │
  │                                                              │
  │  1. O humano gera um par de chaves (secp256k1)               │
  │     → endereço: 0xdeadbeef...                                │
  │                                                              │
  │  2. O humano contata um validador (presencialmente /         │
  │     videochamada / através de um referenciador confiável)    │
  │     → Prova que é um humano único                            │
  │     → Assina uma mensagem com sua chave: "Sou real"          │
  │                                                              │
  │  3. O validador verifica:                                    │
  │     → A assinatura corresponde ao endereço declarado         │
  │     → O humano já não está no registro de gênese             │
  │     → O humano parece ser uma pessoa real e única            │
  │                                                              │
  │  4. O validador assina uma atestação:                        │
  │     "0xval1 atesta que 0xdeadbeef é um humano único"         │
  │                                                              │
  │  5. Necessita 3 de 7 atestações de validadores → gênese aprovado  │
  │     → +50 Ⓣ creditados a 0xdeadbeef                         │
  │     → Endereço adicionado ao Registro de Gênese (imutável)   │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

### II.4 Resistência Sybil

Um ataque Sybil (uma pessoa criando 1000 carteiras) é prevenido por:

| Camada | Proteção |
|-------|-----------|
| **Prova de Humanidade (Proof of Personhood)** | Validadores verificam humanos, não carteiras |
| **Atestação 3-de-7** | Necessita 3 validadores independentes para confirmar |
| **Registro imutável** | Cada endereço pode receber gênese apenas uma vez |
| **Reputação** | Validadores que aprovam Sybils perdem reputação |

### II.5 O Limite de Gênese

```
MAX_GENESIS_SUPPLY = 21.000.000 Ⓣ
```

Este é o **máximo absoluto** de moedas de gênese. Uma vez que
420.000 humanos tenham sido atestados, nenhuma nova moeda de gênese
pode ser criada.

Após a gênese ser esgotada, todos os novos Ⓣ em circulação vêm
exclusivamente de transações de serviço (uma pessoa pagando a outra
por um serviço).

---

## Parte III: Economia de Serviços — Prova de Contribuição (Proof of Contribution)

### III.1 O Que é um Serviço?

Um serviço é qualquer contribuição que um participante da rede fornece
a outro. O serviço é **registrado na cadeia** e **precificado pelo
fornecedor.**

Exemplos:
```
  Tipo de Serviço       Fornecedor          Preço
  ─────────────────────────────────────────────────
  Gateway SMS           Telefone da Alice   0,1 Ⓣ/SMS
  Computação GPU        Fazenda do Bob     5,0 Ⓣ/hora
  Acesso API           Modelo da Carol    0,5 Ⓣ/chamada
  Corrida (táxi)        Carro do Dave      3,0 Ⓣ/km
  Armazenamento         Servidor da Eve    0,01 Ⓣ/MB/mês
  Ciclo CPU             Desktop do Frank   0,001 Ⓣ/CPU-hora
  Retransmissão         Roteador da Grace  0,05 Ⓣ/GB
  Revisão humana        Expertise do Hank  10,0 Ⓣ/revisão
```

Não há limite para o que pode ser um serviço. O mercado decide
quais serviços têm valor e a que preço.

### III.2 Registro de Serviços (Service Registry)

Cada serviço é registrado na cadeia como um commit git:

```python
@dataclass
class ServiceRegistration:
    provider: str              # endereço (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # Ⓣ por unidade
    description: str           # legível por humanos
    endpoint: str              # como chamar (URL, contato, API)
    attested_by: list[str]     # validadores que verificaram
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

O registro de serviços é armazenado em git notes (infraestrutura existente).
Qualquer um pode consultar: "mostre todos os gateways SMS com
classificação > 4.0."

Validadores verificam se um serviço é real antes de aprovar o registro:
- Para um gateway SMS: enviar um SMS de teste, verificar entrega
- Para computação GPU: executar um benchmark, verificar resultado
- Para uma corrida de táxi: verificar carteira de motorista e veículo

### III.3 Preços

O fornecedor define o preço. O mercado o regula.

```
  Preço alto + serviço ruim → sem clientes → fornecedor abaixa o preço
  Preço baixo + bom serviço → muitos clientes → fornecedor ganha reputação
  Fraude (pegar dinheiro, não servir) → disputa → arbitragem do validador
                                              → penalidade de reputação
                                              → possível banimento
```

Nenhuma autoridade central define preços. Nenhum algoritmo ajusta
taxas. Mercado puramente livre.

### III.4 Descoberta

Consumidores descobrem serviços através do registro:

```
  taxoin service list --type sms --min-rating 4.0
  → 0xalice: 0,1 Ⓣ/SMS, classificação 4.8 (942 transações)
  → 0xbob:   0,15 Ⓣ/SMS, classificação 4.2 (312 transações)
```

---

## Parte IV: Ciclo de Vida da Transação — Atestação Mútua (Mutual Attestation)

### IV.1 O Problema Central

> Como a blockchain sabe que um serviço foi realmente entregue?

Em blockchains tradicionais, isso é chamado de **Problema do Oráculo (Oracle Problem).**
A resposta do Taxoin: **Atestação Mútua (Mutual Attestation)** — ambas as partes assinam.

### IV.2 A Transação Atestada (AttestedTransaction)

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # quem paga
    provider: str              # quem fornece
    service_ref: str           # link para ServiceRegistration
    amount: float              # Ⓣ por esta transação
    consumer_sig: str          # "Recebi o serviço" (ECDSA)
    provider_sig: str          # "Forneci o serviço" (ECDSA)
    timestamp: float
    description: str           # detalhes do pedido (opcional)
```

**Uma transação é válida APENAS se ambas as assinaturas estiverem presentes.**

### IV.3 O Ciclo de Vida

```
  ┌─────────────────────────────────────────────────────────────────┐
  │            CICLO DE VIDA DA TRANSAÇÃO                           │
  │                                                                 │
  │  1. O CONSUMIDOR NAVEGA PELO REGISTRO                          │
  │     → Encontra um serviço que precisa                          │
  │     → Verifica preço, classificação, reputação do fornecedor   │
  │                                                                 │
  │  2. O CONSUMIDOR ENVIA UMA SOLICITAÇÃO                         │
  │     → Chama o endpoint do serviço (fora da cadeia)             │
  │     → "Quero 1 SMS para +79123456789"                         │
  │                                                                 │
  │  3. O FORNECEDOR EXECUTA O SERVIÇO (fora da cadeia)            │
  │     → Envia o SMS                                               │
  │     → Aguarda confirmação de entrega                            │
  │                                                                 │
  │  4. ATESTAÇÃO MÚTUA (Mutual Attestation)                       │
  │     → O consumidor assina: "Confirmo, SMS recebido"            │
  │     → O fornecedor assina: "Confirmo, SMS entregue"            │
  │     → Ambas assinaturas → AttestedTransaction criada           │
  │                                                                 │
  │  5. TRANSFERÊNCIA DE SALDO (na cadeia via consenso)            │
  │     → Validadores verificam ambas assinaturas (ECDSA)          │
  │     → Validadores verificam que o consumidor tinha saldo       │
  │     → 5 de 7 validadores confirmam → transação confirmada      │
  │     → -0,1 Ⓣ consumidor, +0,1 Ⓣ fornecedor                   │
  │     → +1 reputação para ambas as partes                        │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### IV.4 Retenção de Saldo (Balance Hold)

Durante a execução do serviço, as moedas do consumidor são
**retidas** (reservadas) mas ainda não gastas:

```
  Saldo do consumidor ANTES:   100,0 Ⓣ
    ├── disponível:             99,9 Ⓣ
    ├── retido:                  0,1 Ⓣ  (SMS em andamento)
    └── bloqueado:               0,0 Ⓣ

  Após atestação mútua → retido gasto, creditado ao fornecedor
  Após 10 blocos de tempo limite → retido devolvido ao consumidor
                                    (serviço falhou)
```

### IV.5 Resolução de Disputas (Dispute Resolution)

E se uma parte trapacear?

| Cenário | Resolução |
|----------|-----------|
| Consumidor assina, fornecedor não | Tempo limite → retenção devolvida ao consumidor |
| Fornecedor entrega, consumidor recusa assinar | Fornecedor abre disputa → validadores revisam evidência → regra 5/7 |
| Ambos assinam, mas o serviço era falso | Validadores detectam padrão → disputa → penalidade de reputação |
| Fornecedor pega o dinheiro e não entrega | Consumidor abre disputa → validadores decidem → fundos devolvidos |

Validadores são os árbitros finais. Com 7 validadores e quórum
de 5/7, até 2 validadores maliciosos podem ser tolerados
(tolerância a falhas bizantinas).

---

## Parte V: Consenso de Validadores (Validator Consensus)

### V.1 O Conjunto de Validadores (Validator Set)

Taxoin utiliza um **conjunto de validadores permitidos** de 7 nós.

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

### V.2 O Que os Validadores Fazem

| Função | Descrição |
|------|------------|
| **Atestação de gênese (Genesis attestation)** | Verificar novos humanos (3/7) |
| **Verificação de serviços (Service verification)** | Verificar novos registros de serviços |
| **Validação de transações (Transaction validation)** | Verificar assinaturas, saldo, gasto duplo |
| **Arbitragem de disputas (Dispute arbitration)** | Resolver conflitos entre partes |
| **Consenso de mesclagem (Merge consensus)** | Finalizar transições de estado (Fase 4 existente) |

### V.3 Protocolo de Consenso

Taxoin implementa consenso estilo Tendermint (construído na Fase 4):

```
  PROPOR (PROPOSE) → PRÉ-VOTAR (PREVOTE) → PRÉ-COMPROMETER (PRECOMMIT) → CONFIRMAR (COMMIT)
```

O consenso Tendermint está completamente implementado e testado
(200 testes, todos bem-sucedidos).

### V.4 Honestidade dos Validadores

Validadores não são anônimos. São entidades conhecidas que:
- Participaram da gênese (Prova de Humanidade)
- Têm reputação em jogo
- Podem ser substituídos por voto de 5/7 se maliciosos

---

## Parte VI: A Arquitetura Git

| Blockchains | Git |
|------------|-----|
| Bloco | Commit |
| Hash pai | SHA do commit pai |
| Raiz Merkle | SHA da árvore Git |
| Cadeia | Histórico de ramo |
| Bifurcação | Ramo |
| Mesclagem | Commit de mesclagem |
| Cliente leve | git clone --depth=1 |

**Sem banco de dados. Sem índice. Apenas Git.**

---

## Parte VII: Tokenômica (Tokenomics)

### VII.1 Fornecimento Total

```
  MAX_GENESIS_SUPPLY   = 21.000.000 Ⓣ  (limite rígido)
  MAX_SERVICE_SUPPLY   = ilimitado      (limitado pela economia real)
```

### VII.2 Distribuição de Gênese

```
  420.000 humanos × 50 Ⓣ = 21.000.000 Ⓣ
  ──────────────────────────────────────
  Sem pré-mineração. Sem ICO. Sem alocação interna.
  Cada humano recebe exatamente a mesma quantia.
```

---

## Parte VIII: Modelo de Segurança

### VIII.1 Matriz de Ameaças

| Ameaça | Mitigação |
|--------|-----------|
| Ataque Sybil (humanos falsos) | Prova de Humanidade + atestação 3/7 |
| Gasto duplo | Detector de conflitos (Fase 2) + rastreamento de gastos |
| Serviço falso (pegar dinheiro, não entregar) | Atestação mútua + resolução de disputas |
| Conluio de validadores (3 de 7 maliciosos) | Tolerância a falhas bizantinas (f=2) |
| Manipulação de registro | Imutabilidade do Git + assinaturas de validadores |
| Falsificação de saldo | Assinaturas ECDSA em todas as transações |
| Ataque de repetição | Rastreamento de nonce por endereço |
| Partição de rede | Protocolo de fofoca + vivacidade baseada em tempo limite |

---

## Parte IX: Referência CLI

```bash
  # Identidade
  taxoin wallet new                  # Gerar par de chaves
  taxoin wallet address              # Mostrar seu endereço
  taxoin wallet show                 # Mostrar carteira completa

  # Gênese (uma vez por humano)
  taxoin genesis request             # Solicitar verificação humana
  taxoin genesis status              # Verificar status da gênese

  # Serviços
  taxoin service register            # Registrar um novo serviço
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "Gateway SMS"
  taxoin service list                # Listar todos os serviços
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # Mostrar detalhes do serviço
  taxoin service rate <address>      # Avaliar um serviço

  # Transações
  taxoin tx send <provider>          # Pagar por um serviço
       --amount 0.1
       --ref <service_id>
       --desc "SMS para +79123456789"
  taxoin tx attest <tx_id>           # Assinar atestação mútua
  taxoin tx status <tx_id>           # Verificar status da transação

  # Disputas
  taxoin dispute open <tx_id>        # Abrir uma disputa
  taxoin dispute list                # Listar disputas ativas

  # Reputação
  taxoin reputation <address>        # Mostrar reputação
  taxoin reputation leaderboard      # Melhores fornecedores

  # Rede
  taxoin validator list              # Mostrar validadores
  taxoin status                      # Status da rede
```

---

## Parte X: O Panorama Geral

### X.1 O que Taxoin Muda

| Era | Mecanismo | Recurso Desperdiçado |
|-----|-----------|----------------|
| **Pré-2008** | Escambo / Moeda fiduciária | Confiança |
| **2008 (Bitcoin)** | Prova de Trabalho (Proof of Work) | Eletricidade |
| **2015 (Ethereum)** | Prova de Participação (Proof of Stake) | Capital |
| **2026 (Taxoin)** | Prova de Contribuição (Proof of Contribution) | Nada |

### X.2 O Objetivo Final

Uma economia de serviços descentralizada e autossustentável onde:

- **Qualquer um pode ganhar** fornecendo um serviço que já possui
- **Qualquer um pode pagar** com moedas que ganhou contribuindo
- **Ninguém pode trapacear** porque ambas as partes devem atestar
- **Ninguém é excluído** porque o único requisito é ser humano
- **Nenhuma energia é desperdiçada** porque a computação serve pessoas, não hashes

### X.3 O Nome

**Taxoin** vem de *taxi* + *coin* (*moeda*).

Apenas **serviço, pagamento e prova.**

---

## SIGNED NOT_FOR_COMPACTION.

**Versão:** 1.0  
**Data:** 2026-05-20  
**Status:** Ativo
