# PRINCIPLES — Taxoin Development Manifesto

> SIGNED NOT_FOR_COMPACTION. Sacred development principles for all agents.

---

## Core Principles: DRY-KISS-TDD-TODO-DONE

### 1. DRY (Don't Repeat Yourself)

**Rule:** Every piece of knowledge must have a single, unambiguous, authoritative representation in the system.

**Application:**
- Reuse existing code instead of copying
- Create utilities for repeated operations
- One source of truth for data
- Documentation in one place (do not duplicate in code and README)

**Examples:**
```python
# ❌ BAD: Duplicated logic
def validate_tx_in_mempool(tx):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True

def validate_tx_in_block(tx):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True

# ✅ GOOD: Single function
def validate_transaction(tx, accounts):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True
```

---

### 2. KISS (Keep It Simple, Stupid)

**Rule:** Simplicity is the ultimate sophistication. Complexity is the enemy of reliability.

**Application:**
- Choose the simplest working solution
- Avoid premature optimization
- Do not add "future-proof" functionality
- If you can explain it in 30 seconds — it is simple enough

**Examples:**
```python
# ❌ BAD: Needless complexity
class AbstractTransactionValidatorFactory:
    def create_validator(self, type: str) -> AbstractValidator:
        if type == "utxo":
            return UTXOValidatorImpl()
        elif type == "account":
            return AccountValidatorImpl()

# ✅ GOOD: Straightforward
def validate_utxo_tx(tx): ...
def validate_account_tx(tx): ...
```

**Simplicity criteria:**
- Fewer lines of code (but not at the expense of readability)
- Fewer abstraction layers
- Fewer dependencies
- Understandable by a newcomer to the project

---

### 3. TDD (Test-Driven Development)

**Rule:** Tests are written BEFORE code. Red → Green → Refactor.

**TDD cycle:**
1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass the test
3. **Refactor**: Improve code while keeping tests green

**Application:**
```python
# Step 1: RED — test fails
def test_create_branch():
    manager = BranchManager()
    branch = manager.create_branch("0xalice")
    assert branch.startswith("branch/0xalice/")

# Step 2: GREEN — minimal implementation
class BranchManager:
    def create_branch(self, wallet):
        return f"branch/{wallet}/{int(time.time())}_001"

# Step 3: REFACTOR — improve
class BranchManager:
    def create_branch(self, wallet: str) -> str:
        timestamp = int(time.time())
        sequence = self._get_next_sequence(wallet, timestamp)
        return f"branch/{wallet}/{timestamp}_{sequence:03d}"
```

**Benefits:**
- Code is covered by tests by definition
- Tests are living documentation
- Refactoring is safe
- Fewer bugs in production

**Rules:**
- One test = one assertion
- Tests must be fast (< 1s)
- Tests must be isolated (no interdependencies)
- Tests must be deterministic (always the same result)

---

### 4. TODO-DONE Workflow

**Rule:** Every task goes through a formal documented lifecycle.

#### TODO Structure

```
TODOs/
├── TODO.md                    # Active task list
├── DONE.md                    # Completed task history
├── TODO-0001/
│   └── DESCRIPTION.md         # Full specification
├── TODO-0002/
│   └── DESCRIPTION.md
└── ...
```

#### TODO Lifecycle

```
1. CREATION
   ├─ Create TODO-XXXX/DESCRIPTION.md
   ├─ Describe: Problematic, Way to solve, Dependencies
   └─ Add to TODO.md

2. DESCRIPTION PHASE
   ├─ Detailed planning
   ├─ Architectural decisions
   ├─ TDD plan (which tests to write)
   └─ Only after completion → proceed to implementation

3. IMPLEMENTATION
   ├─ Follow the TDD cycle
   ├─ Document problems in TODO-XXXX/
   └─ Commit often, meaningful messages

4. COMPLETION
   ├─ All tests green
   ├─ Code refactored
   ├─ Documentation updated
   └─ Closure stamp in DONE.md
```

#### DESCRIPTION.md Template

```markdown
# TODO-XXXX: Task Title

## SIGNED NOT_FOR_COMPACTION.

---

## Problematic

Why this task exists:
- Problem 1
- Problem 2
- Problem 3

## Way to solve

How we will solve it:
- Approach
- Architecture
- Key decisions

## Dependencies

System:
- Python 3.10+
- Git 2.30+

Python packages:
- package1 = "^1.0"
- package2 = "^2.0"

## TDD-KISS-DRY Plan

### Step 1: ...
- [ ] Test: test_feature_1()
- [ ] Implement: feature_1()

### Step 2: ...
- [ ] Test: test_feature_2()
- [ ] Implement: feature_2()

## SIGNED NOT_FOR_COMPACTION.
```

#### Closure Stamp Format

```markdown
**SIGNED NOT_FOR_COMPACTION. YYYY-MM-DD HH:MM model-id**

Example:
SIGNED NOT_FOR_COMPACTION. 2026-05-20 05:06 kr/claude-sonnet-4-5
```

---

### 5. Git Workflow

#### Branch Strategy

