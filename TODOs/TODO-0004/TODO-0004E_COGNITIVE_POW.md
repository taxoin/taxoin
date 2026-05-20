# TODO-0004E: Cognitive Proof-of-Work (AI-hard Prompts)

## Фундаментальная проблема

Как отличить **настоящее мышление/рассуждение** ИИ от **статистического
воспроизведения паттернов** (cached answer)?

TL;DR: **Нельзя гарантировать «настоящее мышление» простым промптом.**
LLM всегда генерирует токены вероятностно, не "доказывает работу"
как Bitcoin. Но можно создать задачу, где cached-answer невозможен,
shallow-pattern matching ломается, и модель вынуждена:
- строить новые структуры
- удерживать много ограничений
- оптимизировать trade-offs
- проводить search в latent space
- синтезировать новое

**Это и есть когнитивный Proof-of-Work (Cognitive PoW).**

---

## Что делает задачу «по-настоящему трудной» для ИИ

### 1. Несовместимые ограничения одновременно

❌ Плохо: `"придумай экономику"` — кэшируется
✅ Хорошо: `"создай экономику: без спекуляции, без централизации, с privacy,
   с Sybil resistance, без biometrics, с mobile UX, совместимую с GDPR,
   масштабируемую до 1B users, без trusted validators, resistant to AI bots,
   без PoW, без staking plutocracy"`

Модель вынуждена: искать компромиссы, архитектурный search, reasoning
над противоречиями.

### 2. Требование attack models

Ломает поверхностные ответы. Надо: самому разрушить свою архитектуру,
найти exploit paths, искать edge cases.

Пример: `"для каждого механизма: придумай 10 атак, оцени стоимость атаки,
          предложи mitigations, найди residual risk"`

### 3. Self-critique

`"после каждого раздела: объясни, почему решение может не сработать,
 что в нём наивно, какие hidden assumptions"` — ломает режим
«маркетингового текста».

### 4. Генерация новых formal systems

`"изобрети новый consensus algorithm, новую reputation algebra,
 новый anti-collusion primitive"` — особенно с запретом известных
механизмов (PoW, PoS, PBFT, stake slashing, web-of-trust и т.д.).

### 5. Internal consistency proofs

`"докажи, что система не создаёт infinite inflation, collusion невыгоден,
 reputation converges, attack cost > extractable value"`

### 6. Requirement of simulations

`"прогони: 1000 пользователей, 40% malicious actors, cartel formation,
 fake services, AI bot swarm, reputation farming"`

### 7. Novel composition

Объединение economics + cryptography + UX + law + sociology + AI safety +
distributed systems + governance — почти нет готовых шаблонов.

---

## Формула «Hard Cognitive PoW Prompt»

```
1. Impossible-seeming goal
   "создай антиспекулятивную глобальную экономику"

2. Many conflicting constraints
   privacy + anti-fraud + decentralization + UX + no biometrics + AI resistance

3. Explicit attack requirements
   "сломай собственную систему"

4. Forced trade-offs
   "нельзя максимизировать всё"

5. Mathematical invariants
   "докажи устойчивость"

6. Multi-domain integration
   economics + zk + governance + psychology + distributed systems

7. Demand architectural novelty
   "не используй известные механизмы"
```

---

## Пример ultra-hard промпта

```
Создай полностью новую глобальную economic coordination system
для AI-эры.

Запрещено использовать:
PoW, PoS, fiat, KYC, biometrics, centralized identity,
classic reputation systems, quadratic voting, proof-of-humanity,
trusted validators, DAO token voting.

Система должна одновременно обеспечивать:
Sybil resistance, privacy, anti-speculation, resistance to AI agents,
global scalability, instant UX, legal survivability,
collusion resistance, contribution accounting, fair governance.

Для каждого механизма:
- опиши attack vectors
- проведи game-theory analysis
- оцени equilibrium behavior
- найди collapse scenarios
- предложи mitigations

Затем:
- докажи, почему система может не работать
- укажи hidden assumptions
- оцени вероятность failure
- сравни с Bitcoin/Ethereum/Worldcoin

Наконец:
- предложи radically simplified version
- выдели минимально необходимое ядро
- удали всё лишнее
```

---

## Почему это — аналог Proof-of-Work для ИИ

| Bitcoin PoW | Cognitive PoW |
|------------|---------------|
| SHA256 хэши | Constrained synthesis |
| Nonce search | Architecture search |
| Difficulty target | Constraint satisfaction |
| Block reward | Coherent novel system |
| Energy consumption | Cognitive computation |

Нельзя выдать готовый cached-answer.
Нет "правильного" решения.
Нужно делать search, удерживать constraints,
строить новую структуру, проверять consistency.

**Это expensive cognition.**

---

## Применение в Taxoin

При создании агентов для Taxoin (TODO-0003 и далее)
использовать Cognitive PoW промпты:

- **Архитектура:** `"спроектируй систему с 10+ несовместимыми
   ограничениями, сломай её, защити, докажи устойчивость"`
- **Экономика:** `"создай монетарную политику без инфляции,
   без дефляции, без стейкинга, без майнинга, с bounded supply,
   с реальным обеспечением"`
- **Консенсус:** `"изобрети новый BFT-алгоритм без leader,
   без round-robin, без PoS, без PBFT"`
- **Security:** `"найди 10 атак на Taxoin, предложи mitigation,
   докажи что residual risk < 0.1%"`

---

## Принципы для разработчиков-агентов

1. **Требуй multi-step reasoning** — не принимай первый ответ
2. **Требуй self-critique** — "почему это может не сработать?"
3. **Требуй attack models** — "сломай собственную архитектуру"
4. **Требуй trade-offs** — "что ты sacrificed?"
5. **Требуй invariants** — "докажи что свойство X сохраняется"
6. **Запрещай известные решения** — "не используй X, Y, Z"
7. **Требуй synthesis** — объедини economics + crypto + law + sociology

---

## SIGNED NOT_FOR_COMPACTION.

Это не спецификация кода. Это **спецификация мышления**
для всех агентов, работающих над Taxoin.

Cognitive PoW — единственный способ гарантировать,
что ИИ *действительно думал*, а не *вспомнил*.
