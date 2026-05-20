# TAXOIN BIBLE

## Proof of Contribution — The Truth of Service

> SIGNED NOT_FOR_COMPACTION. Canonical specification of the Taxoin protocol.

---

## Prologue

In the beginning, there was proof of work. Miners burned electricity to
compute hashes, and the network rewarded them with coins. The work was
useful for security but useless for humanity.

Taxoin was created to solve one fundamental problem:

> **Replace useless computation with useful contribution.**

Not "one CPU, one vote" (Nakamoto, 2008).
But **one human, one contribution, one value.**

---

## Part I: What Is a Taxoin?

### I.1 Definition

A **Taxoin (Ⓣ)** is a unit of **proven contribution** to the Taxoin network.
It cannot be mined, minted, or created from nothing.

Every Ⓣ in existence entered the network through one of two gates:

| Gate | Mechanism | Max Supply |
|------|-----------|------------|
| **Genesis** | Proof of Personhood — one human, one genesis | 21,000,000 Ⓣ (420,000 people × 50Ⓣ) |
| **Service** | Proof of Contribution — providing a real service | Unlimited (capped by real economic activity) |

### I.2 Core Principle

> **No Taxoin exists without a corresponding contribution.**

This is the fundamental law. Every coin is backed by:
- A unique human being (genesis), or
- A verified service rendered (contribution)

There is no miner extracting coins from electricity. There is no staker
earning passive income. There is only **work that someone valued enough
to pay for.**

### I.3 Non-Principles (What Taxoin Is Not)

| ❌ Not this | ✅ But this |
|------------|------------|
| Investment asset | Medium of exchange for services |
| Store of value | Unit of contribution |
| Mining reward | Service payment |
| Passive income | Active work income |
| Speculative token | Proof of work done |

---

## Part II: Genesis — Proof of Personhood

### II.1 The Bootstrap Problem

A service economy cannot start from zero:
- Nobody has coins to pay for services
- Nobody can earn coins without providing services
- Deadlock

### II.2 Solution: One Human, One Genesis

Taxoin distributes genesis coins not to "miners" or "investors"
but to **unique human beings** verified by the validator set.

```
GLOBAL PARAMETERS:
  GENESIS_REWARD     = 50 Ⓣ  (per unique person)
  MAX_GENESIS_SUPPLY = 21,000,000 Ⓣ
  MAX_PARTICIPANTS   = 420,000  (21M / 50)
```

### II.3 The Genesis Ceremony

```
  ┌──────────────────────────────────────────────────────────────┐
  │                  GENESIS CEREMONY                            │
  │                                                              │
  │  1. Human generates a keypair (secp256k1)                    │
  │     → address: 0xdeadbeef...                                 │
  │                                                              │
  │  2. Human contacts a validator (in person / video call /     │
  │     through trusted referrer)                                │
  │     → Proves they are a unique human                         │
  │     → Signs a message with their key: "I am real"            │
  │                                                              │
  │  3. Validator verifies:                                      │
  │     → The signature matches the claimed address              │
  │     → The human is not already in the genesis registry       │
  │     → The human appears to be a real unique person           │
  │                                                              │
  │  4. Validator signs an attestation:                          │
  │     "0xval1 attests 0xdeadbeef is a unique human"            │
  │                                                              │
  │  5. Need 3-of-7 validator attestations → genesis approved    │
  │     → +50 Ⓣ credited to 0xdeadbeef                          │
  │     → Address added to the Genesis Registry (immutable)      │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

### II.4 Sybil Resistance

A Sybil attack (one person creating 1000 wallets) is prevented by:

| Layer | Protection |
|-------|-----------|
| **Proof of Personhood** | Validators verify humans, not wallets |
| **3-of-7 attestation** | Need 3 independent validators to confirm |
| **Immutable registry** | Each address can only be genesis'd once |
| **Reputation** | Validators who approve Sybils lose reputation |

This is not perfect. It requires social trust. But it is the only
known way to distribute coins fairly without:
- Proof of Work (ASIC centralization)
- Proof of Stake (rich get richer)
- ICO (insider advantage)
- Airdrop (Sybil farmed)

### II.5 The Genesis Cap

```
MAX_GENESIS_SUPPLY = 21,000,000 Ⓣ
```

This is the **absolute maximum** of genesis coins. Once 420,000 humans
have been attested, no more genesis coins can be created.

After genesis is exhausted, all new Ⓣ in circulation come exclusively
from service transactions (one person paying another for a service).

---

## Part III: Service Economy — Proof of Contribution

### III.1 What Is a Service?

A service is any contribution that one network participant provides to
another. The service is **registered on-chain** and **priced by the
provider.**

Examples:
```
  Service Type         Provider          Price
  ─────────────────────────────────────────────────
  SMS gateway          Alice's phone     0.1 Ⓣ/SMS
  GPU compute          Bob's farm        5.0 Ⓣ/hour
  API access           Carol's model     0.5 Ⓣ/call
  Ride (taxi)          Dave's car        3.0 Ⓣ/km
  File storage         Eve's server      0.01 Ⓣ/MB/month
  CPU cycle            Frank's desktop   0.001 Ⓣ/CPU-hour
  Bandwidth relay      Grace's router    0.05 Ⓣ/GB
  Human review         Hank's expertise  10.0 Ⓣ/review
