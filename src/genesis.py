"""Genesis: Proof of Personhood coin distribution with persistence."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

GENESIS_REWARD = 50.0
MAX_GENESIS_SUPPLY = 21_000_000.0


@dataclass
class GenesisAttestation:
    address: str
    attested_by: list[str] = field(default_factory=list)
    completed: bool = False
    timestamp: float = 0.0


class GenesisRegistry:
    """Tracks Proof of Personhood attestations and genesis distribution.

    Persists to a JSON file when store_path is provided.
    Data survives restarts, supply cap is preserved.
    """

    def __init__(self, validators: list[str], store_path: str | None = None):
        self.validators = list(validators)
        self._store_path = store_path
        self._attestations: dict[str, GenesisAttestation] = {}
        self._total_supply = 0.0
        if store_path and os.path.exists(store_path):
            self._load()

    def _save(self) -> None:
        if not self._store_path:
            return
        data = {
            addr: {
                "address": att.address,
                "attested_by": att.attested_by,
                "completed": att.completed,
                "timestamp": att.timestamp,
            }
            for addr, att in self._attestations.items()
        }
        data["_meta"] = {"total_supply": self._total_supply}
        with open(self._store_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        if not self._store_path or not os.path.exists(self._store_path):
            return
        with open(self._store_path) as f:
            data = json.load(f)
        meta = data.pop("_meta", {})
        self._total_supply = meta.get("total_supply", 0.0)
        for addr, att_data in data.items():
            self._attestations[addr] = GenesisAttestation(
                address=att_data.get("address", addr),
                attested_by=list(att_data.get("attested_by", [])),
                completed=att_data.get("completed", False),
                timestamp=att_data.get("timestamp", 0.0),
            )

    def add_attestation(self, address: str, validator: str) -> bool:
        """Add a validator attestation for an address."""
        if self._total_supply >= MAX_GENESIS_SUPPLY:
            return False

        if address not in self._attestations:
            self._attestations[address] = GenesisAttestation(
                address=address, timestamp=time.time()
            )

        attestation = self._attestations[address]

        if attestation.completed:
            return False

        if validator in attestation.attested_by:
            return False

        attestation.attested_by.append(validator)

        if len(attestation.attested_by) >= 3 and not attestation.completed:
            attestation.completed = True
            self._total_supply += GENESIS_REWARD

        self._save()
        return True

    def is_attestation_complete(self, address: str) -> bool:
        att = self._attestations.get(address)
        return att is not None and len(att.attested_by) >= 3

    def get_attestation_count(self, address: str) -> int:
        att = self._attestations.get(address)
        return len(att.attested_by) if att else 0

    def is_genesis_done(self, address: str) -> bool:
        att = self._attestations.get(address)
        return att is not None and att.completed

    def get_total_genesis_supply(self) -> float:
        return self._total_supply

    def get_attestation(self, address: str) -> Optional[GenesisAttestation]:
        return self._attestations.get(address)
