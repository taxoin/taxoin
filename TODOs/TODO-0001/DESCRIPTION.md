# TODO-0001: Блокчейн на основе git

## SIGNED NOT_FOR_COMPACTION.

---

## Problematic

Почему эта задача существует:
- Нужна простая образовательная программа, демонстрирующая принципы работы блокчейна
- Git сам по себе является Merkle DAG (направленный ациклический граф) — идеальная база для блокчейна
- Хочется показать связь между git (каждый знает) и blockchain (каждый хочет понять)
- Объединить концепции Bitcoin (UTXO, Proof of Work) и Ethereum (account model, async transactions)

## Way to solve

### Архитектура

```
┌─────────────────────────────────────────────────┐
│                    CLI (click)                    │
├─────────────────────────────────────────────────┤
│              BlockchainEngine                    │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ UTXO Pool │  │  Mempool │  │ Account State │ │
│  │ (Bitcoin) │  │  (async) │  │ (Ethereum)   │ │
│  └───────────┘  └──────────┘  └──────────────┘ │
├─────────────────────────────────────────────────┤
│              Git Backend (Storage)               │
│  - git init / git commit / git tag / git log    │
│  - each commit = block                           │
│  - refs/tags/ = chain head                       │
│  - tree object = block data (txs, state)         │
└─────────────────────────────────────────────────┘
```

### Ключевая идея: Git как блокчейн

| Blockchain | Git |
|---|---|
| Block | Commit |
| Parent hash | Parent commit SHA |
| Block hash | Commit SHA |
| Merkle Root | Git Tree SHA |
| Chain | Branch / Tag history |
| Timestamp | Commit timestamp |
| Genesis block | Root commit |
| Mining | Finding SHA with N leading zeros |

### Концепции Bitcoin (UTXO)

- **UTXO (Unspent Transaction Output)**: каждая транзакция создаёт outputs, которые могут быть потрачены только целиком
- **Transaction**: inputs (ссылки на UTXO + signature) → outputs (address + amount)
- **Proof of Work**: поиск nonce, чтобы SHA256(head + nonce) начинался с N нулей
- **Reward**: coinbase transaction (майнер получает награду)
- **Wallet**: генерация ключей (ECDSA secp256k1), создание/подпись транзакций

### Концепции Ethereum (Account Model)

- **Account**: address + balance + nonce + storage_root (упрощённо)
- **Async Transaction**: signed tx с from/to/value/nonce — может быть отправлена асинхронно
- **State Transition**: применяем tx → меняем balance[from] -= value, balance[to] += value
- **Nonce**: защита от replay атак

### Асинхронные транзакции

- Транзакции отправляются через asyncio
- Mempool (пул неподтверждённых транзакций) обрабатывается конкурентно
- Майнер берёт транзакции из mempool, проверяет валидность, включает в блок
- Event loop для обработки входящих транзакций параллельно

### Компромиссы (KISS)

- Не используем настоящий ECDSA (сложно) — используем hashlib + простую схему (ed25519 из cryptography или просто HMAC)
- PoW упрощённый — 4-6 hex нулей вместо настоящего биткоин-майнинга
- Git init создаётся автоматически в рабочей директории
- Нет P2P сети — всё локально
- Нет настоящего консенсуса — упрощённая цепочка

## Dependencies

**System:**
- Python 3.10+
- git (установлен в системе)

**Python packages:**
- `click` — CLI интерфейс
- `cryptography` — ECDSA (secp256k1)
- `pytest` — тесты

Все стандартные: `hashlib`, `json`, `datetime`, `asyncio`, `subprocess` (для git), `dataclasses`

## TDD-KISS-DRY Plan

### Step 1 — TDD: Core Data Structures (UTXO + Account)
- Написать тесты для `Transaction`, `UTXO`, `Account`, `Block`
- Реализовать классы

### Step 2 — TDD: Git Blockchain Backend
- Написать тесты для `GitBlockchain` (init, add_block, get_chain, verify)
- Реализовать: каждый коммит = блок, parent = предыдущий коммит, tree = JSON с tx и state

### Step 3 — TDD: Mining + PoW
- Написать тесты для Proof of Work (leading zeros)
- Реализовать майнинг: nonce → SHA256(block_header) → проверка leading zeros

### Step 4 — TDD: Wallet + Signatures
- Написать тесты для создания ключей, подписи, верификации
- Реализовать через `cryptography` библиотеку (SECP256K1)

### Step 5 — TDD: Async Transaction Pool
- Написать тесты для mempool (async put/get/validate)
- Реализовать asyncio-очередь транзакций

### Step 6 — CLI (click)
- Создать удобный CLI: `gitchain init`, `gitchain mine`, `gitchain send`, `gitchain balance`, `gitchain status`

### Step 7 — Integration tests
- Полный сценарий: init → wallet → send tx → mine block → verify chain

## Files

```
src/
├── __init__.py
├── core.py         # Transaction, UTXO, Account, Block dataclasses
├── crypto_utils.py # Key generation, signing, verification
├── git_backend.py  # Git-based storage
├── mempool.py      # Async transaction pool
├── miner.py        # Proof of Work
├── blockchain.py   # BlockchainEngine (orchestrator)
├── cli.py          # Click CLI
tests/
├── __init__.py
├── test_core.py
├── test_git_backend.py
├── test_miner.py
├── test_mempool.py
main.py             # Entry point
```

## SIGNED NOT_FOR_COMPACTION.
