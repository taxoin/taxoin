"""
ValidatorNetwork: Validator nodes, sets, and in-process message passing.

Part of TODO-0002 Phase 3: Validator Network
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from .crypto_utils import (
    generate_keypair,
    private_key_from_pem,
    private_key_to_address,
    public_key_from_pem,
    public_key_to_address,
    sign,
    verify,
)


class ValidatorStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BYZANTINE = "byzantine"


@dataclass
class ValidatorNode:
    """A single validator node with identity and voting power."""

    address: str
    public_key: str  # PEM-encoded public key
    voting_power: int = 1
    status: ValidatorStatus = ValidatorStatus.ACTIVE
    last_seen: float = 0.0

    @staticmethod
    def generate() -> ValidatorNode:
        """Generate a new validator node with a fresh keypair.

        Returns:
            ValidatorNode with address derived from the public key
        """
        priv, pub = generate_keypair()
        address = public_key_to_address(pub)
        from .crypto_utils import public_to_bytes
        pub_pem = public_to_bytes(pub).decode("utf-8")
        return ValidatorNode(
            address=address,
            public_key=pub_pem,
        )

    @staticmethod
    def generate_with_private_key() -> tuple[ValidatorNode, str]:
        """Generate a validator node and return it together with its private key.

        Returns:
            Tuple of (ValidatorNode, private_key_pem)
        """
        priv, pub = generate_keypair()
        address = public_key_to_address(pub)
        from .crypto_utils import private_to_bytes, public_to_bytes
        priv_pem = private_to_bytes(priv).decode("utf-8")
        pub_pem = public_to_bytes(pub).decode("utf-8")
        node = ValidatorNode(address=address, public_key=pub_pem)
        return node, priv_pem

    @staticmethod
    def sign_data(data: str, private_key_pem: str) -> str:
        """Sign data with a PEM-encoded private key.

        Args:
            data: String data to sign
            private_key_pem: PEM-encoded private key

        Returns:
            Hex-encoded signature
        """
        key = private_key_from_pem(private_key_pem)
        return sign(key, data)

    @staticmethod
    def verify_signature(
        data: str,
        signature_hex: str,
        public_key_pem: str,
    ) -> bool:
        """Verify a signature against a PEM-encoded public key.

        Args:
            data: The original signed data
            signature_hex: Hex-encoded signature
            public_key_pem: PEM-encoded public key

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            key = public_key_from_pem(public_key_pem)
            return verify(key, data, signature_hex)
        except Exception:
            return False


@dataclass
class MergeProposal:
    """A proposal to merge a branch into main, to be voted on by validators."""

    branch_name: str
    proposer: str
    parent_hash: str
    final_state_hash: str
    transaction_count: int
    timestamp: float
    signature: str = ""


class ValidatorSet:
    """Manages the set of validators and quorum calculations."""

    # Default consensus parameters
    VALIDATOR_COUNT = 7
    BYZANTINE_FAULTS = 2  # f = floor((7-1)/3) = 2
    QUORUM_SIZE = 5       # 2f+1 = 5

    def __init__(self, validators: list[ValidatorNode] | None = None):
        self._validators: dict[str, ValidatorNode] = {}

        if validators is not None:
            for v in validators:
                self._validators[v.address] = v
        else:
            # Generate default set of 7 validators
            for _ in range(self.VALIDATOR_COUNT):
                v = ValidatorNode.generate()
                self._validators[v.address] = v

    def add_validator(self, validator: ValidatorNode) -> None:
        """Add a validator to the set."""
        self._validators[validator.address] = validator

    def remove_validator(self, address: str) -> None:
        """Remove a validator from the set by address."""
        self._validators.pop(address, None)

    def get_validator(self, address: str) -> Optional[ValidatorNode]:
        """Get a validator by address."""
        return self._validators.get(address)

    def get_active_validators(self) -> list[ValidatorNode]:
        """Get all active validators."""
        return [
            v for v in self._validators.values()
            if v.status == ValidatorStatus.ACTIVE
        ]

    def get_total_voting_power(self) -> int:
        """Sum of voting power of all active validators."""
        return sum(v.voting_power for v in self.get_active_validators())

    def get_quorum_size(self) -> int:
        """Calculate quorum size for current active validators.

        Uses 2f+1 where f = floor((n-1)/3), n = number of active validators.
        """
        n = len(self.get_active_validators())
        f = max(0, (n - 1) // 3)
        return 2 * f + 1

    def is_quorum_achieved(self, vote_addresses: list[str]) -> bool:
        """Check if the given votes meet quorum.

        Args:
            vote_addresses: List of validator addresses who voted

        Returns:
            True if sum of voting power >= quorum size
        """
        vote_power = 0
        for addr in vote_addresses:
            v = self._validators.get(addr)
            if v and v.status == ValidatorStatus.ACTIVE:
                vote_power += v.voting_power
        return vote_power >= self.get_quorum_size()


class ValidatorNetwork:
    """In-process validator network simulating message passing."""

    def __init__(
        self,
        validator_set: ValidatorSet,
        private_keys: dict[str, str] | None = None,
    ):
        self.validator_set = validator_set
        self._private_keys: dict[str, str] = private_keys or {}

    def broadcast(self, proposal: MergeProposal) -> list[str]:
        """Broadcast a proposal to all active validators.

        Args:
            proposal: The proposal to broadcast

        Returns:
            List of validator addresses that acknowledged
        """
        return [
            v.address
            for v in self.validator_set.get_active_validators()
        ]

    def collect_votes(
        self,
        proposal: MergeProposal,
        validate_fn: Callable[[MergeProposal, ValidatorNode], str],
    ) -> dict[str, str]:
        """Collect votes from all active validators.

        Each validator runs the validate_fn to determine their vote.

        Args:
            proposal: The proposal being voted on
            validate_fn: Function that takes (proposal, validator) and returns
                        "yes" or "no"

        Returns:
            Dict of validator_address -> "yes"/"no"
        """
        votes: dict[str, str] = {}
        for validator in self.validator_set.get_active_validators():
            vote = validate_fn(proposal, validator)
            votes[validator.address] = vote
        return votes

    def propose_merge(
        self,
        branch_name: str,
        proposer: str,
        branch_state,
    ) -> MergeProposal:
        """Create a signed merge proposal from a branch state.

        Args:
            branch_name: Name of the branch to merge
            proposer: Validator address making the proposal
            branch_state: BranchState to derive proposal fields from

        Returns:
            A signed MergeProposal
        """
        # Compute final_state_hash from branch state
        state_data = (
            str(branch_state.accounts) +
            str(branch_state.utxo_set) +
            str(branch_state.spent_utxos) +
            str(branch_state.used_nonces)
        )
        final_state_hash = hashlib.sha256(state_data.encode()).hexdigest()

        proposal = MergeProposal(
            branch_name=branch_name,
            proposer=proposer,
            parent_hash=branch_state.parent_hash,
            final_state_hash=final_state_hash,
            transaction_count=branch_state.transaction_count,
            timestamp=time.time(),
        )

        # Sign the proposal
        priv_key_pem = self._private_keys.get(proposer)
        if priv_key_pem:
            proposal_data = (
                f"{proposal.branch_name}{proposal.parent_hash}"
                f"{proposal.final_state_hash}{proposal.transaction_count}"
            )
            proposal.signature = ValidatorNode.sign_data(proposal_data, priv_key_pem)

        return proposal
