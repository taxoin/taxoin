"""Genesis: Proof of Personhood coin distribution."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
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

    Each unique human needs 3-of-N validator attestations to receive
    50 genesis Ⓣ. Maximum 420,000 participants (21M / 50).
    """

    def __init__(self, validators: list[str]):
        self.validators = list(validators)
        self._attestations: dict[str, GenesisAttestation] = {}
        self._total_supply = 0.0

    def add_attestation(self, address: str, validator: str) -> bool:
        """Add a validator attestation for an address.

        Returns True if attestation was recorded, False if duplicate or
        supply cap reached.
        """
        if self._total_supply >= MAX_GENESIS_SUPPLY:
            return False

        if address not in self._attestations:
            self._attestations[address] = GenesisAttestation(
                address=address, timestamp=time.time()
            )

        attestation = self._attestations[address]

        # Prevent genesis if already done
        if attestation.completed:
            return False

        # Deduplicate validator
        if validator in attestation.attested_by:
            return False

        attestation.attested_by.append(validator)

        # Check if we have 3 attestations → genesis complete
        if len(attestation.attested_by) >= 3 and not attestation.completed:
            attestation.completed = True
            self._total_supply += GENESIS_REWARD

        return True

    def is_attestation_complete(self, address: str) -> bool:
        """Check if address has 3+ attestations."""
        att = self._attestations.get(address)
        return att is not None and len(att.attested_by) >= 3

    def get_attestation_count(self, address: str) -> int:
        """Get number of attestations for an address."""
        att = self._attestations.get(address)
        return len(att.attested_by) if att else 0

    def is_genesis_done(self, address: str) -> bool:
        """Check if address already received genesis coins."""
        att = self._attestations.get(address)
        return att is not None and att.completed

    def get_total_genesis_supply(self) -> float:
        """Total genesis coins distributed so far."""
        return self._total_supply

    def get_attestation(self, address: str) -> Optional[GenesisAttestation]:
        """Get the full attestation record for an address."""
        return self._attestations.get(address)
