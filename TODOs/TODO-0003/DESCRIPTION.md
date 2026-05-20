# TODO-0003: Proof of Contribution — Service Economy

## SIGNED NOT_FOR_COMPACTION.

---

## Problematic

Почему эта задача существует:

1. **PoW бесполезен** — сжигает CPU-циклы, не создавая ценности. Майнинг = бессмысленный расчёт хэшей.

2. **Coinbase из воздуха** — 50Ⓣ за блок без обеспечения. Нет связи между эмиссией и реальной ценностью.

3. **Нет экономической модели** — Taxoin не на что тратить. Монеты копятся, но не имеют применения внутри системы.

4. **Уникальность упущена** — блокчейн идеально подходит для peer-to-peer расчётов, но мы используем его только как "распределённый реестр", а не как "распределённый рынок."

---

## Way to solve

### Концепция: Taxoin = единица доказанного вклада

> CPU-циклы → работа. PoW (бесполезный) → Proof of Contribution (полезный).

```
СТАРАЯ МОДЕЛЬ (Bitcoin):
  Майнер считает хэши (бесполезно) → расходует энергию → получает 50Ⓣ

НОВАЯ МОДЕЛЬ (Taxoin):
  Участник предоставляет сервис (полезно) → получает Ⓣ от благополучателей
  └── SMS-шлюз, GPU-расчёт, такси, API-доступ, обучение модели и т.д.
```

### Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                      TAXOIN v2.0                                │
│              Proof of Contribution Network                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Provider A  │  │  Provider B  │  │  Consumer C  │
│  (SMS-шлюз)  │  │  (GPU-farm)  │  │  (клиент)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │ register_service()                │
       ├──────────────────────────────────▶│
       │                 │                 │
       │                 │ discover()      │
       │                 ├────────────────>│
       │                 │                 │
       │                 │ consume_service(tx) │
       │                 │<────────────────┤
       │                 │ attest_both()   │
       │                 │<───────────────>│
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ValidatorNetwork (5/7)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Validator1│  │Validator2│  │Validator3│  │Validator4│  ...  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       │  validate_tx (attestation, balance, fraud)             │
│       │<────────────│<────────────│<────────────│              │
│       │             │             │             │              │
│       │  5/7 confirm → commit                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Жизненный цикл транзакции

```
1. REGISTER SERVICE
   Provider → git commit
   ├── Тип сервиса: sms, compute, taxi, api, ...
   ├── Цена: 0.1 Ⓣ/unit
   ├── Описание: что и как предоставляется
   └── Валидаторы верифицируют (5/7) → сервис в реестре

2. DISCOVER
   Consumer → git реестр
   ├── "Покажи все SMS-шлюзы с рейтингом > 4.0"
   └── Выбирает: Provider A (0.1Ⓣ/sms, рейтинг 4.8)

3. CONSUME + ATTEST
   Consumer вызывает сервис → Provider исполняет
   ├── Consumer: -0.1Ⓣ (hold на балансе валидатора)
   ├── Provider: исполняет заказ (отправляет SMS)
   ├── Mutual attestation: обе стороны подписывают:
   │   └── "Заказ выполнен" (подпись Consumer)
   │   └── "Я предоставил услугу" (подпись Provider)
   └── Транзакция в mempool → ожидает мержа

4. VALIDATE & COMMIT
   ValidatorNetwork:
   ├── 5/7 валидаторов проверяют:
   │   ├── Обе подписи присутствуют (mutual attestation)
   │   ├── У Consumer был баланс на момент запроса
   │   ├── Нет конфликта (double-spend, nonce)
   │   └── Сервис зарегистрирован в реестре
   ├── Консенсус (готов, Phase 4):
   │   └── 5/7 голосуют YES → финализация
   └── Git merge: балансы обновлены
```

---

## Ключевые механики

### 1. Genesis — 1M Ⓣ для основателей

```python
GENESIS_SUPPLY = 1_000_000  # 1M Ⓣ
GENESIS_VALIDATORS = 7      # первые 7 валидаторов
# Каждый получает ≈ 142_857 Ⓣ при genesis
```

❌ **Нет "бесплатных" монет для новых участников.**
✅ **Каждый Taxoin заработан вкладом или получен от того, кто заработал.**

**Новый участник:** начинает с 0Ⓣ. Предлагает сервис. Получает первые Ⓣ от потребителей. Если сервис востребован — зарабатывает.

**Микрокредиты** (опционально): существующие участники могут выдать кредит новичку под его будущие услуги.

