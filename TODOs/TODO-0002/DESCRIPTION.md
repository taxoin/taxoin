# TODO-0002: Параллельные ветвления транзакций с консенсусом

## SIGNED NOT_FOR_COMPACTION.

---

## Problematic

Почему эта задача существует:

1. **Ограничение пропускной способности**: Текущая реализация обрабатывает транзакции последовательно — один блок за раз. Это создаёт узкое место: все кошельки конкурируют за место в одном блоке.

2. **Блокировка независимых операций**: Транзакции от разных кошельков, которые не конфликтуют друг с другом (разные UTXO, разные балансы), всё равно обрабатываются последовательно.

3. **Масштабируемость**: Для реального использования нужна возможность обрабатывать тысячи транзакций параллельно, как в Solana (65k TPS) или Aptos (160k TPS).

4. **Git как DAG**: Git изначально поддерживает ветвление и слияние (Directed Acyclic Graph). Мы не используем эту мощную возможность — работаем только с линейной историей.

5. **Отсутствие консенсуса**: Нет механизма для валидации и подтверждения слияний веток несколькими участниками сети. Это критично для децентрализованной системы.

---

## Way to solve

### Концепция: Git Branches = Transaction Isolation

Каждый кошелёк может создать свою ветку для обработки транзакций независимо от других. Ветки сливаются обратно в `main` через консенсус валидаторов.

```
main ──────●──────●──────●──────●──────●──────●──────
           │              │              │
           ├─ alice-1 ────┤              │
           │   (tx1, tx2) │              │
           │              │              │
           └─ bob-1 ──────┴─ alice-2 ────┤
               (tx3)         (tx4, tx5)  │
```

### Ключевые принципы

1. **Изоляция**: Каждая ветка имеет свою копию состояния (accounts, utxo_set, mempool)
2. **Параллелизм**: Ветки обрабатываются независимо — нет блокировок между ветками
3. **Консенсус**: Слияние требует одобрения кворума валидаторов (2f+1 из 3f+1)
4. **Детекция конфликтов**: Автоматическая проверка на double-spend, nonce collision, balance inconsistency
5. **Безопасность**: Byzantine Fault Tolerance — система работает даже если до f валидаторов злонамеренны

---

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITCHAIN v2.0                            │
│              Parallel Transaction Branching                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Wallet A   │  │   Wallet B   │  │   Wallet C   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │ create_branch() │                 │
       ├────────────────>│                 │
       │                 │                 │
       │ submit_tx()     │                 │
       ├────────────────>│                 │
       │                 │                 │
       │                 │ create_branch() │
       │                 ├────────────────>│
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BranchManager                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Branch State │  │ Branch State │  │ Branch State │         │
│  │   (alice-1)  │  │   (bob-1)    │  │  (alice-2)   │         │
│  │              │  │              │  │              │         │
│  │ • accounts   │  │ • accounts   │  │ • accounts   │         │
│  │ • utxo_set   │  │ • utxo_set   │  │ • utxo_set   │         │
│  │ • mempool    │  │ • mempool    │  │ • mempool    │         │
│  │ • lock       │  │ • lock       │  │ • lock       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
       │                 │                 │
       │ propose_merge() │                 │
       └────────────────>│                 │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ValidatorNetwork                              │