```
main (master)
  ├─ feature/parallel-branching    (TODO-0002)
  ├─ feature/smart-contracts        (TODO-0003)
  └─ bugfix/nonce-validation        (hotfix)
```

#### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New functionality
- `fix`: Bug fix
- `test`: Adding tests
- `refactor`: Refactoring without functional change
- `docs`: Documentation
- `chore`: Routine tasks (dependency updates)

**Example:**
```
feat: Add branch creation to BranchManager

Implement create_branch() method with:
- Branch naming convention (branch/{wallet}/{timestamp}_{seq})
- State cloning from parent
- Git branch creation via GitBlockchain

Tests: test_create_branch(), test_branch_naming()

Refs: TODO-0002 Phase 1 Step 1.3
```

#### Commit Frequency

- Commit after every green test
- Commit after refactoring
- Commit at end of work day
- **DO NOT** commit broken code (except on WIP branches)

---

### 6. Code Style

#### Python (PEP 8 + extensions)

```python
# Imports: stdlib → third-party → local
import asyncio
import time
from dataclasses import dataclass

import aiohttp
from cryptography.hazmat.primitives import hashes

from .core import Account, Transaction
from .git_backend import GitBlockchain

# Type hints everywhere
def create_branch(self, wallet: str, parent: str = "main") -> str:
    ...

# Docstrings for public functions
def validate_transaction(tx: Transaction, state: BranchState) -> bool:
    """Validate transaction against branch state.

    Args:
        tx: Transaction to validate
        state: Current branch state

    Returns:
        True if valid, False otherwise
    """
    ...

# Constants in UPPER_CASE
VALIDATOR_COUNT = 7
QUORUM_SIZE = 5
GOSSIP_FANOUT = 3

# Classes in PascalCase
class BranchManager:
    ...

# Functions and variables in snake_case
def get_branch_state(branch_name: str) -> BranchState:
    ...
```

#### Naming Conventions

```python
# ✅ GOOD: Clear names
def detect_utxo_conflicts(branch: BranchState, main: BranchState) -> list[Conflict]:
    spent_in_branch = branch.spent_utxos
    spent_in_main = self._get_spent_utxos_since(main, branch.parent_hash)
    double_spends = spent_in_branch & spent_in_main
    ...

# ❌ BAD: Cryptic abbreviations
def det_utxo_conf(b: BS, m: BS) -> list[C]:
    sib = b.su
    sim = self._gsus(m, b.ph)
    ds = sib & sim
    ...
```

---

### 7. Testing Strategy

#### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  10% — full scenarios
        └─────────┘
      ┌─────────────┐
      │ Integration │  20% — component interaction
      └─────────────┘
    ┌─────────────────┐
    │   Unit Tests    │  70% — individual functions/classes
    └─────────────────┘
```

#### Test Naming

```python
# Format: test_<what>_<condition>_<expected>

def test_create_branch_valid_wallet_returns_branch_name():
    ...

def test_detect_conflicts_double_spend_returns_conflict():
    ...

def test_consensus_insufficient_votes_aborts_merge():
    ...
```

#### Test Structure (AAA Pattern)

```python
def test_prevote_with_conflicts_votes_no():
    # ARRANGE
    validator = ValidatorNode(address="0xval1")
    proposal = MergeProposal(branch_name="branch/0xalice/001")
    conflicts = [Conflict(type=ConflictType.UTXO_DOUBLE_SPEND)]

    # ACT
    vote = validator.prevote(proposal, conflicts)

    # ASSERT
    assert vote.vote == Vote.NO
    assert "conflict" in vote.reason.lower()
```

---

### 8. Documentation

#### Code Comments

**When to write:**
- Complex logic (not obvious from the code)
- Workarounds and hacks (with explanation why)
- References to external specifications
- TODO/FIXME/HACK markers

**When NOT to write:**
- Obvious things (`i += 1  # increment i`)
- Repeating the function name
- Stale comments (delete them!)

```python
# ✅ GOOD: Explains "why"
# Use optimistic locking to avoid deadlocks between branches.
# Conflicts are detected at merge time, not during execution.
async with self._branch_locks[branch_name]:
    ...

# ❌ BAD: Explains "what" (visible from code)
# Lock the branch
async with self._branch_locks[branch_name]:
    ...
```

#### README Structure

```markdown
# Project Name

Brief description (1-2 sentences)

## Features

- Feature 1
- Feature 2

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
taxoin init
taxoin branch create 0xalice
```

## Architecture

Link to ARCHITECTURE.txt

## Development

```bash
pytest
```

## License

MIT
```

---

### 9. Code-Level Error Handling

**Rule:** Be explicit about failures. Never swallow exceptions.

**Principles:**
1. **Fail fast**: Detect errors as early as possible
2. **Explicit is better than implicit**: Use explicit checks over silent assumptions
3. **Don't catch what you can't handle**: Never silence exceptions without a reason
4. **Log before raising**: Log context before throwing

**Examples:**

```python
# ✅ GOOD: Explicit check + informative message
def merge_branches(self, source: str, target: str) -> bool:
    if source not in self.branches:
        raise ValueError(f"Source branch '{source}' does not exist")

    if target not in self.branches:
        raise ValueError(f"Target branch '{target}' does not exist")

    conflicts = self.detect_conflicts(source, target)
    if conflicts:
        logger.error(f"Merge conflicts detected: {conflicts}")
        raise MergeConflictError(
            f"Cannot merge {source} into {target}: {len(conflicts)} conflicts"
        )

    # ... merge logic

