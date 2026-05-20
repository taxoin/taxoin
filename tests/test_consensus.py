"""
Tests for Consensus Protocol.

Tests for TODO-0002 Phase 4: Tendermint-style Consensus
"""
import time
import tempfile
import pytest

from src.core import Account
from src.branch_state import BranchState
from src.mempool import Mempool
from src.conflict_detector import ConflictDetector, ConflictType


# Import will fail until we create consensus.py
try:
    from src.consensus import (
        Vote,
        ConsensusStatus,
        ConsensusRound,
        MergeConsensus,
    )
except ImportError:
    Vote = None
    ConsensusStatus = None
    ConsensusRound = None
    MergeConsensus = None

try:
    from src.validator_network import (
        ValidatorStatus,
        ValidatorNode,
        MergeProposal,
        ValidatorSet,
        ValidatorNetwork,
    )
except ImportError:
    ValidatorNode = None
    MergeProposal = None
    ValidatorSet = None
    ValidatorNetwork = None

try:
    from src.branch_manager import BranchManager
except ImportError:
    BranchManager = None


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def validator_network():
    """Create a 7-validator network with private keys."""
    vals = []
    priv_keys = {}
    for _ in range(7):
        node, priv = ValidatorNode.generate_with_private_key()
        vals.append(node)
        priv_keys[node.address] = priv
    vset = ValidatorSet(vals)
    return ValidatorNetwork(vset, priv_keys)


