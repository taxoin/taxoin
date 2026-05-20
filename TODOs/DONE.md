# DONE — Completed Tasks

> SIGNED NOT_FOR_COMPACTION. Knowledge base of solved problems.

---

## Closure Log

### TODO-0001: Блокчейн на основе git

**Completed:** 2026-05-20 04:21 UTC  
**Model:** kr/claude-sonnet-4-5

**What was built:**
- Git-backed blockchain combining Bitcoin (UTXO, PoW) and Ethereum (account model, async transactions) concepts
- 7 core modules: `core.py`, `crypto_utils.py`, `git_backend.py`, `mempool.py`, `miner.py`, `blockchain.py`, `cli.py`
- Comprehensive test suite: 67 tests (58 unit + 9 integration)
- Full TDD approach following KISS-DRY principles

**Key features:**
- Git commits as blocks, SHA as block hash, Merkle tree for transactions
- ECDSA secp256k1 signatures, address derivation
- Proof of Work with dynamic difficulty adjustment
- Async transaction pool with validation
- Account-based state with nonce for replay protection
- CLI interface for all operations

**Technical highlights:**
- Fixed critical bug in `create_block_template`: transactions now correctly applied to state snapshot before block creation
- All integration tests pass: wallet generation → funding → transactions → mining → verification
- Chain persistence and reload verified

**Test coverage:**
- Core data structures (17 tests)
- Cryptography (7 tests)
- Git backend (7 tests)
- Mempool (8 tests)
- Mining & PoW (8 tests)
- Blockchain engine (9 tests)
- Integration scenarios (9 tests)

**SIGNED NOT_FOR_COMPACTION. 2026-05-20 04:21 kr/claude-sonnet-4-5**

---

*This file serves as a well-tested knowledge base for daily usage. Read it to extend skills continuously.*
