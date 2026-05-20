# Taxoin Throughput: VPS Capacity Analysis

## Архитектура (текущая)

```
Клиент → FastAPI (uvicorn) → BranchManager (dict) → Git (.taxoin/.git)
                                          ↑
                                    Validator Consensus (in-process)
```

## Пропускная способность по слоям

### Layer 1: API (FastAPI)

| Операция | Время | TPS (1 core) | TPS (4 core) |
|----------|-------|-------------|-------------|
| GET /api/balance | ~0.5ms | 2,000 | 8,000 |
| POST /api/wallet | ~2ms (ECDSA gen) | 500 | 2,000 |
| GET /api/status | ~1ms | 1,000 | 4,000 |
| GET /api/services | ~0.5ms | 2,000 | 8,000 |

✅ API — не узкое место

### Layer 2: Транзакции (AttestedTransaction)

| Шаг | Время |
|-----|-------|
| Создание tx (in-memory) | ~0.01ms |
| ECDSA verify (2 подписи) | ~1ms |
| Balance check (dict lookup) | ~0.001ms |
| Conflict detection | ~0.01ms |
| **Итого на tx** | **~1ms** |

✅ 1000 tx/s чисто по логике

### Layer 3: Git commit (узкое место)

```
Блок = git add .taxoin/block.json + git commit
```

| Операция | Время | TPS |
|----------|-------|-----|
| git add (1 файл) | ~5ms | 200 |
| git commit | ~15-30ms | 33-66 |
| git notes add | ~10ms | 100 |
| **Итого на блок** | **~30-50ms** | **20-33 TPS** |

❌ **Git commit — узкое место.** 20-33 блока/сек — потолок.

### Layer 4: Validator Consensus

```
3-7 валидоров, все in-process. Консенсус ~5ms на раунд.
Не узкое место (пока сеть не распределённая).
```

## Реалистичные цифры для VPS (2 core, 4GB RAM)

| Сценарий | Макс | Комфортно |
|----------|------|-----------|
| **Чтение баланса** | 8,000 req/s | 2,000 req/s |
| **Создание кошелька** | 2,000 req/s | 500 req/s |
| **Отправка tx (чтение)** | 33 tx/s | 10 tx/s |
| **Отправка tx (пакетная)** | 100 tx/s | 30 tx/s |
| **Регистрация услуги** | 100 req/s | 30 req/s |
| **Одновременных пользователей** | 5,000 | 500 |

## Сравнение

| Сеть | TPS | Архитектура |
|------|-----|-------------|
| **Bitcoin** | ~7 | PoW, UTXO |
| **Ethereum** | ~15 | EVM, Account |
| **Taxoin (сейчас)** | **~33** | Git + in-memory |
| **Taxoin (с batch)** | **~100** | Batch commits |
| Visa | ~24,000 | Centralized |

## Как улучшить (TODO)

| Улучшение | Прирост | Сложность |
|-----------|---------|-----------|
| **Batch commits** (1 git commit = N tx) | 33 → 100 TPS | 🟢 Низкая |
| **Async git** (celery/rq для git write) | 100 → 200 TPS | 🟡 Средняя |
| **Убрать state snapshot из каждого блока** | +50% | 🟢 Низкая |
| **Incremental state** (не full snapshot) | +100% | 🟡 Средняя |
| **LevelDB/SQLite вместо git** | 200 → 10,000 TPS | 🔴 Высокая |
| **Sharding** (N нод × M шардов) | 10,000 → ∞ | 🔴 Очень высокая |

## Вывод

> **33 TPS сейчас.** Для таксопарка с 100 поездками/день — хватит с запасом.
> Для Visa-level — нужно менять git на LevelDB/SQLite.

```
VPS 2 vCPU / 4GB RAM / SSD:
  • READ:   2,000+ запросов/сек
  • WRITE:    33 транзакции/сек
  • USERS:   500 одновременных
  • COST:    ~$10-20/мес (Hetnzer, DigitalOcean)

  Запас для бизнеса:
  • Таксопарк (50 машин):        ~500 tx/день  → 0.5% capacity
  • Парикмахерская (1 мастер):    ~20 tx/день  → 0.02% capacity
  • Город (1000 бизнесов):        ~50,000 tx/день → ~1.7% capacity
```
