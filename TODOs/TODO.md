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

