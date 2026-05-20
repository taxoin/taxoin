"""
Tests for BranchState data structure.

Tests for TODO-0002 Phase 1.2: BranchState Management
"""
import asyncio
import pytest
from copy import deepcopy

from src.core import Account, UTXO, AsyncTransaction
from src.mempool import Mempool


# Import will fail until we create branch_state.py
try:
    from src.branch_state import BranchState
except ImportError:
    BranchState = None


@pytest.mark.skipif(BranchState is None, reason="BranchState not implemented yet")
class TestBranchStateCreation:
    """Tests for BranchState creation and initialization."""

    def test_branch_state_creation(self):
        """Test creating a BranchState with all fields."""
        state = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        assert state.branch_name == "branch/0xalice/001"
        assert state.parent_hash == "0" * 64
        assert isinstance(state.accounts, dict)
        assert isinstance(state.utxo_set, dict)
        assert isinstance(state.mempool, Mempool)
        assert state.transaction_count == 0

    def test_branch_state_with_accounts(self):
        """Test BranchState with account data."""
        accounts = {
            "0xalice": Account(address="0xalice", balance=1000.0, nonce=0),
            "0xbob": Account(address="0xbob", balance=500.0, nonce=0),
        }

        state = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts=accounts,
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        assert len(state.accounts) == 2
        assert state.accounts["0xalice"].balance == 1000.0
        assert state.accounts["0xbob"].balance == 500.0

    def test_branch_state_with_utxos(self):
        """Test BranchState with UTXO data."""
        utxo_set = {
            ("tx1", 0): UTXO(tx_id="tx1", output_index=0, address="0xalice", amount=100.0),
            ("tx2", 0): UTXO(tx_id="tx2", output_index=0, address="0xbob", amount=50.0),
        }

        state = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set=utxo_set,
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        assert len(state.utxo_set) == 2
        assert state.utxo_set[("tx1", 0)].amount == 100.0

    def test_branch_state_has_lock(self):
        """Test that BranchState has an asyncio.Lock."""
        state = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        assert hasattr(state, "lock")
        assert isinstance(state.lock, asyncio.Lock)


@pytest.mark.skipif(BranchState is None, reason="BranchState not implemented yet")
class TestBranchStateClone:
    """Tests for cloning BranchState."""

    def test_clone_creates_independent_copy(self):
        """Test that clone creates a deep copy."""
        original = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=0)},
            utxo_set={("tx1", 0): UTXO(tx_id="tx1", output_index=0, address="0xalice", amount=100.0)},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=5,
            spent_utxos={("tx1", 0)},
            used_nonces={"0xalice": {0, 1, 2}},
        )

        cloned = original.clone()

        # Verify it's a different object
        assert cloned is not original
        assert cloned.accounts is not original.accounts
        assert cloned.utxo_set is not original.utxo_set
        assert cloned.spent_utxos is not original.spent_utxos
        assert cloned.used_nonces is not original.used_nonces

        # Verify data is copied
        assert cloned.branch_name == original.branch_name
        assert cloned.parent_hash == original.parent_hash
        assert cloned.accounts["0xalice"].balance == 1000.0
        assert len(cloned.utxo_set) == 1

    def test_clone_modifications_dont_affect_original(self):
        """Test that modifying clone doesn't affect original."""
        original = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=0)},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        cloned = original.clone()

        # Modify clone
        cloned.accounts["0xalice"].balance = 500.0
        cloned.accounts["0xbob"] = Account(address="0xbob", balance=100.0, nonce=0)
        cloned.transaction_count = 10

        # Original should be unchanged
        assert original.accounts["0xalice"].balance == 1000.0
        assert "0xbob" not in original.accounts
        assert original.transaction_count == 0

    def test_clone_resets_mempool(self):
        """Test that clone creates a fresh mempool."""
        original = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        # Add transaction to original mempool
        async def add_tx():
            tx = AsyncTransaction(sender="0xalice", recipient="0xbob", value=100, nonce=0)
            await original.mempool.submit(tx)

        asyncio.run(add_tx())

        cloned = original.clone()

        # Cloned mempool should be empty
        assert cloned.mempool.get_pending_count() == 0
        assert original.mempool.get_pending_count() == 1


@pytest.mark.skipif(BranchState is None, reason="BranchState not implemented yet")
class TestBranchStateIsolation:
    """Tests for state isolation between branches."""

    def test_independent_account_modifications(self):
        """Test that account modifications are isolated."""
        state1 = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=0)},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        state2 = state1.clone()

        # Modify state2
        state2.accounts["0xalice"].balance = 500.0

        # state1 should be unchanged
        assert state1.accounts["0xalice"].balance == 1000.0
        assert state2.accounts["0xalice"].balance == 500.0

    def test_independent_utxo_modifications(self):
        """Test that UTXO modifications are isolated."""
        state1 = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set={("tx1", 0): UTXO(tx_id="tx1", output_index=0, address="0xalice", amount=100.0)},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        state2 = state1.clone()

        # Remove UTXO from state2
        del state2.utxo_set[("tx1", 0)]

        # state1 should still have the UTXO
        assert ("tx1", 0) in state1.utxo_set
        assert ("tx1", 0) not in state2.utxo_set

    def test_independent_conflict_tracking(self):
        """Test that conflict tracking is isolated."""
        state1 = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        state2 = state1.clone()

        # Add spent UTXO to state2
        state2.spent_utxos.add(("tx1", 0))
        state2.used_nonces["0xalice"] = {0, 1}

        # state1 should be unchanged
        assert len(state1.spent_utxos) == 0
        assert len(state1.used_nonces) == 0
        assert len(state2.spent_utxos) == 1
        assert len(state2.used_nonces) == 1


@pytest.mark.skipif(BranchState is None, reason="BranchState not implemented yet")
class TestBranchStateConcurrency:
    """Tests for concurrent access to BranchState."""

    @pytest.mark.asyncio
    async def test_lock_prevents_concurrent_modification(self):
        """Test that lock prevents race conditions."""
        state = BranchState(
            branch_name="branch/0xalice/001",
            parent_hash="0" * 64,
            accounts={"0xalice": Account(address="0xalice", balance=1000.0, nonce=0)},
            utxo_set={},
            mempool=Mempool(),
            created_at=1716172800.0,
            last_updated=1716172800.0,
            transaction_count=0,
            spent_utxos=set(),
            used_nonces={},
        )

        async def modify_balance():
            async with state.lock:
                current = state.accounts["0xalice"].balance
                await asyncio.sleep(0.01)  # Simulate work
                state.accounts["0xalice"].balance = current - 100

        # Run two concurrent modifications
        await asyncio.gather(modify_balance(), modify_balance())

        # With proper locking, balance should be 800 (1000 - 100 - 100)
        assert state.accounts["0xalice"].balance == 800.0
