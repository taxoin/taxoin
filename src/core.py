"""
Core data structures: Transaction, UTXO, Account, Block.
Bitcoin (UTXO) + Ethereum (Account model) hybrid.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Hashing ──────────────────────────────────────────────────────────────

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def double_sha256(data: str) -> str:
    """Bitcoin-style double SHA256."""
    return sha256(sha256(data))


# ── Bitcoin: UTXO / Transaction ────────────────────────────────────────

@dataclass
class TxInput:
    """Reference to a previous UTXO being spent."""
    tx_id: str          # transaction hash that created the UTXO
    output_index: int   # which output in that tx
    signature: str = "" # signed by the private key of the address

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


@dataclass
class TxOutput:
    """An (address, amount) pair — becomes a UTXO."""
    address: str  # recipient public key hash (simplified)
    amount: float

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


@dataclass
class Transaction:
    """Bitcoin-style transaction with multiple inputs and outputs.

    Coinbase (mining reward) transactions have inputs=[].
    """
    inputs: list[TxInput]
    outputs: list[TxOutput]
    tx_id: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.tx_id:
            self.tx_id = self._compute_hash()

    def _compute_hash(self) -> str:
        raw = json.dumps({
            "inputs": [asdict(i) for i in self.inputs],
            "outputs": [asdict(o) for o in self.outputs],
            "timestamp": self.timestamp,
        }, sort_keys=True)
        return double_sha256(raw)

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @staticmethod
    def coinbase(address: str, reward: float = 50.0) -> Transaction:
        return Transaction(
            inputs=[],
            outputs=[TxOutput(address=address, amount=reward)],
        )


@dataclass
class UTXO:
    """Unspent Transaction Output — tracked by the UTXO pool."""
    tx_id: str
    output_index: int
    address: str
    amount: float

    def outpoint(self) -> tuple[str, int]:
        return (self.tx_id, self.output_index)

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


# ── Ethereum: Account model ────────────────────────────────────────────

@dataclass
class Account:
    """Simplified Ethereum account."""
    address: str
    balance: float = 0.0
    nonce: int = 0  # transaction count — prevents replay

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


@dataclass
class AsyncTransaction:
    """Signed transaction for the account-based (Ethereum) model.

    Can be sent asynchronously via the mempool.
    """
    sender: str
    recipient: str
    value: float
    nonce: int
    gas_price: float = 1.0
    gas_limit: int = 21000
    signature: str = ""
    tx_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.tx_hash:
            self.tx_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True)
        return sha256(raw)

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


# ── Block ───────────────────────────────────────────────────────────────

@dataclass
class BlockHeader:
    """Block header — mined via Proof of Work."""
    parent_hash: str          # SHA256 of previous block
    merkle_root: str          # SHA256 of all transaction IDs
    timestamp: float
    difficulty: int            # number of leading hex zeros needed
    nonce: int = 0
    version: int = 1

    def serialize(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    def hash(self) -> str:
        return double_sha256(self.serialize())

    def meets_difficulty(self) -> bool:
        return self.hash().startswith("0" * self.difficulty)


@dataclass
class Block:
    """A block in the chain. Stored as a git commit."""
    header: BlockHeader
    transactions: list[Transaction]
    state_snapshot: dict[str, float] = field(default_factory=dict)
    # ^ simplified account state at this block (address -> balance)

    def serialize(self) -> str:
        return json.dumps(
            {"header": asdict(self.header),
             "transactions": [asdict(tx) for tx in self.transactions],
             "state_snapshot": self.state_snapshot},
            sort_keys=True, default=str,
        )

    @property
    def hash(self) -> str:
        return self.header.hash()


# ── Genesis ─────────────────────────────────────────────────────────────

def make_genesis_block(difficulty: int = 4) -> Block:
    """Create the genesis block — first block in the chain."""
    genesis_tx = Transaction(
        inputs=[],
        outputs=[],
        tx_id="genesis",
        timestamp=0.0,
    )
    header = BlockHeader(
        parent_hash="0" * 64,
        merkle_root=genesis_tx.tx_id,
        timestamp=0.0,
        difficulty=difficulty,
        nonce=0,
    )
    return Block(header=header, transactions=[genesis_tx])