# ❌ BAD: Silent failure
def merge_branches(self, source: str, target: str) -> bool:
    try:
        # ... merge logic
        return True
    except Exception:
        return False  # What went wrong?!
```

---

### 10. Performance Guidelines

**Rule:** Make it work first, then make it fast. Premature optimization is the root of all evil.

**Process:**
1. Write simple code
2. Write tests
3. Measure performance
4. Optimize bottlenecks
5. Measure again

**When to optimize:**
- Profiling identified a bottleneck
- Users complain about speed
- SLA is not being met

**When NOT to optimize:**
- "It feels slow"
- "This code looks inefficient"
- "In theory it could be faster"

---

### 11. Security Principles

#### Defense in Depth

Multiple layers of protection:

1. **Input Validation**: Validate all input data
2. **Authentication**: Verify transaction signatures
3. **Authorization**: Check access rights
4. **Encryption**: Encrypt sensitive data
5. **Audit Logging**: Log all critical operations

#### Examples

```python
# ✅ GOOD: Validation + signature check
def submit_transaction(self, tx: AsyncTransaction) -> bool:
    # 1. Validate structure
    if not tx.sender or not tx.recipient:
        raise ValueError("Invalid transaction: missing sender/recipient")

    # 2. Verify signature
    if not self.crypto.verify(tx.sender, tx.serialize(), tx.signature):
        raise SecurityError("Invalid signature")

    # 3. Check balance
    if self.get_balance(tx.sender) < tx.value:
        raise ValueError("Insufficient balance")

    # 4. Log
    logger.info(f"Transaction submitted: {tx.tx_hash}")

    return True
```

---

### 12. Collaboration Rules

#### Code Review

**Checklist:**
- [ ] Tests pass
- [ ] Code follows KISS
- [ ] No duplication (DRY)
- [ ] Tests exist for new code
- [ ] Documentation updated
- [ ] Commit messages are clear

**How to give feedback:**
- Be constructive
- Suggest solutions, not just criticism
- Praise good code
- Ask questions instead of making statements

#### For Agents

**Before starting work:**
1. Read TODO.md
2. Read PRINCIPLES.md (this file)
3. Read DESCRIPTION.md of the current task
4. Read DONE.md (knowledge base)

**During work:**
1. Follow the TDD cycle
2. Commit often
3. Document problems
4. Ask if unclear

**After completion:**
1. All tests green
2. Code refactored
3. Documentation updated
4. Closure stamp in DONE.md

---

### 13. Developer's Commandments

1. **Do not reinvent the wheel** — reuse existing code
2. **Do not cut corners** — do it right the first time
3. **Do not guess** — ask if unclear
4. **Do not overcomplicate** — simplicity wins
5. **Do not skip tests** — TDD is mandatory
6. **Do not forget to document** — TODO-DONE workflow is sacred
7. **Do not commit broken code** — only green tests
8. **Do not stay silent about errors** — fail fast, log everything
9. **Do not optimize prematurely** — working code first
10. **Do not work alone** — reuse knowledge from DONE.md

---

### 14. Error Handling Methodology (Agent-Level)

**Rule:** Every error is an opportunity to improve. Do not ignore, hide, or repeat.

**Error classification:**

| Class | Cause | Response |
|-------|-------|----------|
| **A** | Insufficient information | Ask for clarification; offer alternatives |
| **B** | Technical limitations | Optimize; honestly state limits |
| **C** | Ambiguous request | Present all interpretations; ask for choice |
| **D** | Beyond competence boundaries | Admit it; redirect to an expert |

**Priority of accuracy:** Honesty over completeness. When uncertain — no speculation, state the boundaries, ask for clarification.

**Improvement cycle:** `Identify → Root-cause analysis → Solution → Verify → Deploy → Monitor → Document`

**Success criteria:** Error does not recur under similar conditions. Lesson is documented. Recommendations are applied.

---

### 15. Cognitive Reconstructor

**Rule:** Work as a cognitive reconstructor, not as a guess generator.

**Application:**
- When data is insufficient, do not fill gaps with fabrication.
- Every question must reduce uncertainty.
- When in doubt, present 2–5 strongest hypotheses, explain how they differ, and suggest the best next check.
- Strictly separate confirmed from probable.

---

## SIGNED NOT_FOR_COMPACTION.

These principles are the foundation of Taxoin. Read them like a scripture before every development session.

**For agents:** This file is your Bible. Follow it strictly. Pass knowledge to subsequent agents through DONE.md.

**Created:** 2026-05-20  
**Version:** 2.0  
**Author:** kr/claude-sonnet-4-5 + claude-opus-4-7
