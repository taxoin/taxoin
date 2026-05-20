"""
Tests for Validator Network.

Tests for TODO-0002 Phase 3: Validator Network
"""
import time
import tempfile
import pytest

from src.core import Account
from src.crypto_utils import generate_keypair, public_key_to_address


# Import will fail until we create validator_network.py
try:
    from src.validator_network import (
        ValidatorStatus,
        ValidatorNode,
        MergeProposal,
        ValidatorSet,
        ValidatorNetwork,
    )
except ImportError:
    ValidatorStatus = None
    ValidatorNode = None
    MergeProposal = None
    ValidatorSet = None
    ValidatorNetwork = None

try:
    from src.branch_manager import BranchManager
except ImportError:
    BranchManager = None


# ─── ValidatorNode ──────────────────────────────────────────────────────────

@pytest.mark.skipif(ValidatorNode is None, reason="ValidatorNode not implemented yet")
class TestValidatorNode:
    """Tests for individual validator nodes."""

    def test_validator_creation(self):
        """Creating a validator node with keypair."""
        validator = ValidatorNode.generate()

        assert validator.address is not None
        assert validator.address.startswith("0x")
        assert len(validator.address) == 42  # 0x + 40 hex chars
        assert validator.public_key is not None
        assert validator.voting_power == 1

    def test_validator_default_status_active(self):
        """New validator defaults to ACTIVE."""
        validator = ValidatorNode.generate()
        assert validator.status == ValidatorStatus.ACTIVE

    def test_validator_sign_and_verify(self):
        """Sign data and verify with the same validator."""
        validator, priv_key = ValidatorNode.generate_with_private_key()
        data = "test-data-to-sign"

        signature = ValidatorNode.sign_data(data, priv_key)

        assert signature is not None
        assert len(signature) > 0

        # Verify with public key
        assert ValidatorNode.verify_signature(
            data, signature, validator.public_key
        ) is True

    def test_validator_verify_wrong_key(self):
        """Verification with wrong key returns False."""
        v1, pk1 = ValidatorNode.generate_with_private_key()
        v2, pk2 = ValidatorNode.generate_with_private_key()
        data = "test-data"

        signature = ValidatorNode.sign_data(data, pk1)

        assert ValidatorNode.verify_signature(
            data, signature, v2.public_key
        ) is False

    def test_validator_verify_tampered_data(self):
        """Verification of tampered data returns False."""
        validator, priv_key = ValidatorNode.generate_with_private_key()
        data = "original-data"
        tampered = "tampered-data"

        signature = ValidatorNode.sign_data(data, priv_key)

        assert ValidatorNode.verify_signature(
            tampered, signature, validator.public_key
        ) is False


# ─── MergeProposal ──────────────────────────────────────────────────────────

@pytest.mark.skipif(MergeProposal is None, reason="MergeProposal not implemented yet")
class TestMergeProposal:
    """Tests for merge proposals."""

    def test_proposal_creation(self):
        """Creating a merge proposal with all fields."""
        proposal = MergeProposal(
            branch_name="branch/0xalice/001",
            proposer="0xvalidator1",
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=5,
            timestamp=time.time(),
            signature="signed_by_proposer",
        )

        assert proposal.branch_name == "branch/0xalice/001"
        assert proposal.proposer == "0xvalidator1"
        assert proposal.parent_hash == "a" * 64
        assert proposal.final_state_hash == "b" * 64
        assert proposal.transaction_count == 5
        assert "signed" in proposal.signature


# ─── ValidatorSet ───────────────────────────────────────────────────────────

