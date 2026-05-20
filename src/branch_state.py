"""
BranchState: Isolated state for transaction branches.

Part of TODO-0002 Phase 1.2: BranchState Management
"""
from __future__ import annotations

import asyncio
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional

from .core import Account, UTXO
from .mempool import Mempool


@dataclass
class BranchState:
    """Isolated state for a transaction branch.

    Each branch maintains its own copy of:
    - Account balances and nonces (Ethereum model)
    - UTXO set (Bitcoin model)
    - Mempool (pending transactions)
    - Conflict tracking (spent UTXOs, used nonces)

    The lock ensures thread-safe modifications within a branch.
    """
    branch_name: str
    parent_hash: str  # block hash at branch point

    # State (cloned from parent)
    accounts: dict[str, Account]
    utxo_set: dict[tuple[str, int], UTXO]  # (tx_id, output_index) -> UTXO
    mempool: Mempool

    # Metadata
    created_at: float
    last_updated: float
    transaction_count: int

    # Conflict tracking
    spent_utxos: set[tuple[str, int]]  # UTXOs spent in this branch
    used_nonces: dict[str, set[int]]   # address -> set of nonces used

    # Concurrency control
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def clone(self) -> BranchState:
        """Create a deep copy of this branch state.

        Used when creating a new branch from an existing one.
        The mempool is reset (empty) in the clone.

        Returns:
            A new BranchState with copied data
        """
        return BranchState(
            branch_name=self.branch_name,
            parent_hash=self.parent_hash,

            # Deep copy accounts
            accounts={
                addr: Account(
                    address=acc.address,
                    balance=acc.balance,
                    nonce=acc.nonce,
                )
                for addr, acc in self.accounts.items()
            },

            # Deep copy UTXO set
            utxo_set={
                key: UTXO(
                    tx_id=utxo.tx_id,
                    output_index=utxo.output_index,
                    address=utxo.address,
                    amount=utxo.amount,
                )
                for key, utxo in self.utxo_set.items()
            },

            # Fresh mempool
            mempool=Mempool(),

            # Copy metadata
            created_at=time.time(),
            last_updated=time.time(),
            transaction_count=0,

            # Deep copy conflict tracking
            spent_utxos=set(self.spent_utxos),
            used_nonces={
                addr: set(nonces)
                for addr, nonces in self.used_nonces.items()
            },

            # New lock (don't share locks between branches!)
            lock=asyncio.Lock(),
        )

    def get_account(self, address: str) -> Account:
        """Get account by address, creating if doesn't exist.

        Args:
            address: Account address

        Returns:
            Account object
        """
        if address not in self.accounts:
            self.accounts[address] = Account(address=address, balance=0.0, nonce=0)
        return self.accounts[address]

    def track_spent_utxo(self, tx_id: str, output_index: int) -> None:
        """Track a UTXO as spent in this branch.

        Args:
            tx_id: Transaction ID
            output_index: Output index
        """
        self.spent_utxos.add((tx_id, output_index))

    def track_used_nonce(self, address: str, nonce: int) -> None:
        """Track a nonce as used in this branch.

        Args:
            address: Account address
            nonce: Nonce value
        """
        if address not in self.used_nonces:
            self.used_nonces[address] = set()
        self.used_nonces[address].add(nonce)

    def is_utxo_spent(self, tx_id: str, output_index: int) -> bool:
        """Check if a UTXO has been spent in this branch.

        Args:
            tx_id: Transaction ID
            output_index: Output index

        Returns:
            True if spent, False otherwise
        """
        return (tx_id, output_index) in self.spent_utxos

    def is_nonce_used(self, address: str, nonce: int) -> bool:
        """Check if a nonce has been used in this branch.

        Args:
            address: Account address
            nonce: Nonce value

        Returns:
            True if used, False otherwise
        """
        return address in self.used_nonces and nonce in self.used_nonces[address]
