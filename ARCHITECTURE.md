# Taxoin Architecture

```
╔══════════════════════════════════════════════════════════════════════════╗
║                          TAXOIN NETWORK                                 ║
║                 Proof of Contribution — Service Economy                  ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                           USERS (3+ minimum)                            │
│                                                                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│   │   Consumer   │    │   Provider   │    │  Validator   │              │
│   │  (платит)    │    │  (оказывает  │    │ (подтверждает)│              │
│   │              │    │   услугу)    │    │              │              │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
│          │                  │                    │                      │
└──────────┼──────────────────┼────────────────────┼──────────────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                │
│                                                                          │
│  ┌────────────────────┐  ┌────────────────────┐                         │
│  │    Genesis         │  │  Service Registry  │                         │
│  │  (Proof of Human)  │  │  (register/list)   │                         │
│  │  50Ⓣ per person   │  │  фильтр по типу    │                         │
│  │  21M cap          │  │  рейтинг > 4.0     │                         │
│  └────────┬───────────┘  └────────┬───────────┘                         │
│           │                       │                                      │
│  ┌────────┴───────────────────────┴───────────┐                         │
│  │         Attested Transaction                │                         │
│  │  ┌──────────────────┐  ┌──────────────────┐ │                         │
│  │  │  Mutual Attest.  │  │  Balance Hold    │ │                         │
│  │  │  consumer_sig +  │  │  создание hold   │ │                         │
│  │  │  provider_sig    │  │  claim/release   │ │                         │
│  │  └──────────────────┘  └──────────────────┘ │                         │
│  └──────────────────────────────────────────────┘                         │
│                       │                                                  │
│  ┌────────────────────┴────────────────────┐                            │
│  │            Reputation                    │                            │
│  │  rating = 5.0 - (disputes × 0.5)       │                            │
│  │  leaderboard, анти-Sybil                │                            │
│  └─────────────────────────────────────────┘                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
           │                  │
           ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        CONSENSUS LAYER                                   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    ValidatorNetwork (7 nodes)                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │Validator1│  │Validator2│  │Validator3│  │Validator4│  ...    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │   │
│  │       │             │             │             │                │   │
│  │       │    PROPOSE/PREVOTE/PRECOMMIT/COMMIT    │                │   │
│  │       │    (Tendermint, quorum=5/7, f=2)       │                │   │
│  │       └──────────────┬──────────────┬───────────┘                │   │
│  └──────────────────────┼──────────────┼────────────────────────────┘   │
│                         │              │                                │
│  ┌──────────────────────┴──────────────┴────────────────────────────┐  │
│  │                    MergeConsensus                                │  │
│  │  PROPOSE → PREVOTE → PRECOMMIT → COMMIT                         │  │
│  │  валидация: signatures + conflict detection + balance hold      │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    ConflictDetector                                │  │
│  │  UTXO double-spend · Nonce collision · Balance mismatch         │   │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    GossipProtocol                                 │  │
│  │  Epidemic broadcast · fanout=3 · bounded cache                  │   │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    BranchManager                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │ Branch State │  │ Branch State │  │ Branch State │            │  │
│  │  │ (alice/bob)  │  │ (main)       │  │ (carol)     │            │  │
│  │  │ accounts     │  │ accounts     │  │ accounts    │            │  │
│  │  │ utxo_set     │  │ utxo_set     │  │ utxo_set    │            │  │
│  │  │ spent_utxos  │  │ spent_utxos  │  │ spent_utxos │            │  │
│  │  │ used_nonces  │  │ used_nonces  │  │ used_nonces │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Git Backend                                    │   │
│  │                                                                  │   │
│  │  .taxoin/                                                        │   │
│  │  └── .git/                                                       │   │
│  │      ├── objects/     ← blocks as commits                        │   │
│  │      ├── refs/heads/  ← branches + main chain                    │   │
│  │      └── notes/       ← metadata, service registry, genesis     │   │
│  │                                                                  │   │
│  │  Дополнительно: services.json, genesis.json, reputation.json    │   │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           CLI LAYER                                      │
│                                                                          │
│  taxoin                                                                  │
│  ├── wallet new | address | show                                         │
│  ├── genesis attest <address>                                            │
│  ├── service register | list | show | rate                               │
│  ├── tx send <provider> | attest <tx_id> | status                        │
│  ├── dispute open <tx_id> | list                                         │
│  ├── reputation <address> | leaderboard                                  │
│  ├── branch create | list | merge | status                               │
│  ├── validator init | list                                               │
│  └── init | status | accounts | chain | verify                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Full Transaction Lifecycle

```
CONSUMER                     PROVIDER                     VALIDATORS
    │                           │                            │
    ├── 1. Discover service ────┤                            │
    │      (service list --type sms)                         │
    │                           │                            │
    ├── 2. Request service ─────┤                            │
    │      (off-chain: call endpoint)                        │
    │                           │                            │
    │     3. Execute service (off-chain)                     │
    │                           │                            │
    ├── 4. Sign (consumer_sig) ─┤                            │
    │                           ├── 5. Sign (provider_sig)   │
    │                           │                            │
    └────── 6. AttestedTransaction ──────────────────────────┤
                submit_attested_tx(tx, balances)             │
                                                             │
                         ┌── 7. PROPOSE (broadcast) ────────┤
                         │                                  │
                         │── 8. PREVOTE ────────────────────┤
                         │      verify:                     │
                         │      ├── signatures (ECDSA)      │
                         │      ├── balance hold            │
                         │      ├── conflict detection      │
                         │      └── service exists          │
                         │                                  │
                         │── 9. PRECOMMIT (sign) ──────────┤
                         │                                  │
                         └── 10. COMMIT (merge) ───────────┤
                                                             │
                         ┌──── 11. Balance claim ───────────┤
                         │     ├── balances[alice] += 1.0   │
                         │     └── reputation +1 to both    │
                         │                                  │
                         └──── 12. Done ────────────────────┤