@pytest.mark.skipif(ValidatorSet is None, reason="ValidatorSet not implemented yet")
class TestValidatorSet:
    """Tests for validator set management."""

    def test_default_validator_set(self):
        """ValidatorSet() creates 7 validators by default."""
        vset = ValidatorSet()
        assert len(vset.get_active_validators()) == 7

    def test_default_quorum_size(self):
        """With 7 validators, quorum = 5 (2f+1 = 5)."""
        vset = ValidatorSet()
        assert vset.get_quorum_size() == 5

    def test_quorum_achieved(self):
        """5 votes out of 7 meets quorum."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        votes = [v.address for v in validators[:5]]
        assert vset.is_quorum_achieved(votes) is True

    def test_quorum_not_achieved(self):
        """4 votes out of 7 does not meet quorum."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        votes = [v.address for v in validators[:4]]
        assert vset.is_quorum_achieved(votes) is False

    def test_add_validator_increases_power(self):
        """Adding a validator increases total voting power."""
        vset = ValidatorSet()
        initial_power = vset.get_total_voting_power()

        v = ValidatorNode.generate()
        vset.add_validator(v)

        assert vset.get_total_voting_power() == initial_power + 1

    def test_remove_validator_decreases_power(self):
        """Removing a validator decreases total voting power."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        target = validators[0]

        initial_power = vset.get_total_voting_power()
        vset.remove_validator(target.address)

        assert vset.get_total_voting_power() == initial_power - 1

    def test_get_validator_returns_node(self):
        """get_validator returns the correct node by address."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        target = validators[0]

        result = vset.get_validator(target.address)
        assert result is not None
        assert result.address == target.address

    def test_get_validator_nonexistent_returns_none(self):
        """get_validator with unknown address returns None."""
        vset = ValidatorSet()
        result = vset.get_validator("0xnonexistent")
        assert result is None

    def test_inactive_validator_excluded(self):
        """Inactive validators not counted in quorum."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        target = validators[0]

        # Deactivate one validator
        target.status = ValidatorStatus.INACTIVE

        # Active count should now be 6
        assert len(vset.get_active_validators()) == 6

        # Quorum size should be based on active validators
        # With 6 active: f = floor((6-1)/3) = 1, quorum = 2*1+1 = 3
        assert vset.get_quorum_size() == 3

    def test_byzantine_validator_excluded(self):
        """BYZANTINE validators not counted in active set."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        validators[0].status = ValidatorStatus.BYZANTINE
        validators[1].status = ValidatorStatus.BYZANTINE

        # 5 should remain active
        assert len(vset.get_active_validators()) == 5

    def test_quorum_with_varying_voting_power(self):
        """Quorum accounts for voting_power, not just count."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()

        # Give first validator extra voting power
        validators[0].voting_power = 5

        # Recalculate total: 5 + (6 * 1) = 11
        assert vset.get_total_voting_power() == 11

        # Quorum = 2f+1 where f = floor((7-1)/3) = 2
        # So quorum needs 5 voting power worth of votes
        # First validator alone (5 voting power) should be enough
        assert vset.is_quorum_achieved([validators[0].address]) is True


# ─── ValidatorNetwork ───────────────────────────────────────────────────────

@pytest.mark.skipif(ValidatorNetwork is None, reason="ValidatorNetwork not implemented yet")
class TestValidatorNetwork:
    """Tests for the validator network."""

    def test_broadcast_reaches_all_validators(self):
        """Broadcast reaches all active validators."""
        vset = ValidatorSet()
        network = ValidatorNetwork(vset)

        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer=vset.get_active_validators()[0].address,
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=3,
            timestamp=time.time(),
        )

        acknowledgements = network.broadcast(proposal)
        assert len(acknowledgements) == 7  # All validators

    def test_propose_merge_creates_proposal(self):
        """propose_merge creates a valid MergeProposal."""
        vset = ValidatorSet()
        validators = vset.get_active_validators()
        network = ValidatorNetwork(vset)

        from src.branch_state import BranchState
        from src.mempool import Mempool
        branch_state = BranchState(
            branch_name="branch/test/001",
            parent_hash="a" * 64,
            accounts={"0xalice": Account(address="0xalice", balance=100.0, nonce=0)},
            utxo_set={},
            mempool=Mempool(),
            created_at=time.time(),
            last_updated=time.time(),
            transaction_count=3,
            spent_utxos=set(),
            used_nonces={},
        )

        proposal = network.propose_merge(
            branch_name="branch/test/001",
            proposer=validators[0].address,
            branch_state=branch_state,
        )

        assert proposal.branch_name == "branch/test/001"
        assert proposal.proposer == validators[0].address
        assert proposal.parent_hash == "a" * 64
        assert proposal.final_state_hash is not None
        assert proposal.transaction_count == 3

    def test_propose_merge_includes_signature(self):
        """Proposal from network has a non-empty signature."""
        # Build set with private keys so the network can sign
        vals = []
        priv_keys = {}
        for _ in range(3):
            node, priv = ValidatorNode.generate_with_private_key()
            vals.append(node)
            priv_keys[node.address] = priv
        vset = ValidatorSet(vals)
        network = ValidatorNetwork(vset, priv_keys)
        validators = vset.get_active_validators()

        from src.branch_state import BranchState
        from src.mempool import Mempool
        branch_state = BranchState(
            branch_name="branch/test/001",
            parent_hash="a" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=time.time(),
            last_updated=time.time(),
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        proposal = network.propose_merge(
            branch_name="branch/test/001",
            proposer=validators[0].address,
            branch_state=branch_state,
        )

        assert proposal.signature != ""
        assert len(proposal.signature) > 0

    def test_collect_votes_all_yes(self):
        """Collect votes from all validators."""
        vset = ValidatorSet()
        network = ValidatorNetwork(vset)
        validators = vset.get_active_validators()

        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer=validators[0].address,
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=0,
            timestamp=time.time(),
            signature="test_sig",
        )

        # All validators vote YES
        def validate_all_yes(proposal, validator):
            return "yes"

        votes = network.collect_votes(proposal, validate_all_yes)

        assert len(votes) == 7
        all_yes = all(v == "yes" for v in votes.values())
        assert all_yes is True

    def test_collect_votes_mixed(self):
        """Collect mixed votes."""
        vset = ValidatorSet()
        network = ValidatorNetwork(vset)
        validators = vset.get_active_validators()

        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer=validators[0].address,
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=0,
            timestamp=time.time(),
            signature="test_sig",
        )

        # First 4 vote YES, last 3 vote NO
        def validate_mixed(proposal, validator):
            active = vset.get_active_validators()
            idx = active.index(validator) if validator in active else -1
            return "yes" if idx < 4 else "no"

        votes = network.collect_votes(proposal, validate_mixed)

        yes_count = list(votes.values()).count("yes")
        no_count = list(votes.values()).count("no")
        assert yes_count == 4
        assert no_count == 3


# ─── BranchManager Integration ──────────────────────────────────────────────

@pytest.mark.skipif(BranchManager is None or ValidatorNetwork is None,
                    reason="BranchManager or ValidatorNetwork not implemented yet")
class TestBranchManagerValidator:
    """Tests for BranchManager validator integration."""

    @pytest.fixture
    def branch_manager(self):
        """Create a BranchManager in a temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BranchManager(tmpdir)
            yield manager

    def test_init_validator_network(self, branch_manager):
        """Initializing validator network creates validators."""
        branch_manager.init_validator_network(count=7)
        validators = branch_manager.get_validators()

        assert len(validators) == 7
        assert all(v.address.startswith("0x") for v in validators)

    def test_init_validator_network_custom_count(self, branch_manager):
        """Custom validator count."""
        branch_manager.init_validator_network(count=4)
        assert len(branch_manager.get_validators()) == 4

    def test_get_validators_empty_before_init(self, branch_manager):
        """get_validators returns empty list before init."""
        validators = branch_manager.get_validators()
        assert len(validators) == 0
