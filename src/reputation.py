"""Reputation — rating and dispute tracking for service providers."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class ReputationRecord:
    address: str
    successful_tx: int = 0
    disputes: int = 0
    rating: float = 0.0


class ReputationTracker:
    """Tracks provider reputation based on successful transactions and disputes.

    Rating formula:
        base = (successful_tx / max(total_tx, 1)) * 5.0
        penalty = disputes * 0.5
        rating = max(0.0, min(5.0, base - penalty))

    Persists to JSON when store_path is provided.
    """

    def __init__(self, store_path: str | None = None):
        self._store_path = store_path
        self._records: dict[str, ReputationRecord] = {}
        if store_path and os.path.exists(store_path):
            self._load()

    def _save(self) -> None:
        if not self._store_path:
            return
        data = {
            addr: {
                "address": r.address,
                "successful_tx": r.successful_tx,
                "disputes": r.disputes,
                "rating": r.rating,
            }
            for addr, r in self._records.items()
        }
        with open(self._store_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        if not self._store_path or not os.path.exists(self._store_path):
            return
        with open(self._store_path) as f:
            data = json.load(f)
        for addr, r_data in data.items():
            self._records[addr] = ReputationRecord(**r_data)

    def _recalculate(self, address: str) -> float:
        """Recalculate rating for an address."""
        rec = self._records.get(address)
        if not rec or rec.successful_tx == 0:
            return 0.0
        base = min(5.0, rec.successful_tx * 0.1)  # 0.1 per tx, cap at 5.0
        penalty = rec.disputes * 0.5
        return max(0.0, base - penalty)

    def record_successful_tx(self, address: str) -> None:
        """Record a successful transaction (increases rating)."""
        if address not in self._records:
            self._records[address] = ReputationRecord(address=address)
        self._records[address].successful_tx += 1
        self._records[address].rating = self._recalculate(address)
        self._save()

    def record_dispute(self, address: str, guilty: bool) -> None:
        """Record a dispute resolution.

        Args:
            address: Provider address
            guilty: True if provider was found guilty
        """
        if not guilty:
            return
        if address not in self._records:
            self._records[address] = ReputationRecord(address=address)
        self._records[address].disputes += 1
        self._records[address].rating = self._recalculate(address)
        self._save()

    def get_rating(self, address: str) -> float:
        """Get current rating for an address."""
        rec = self._records.get(address)
        return rec.rating if rec else 0.0

    def get_dispute_count(self, address: str) -> int:
        """Get number of disputes for an address."""
        rec = self._records.get(address)
        return rec.disputes if rec else 0

    def get_successful_tx_count(self, address: str) -> int:
        """Get number of successful transactions for an address."""
        rec = self._records.get(address)
        return rec.successful_tx if rec else 0

    def get_leaderboard(self, top_n: int = 10) -> list[tuple[str, float]]:
        """Get top N providers by rating.

        Returns:
            List of (address, rating) tuples, sorted by rating descending
        """
        sorted_records = sorted(
            self._records.values(),
            key=lambda r: r.rating,
            reverse=True,
        )
        return [(r.address, r.rating) for r in sorted_records[:top_n]]
