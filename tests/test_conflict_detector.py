"""
Tests for Conflict Detector.

Tests for TODO-0002 Phase 2: Conflict Detection
"""
import pytest

from src.core import Account, UTXO
from src.mempool import Mempool
from src.branch_state import BranchState


# Import will fail until we create conflict_detector.py
try:
    from src.conflict_detector import (
        ConflictType,
        Conflict,
        ResolutionStrategy,
        MergeResult,
        ConflictDetector,
    )
except ImportError:
    ConflictType = None
    Conflict = None
    ResolutionStrategy = None
    MergeResult = None
    ConflictDetector = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_branch_state(
    branch_name="branch/test/001",
    parent_hash="0" * 64,
    accounts=None,
    utxo_set=None,
    spent_utxos=None,
    used_nonces=None,
) -> BranchState:
    """Helper to create a BranchState with default empty values."""
    return BranchState(
        branch_name=branch_name,
        parent_hash=parent_hash,
        accounts=accounts or {},
        utxo_set=utxo_set or {},
        mempool=Mempool(),
        created_at=1716172800.0,
        last_updated=1716172800.0,
        transaction_count=0,
        spent_utxos=spent_utxos or set(),
        used_nonces=used_nonces or {},
    )


# ─── UTXO Conflict Detection ─────────────────────────────────────────────────