### 2. Service Registry — реестр сервисов

```python
@dataclass
class ServiceRegistration:
    provider: str               # address владельца
    service_type: ServiceType   # SMS | GPU | API | TAXI | ...
    price_per_unit: float       # Ⓣ за единицу
    description: str            # что предоставляется
    endpoint: str               # как вызвать (URL, API, контакт)
    attested_by: list[str]      # кто подтвердил (5/7 валидаторов)
    created_at: float
    rating: float = 0.0
    total_tx: int = 0
```

**Хранение:** git notes на корневом коммите (аналогично branch metadata).
**Верификация:** валидаторы проверяют что сервис реально работает перед регистрацией.

### 3. Mutual Attestation — обоюдная подпись

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str           # кто платит
    provider: str           # кто предоставляет
    service: str            # ссылка на ServiceRegistration
    amount: float           # Ⓣ за эту транзакцию
    consumer_sig: str       # "Я получил услугу" (ECDSA)
    provider_sig: str       # "Я предоставил услугу" (ECDSA)
    timestamp: float
    description: str        # детали заказа (опционально)
```

**Критическое правило:** транзакция считается валидной ТОЛЬКО если обе подписи присутствуют. Одна подпись → спор → арбитраж валидаторов.

### 4. Balance Hold — резервирование средств

Когда Consumer вызывает сервис, Ⓣ резервируются, но не списываются:

```
Consumer balance:  100.0 Ⓣ
  ├── available:    99.3 Ⓣ
  ├── held:          0.7 Ⓣ  (текущие заказы в обработке)
  └── locked:        0.0 Ⓣ  (timelock-контракты)
```

После mutual attestation: held → списывается, зачисляется Provider'у.
После таймаута (10 блоков): held → возвращается Consumer'у (заказ не выполнен).

### 5. Репутация (Reputation)

```python
@dataclass
class Reputation:
    address: str
    total_tx: int                   # всего транзакций
    successful_tx: int              # успешно выполненных
    disputes: int                   # споров (решено валидаторами)
    rating: float                   # weighted average отзывов
    tokens_earned: float            # всего заработано Ⓣ
```

**Формула рейтинга:**
```python
rating = (successful_tx / max(total_tx, 1)) * 5.0
         - (disputes * 0.5)  # штраф за споры
```

Репутация влияет:
- Выше рейтинг → сервис показывается выше в discover
- Ниже рейтинг → выше шанс что валидаторы проверят транзакцию
- Рейтинг < 1.0 → сервис временно блокируется

---

## Изменения в коде

### Новые модули

```
src/
├── service_registry.py     # Service Registration + Registry
├── attested_tx.py          # AttestedTransaction + validation
├── reputation.py           # Reputation tracking
├── balance_hold.py         # Balance hold / escrow
└── genesis.py              # Genesis distribution
```

### Изменяемые модули

| Модуль | Что меняется |
|--------|-------------|
| `src/core.py` | Новые типы: `AttestedTransaction`, `ServiceRegistration` |
| `src/branch_manager.py` | Убрать PoW. Добавить `register_service()`, `attested_transfer()` |
| `src/consensus.py` | Валидация mutual attestation (5/7 проверяют подписи) |
| `src/conflict_detector.py` | Проверка holds/disputes |
| `src/miner.py` | Deprecated (убрать PoW) |
| `src/branch_state.py` | Balance hold, disputed transactions |

---

## Что НЕ меняется (работает как есть)

- ✅ **ValidatorNetwork** (Phase 3) — 7 валидаторов, голосование
- ✅ **MergeConsensus** (Phase 4) — 5/7 quorum, commit flow
- ✅ **GitBackend** (Phase 1) — commit-based storage
- ✅ **BranchState** (Phase 1) — state isolation
- ✅ **GossipProtocol** (Phase 5) — message propagation
- ✅ **CLI base** (Phase 6) — команды, click groups

---

## Success Criteria

1. [ ] Genesis: 1M Ⓣ распределены между 7 валидаторами
2. [ ] Service Registry: регистрация + верификация сервиса
3. [ ] Attested Transaction: обоюдная подпись, валидация
4. [ ] Balance Hold: резервирование + таймаут возврата
5. [ ] Reputation: рейтинг, влияние на discover
6. [ ] Validator arbitration: решение споров
7. [ ] PoW удалён из codebase
8. [ ] 60-80 новых тестов
9. [ ] Full CLI: `service register`, `service list`, `tx send`, `tx attest`

---

## SIGNED NOT_FOR_COMPACTION.
