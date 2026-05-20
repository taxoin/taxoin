"""
Blockchain Engine — the main orchestrator.

Combines:
  - GitBackend (storage)
  - Mempool (async transaction pool)
  - Miner (PoW)
  - Wallet (crypto)
  - UTXO set & Account state
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional

from .core import (
    Account, AsyncTransaction, Block, BlockHeader, Transaction,
    TxInput, TxOutput, UTXO, make_genesis_block, sha256,
)
from .git_backend import GitBlockchain
from .mempool import Mempool
from .miner import mine_block, validate_pow


class BlockchainEngine:
    """High-level blockchain orchestrator."""

    def __init__(self, repo_path: str = "."):
        self.git = GitBlockchain(repo_path)
        self.mempool = Mempool()
        self.utxo_set: dict[tuple[str, int], UTXO] = {}
        self.accounts: dict[str, Account] = {}
        self.difficulty = 4
        self._running = False
        self._mining = False

    # ── Init / Load ──────────────────────────────────────────────────

    def load_state(self) -> None:
        """Load the current chain state into memory."""
        # Rebuild UTXO set from all blocks
        chain = self.git.get_chain_summary()
        for entry in chain:
            if not entry["hash"]:
                continue
            block_data = self.git.get_block_by_hash(entry["commit"])
            if not block_data:
                continue
            for tx_data in block_data.get("transactions", []):
                tx = self._deserialize_transaction(tx_data)
                self._apply_transaction_utxo(tx)

        # Load account state from latest block if available
        latest = self.git.get_latest_block()
        if latest and latest.state_snapshot:
            for addr, balance in latest.state_snapshot.items():
                nonce = 0
                if addr in self.accounts:
                    nonce = self.accounts[addr].nonce
                self.accounts[addr] = Account(address=addr, balance=balance, nonce=nonce)

    @staticmethod
    def _deserialize_transaction(tx_data: dict) -> Transaction:
        """Reconstruct a Transaction from a deserialized JSON dict."""
        inputs = [TxInput(**i) if isinstance(i, dict) else i for i in tx_data.get("inputs", [])]
        outputs = [TxOutput(**o) if isinstance(o, dict) else o for o in tx_data.get("outputs", [])]
        return Transaction(
            inputs=inputs,
            outputs=outputs,
            tx_id=tx_data.get("tx_id", ""),
            timestamp=tx_data.get("timestamp", 0.0),
        )

        # Load account state from latest block if available
        latest = self.git.get_latest_block()
        if latest and latest.state_snapshot:
            for addr, balance in latest.state_snapshot.items():
                nonce = 0
                if addr in self.accounts:
                    nonce = self.accounts[addr].nonce
                self.accounts[addr] = Account(address=addr, balance=balance, nonce=nonce)

    def _apply_transaction_utxo(self, tx: Transaction) -> None:
        """Apply a transaction to the UTXO set."""
        # Remove spent inputs
        for inp in tx.inputs:
            key = (inp.tx_id, inp.output_index)
            self.utxo_set.pop(key, None)

        # Add new outputs
        for i, out in enumerate(tx.outputs):
            key = (tx.tx_id, i)
            self.utxo_set[key] = UTXO(
                tx_id=tx.tx_id,
                output_index=i,
                address=out.address,
                amount=out.amount,
            )

    # ── Account model (Ethereum) ─────────────────────────────────────

    def create_account(self, address: str, initial_balance: float = 0.0) -> Account:
        if address not in self.accounts:
            self.accounts[address] = Account(address=address, balance=initial_balance)
        return self.accounts[address]

    def get_balance(self, address: str) -> float:
        return self.accounts.get(address, Account(address=address)).balance

    def get_nonce(self, address: str) -> int:
        return self.accounts.get(address, Account(address=address)).nonce

    async def submit_async_transaction(self, tx: AsyncTransaction) -> tuple[bool, str]:
        """Submit an Ethereum-style transaction (async)."""
        sender_acct = self.accounts.get(tx.sender)
        if not sender_acct:
            return False, f"sender {tx.sender} does not exist"

        valid, msg = self.mempool.validate_tx(
            tx, sender_acct.balance, sender_acct.nonce,
        )
        if not valid:
            return False, msg

        return await self.mempool.submit(tx), "ok"

    # ── Mining ───────────────────────────────────────────────────────

    def create_block_template(self, coinbase_address: str) -> Block:
        """Prepare a new block for mining with pending txs."""
        parent = self.git.get_latest_block()
        parent_hash = parent.hash if parent else "0" * 64

        # Get pending transactions
        pending_txs = self.mempool.get_pending_transactions()
        account_txs = [tx for tx in pending_txs if isinstance(tx, AsyncTransaction)]

        # Create coinbase transaction
        reward = 50.0
        coinbase_tx = Transaction.coinbase(coinbase_address, reward)

        # Build account state snapshot by simulating transaction application
        state_snapshot = {}
        for addr, acct in self.accounts.items():
            state_snapshot[addr] = acct.balance

        # Apply account transactions to snapshot
        for tx in account_txs:
            if tx.sender not in state_snapshot:
                continue
            if tx.recipient not in state_snapshot:
                state_snapshot[tx.recipient] = 0.0

            total_cost = tx.value + (tx.gas_price * tx.gas_limit)
            if state_snapshot[tx.sender] >= total_cost:
                state_snapshot[tx.sender] -= total_cost
                state_snapshot[tx.recipient] += tx.value
                # Gas fees go to miner
                if coinbase_address not in state_snapshot:
                    state_snapshot[coinbase_address] = 0.0
                state_snapshot[coinbase_address] += (tx.gas_price * tx.gas_limit)

        # Add coinbase reward to miner's balance
        if coinbase_address in state_snapshot:
            state_snapshot[coinbase_address] += reward
        else:
            state_snapshot[coinbase_address] = reward

        all_txs = [coinbase_tx] + account_txs
        merkle = sha256("".join(
            t.tx_hash if hasattr(t, "tx_hash") else t.tx_id for t in all_txs
        ))

        header = BlockHeader(
            parent_hash=parent_hash,
            merkle_root=merkle,
            timestamp=time.time(),
            difficulty=self.difficulty,
        )

        return Block(header=header, transactions=all_txs, state_snapshot=state_snapshot)

    def mine_block(self, coinbase_address: str) -> Optional[Block]:
        """Mine a new block with pending transactions."""
        if self._mining:
            return None

        self._mining = True
        try:
            block = self.create_block_template(coinbase_address)
            try:
                mine_block(block.header)
            except RuntimeError as e:
                return None

            # Commit to git
            self.git.add_block(block)

            # Update account state from block snapshot (already includes tx effects)
            for addr, balance in block.state_snapshot.items():
                if addr not in self.accounts:
                    self.accounts[addr] = Account(address=addr)
                self.accounts[addr].balance = balance

            # Update nonces for senders
            for tx in block.transactions:
                if isinstance(tx, AsyncTransaction):
                    if tx.sender in self.accounts:
                        self.accounts[tx.sender].nonce = max(
                            self.accounts[tx.sender].nonce, tx.nonce + 1
                        )

            # Apply UTXO updates
            for tx in block.transactions:
                self._apply_transaction_utxo(
                    tx if isinstance(tx, Transaction)
                    else Transaction(
                        inputs=[],
                        outputs=[TxOutput(address=tx.recipient, amount=tx.value)],
                        tx_id=tx.tx_hash,
                    )
                )

            # Update chain state
            self.difficulty = block.header.difficulty

            # Remove confirmed txs from mempool
            confirmed = set()
            for tx in block.transactions:
                h = tx.tx_hash if hasattr(tx, "tx_hash") else tx.tx_id
                confirmed.add(h)
            self.mempool.remove_confirmed(confirmed)

            return block
        finally:
            self._mining = False

    def _apply_account_tx(self, tx: AsyncTransaction) -> None:
        """Apply an account-based transaction to local state."""
        if tx.sender not in self.accounts:
            return
        if tx.recipient not in self.accounts:
            self.accounts[tx.recipient] = Account(address=tx.recipient)

        sender = self.accounts[tx.sender]
        recipient = self.accounts[tx.recipient]

        total_cost = tx.value + (tx.gas_price * tx.gas_limit)
        if sender.balance >= total_cost:
            sender.balance -= total_cost
            recipient.balance += tx.value

        sender.nonce = max(sender.nonce, tx.nonce + 1)

    # ── Queries ──────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Return a status summary."""
        chain = self.git.get_chain_summary()
        latest = self.git.get_latest_block()
        return {
            "chain_height": len(chain),
            "latest_hash": latest.hash if latest else "none",
            "difficulty": self.difficulty,
            "mempool_size": self.mempool.get_pending_count(),
            "utxo_count": len(self.utxo_set),
            "account_count": len(self.accounts),
        }

    def get_accounts(self) -> dict[str, Account]:
        return dict(self.accounts)

    def get_utxos(self, address: Optional[str] = None) -> list[UTXO]:
        if address:
            return [u for u in self.utxo_set.values() if u.address == address]
        return list(self.utxo_set.values())

    def get_chain(self) -> list[dict]:
        return self.git.get_chain_summary()

    def verify(self) -> bool:
        return self.git.verify_chain()