```

## Module Map

```
src/
├── cli.py               CLI entry point (taxoin commands)
├── core.py              Data structures (Account, UTXO, Block, Transaction)
├── crypto_utils.py      ECDSA secp256k1 keys, signing, verification
│
├── genesis.py           Proof of Personhood, 21M cap, attestations
├── service_registry.py  Service registration and discovery
├── attested_tx.py       Mutual attestation, balance hold
├── reputation.py        Ratings, disputes, leaderboard
│
├── git_backend.py       Git-based storage (commits, branches, notes)
├── branch_state.py      Isolated state per branch (accounts, utxos)
├── branch_manager.py    Branch lifecycle + merge orchestration
├── conflict_detector.py UTXO double-spend, nonce, balance checks
│
├── validator_network.py Validator nodes, sets, quorum math
├── consensus.py         Tendermint-style PROPOSE → PREVOTE → PRECOMMIT → COMMIT
├── gossip_protocol.py   Epidemic message propagation (fanout=3)
│
├── miner.py             [deprecated] legacy PoW (not used with skip_pow)
└── blockchain.py        [deprecated] legacy engine (not used in new flow)
```

## Quick Stats

```
  Modules:  18 source files
  Tests:    256 total, 100% passing
  Versions: mvp-v3 tagged
  Storage:  Git backend (blocks as commits)
  Consensus: Tendermint 5/7, Byzantine fault tolerance f=2
  Economy:  Proof of Contribution, mutual attestation, reputation
  CLI:      25+ commands
```


---

## FAQ: Как это работает (для чайников)

### ❓ Где хранятся деньги?

**У каждого валидатора.** Полная копия всего:
- Все балансы — в памяти (`dict`)
- Все транзакции — в git-коммитах (каждый блок = git commit)
- Все услуги — в services.json
- Все репутации — в reputation.json

Никакой "центральной базы данных". 7 валидоров = 7 полных копий.
Если 6 упали — один восстановит сеть.

### ❓ Как проходят транзакции?

**Через консенсус.** Алиса хочет отправить 1Ⓣ Бобу:

```
1. Алиса подписывает транзакцию (ECDSA)
2. Транзакция идёт всем 7 валидорам
3. Каждый валидатор проверяет:
   ├── подпись Алисы ✅ (криптография)
   ├── у Алисы есть 1Ⓣ ✅ (баланс)
   └── нет double-spend ✅ (UTXO)
4. 5 из 7 должны сказать "ДА" (кворум)
5. Если да → git commit → баланс обновлён
```

### ❓ Можно ли подделать баланс?

Нет. Даже если один валидатор "сломается" и сам себе начислит миллион —
остальные 6 не подтвердят (5/7 консенсус). Его "миллион" останется
только у него в локальной копии. Сеть его проигнорирует.

### ❓ Кто может украсть деньги?

Только тот, у кого **приватный ключ** (private_key) жертвы.
Всё остальное (консенсус, подписи, git, балансы) — математически
защищено.

### ❓ Сколько транзакций в секунду?

**~33 tx/s** (ограничение git commit).
Для таксопарка хватит. Для Visa — доработаем.

### ❓ Что видит обычный пользователь?

Просто кошелёк в Telegram: баланс, отправить, получить.
Никакой сложной криптографии — всё под капотом.

### ❓ Как стать валидатором?

Сейчас: нужно запустить Docker, пройти Proof of Personhood,
получить genesis-монеты. Позже — будет автоматизировано.