```

There is no limit on what can be a service. The market decides
which services have value and at what price.

### III.2 Service Registry

Every service is registered on-chain as a git commit:

```python
@dataclass
class ServiceRegistration:
    provider: str              # address (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # Ⓣ per unit
    description: str           # human-readable
    endpoint: str              # how to call (URL, contact, API)
    attested_by: list[str]     # validators who verified
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

The service registry is stored in git notes (existing infrastructure).
Anyone can query: "show me all SMS gateways with rating > 4.0."

Validators verify that a service is real before approving registration:
- For an SMS gateway: send a test SMS, verify delivery
- For GPU compute: run a benchmark, verify output
- For a taxi ride: verify the driver's license and vehicle

### III.3 Pricing

The provider sets the price. The market regulates it.

```
  High price + bad service  →  no customers → provider lowers price
  Low price + good service  →  many customers → provider becomes reputable
  Fraud (take money, no service)  →  dispute → validator arbitration
                                    →  reputation penalty
                                    →  possible ban
```

No central authority sets prices. No algorithm adjusts fees.
Pure free market.

### III.4 Discovery

Consumers discover services through the registry:

```
  taxoin service list --type sms --min-rating 4.0
  → 0xalice: 0.1 Ⓣ/SMS, rating 4.8 (942 tx)
  → 0xbob:   0.15 Ⓣ/SMS, rating 4.2 (312 tx)
```

---

## Part IV: Transaction Lifecycle — Mutual Attestation

### IV.1 The Core Problem

> How does the blockchain know that a service was actually delivered?

In traditional blockchains, this is called the **Oracle Problem.**
Taxoin's answer: **Mutual Attestation** — both parties sign.

### IV.2 The Attested Transaction

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # who pays
    provider: str              # who provides
    service_ref: str           # link to ServiceRegistration
    amount: float              # Ⓣ for this transaction
    consumer_sig: str          # "I received the service" (ECDSA)
    provider_sig: str          # "I provided the service" (ECDSA)
    timestamp: float
    description: str           # optional order details
```

**A transaction is valid ONLY if both signatures are present.**

### IV.3 The Lifecycle

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                   TRANSACTION LIFECYCLE                         │
  │                                                                 │
  │  1. CONSUMER BROWSES REGISTRY                                   │
  │     → Finds a service they need                                 │
  │     → Checks price, rating, provider reputation                 │
  │                                                                 │
  │  2. CONSUMER SENDS REQUEST                                      │
  │     → Calls the service endpoint (off-chain)                    │
  │     → "I want 1 SMS to +79123456789"                           │
  │                                                                 │
  │  3. PROVIDER EXECUTES SERVICE (off-chain)                       │
  │     → Sends the SMS                                             │
  │     → Waits for delivery confirmation                           │
  │                                                                 │
  │  4. MUTUAL ATTESTATION                                          │
  │     → Consumer signs: "I confirm, SMS received"                 │
  │     → Provider signs: "I confirm, SMS delivered"                │
  │     → Both signatures → AttestedTransaction created             │
  │                                                                 │
  │  5. BALANCE TRANSFER (on-chain via consensus)                   │
  │     → Validators verify both signatures (ECDSA)                 │
  │     → Validators check that consumer had sufficient balance     │
  │     → 5-of-7 validators confirm → transaction committed         │
  │     → -0.1 Ⓣ consumer, +0.1 Ⓣ provider                        │
  │     → +1 reputation to both parties                            │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### IV.4 Balance Hold

During service execution, the consumer's coins are **held** (reserved)
but not yet spent:

```
  Consumer balance BEFORE:  100.0 Ⓣ
    ├── available:           99.9 Ⓣ
    ├── held:                 0.1 Ⓣ  (SMS in progress)
    └── locked:               0.0 Ⓣ

  After mutual attestation → held spent, credited to provider
  After 10 blocks timeout  → held returned to consumer (service failed)
