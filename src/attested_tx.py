"""Attested Transactions and Balance Hold service economy."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

TX_TIMEOUT_BLOCKS = 10


@dataclass
class AttestedTransaction:
    """A transaction attested by both consumer and provider.

    Only valid when both parties have signed, confirming
    that the service was actually delivered.
    """
    consumer: str
    provider: str
    service_ref: str
    amount: float
    consumer_sig: str
    provider_sig: str
    timestamp: float = 0.0
    description: str = ""
    tx_id: str = ""

    def __post_init__(self):
        if not self.tx_id:
            raw = f"{self.consumer}:{self.provider}:{self.amount}:{time.time()}"
            self.tx_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
        if not self.timestamp:
            self.timestamp = time.time()

    def is_valid(self) -> bool:
        """Check if this transaction has both signatures and positive amount."""
        return bool(self.consumer_sig) and bool(self.provider_sig) and self.amount > 0.0


@dataclass
class HoldRecord:
    """A pending balance hold."""
    tx_id: str
    consumer: str
    amount: float
    created_at: float = 0.0


class BalanceHold:
    """Manages balance reservations during service execution.

    When a consumer requests a service, the amount is held (reserved)
    but not yet transferred. After mutual attestation, the hold is
    claimed (transferred to provider) or released (returned to consumer
    on timeout).
    """

    def __init__(self, balances: dict[str, float]):
        self._holds: dict[str, HoldRecord] = {}
        self._balances = balances  # reference to external balance dict

    def create_hold(self, consumer: str, amount: float, tx_id: str) -> bool:
        """Reserve funds for a pending transaction.

        Args:
            consumer: Consumer address
            amount: Amount to hold
            tx_id: Transaction ID

        Returns:
            True if hold created, False if insufficient balance
        """
        available = self._balances.get(consumer, 0.0) - self.get_held(consumer)
        if available < amount:
            return False

        # Deduct from available balance
        self._balances[consumer] = self._balances.get(consumer, 0.0) - amount

        self._holds[tx_id] = HoldRecord(
            tx_id=tx_id,
            consumer=consumer,
            amount=amount,
            created_at=time.time(),
        )
        return True

    def get_held(self, consumer: str) -> float:
        """Get total held amount for a consumer."""
        return sum(
            h.amount for h in self._holds.values()
            if h.consumer == consumer
        )

    def release_hold(self, tx_id: str) -> bool:
        """Release a hold (return funds to consumer, e.g. on timeout/failure)."""
        hold = self._holds.pop(tx_id, None)
        if hold is None:
            return False
        self._balances[hold.consumer] = self._balances.get(hold.consumer, 0.0) + hold.amount
        return True

    def claim_hold(self, tx_id: str, provider: str, balances: dict[str, float]) -> bool:
        """Claim held funds for the provider (after successful attestation).

        Args:
            tx_id: Transaction ID
            provider: Provider address
            balances: Balance dict to update

        Returns:
            True if claimed, False if hold not found
        """
        hold = self._holds.pop(tx_id, None)
        if hold is None:
            return False

        # Funds are already deducted from consumer at hold time
        # Just credit the provider
        balances[provider] = balances.get(provider, 0.0) + hold.amount
        return True
