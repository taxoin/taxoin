# TODO-0004F: Technical Wishlist — Mobile Blockchain & Distributed Consensus

> Детализированный технический wishlist для мобильного блокчейна
> с распределённым подтверждением транзакций.

---

## 1. Иммутабельность и управляемость алгоритма

### Проблема
Если алгоритм можно легко поменять — система уязвима к захвату.
Если нельзя — она не эволюционирует и умирает.

### Предлагаемое решение: двухслойная архитектура протокола

**Constitution Layer** (конституция) — меняется крайне редко:
- supermajority hard fork (80–90% стейкинга + 70% активных нод)
- время принятия: 3–6 месяцев
- содержит: базовые принципы, monetary policy, governance rules

**Protocol Layer** — операционные правила:
- fee structure, block size, consensus parameters
- on-chain governance с мягкими форками
- обновляется без хардфорка

### Механизмы governance
- Quadratic Voting + Conviction Voting
- Time-lock + delayed execution (30–90 дней до вступления)
- Emergency pause / kill-switch для критических багов (многоуровневое подтверждение)
- User sovereignty: каждый клиент выбирает версию протокола (fork-choice rule)

---

## 2. Контроль и борьба с централизацией

### P2P архитектура
- Kademlia DHT + Gossip protocol (libp2p или аналог)
- Bootstrap через децентрализованные механизмы (IPFS + ENS-подобные имена)

### Верификация нод
- Публичный ключ + proof-of-stake / proof-of-resource для каждой ноды
- Random sampling: периодическая проверка случайных частей данных
- Reproducible builds + deterministic compilation (пользователь может собрать и сравнить хэш)
- Ограничение влияния крупных игроков (stake weighting с diminishing returns)

---

## 3. Экономическая модель и мотивация

### Ключевой вопрос: кто будет делать «грязную работу»?

### Многоуровневая система вознаграждений
| Уровень | Что вознаграждается |
|---------|-------------------|
| Staking | Хранение и доступность |
| Validation | Проверка транзакций и блоков |
| Data Availability | Хранение шардов |
| Reputation | Долгосрочный бонус за честное поведение |

### Delegated Resource Model
- Пользователь делегирует ресурсы телефона (батарея, storage, bandwidth)
- «Профессиональным» нодам
- Получает долю вознаграждения

### Taxoin-экономика
- Utility-токен (оплата газа)
- Governance-токен (управление)
- Возможно: неинфляционная модель или низкая контролируемая эмиссия

---

## 4. Технические ограничения мобильных устройств

### Light-first дизайн
- Большинство пользователей → Ultra-light clients
- zk-SNARKs / STARKs для верификации состояний без хранения всего блокчейна
- Data sharding + Random Sampling (Celestia / danksharding подход)

### Хранение
- Pruning + Archive nodes (только небольшая часть нод хранит полную историю)
- IPFS / Arweave-подобное децентрализованное хранилище для off-chain данных

### Энергопотребление
- Adaptive sync: синхронизация только по Wi-Fi + при зарядке > 30%
- Background tasks с WorkManager (Android) / BackgroundTasks (iOS)
- Sleep mode для ноды, пробуждение только при необходимости

### Offline-first
- Транзакции создаются локально
- Попадают в сеть при появлении соединения
- Мемпул с TTL + защита от спама

---

## 5. Безопасность и доверие к коду

- Полностью Open Source
- Регулярные внешние аудиты + bug bounty (высокие награды в токенах)
- Постепенный rollout обновлений: canary releases (1% → 10% → 100%)
- Формальная верификация критических частей: TLA+, Coq, Lean
- Многосигнатурные мультисиг-кошельки для важных контрактов/параметров

---

## 6. TTL-транзакций и «сгорание»

- TTL по умолчанию (7–30 дней)
- Пользователь может установить свой TTL (повышенная комиссия)
- Anti-DoS: лимит pending-транзакций на аккаунт + минимальная плата
- Плата сжигается даже при экспирации
- Прозрачные правила: параметры TTL в genesis/constitution layer

---

## 7. Философские и системные улучшения

- Чёткое разделение «деньги» и «ценности» (несколько типов токенов или репутационных баллов)
- Механизмы защиты от гиперинфляции
- Простой и понятный UI/UX (критично для массового adoption)
- Real-world integrations: proof-of-humanity, proof-of-location, proof-of-attendance

---

## Сравнение с текущей архитектурой Taxoin

| Wishlist | Taxoin сегодня | Статус |
|----------|---------------|--------|
| Constitution Layer | Нет | ❌ |
| On-chain governance | Нет (валидаторы 5/7) | 🟡 Частично |
| Quadratic Voting | Нет | ❌ |
| Mobile light client | Нет (CLI только) | ❌ |
| zk-верификация | Нет | ❌ (TODO-0004D) |
| Data sharding | Нет | ❌ |
| Adaptive sync | Нет | ❌ |
| Offline-first | Нет | ❌ |
| Formal verification | Нет | ❌ |
| Bug bounty | Нет | ❌ |
| TTL транзакций | Только timeout (10 блоков) | 🟡 Частично |
| Utility vs Governance токены | Нет | ❌ |
| Delegated Resource Model | Нет | ❌ |
| UI/UX | CLI only | ❌ |

---

## Приоритеты имплементации

| Приоритет | Что делать |
|-----------|-----------|
| 🔴 P0 | Formal verification consensus, Bug bounty, Open source audit |
| 🟡 P1 | TTL транзакций, Constitution Layer, Governance |
| 🟢 P2 | Mobile light client, Adaptive sync, Offline-first |
| 🔵 P3 | zk-верификация, Data sharding, Delegated Resource Model |
| ⚪ P4 | Quadratic Voting, Real-world integrations, UI/UX |