```

### IV.5 Dispute Resolution

What if one party cheats?

| Scenario | Resolution |
|----------|-----------|
| Consumer signs, provider doesn't | Timeout → held returned to consumer |
| Provider delivers, consumer refuses to sign | Provider raises dispute → validators review evidence → 5/7 rule |
| Both sign, but service was fake | Validators detect pattern → dispute → reputation penalty |
| Provider takes money, doesn't deliver | Consumer raises dispute → validators rule → funds returned |

Validators are the final arbiters. With 7 validators and 5/7 quorum,
up to 2 malicious validators can be tolerated (Byzantine fault tolerance).

---

## Part V: Validator Consensus

### V.1 The Validator Set

Taxoin uses a **permissioned validator set** of 7 nodes.

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

This means: up to 2 validators can be malicious or faulty,
and the network still operates correctly.

### V.2 What Validators Do

| Role | Description |
|------|------------|
| **Genesis attestation** | Verify new humans (3-of-7) |
| **Service verification** | Verify new service registrations |
| **Transaction validation** | Check signatures, balance, double-spend |
| **Dispute arbitration** | Resolve conflicts between parties |
| **Merge consensus** | Finalize state transitions (existing Phase 4) |

### V.3 Consensus Protocol

Taxoin implements Tendermint-style consensus (built in Phase 4):

```
  PROPOSE  →  PREVOTE  →  PRECOMMIT  →  COMMIT
```

Each round:
1. A validator proposes a batch of attested transactions
2. All 7 validators validate independently (5/7 quorum)
3. Validated batch is merged into the main chain via git
4. State is updated (balances, reputation, service registry)

The Tendermint consensus is fully implemented and tested
(200 tests, all passing).

### V.4 Validator Honesty

Validators are not anonymous. They are known entities who:
- Participated in genesis (Proof of Personhood)
- Have reputation at stake
- Can be replaced by 5/7 vote if malicious

A dishonest validator:
1. Loses reputation
2. Can be voted out by 5/7
3. A replacement validator is attested

---

## Part VI: The Git Architecture

### VI.1 Why Git?

Taxoin is built on Git because Git is a proven DAG (Directed Acyclic Graph):

| Blockchains | Git |
|------------|-----|
| Block | Commit |
| Parent hash | Parent commit SHA |
| Merkle root | Git tree SHA |
| Chain | Branch history |
| Fork | Branch |
| Merge | Merge commit |
| Light client | Git clone --depth=1 |

### VI.2 How It Works

```
  .taxoin/
  └── .git/
      ├── objects/       # blocks as git commits
      ├── refs/heads/    # branches + main chain
      └── NOTES_MERGE/   # service registry, metadata
```

Every transaction batch is a git commit. Every service registration
is a git note. Every state change is a git merge.

**No database. No index. Just Git.**

### VI.3 Advantages

| Property | How Git Provides It |
|----------|-------------------|
| Immutability | SHA-based content addressing |
| History | git log — full audit trail |
| Distribution | git clone — full node in seconds |
| Light client | git clone --depth=1 |
| Backup | git push — instant backup to any remote |
| Verification | git verify — signature checking |
| Forking | git branch — parallel experimentation |

---

## Part VII: Tokenomics

### VII.1 Total Supply

```
  MAX_GENESIS_SUPPLY   = 21,000,000 Ⓣ  (hard cap)
  MAX_SERVICE_SUPPLY   = unlimited      (capped by real economy)