│                 (Tendermint Consensus)                          │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Validator1│  │Validator2│  │Validator3│  │Validator4│  ...  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       │  1. PROPOSE │             │             │              │
│       ├────────────>│────────────>│────────────>│              │
│       │             │             │             │              │
│       │  2. PREVOTE │             │             │              │
│       │<────────────┤<────────────┤<────────────┤              │
│       │             │             │             │              │
│       │  3. PRECOMMIT (quorum: 2f+1)            │              │
│       │<────────────┤<────────────┤<────────────┤              │
│       │             │             │             │              │
│       │  4. FINALIZE                            │              │
│       └─────────────┴─────────────┴─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitBackend (Multi-Branch)                    │
│                                                                 │
│  .git/                                                          │
│  ├── refs/heads/                                                │
│  │   ├── main                    (canonical chain)             │
│  │   ├── branch/0xalice.../001   (alice's tx branch)           │
│  │   ├── branch/0xbob.../001     (bob's tx branch)             │
│  │   └── branch/0xalice.../002   (alice's 2nd branch)          │
│  ├── objects/                    (blocks as commits)           │
│  └── notes/                      (branch metadata)             │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Transaction Lifecycle

```
1. BRANCH CREATION
   Wallet → BranchManager.create_branch()
   ├─ Clone parent state (main)
   ├─ Create git branch
   └─ Register BranchState

2. TRANSACTION SUBMISSION
   Wallet → BranchManager.submit_tx(branch_name, tx)
   ├─ Validate tx (balance, nonce)
   ├─ Add to branch mempool
   └─ Process independently (no blocking)

3. MINING (per-branch)
   Miner → BranchManager.mine_block(branch_name)
   ├─ Create block template
   ├─ PoW mining
   ├─ Commit to git branch
   └─ Update branch state

4. MERGE PROPOSAL
   Wallet → ValidatorNetwork.propose_merge(branch_name)
   ├─ Broadcast to all validators
   └─ Start consensus round

5. CONSENSUS (Tendermint-style)
   Phase 1: PROPOSE
   ├─ Leader broadcasts merge proposal
   └─ Includes: branch_name, final_state_hash, transactions

   Phase 2: PREVOTE
   ├─ Each validator validates independently:
   │  ├─ Check conflicts (UTXO, nonce, balance)
   │  ├─ Verify signatures
   │  └─ Validate state transition
   ├─ Vote YES/NO
   └─ Collect votes (timeout: 10s)

   Phase 3: PRECOMMIT
   ├─ If 2f+1 prevotes YES → validators precommit
   ├─ Sign precommit message
   └─ Collect precommits (timeout: 10s)

   Phase 4: FINALITY
   ├─ If 2f+1 precommits → execute merge
   ├─ git merge branch → main
   ├─ Update main state
   └─ Broadcast confirmation

6. CONFLICT RESOLUTION
   If conflicts detected:
   ├─ Abort merge
   ├─ Return conflict details
   └─ Wallet options:
      ├─ Rebase on latest main
      ├─ Abandon branch
      └─ Resolve manually
```

---

## Technical Specifications

### 1. Branch Naming Convention

```
Format: branch/{wallet_address}/{timestamp}_{sequence}

Examples:
- branch/0xalice123abc.../1716172800_001
- branch/0xbob456def.../1716172801_001
- branch/0xalice123abc.../1716172900_002

Rules:
- Prefix: "branch/" (distinguishes from main)
- Address: Full 40-char hex address
- Timestamp: Unix timestamp (10 digits)
- Sequence: 3-digit counter (000-999)
```

### 2. BranchState Data Structure

```python
@dataclass
class BranchState:
    """Isolated state for a transaction branch."""
    branch_name: str
    parent_hash: str  # block hash at branch point
    
    # State (cloned from parent)
    accounts: dict[str, Account]
    utxo_set: dict[tuple[str, int], UTXO]
    mempool: Mempool
    
    # Metadata
    created_at: float
    last_updated: float
    transaction_count: int
    
    # Conflict tracking
    spent_utxos: set[tuple[str, int]]
    used_nonces: dict[str, set[int]]
    
    # Concurrency
    lock: asyncio.Lock
```

### 3. Conflict Detection Rules

**UTXO Double-Spend:**
```
Conflict if:
  UTXO spent in branch ∩ UTXO spent in main ≠ ∅
```

**Nonce Collision:**
```
Conflict if:
  For any address:
    nonces used in branch ∩ nonces used in main ≠ ∅
```

**Balance Insufficient:**
```
Conflict if:
  After simulated merge:
    Any account.balance < 0
```

**State Divergence:**
```
Warning if:
  branch.parent_hash ≠ main.latest_block_hash
  (branch is stale, may need rebase)
```

### 4. Consensus Parameters

```python
# Validator network
VALIDATOR_COUNT = 7  # minimum for 2-fault tolerance
BYZANTINE_FAULTS = 2  # f = 2
QUORUM_SIZE = 5      # 2f+1 = 5

# Timeouts
PROPOSE_TIMEOUT = 10_000  # ms
PREVOTE_TIMEOUT = 10_000  # ms
PRECOMMIT_TIMEOUT = 10_000  # ms

# Gossip
GOSSIP_FANOUT = 3  # forward to 3 random peers
MESSAGE_CACHE_SIZE = 1000  # deduplication cache
```

### 5. Validator Message Types

```python
class MessageType(Enum):
    PROPOSE_MERGE = "propose_merge"
    PREVOTE = "prevote"
    PRECOMMIT = "precommit"
    MERGE_CONFIRM = "merge_confirm"
    HEARTBEAT = "heartbeat"

@dataclass
class MergeProposal:
    branch_name: str
    proposer: str  # validator address
    parent_hash: str
    final_state_hash: str
    transactions: list[Transaction]
    timestamp: float
    signature: str

@dataclass
class Prevote:
    validator: str
    proposal_hash: str
    vote: Vote  # YES/NO
    reason: Optional[str]
    signature: str

@dataclass
class Precommit:
    validator: str
    proposal_hash: str
    signature: str
```

---

## Dependencies

### System Requirements

- Python 3.10+
- Git 2.30+ (for advanced branch operations)
- Network connectivity (for validator communication)

### New Python Packages

```toml
[project.dependencies]
# Existing
click = "^8.1.0"
cryptography = "^41.0.0"
pytest = "^7.4.0"

# NEW for parallel branching
aiohttp = "^3.9.0"      # async HTTP for validator network
grpcio = "^1.60.0"      # gRPC for efficient validator communication
protobuf = "^4.25.0"    # message serialization
asyncio-mqtt = "^0.16"  # optional: MQTT for gossip protocol
```

### New Modules

```
src/
├── branch_manager.py      # Branch lifecycle management
├── validator_network.py   # Validator coordination
├── consensus.py           # Tendermint-style consensus
├── conflict_detector.py   # Conflict detection algorithms
├── gossip_protocol.py     # Message dissemination
└── validator_node.py      # Individual validator logic
```

---

## Implementation Plan (TDD-KISS-DRY)

### Phase 1: Branch Management (Foundation)

**Step 1.1: Git Backend Extensions**
- [ ] Test: `test_create_branch()`
- [ ] Test: `test_switch_branch()`
- [ ] Test: `test_list_branches()`
- [ ] Test: `test_merge_branches()`
- [ ] Test: `test_delete_branch()`
- [ ] Implement: `GitBlockchain.create_branch()`
- [ ] Implement: `GitBlockchain.switch_branch()`
- [ ] Implement: `GitBlockchain.list_branches()`
- [ ] Implement: `GitBlockchain.merge_branches()`
- [ ] Implement: `GitBlockchain.delete_branch()`

**Step 1.2: BranchState Management**
- [ ] Test: `test_branch_state_creation()`
- [ ] Test: `test_branch_state_clone()`
- [ ] Test: `test_branch_state_isolation()`
- [ ] Implement: `BranchState` dataclass
- [ ] Implement: `BranchState.clone()`
- [ ] Implement: Copy-on-Write optimization

**Step 1.3: BranchManager**
- [ ] Test: `test_create_branch()`
- [ ] Test: `test_submit_tx_to_branch()`
- [ ] Test: `test_mine_block_on_branch()`
- [ ] Test: `test_get_branch_state()`
- [ ] Implement: `BranchManager` class
- [ ] Implement: Branch naming convention
- [ ] Implement: Branch metadata storage (git notes)

### Phase 2: Conflict Detection

**Step 2.1: UTXO Conflict Detection**
- [ ] Test: `test_detect_utxo_double_spend()`
- [ ] Test: `test_no_utxo_conflict()`
- [ ] Implement: `ConflictDetector.check_utxo_conflicts()`

**Step 2.2: Nonce Conflict Detection**
- [ ] Test: `test_detect_nonce_collision()`
- [ ] Test: `test_no_nonce_conflict()`
- [ ] Implement: `ConflictDetector.check_nonce_conflicts()`

**Step 2.3: Balance Validation**
- [ ] Test: `test_detect_insufficient_balance()`
- [ ] Test: `test_balance_valid()`
- [ ] Implement: `ConflictDetector.check_balance_conflicts()`

**Step 2.4: State Divergence**
- [ ] Test: `test_detect_stale_branch()`
- [ ] Test: `test_branch_up_to_date()`
- [ ] Implement: `ConflictDetector.check_state_divergence()`

### Phase 3: Validator Network

**Step 3.1: Validator Node**
- [ ] Test: `test_validator_creation()`
- [ ] Test: `test_validator_sign_message()`
- [ ] Test: `test_validator_verify_signature()`
- [ ] Implement: `ValidatorNode` class
- [ ] Implement: Key generation for validators

**Step 3.2: Gossip Protocol**
- [ ] Test: `test_gossip_broadcast()`
- [ ] Test: `test_gossip_deduplication()`
- [ ] Test: `test_gossip_convergence()`
- [ ] Implement: `GossipProtocol` class
- [ ] Implement: Message deduplication
- [ ] Implement: Fanout forwarding

**Step 3.3: Validator Network**
- [ ] Test: `test_validator_discovery()`
- [ ] Test: `test_validator_communication()`
- [ ] Implement: `ValidatorNetwork` class
- [ ] Implement: Peer management
- [ ] Implement: Message routing

### Phase 4: Consensus Protocol

**Step 4.1: Propose Phase**
- [ ] Test: `test_propose_merge()`
- [ ] Test: `test_proposal_broadcast()`
- [ ] Test: `test_proposal_validation()`
- [ ] Implement: `MergeConsensus.propose_merge()`
- [ ] Implement: Proposal serialization

**Step 4.2: Prevote Phase**
- [ ] Test: `test_prevote_yes()`
- [ ] Test: `test_prevote_no_conflict()`
- [ ] Test: `test_prevote_quorum()`
- [ ] Implement: `MergeConsensus.prevote_phase()`
- [ ] Implement: Vote collection

**Step 4.3: Precommit Phase**
- [ ] Test: `test_precommit_after_prevote()`
- [ ] Test: `test_precommit_quorum()`
- [ ] Implement: `MergeConsensus.precommit_phase()`

**Step 4.4: Finality**
- [ ] Test: `test_finalize_merge()`
- [ ] Test: `test_merge_confirmation()`
- [ ] Implement: `MergeConsensus.finalize_merge()`
- [ ] Implement: Git merge execution
- [ ] Implement: State update

### Phase 5: Integration & CLI

**Step 5.1: CLI Commands**
- [ ] Test: `test_cli_branch_create()`
- [ ] Test: `test_cli_branch_list()`
- [ ] Test: `test_cli_branch_merge()`
- [ ] Implement: `gitchain branch create <wallet>`
- [ ] Implement: `gitchain branch list`
- [ ] Implement: `gitchain branch merge <branch>`
- [ ] Implement: `gitchain branch status <branch>`

**Step 5.2: Integration Tests**
- [ ] Test: `test_full_parallel_workflow()`
- [ ] Test: `test_concurrent_branches()`
- [ ] Test: `test_conflict_resolution()`
- [ ] Test: `test_byzantine_validator()`

**Step 5.3: Performance Tests**
- [ ] Test: `test_parallel_throughput()`
- [ ] Test: `test_consensus_latency()`
- [ ] Test: `test_branch_scalability()`

---

## Success Criteria

1. **Functionality:**
   - ✅ Multiple branches can process transactions in parallel
   - ✅ Conflicts are detected automatically
   - ✅ Consensus reaches finality with 2f+1 validators
   - ✅ Merged branches update main state correctly

2. **Performance:**
   - ✅ 10x throughput improvement vs sequential (target: 100+ TPS)
   - ✅ Consensus latency < 30 seconds
   - ✅ Support 100+ concurrent branches

3. **Security:**
   - ✅ Byzantine fault tolerance (tolerate 2 malicious validators)
   - ✅ No double-spend possible
   - ✅ No nonce replay attacks

4. **Testing:**
   - ✅ 100+ tests (unit + integration)
   - ✅ Byzantine behavior tests
   - ✅ Conflict resolution tests

---

## Research References

### Academic Papers & Protocols

1. **Tendermint Consensus**
   - Byzantine Fault Tolerant consensus
   - O(n) message complexity
   - Immediate finality
   - Used by: Cosmos, Binance Chain

2. **Solana Sealevel**
   - Parallel transaction execution
   - Static account declaration
   - 65,000+ TPS

3. **Aptos Block-STM**
   - Software Transactional Memory
   - Optimistic parallel execution
   - 160,000+ TPS

4. **Practical Byzantine Fault Tolerance (PBFT)**
   - Castro & Liskov, 1999
   - 3f+1 validators for f faults
   - Three-phase commit

5. **HotStuff**
   - Modern BFT protocol
   - Linear message complexity
   - Used by: Libra/Diem

### Implementation Patterns

- **Optimistic Concurrency Control (OCC)**: No locks during execution, validate at commit
- **Multi-Version Concurrency Control (MVCC)**: Each branch is a version
- **Gossip Protocol**: Epidemic message dissemination
- **Quorum Systems**: 2f+1 for Byzantine quorum

---

## Risks & Mitigations

### Risk 1: Consensus Complexity
**Risk:** Tendermint consensus is complex to implement correctly  
**Mitigation:** Start with simplified 3-validator network, add complexity incrementally

### Risk 2: Git Performance
**Risk:** Git operations may be slow with many branches  
**Mitigation:** Benchmark early, consider git alternatives (libgit2) if needed

### Risk 3: Network Partitions
**Risk:** Validators may become disconnected  
**Mitigation:** Implement timeout-based liveness, allow manual intervention

### Risk 4: State Explosion
**Risk:** Many branches = many state copies = high memory  
**Mitigation:** Copy-on-Write optimization, branch cleanup policies

---

## SIGNED NOT_FOR_COMPACTION.
