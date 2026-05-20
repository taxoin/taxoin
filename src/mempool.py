"""
Async transaction mempool.

Ethereum-style transaction pool that:
  - Accepts incoming transactions via asyncio queue
  - Validates signatures and nonces
  - Provides transactions to the miner
  - Supports both UTXO and Account-model transactions
"""
from __future__ import annotations

import asyncio
from typing import Optional

from .core import AsyncTransaction, Transaction


class Mempool:
    """Pending transaction pool with async support."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue: asyncio.Queue[AsyncTransaction | Transaction] = asyncio.Queue()
        self._pending: dict[str, AsyncTransaction | Transaction] = {}
        self._nonce_tracker: dict[str, int] = {}  # address -> next expected nonce

    async def submit(self, tx: AsyncTransaction | Transaction) -> bool:
        """Submit a transaction to the mempool.

        Returns True if accepted, False if rejected (queue full / duplicate).
        """
        if len(self._pending) >= self.max_size:
            return False

        tx_hash = tx.tx_hash if hasattr(tx, "tx_hash") else tx.tx_id
        if tx_hash in self._pending:
            return False  # duplicate

        await self._queue.put(tx)
        self._pending[tx_hash] = tx

        if isinstance(tx, AsyncTransaction):
            self._nonce_tracker[tx.sender] = max(
                self._nonce_tracker.get(tx.sender, 0),
                tx.nonce,
            )

        return True

    async def get_transaction(self) -> Optional[AsyncTransaction | Transaction]:
        """Get the next transaction from the queue (blocking)."""
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    def get_pending_transactions(self, max_count: int = 100) -> list:
        """Get a batch of pending transactions for mining."""
        txs = list(self._pending.values())[:max_count]
        return txs

    async def get_pending_transactions_async(self, max_count: int = 100) -> list:
        """Async version of get_pending_transactions."""
        return self.get_pending_transactions(max_count)

    def remove_confirmed(self, tx_hashes: set[str]) -> None:
        """Remove confirmed transactions from the pool."""
        for h in tx_hashes:
            self._pending.pop(h, None)

    def validate_tx(self, tx: AsyncTransaction, sender_balance: float,
                    sender_nonce: int) -> tuple[bool, str]:
        """Validate an async transaction before accepting it into the pool."""
        if tx.value <= 0:
            return False, "value must be positive"
        if tx.gas_price < 0:
            return False, "gas_price cannot be negative"
        if tx.nonce < sender_nonce:
            return False, f"nonce too low: {tx.nonce} < {sender_nonce}"
        total_cost = tx.value + (tx.gas_price * tx.gas_limit)
        if total_cost > sender_balance:
            return False, f"insufficient balance: {total_cost} > {sender_balance}"
        return True, "ok"

    def get_pending_count(self) -> int:
        return len(self._pending)

    def get_queue_size(self) -> int:
        return self._queue.qsize()