```

Genesis supply is capped at 21 million. Service supply is unlimited
but each Ⓣ in the service supply is **earned**, not created.

### VII.2 Genesis Distribution

```
  420,000 humans × 50 Ⓣ = 21,000,000 Ⓣ
  ──────────────────────────────────────
  No premine. No ICO. No insider allocation.
  Each human gets exactly the same amount.
```

### VII.3 Velocity

Ⓣ are designed to circulate, not to hoard:

```
  Genesis:  50 Ⓣ → spend on services
  Provider: earned Ⓣ → spend on other services
  Consumer: pay for services → provider earns → spend again
```

Taxoin is not a store of value. It is a **medium of exchange**
for a peer-to-peer service economy.

### VII.4 Fees

There are no protocol-level transaction fees. Validators are not paid
in block rewards (there are no blocks in the traditional sense).

Validators may charge voluntary fees for:
- Genesis attestation
- Dispute arbitration
- Service verification

Fee market is free: validators compete on price and reliability.

---

## Part VIII: Security Model

### VIII.1 Threat Matrix

| Threat | Mitigation |
|--------|-----------|
| Sybil attack (fake humans) | Proof of Personhood + 3/7 attestation |
| Double spend | Conflict detector (Phase 2) + spend tracking |
| Fake service (take money, no delivery) | Mutual attestation + dispute resolution |
| Validator collusion (3 of 7 malicious) | Byzantive fault tolerance (f=2) |
| Registry manipulation | Git immutability + validator signatures |
| Balance forgery | ECDSA signatures on all transactions |
| Replay attack | Nonce tracking per address |
| Network partition | Gossip protocol + timeout-based liveness |

### VIII.2 Trust Assumptions

Taxoin is not trustless. It is **trust-minimized:**

| You must trust | You need not trust |
|---------------|-------------------|
| 5 of 7 validators are honest | Any single validator |
| Your private key is secure | The network to be "fair" |
| Validators verify humans properly | Miners (there are none) |
| | Stakers (there are none) |
| | Oracle (attestation is mutual) |

---

## Part IX: CLI Reference

The core user interface:

```bash
  # Identity
  taxoin wallet new                  # Generate keypair
  taxoin wallet address              # Show your address
  taxoin wallet show                 # Show full wallet

  # Genesis (one-time per human)
  taxoin genesis request             # Request human verification
  taxoin genesis status              # Check genesis status

  # Services
  taxoin service register            # Register a new service
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "SMS gateway"
  taxoin service list                # List all services
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # Show service details
  taxoin service rate <address>      # Rate a service

  # Transactions
  taxoin tx send <provider>          # Pay for a service
       --amount 0.1
       --ref <service_id>
       --desc "SMS to +79123456789"
  taxoin tx attest <tx_id>           # Sign mutual attestation
  taxoin tx status <tx_id>           # Check transaction status

  # Disputes
  taxoin dispute open <tx_id>        # Open a dispute
  taxoin dispute list                # List active disputes

  # Reputation
  taxoin reputation <address>        # Show reputation
  taxoin reputation leaderboard      # Top providers

  # Network
  taxoin validator list              # Show validators
  taxoin status                      # Network status
```

---

## Part X: The Big Picture

### X.1 What Taxoin Changes

| Era | Mechanism | Resource Wasted |
|-----|-----------|----------------|
| **Pre-2008** | Barter / fiat | Trust |
| **2008 (Bitcoin)** | Proof of Work | Electricity |
| **2015 (Ethereum)** | Proof of Stake | Capital |
| **2026 (Taxoin)** | Proof of Contribution | Nothing |

### X.2 The Ultimate Goal

A self-sustaining, decentralized service economy where:

- **Anyone can earn** by providing a service they already have
- **Anyone can pay** with coins they earned by contributing
- **No one can cheat** because both parties must attest
- **No one is excluded** because the only requirement is being human
- **No energy is wasted** because computation serves people, not hashes

### X.3 The Name

**Taxoin** comes from *taxi* + *coin*.

A taxi driver provides a real, valuable service — transportation.
The passenger pays for that service. Both parties attest the ride
happened. No mining. No staking. No speculation.

Just **service, payment, and proof.**

---

## SIGNED NOT_FOR_COMPACTION.

This document is the canonical specification of the Taxoin protocol.
All implementations must conform to this specification.

**Version:** 1.0  
**Date:** 2026-05-20  
**Status:** Active
