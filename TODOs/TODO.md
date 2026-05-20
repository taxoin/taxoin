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

**Status:** ✅ COMPLETED  
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

### TODO-0003: Proof of Contribution — Service Economy

**Status:** 📋 DESCRIPTION PHASE  
**Branch:** `feature/proof-of-contribution`  
**Goal:** Заменить бесполезный PoW на Proof of Contribution — экономику полезных сервисов (SMS, GPU, API, такси), где каждый Taxoin заработан реальным вкладом

**Key Features:**
- PoW → Proof of Contribution: майнинг CPU заменён на предоставление сервисов
- Genesis: 1M Ⓣ для 7 основателей, дальнейшая эмиссия только через сервисы
- Service Registry: git-based реестр всех сервисов с ценами и рейтингом
- Mutual Attestation: обоюдная подпись (provider + consumer) для каждой транзакции
- Balance Hold: резервирование Ⓣ на время выполнения заказа
- Reputation: рейтинговая система для защиты от спама и мошенников

**Components:**
- `src/service_registry.py` — реестр сервисов + регистрация
- `src/attested_tx.py` — обоюдноподписанные транзакции
- `src/reputation.py` — рейтинг и репутация
- `src/balance_hold.py` — резервирование баланса
- `src/genesis.py` — начальное распределение 1M Ⓣ

**Implementation Plan:** 5 phases, 60-80 tests, TDD approach

---

### TODO-0004: Research & Improvements

**Status:** 🔬 RESEARCH PHASE  
**Goal:** Улучшение Taxoin на основе анализа конкурентов, криптографии и UX

**Sub-tasks:**

- **0004A: Rating Formula** — Bayesian average, time decay, anti-manipulation
  → `TODOs/TODO-0004/TODO-0004A_RATING.md`
  
- **0004B: Dispute Resolution** — arbitrator, 5/7 verdict, timeout, evidence
  → `TODOs/TODO-0004/TODO-0004B_DISPUTES.md`
  
- **0004C: UX — Mutual Attestation** — seamless signing, relay, QR
  → `TODOs/TODO-0004/TODO-0004C_UX.md`
  
- **0004D: ZK-Reputation** — private reputation layer (Noir, UniRep)
  → `TODOs/TODO-0004/TODO-0004D_ZK.md`

