# TODO — Active Tasks

> SIGNED NOT_FOR_COMPACTION. Single point of truth for all active work.

---

## Rules

1. Every new task gets a unique `TODO-XXXX` identifier
2. Every task gets a full description dir `TODOs/TODO-XXXX/` with:
   - problematic (why this task exists)
   - way to solve (approach/plan)
   - all system dependencies
3. Every task is planned with **TDD-KISS-DRY** principles
4. Never split mind — one TODO at a time
5. All steps documented in the TODO dir
6. Only after finishing the description of a TODO it is allowed to start execution
7. Errors and problems → document in TODO dir first, analyze, then proceed
8. Moving to DONE requires a **closure stamp**: `SIGNED NOT_FOR_COMPACTION. [date] [time] [model-id]`
9. DONE.md is read as a well-tested knowledge base — extend skills continuously

---

## Active Tasks

### TODO-0001: Блокчейн на основе git

**Status:** ✅ COMPLETED  
**Goal:** Реализовать простую программу блокчейна, использующую git как бэкенд, с базовыми концепциями Bitcoin (UTXO, PoW) и Ethereum (account model, async transactions)  
**Components:** `src/blockchain.py`, `src/wallet.py`, `src/cli.py`, `tests/`

**Completion Summary:**
- ✅ All 7 steps completed (TDD approach)
- ✅ 67 tests passing (including 9 integration tests)
- ✅ Full end-to-end scenarios tested
- ✅ Bug fixed: transaction state application in mining

---

### TODO-0002: Параллельные ветвления транзакций с консенсусом

**Status:** 📋 DESCRIPTION PHASE  
**Branch:** `feature/parallel-branching`  
**Goal:** Реализовать параллельную обработку транзакций через git-ветки с Byzantine Fault Tolerant консенсусом для слияния  

**Key Features:**
- Каждый кошелёк создаёт независимую ветку для транзакций
- Неограниченный параллельный процессинг (no blocking)
- Автоматическая детекция конфликтов (UTXO, nonce, balance)
- Tendermint-style консенсус (7 валидаторов, 2f+1 quorum)
- Гарантия целостности и непротиворечивости через BFT

**Components:** 
- `src/branch_manager.py` — управление ветками
- `src/validator_network.py` — сеть валидаторов
- `src/consensus.py` — Tendermint консенсус
- `src/conflict_detector.py` — детекция конфликтов
- `src/gossip_protocol.py` — распространение сообщений

**Implementation Plan:** 6 phases completed, 200 tests. Full parallel branching with BFT consensus.

---

### TODO-0003: Monetary Policy, Timelocks & Tiny Script

**Status:** 📋 DESCRIPTION PHASE  
**Branch:** `brainstorm/taxoin-architecture`  
**Goal:** Реализовать прозрачную монетарную политику (Bitcoin-style 21M cap), UTXO timelocks, и Tiny Script VM для смарт-контрактов

**Key Features:**
- Прозрачная эмиссия: халвинг каждые 210K блоков, кап 21M Taxoin
- Отказ от PoW — блоки подписываются валидаторами
- UTXO timelocks — временна́я блокировка средств (блокировка до высоты N)
- Tiny Script — 15-20 стековых опкодов, без циклов, детерминизм
- Contract storage — изолированное KV-хранилище для контрактов
- Исполнение контрактов валидаторами при consensus (5/7 голосов)

**Components:**
- `src/monetary_policy.py` — MonetaryPolicy (supply, halving, cap)
- `src/tiny_script.py` — TinyVM (execute, opcodes, storage)
- `src/tiny_opcodes.py` — Opcode enum + definitions
- `src/core.py` — UTXO.timelock, Opcode types
- `src/branch_state.py` — contract_storage, locked_balance

**Implementation Plan:** 6 phases, 60-80 tests, TDD approach

