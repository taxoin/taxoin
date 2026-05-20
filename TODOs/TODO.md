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

## Completed

### ✅ TODO-0001: Блокчейн на основе git

**Goal:** Базовый блокчейн UTXO + Account model на git  
**Tests:** 67 | **Status:** ✅ COMPLETED

### ✅ TODO-0002: Параллельные ветвления транзакций с консенсусом

**Goal:** Parallel branching + BFT consensus (6 phases, 200 tests)  
**Tests:** 200 | **Status:** ✅ COMPLETED

---

## In Progress

### 🎯 TODO-0003: Proof of Contribution — Service Economy

**Status:** 📋 DESCRIPTION PHASE  
**Branch:** `feature/proof-of-contribution`  
**Goal:** PoW → Proof of Contribution. Genesis, Service Registry, Mutual Attestation, Balance Hold, Reputation  
**Tests:** 256 (core + mvp)  
**Components:** `genesis.py`, `service_registry.py`, `attested_tx.py`, `reputation.py`

**Implementation:** MVP core done (mvp-v3). Needs integration + polish.

---

### 🔬 TODO-0004: Research & Improvements

**Status:** 🔬 RESEARCH PHASE  
**Goal:** Улучшение Taxoin на основе анализа конкурентов, криптографии и UX

| ID | Тема | Приоритет | Статус |
|----|------|-----------|--------|
| **0004A** | Rating Formula — Bayesian average, time decay, anti-manipulation | 🟡 | 📝 Spec |
| **0004B** | Dispute Resolution — arbitrator, 5/7, timeout, evidence | 🔴 | 📝 Spec |
| **0004C** | UX — seamless mutual attestation, relay, QR | 🟡 | 📝 Spec |
| **0004D** | ZK-Reputation — private layer via Noir/UniRep | 🔵 | 📝 Spec |
| **0004E** | Cognitive PoW — AI-hard prompts for agents | ⚪ | ✅ Documented |
| **0004F** | Technical Wishlist — constitution, sharding, mobile, formal verif | 🔵 | 📝 Spec |
| **0004G** | 🆕 **Path to Public** — Docker, REST API, Telegram Wallet, QR | 🔴 **P0** | 🚀 **Start here** |
| **0004H** | **Throughput** — batch commits, LevelDB, async git | 🟡 **P1** | 📝 Spec |
| **0004I** | **Repo Strategy** — code vs blockchain, dual-repo backup | 🟡 **P1** | 📝 Spec |
| **0004J** | **Mainnet Launch** — node requirements, phases, validator recruitment | 🟡 **P1** | 📝 Spec |

### 🚀 TODO-0004G: Path to Public (первая задача к реализации)

**Goal:** Чтобы любой бизнес (таксопарк, парикмахерская, биржа труда)
мот скачать-поставить-запустить Taxoin за 5 минут.

**Что делаем (1 день):**
```
Шаг 1: Docker Compose (3 валидатора + API gateway)
       → docker compose up = готовая сеть
Шаг 2: REST API (FastAPI)
       → POST/GET для wallet, balance, tx, services
Шаг 3: Telegram Mini App
       → кошелёк прямо в Telegram (никаких установок)
Шаг 4: QR-платежи
       → платить как в Сбербанке
Шаг 5: Документация + deploy
       → README, OpenAPI, примеры для бизнеса
```

**Детали:** `TODOs/TODO-0004/TODO-0004G_PATH_TO_PUBLIC.md`

---

## Stack Reference

```
Source:   src/ (18 модулей)
Tests:    tests/ (256 passed)
Storage:  Git backend + JSON persistence
Consensus: Tendermint 5/7 (BFT f=2)
Economy:  Proof of Contribution + Mutual Attestation
Tags:     mvp-v1, mvp-v2, mvp-v3, architecture-v1, research-v1