@pytest.mark.skipif(ConflictDetector is None, reason="ConflictDetector not implemented yet")
class TestUTXOConflictDetection:
    """Tests for UTXO double-spend and missing-UTXO detection."""

    def test_detect_no_conflicts_empty_branches(self):
        """Two branches with no spent UTXOs — no conflicts."""
        branch = make_branch_state()
        target = make_branch_state()

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_no_conflicts_independent_spends(self):
        """Different UTXOs spent in each branch — no conflict."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0), ("tx2", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0),
                       ("tx2", 0): UTXO("tx2", 0, "0xbob", 50.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx3", 0)},
            utxo_set={("tx3", 0): UTXO("tx3", 0, "0xcarol", 75.0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_double_spend_same_utxo(self):
        """Same UTXO spent in both branches — one double-spend conflict."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.UTXO_DOUBLE_SPEND
        assert conflicts[0].outpoint == ("tx1", 0)

    def test_detect_multiple_double_spends(self):
        """Three overlapping UTXOs — three double-spend conflicts."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0), ("tx2", 0), ("tx3", 0)},
            utxo_set={
                ("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0),
                ("tx2", 0): UTXO("tx2", 0, "0xbob", 50.0),
                ("tx3", 0): UTXO("tx3", 0, "0xcarol", 25.0),
            },
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0), ("tx2", 0), ("tx3", 0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        assert len(conflicts) == 3
        assert all(c.conflict_type == ConflictType.UTXO_DOUBLE_SPEND for c in conflicts)
        outpoints = {c.outpoint for c in conflicts}
        assert outpoints == {("tx1", 0), ("tx2", 0), ("tx3", 0)}

    def test_detect_utxo_branch_created_utxo_no_conflict(self):
        """UTXO created and spent in branch (not in target) — not a conflict."""
        branch = make_branch_state(
            spent_utxos={("tx_new", 0)},
            utxo_set={("tx_new", 0): UTXO("tx_new", 0, "0xalice", 100.0)},
        )
        target = make_branch_state()

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        assert len(conflicts) == 0


# ─── Nonce Conflict Detection ───────────────────────────────────────────────

@pytest.mark.skipif(ConflictDetector is None, reason="ConflictDetector not implemented yet")
class TestNonceConflictDetection:
    """Tests for nonce collision detection."""

    def test_detect_no_nonce_conflicts(self):
        """Different addresses, independent nonces — no conflict."""
        branch = make_branch_state(used_nonces={"0xalice": {0, 1}})
        target = make_branch_state(used_nonces={"0xbob": {0, 1}})

        conflicts = ConflictDetector.detect_nonce_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_nonce_collision_same_address(self):
        """Same address, same nonce — collision."""
        branch = make_branch_state(used_nonces={"0xalice": {0, 1, 2}})
        target = make_branch_state(used_nonces={"0xalice": {2, 3}})

        conflicts = ConflictDetector.detect_nonce_conflicts(branch, target)

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.NONCE_COLLISION
        assert conflicts[0].address == "0xalice"

    def test_detect_nonce_collision_multiple_addresses(self):
        """Collisions on multiple addresses."""
        branch = make_branch_state(used_nonces={"0xalice": {0, 1}, "0xbob": {0}})
        target = make_branch_state(used_nonces={"0xalice": {1}, "0xbob": {0, 1}})

        conflicts = ConflictDetector.detect_nonce_conflicts(branch, target)

        assert len(conflicts) == 2
        addresses = {c.address for c in conflicts}
        assert addresses == {"0xalice", "0xbob"}

    def test_detect_nonce_no_conflict_different_nonces(self):
        """Same address, different nonces — no conflict."""
        branch = make_branch_state(used_nonces={"0xalice": {0, 1, 2}})
        target = make_branch_state(used_nonces={"0xalice": {3, 4, 5}})

        conflicts = ConflictDetector.detect_nonce_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_nonce_empty_used_nonces(self):
        """Both branches have empty used_nonces — no conflict."""
        branch = make_branch_state(used_nonces={})
        target = make_branch_state(used_nonces={})

        conflicts = ConflictDetector.detect_nonce_conflicts(branch, target)

        assert len(conflicts) == 0


# ─── Balance Conflict Detection ─────────────────────────────────────────────

@pytest.mark.skipif(ConflictDetector is None, reason="ConflictDetector not implemented yet")
class TestBalanceConflictDetection:
    """Tests for balance mismatch detection."""

    def test_detect_no_balance_conflicts(self):
        """Balances identical — no conflict."""
        branch = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=5),
                "0xbob": Account(address="0xbob", balance=500.0, nonce=3),
            },
        )
        target = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=5),
                "0xbob": Account(address="0xbob", balance=500.0, nonce=3),
            },
        )

        conflicts = ConflictDetector.detect_balance_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_balance_mismatch(self):
        """Diverged balance — mismatch."""
        branch = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=900.0, nonce=5),
            },
        )
        target = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=5),
            },
        )

        conflicts = ConflictDetector.detect_balance_conflicts(branch, target)

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.BALANCE_MISMATCH
        assert conflicts[0].address == "0xalice"

    def test_detect_balance_mismatch_nonzero_nonce_only_no_conflict(self):
        """Different nonces but same balance — no balance conflict."""
        branch = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=10),
            },
        )
        target = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=5),
            },
        )

        conflicts = ConflictDetector.detect_balance_conflicts(branch, target)

        assert len(conflicts) == 0

    def test_detect_balance_mismatch_multiple_accounts(self):
        """Mismatches on several accounts."""
        branch = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=800.0, nonce=1),
                "0xbob": Account(address="0xbob", balance=400.0, nonce=1),
                "0xcarol": Account(address="0xcarol", balance=100.0, nonce=0),
            },
        )
        target = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=1000.0, nonce=5),
                "0xbob": Account(address="0xbob", balance=500.0, nonce=3),
                "0xcarol": Account(address="0xcarol", balance=100.0, nonce=0),
            },
        )

        conflicts = ConflictDetector.detect_balance_conflicts(branch, target)

        assert len(conflicts) == 2
        addresses = {c.address for c in conflicts}
        assert addresses == {"0xalice", "0xbob"}

    def test_detect_balance_address_only_in_branch(self):
        """Address only in source branch — not a conflict (new account)."""
        branch = make_branch_state(
            accounts={
                "0xalice": Account(address="0xalice", balance=100.0, nonce=0),
            },
        )
        target = make_branch_state(accounts={})

        conflicts = ConflictDetector.detect_balance_conflicts(branch, target)

        assert len(conflicts) == 0


# ─── Combined Detection ─────────────────────────────────────────────────────

@pytest.mark.skipif(ConflictDetector is None, reason="ConflictDetector not implemented yet")
class TestConflictDetectorIntegration:
    """Tests for detect_all aggregating all conflict types."""

    def test_detect_all_aggregates_all_types(self):
        """One of each type — detect_all returns 3 conflicts."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
            used_nonces={"0xalice": {1}},
            accounts={"0xalice": Account(address="0xalice", balance=900.0, nonce=5)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
            used_nonces={"0xalice": {1}},
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=5)},
        )

        conflicts = ConflictDetector.detect_all(branch, target)

        assert len(conflicts) == 3
        types = {c.conflict_type for c in conflicts}
        assert types == {ConflictType.UTXO_DOUBLE_SPEND, ConflictType.NONCE_COLLISION, ConflictType.BALANCE_MISMATCH}

    def test_detect_all_no_conflicts(self):
        """No conflicts — empty list."""
        branch = make_branch_state()
        target = make_branch_state()

        conflicts = ConflictDetector.detect_all(branch, target)

        assert len(conflicts) == 0

    def test_detect_all_ordering(self):
        """UTXO conflicts listed before nonce before balance."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
            used_nonces={"0xalice": {1}},
            accounts={"0xalice": Account(address="0xalice", balance=900.0, nonce=5)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
            used_nonces={"0xalice": {1}},
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=5)},
        )

        conflicts = ConflictDetector.detect_all(branch, target)

        # Order: UTXO_DOUBLE_SPEND (0), NONCE_COLLISION (1), BALANCE_MISMATCH (2)
        assert len(conflicts) >= 3
        assert conflicts[0].conflict_type == ConflictType.UTXO_DOUBLE_SPEND


# ─── Resolution Strategy ────────────────────────────────────────────────────

@pytest.mark.skipif(ConflictDetector is None or MergeResult is None or ResolutionStrategy is None,
                    reason="ConflictDetector/MergeResult/ResolutionStrategy not implemented yet")
class TestResolutionStrategy:
    """Tests for conflict resolution via ResolutionStrategy enum."""

    def test_abort_on_conflict(self):
        """ABORT strategy with conflicts — returns MergeResult with success=False."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)
        result = ConflictDetector.resolve(conflicts, ResolutionStrategy.ABORT)

        assert isinstance(result, MergeResult)
        assert result.success is False
        assert len(result.conflicts) == 1

    def test_abort_no_conflicts(self):
        """ABORT strategy with no conflicts — MergeResult with success=True."""
        conflicts = []
        result = ConflictDetector.resolve(conflicts, ResolutionStrategy.ABORT)

        assert result.success is True
        assert len(result.conflicts) == 0

    def test_prefer_source_strategy(self):
        """PREFER_SOURCE — source values win."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)
        result = ConflictDetector.resolve(conflicts, ResolutionStrategy.PREFER_SOURCE)

        assert result.success is True

    def test_prefer_target_strategy(self):
        """PREFER_TARGET — target values win."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)
        result = ConflictDetector.resolve(conflicts, ResolutionStrategy.PREFER_TARGET)

        assert result.success is True

    def test_manual_strategy_raises(self):
        """MANUAL strategy with conflicts — raises MergeConflictError."""
        branch = make_branch_state(
            spent_utxos={("tx1", 0)},
            utxo_set={("tx1", 0): UTXO("tx1", 0, "0xalice", 100.0)},
        )
        target = make_branch_state(
            spent_utxos={("tx1", 0)},
        )

        conflicts = ConflictDetector.detect_utxo_conflicts(branch, target)

        with pytest.raises(Exception) as excinfo:
            ConflictDetector.resolve(conflicts, ResolutionStrategy.MANUAL)

        assert "conflict" in str(excinfo.value).lower()