@pytest.fixture
def branch_manager():
    """Create a BranchManager in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BranchManager(tmpdir)
        yield manager


def make_branch_state(
    branch_name="branch/test/001",
    parent_hash="a" * 64,
    accounts=None,
    spent_utxos=None,
    used_nonces=None,
) -> BranchState:
    """Helper to create a BranchState for testing."""
    return BranchState(
        branch_name=branch_name,
        parent_hash=parent_hash,
        accounts=accounts or {},
        utxo_set={},
        mempool=Mempool(),
        created_at=time.time(),
        last_updated=time.time(),
        transaction_count=len(accounts) if accounts else 0,
        spent_utxos=spent_utxos or set(),
        used_nonces=used_nonces or {},
    )


# ─── ConsensusRound ─────────────────────────────────────────────────────────

@pytest.mark.skipif(ConsensusRound is None or MergeProposal is None or ConsensusStatus is None,
                    reason="consensus types not implemented yet")
class TestConsensusRound:
    """Tests for ConsensusRound data structure."""

    def test_round_creation(self):
        """Creating a round with all fields."""
        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer="0xval1",
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=3,
            timestamp=time.time(),
        )
        round = ConsensusRound(
            proposal=proposal,
            round_id=1,
            status=ConsensusStatus.PROPOSE,
        )

        assert round.proposal.branch_name == "branch/test/001"
        assert round.round_id == 1
        assert round.status == ConsensusStatus.PROPOSE
        assert len(round.prevotes) == 0
        assert len(round.precommits) == 0

    def test_round_tracks_prevotes(self):
        """Round tracks prevotes added during consensus."""
        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer="0xval1",
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=0,
            timestamp=time.time(),
        )
        round = ConsensusRound(
            proposal=proposal,
            round_id=1,
            status=ConsensusStatus.PREVOTE,
        )

        round.prevotes["0xval1"] = "yes"
        round.prevotes["0xval2"] = "yes"
        round.prevotes["0xval3"] = "no"

        assert len(round.prevotes) == 3
        assert round.prevotes["0xval1"] == "yes"
        assert round.prevotes["0xval3"] == "no"

    def test_round_status_transition(self):
        """Round status can transition through phases."""
        proposal = MergeProposal(
            branch_name="branch/test/001",
            proposer="0xval1",
            parent_hash="a" * 64,
            final_state_hash="b" * 64,
            transaction_count=0,
            timestamp=time.time(),
        )
        round = ConsensusRound(
            proposal=proposal,
            round_id=1,
            status=ConsensusStatus.PROPOSE,
        )

        assert round.status == ConsensusStatus.PROPOSE
        round.status = ConsensusStatus.PREVOTE
        assert round.status == ConsensusStatus.PREVOTE
        round.status = ConsensusStatus.PRECOMMIT
        assert round.status == ConsensusStatus.PRECOMMIT
        round.status = ConsensusStatus.COMMIT
        assert round.status == ConsensusStatus.COMMIT


# ─── MergeConsensus ─────────────────────────────────────────────────────────

@pytest.mark.skipif(MergeConsensus is None or ConsensusRound is None,
                    reason="MergeConsensus not implemented yet")
class TestMergeConsensus:
    """Tests for the MergeConsensus protocol."""

    def test_propose_creates_round(self, validator_network):
        """propose() creates a round in PROPOSE status."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(
            branch_state=branch_state,
            branch_name="branch/test/001",
            proposer=validators[0].address,
        )

        assert round is not None
        assert round.status == ConsensusStatus.PROPOSE
        assert round.proposal.branch_name == "branch/test/001"
        assert round.proposal.proposer == validators[0].address

    def test_prevote_all_yes_reaches_quorum(self, validator_network):
        """All 7 vote YES → quorum reached → transitions to PRECOMMIT."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(branch_state, "branch/test/001", validators[0].address)

        # All validators vote YES (no conflicts)
        def all_yes(proposal, validator):
            return "yes"

        round = consensus.prevote_phase(
            round, validator_network, all_yes
        )

        assert round.status == ConsensusStatus.PRECOMMIT
        assert len(round.prevotes) == 7
        assert all(v == "yes" for v in round.prevotes.values())

    def test_prevote_not_enough_yes_rejected(self, validator_network):
        """Only 3 YES out of 7 → REJECTED."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(branch_state, "branch/test/001", validators[0].address)

        # Only 3 vote YES
        def few_yes(proposal, validator):
            active = validator_network.validator_set.get_active_validators()
            idx = active.index(validator)
            return "yes" if idx < 3 else "no"

        round = consensus.prevote_phase(round, validator_network, few_yes)

        assert round.status == ConsensusStatus.REJECTED
        assert round.result is not None
        assert round.result.success is False

    def test_prevote_quorum_exact(self, validator_network):
        """Exactly 5 YES → quorum reached (2f+1 = 5)."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(branch_state, "branch/test/001", validators[0].address)

        # Exactly 5 vote YES
        def exact_quorum(proposal, validator):
            active = validator_network.validator_set.get_active_validators()
            idx = active.index(validator)
            return "yes" if idx < 5 else "no"

        round = consensus.prevote_phase(round, validator_network, exact_quorum)

        assert round.status == ConsensusStatus.PRECOMMIT
        yes_count = list(round.prevotes.values()).count("yes")
        assert yes_count == 5

    def test_precommit_quorum_reached(self, validator_network):
        """5+ precommits → COMMIT."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(branch_state, "branch/test/001", validators[0].address)

        def all_yes(proposal, validator):
            return "yes"

        round = consensus.prevote_phase(round, validator_network, all_yes)

        # 7 validators precommit
        round = consensus.precommit_phase(round, validator_network)

        assert round.status == ConsensusStatus.COMMIT
        assert len(round.precommits) >= 5

    def test_precommit_quorum_not_reached(self, validator_network):
        """Less than 5 precommits → REJECTED."""
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = make_branch_state()

        round = consensus.propose(branch_state, "branch/test/001", validators[0].address)

        def all_yes(proposal, validator):
            return "yes"

        round = consensus.prevote_phase(round, validator_network, all_yes)

        # Only 3 validators precommit
        def few_precommit(proposal, validator):
            active = validator_network.validator_set.get_active_validators()
            idx = active.index(validator)
            return "yes" if idx < 3 else "no"

        round = consensus.precommit_phase(round, validator_network, few_precommit)

        assert round.status == ConsensusStatus.REJECTED

    def test_commit_executes_merge(self, validator_network, branch_manager):
        """commit_phase calls merge_branch and returns result."""
        # Setup: create a branch in BranchManager
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=0)

        branch_name = branch_manager.create_branch("0xalice")

        # Create consensus and run through precommit
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()
        branch_state = branch_manager.get_branch_state(branch_name)

        round = consensus.propose(branch_state, branch_name, validators[0].address)

        def all_yes(proposal, validator):
            return "yes"

        round = consensus.prevote_phase(round, validator_network, all_yes)
        round = consensus.precommit_phase(round, validator_network)

        # Now commit
        round = consensus.commit_phase(round, branch_manager)

        assert round.status == ConsensusStatus.COMMIT
        assert round.result is not None
        assert round.result.success is True

    def test_full_consensus_flow_success(self, validator_network, branch_manager):
        """Full end-to-end happy path."""
        # Setup account and branch
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=0)

        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)

        # Run full consensus
        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()

        round = consensus.run_consensus(
            branch_state=branch_state,
            branch_name=branch_name,
            proposer=validators[0].address,
            branch_manager=branch_manager,
            main_state=main_state,
        )

        assert round.status == ConsensusStatus.COMMIT
        assert round.result is not None
        assert round.result.success is True
        assert round.result.merge_commit is not None

        # Verify state merged
        updated_main = branch_manager.get_main_state()
        assert "0xalice" in updated_main.accounts

    def test_full_consensus_flow_conflict_rejected(self, validator_network, branch_manager):
        """Proposal with conflicts → rejected at prevote."""
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=5)

        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)

        # Modify branch state balance to diverge from main (creates balance mismatch)
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=5)
        branch_state.accounts["0xalice"] = Account(address="0xalice", balance=50.0, nonce=2)

        consensus = MergeConsensus(validator_network)
        validators = validator_network.validator_set.get_active_validators()

        round = consensus.run_consensus(
            branch_state=branch_state,
            branch_name=branch_name,
            proposer=validators[0].address,
            branch_manager=branch_manager,
            main_state=main_state,
        )

        # Should be rejected (balance mismatch → validators vote NO)
        assert round.status != ConsensusStatus.COMMIT
        assert round.status in (ConsensusStatus.REJECTED, ConsensusStatus.PREVOTE)
        assert round.result is None or round.result.success is False


# ─── BranchManager Integration ──────────────────────────────────────────────

@pytest.mark.skipif(BranchManager is None or MergeConsensus is None,
                    reason="BranchManager or MergeConsensus not implemented yet")
class TestBranchManagerConsensus:
    """Tests for BranchManager consensus integration."""

    def test_run_consensus_no_validator_network(self, branch_manager):
        """run_consensus without validator network fails gracefully."""
        branch_name = branch_manager.create_branch("0xalice")
        result = branch_manager.run_consensus(branch_name)
        assert result is not None
        assert result.success is False

    def test_run_consensus_with_network(self, branch_manager):
        """Full consensus via BranchManager with validator network."""
        # Init validator network
        branch_manager.init_validator_network(count=7)

        # Setup account and branch
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=0)

        branch_name = branch_manager.create_branch("0xalice")

        result = branch_manager.run_consensus(branch_name)

        assert result is not None
        assert result.success is True
