"""
Tests for BranchManager.

Tests for TODO-0002 Phase 1.3: BranchManager Implementation
"""
import asyncio
import tempfile
import time
import pytest

from src.core import Account, AsyncTransaction, Block, BlockHeader, UTXO
from src.git_backend import GitBlockchain
from src.mempool import Mempool


# Import will fail until we create branch_manager.py
try:
    from src.branch_manager import BranchManager
except ImportError:
    BranchManager = None

try:
    from src.conflict_detector import ConflictDetector, MergeResult, ResolutionStrategy
except ImportError:
    ConflictDetector = None
    MergeResult = None
    ResolutionStrategy = None


@pytest.fixture
def branch_manager():
    """Create a BranchManager in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = BranchManager(tmpdir)
        yield manager


@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented yet")
class TestBranchCreation:
    """Tests for branch creation."""

    def test_create_branch(self, branch_manager):
        """Test creating a new branch."""
        wallet = "0xalice123"
        branch_name = branch_manager.create_branch(wallet)

        assert branch_name.startswith(f"branch/{wallet}/")
        assert branch_name in branch_manager.list_branches()

    def test_branch_naming_convention(self, branch_manager):
        """Test that branch names follow convention."""
        wallet = "0xalice123"
        branch_name = branch_manager.create_branch(wallet)

        # Format: branch/{wallet}/{timestamp}_{sequence}
        parts = branch_name.split("/")
        assert len(parts) == 3
        assert parts[0] == "branch"
        assert parts[1] == wallet
        assert "_" in parts[2]

        timestamp_seq = parts[2].split("_")
        assert len(timestamp_seq) == 2
        assert timestamp_seq[0].isdigit()  # timestamp
        assert timestamp_seq[1].isdigit()  # sequence

    def test_create_multiple_branches_same_wallet(self, branch_manager):
        """Test creating multiple branches for same wallet."""
        wallet = "0xalice123"

        branch1 = branch_manager.create_branch(wallet)
        time.sleep(0.01)  # Ensure different timestamp
        branch2 = branch_manager.create_branch(wallet)

        assert branch1 != branch2
        assert branch1 in branch_manager.list_branches()
        assert branch2 in branch_manager.list_branches()

    def test_create_branch_clones_main_state(self, branch_manager):
        """Test that new branch clones state from main."""
        # Add account to main
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=1000.0, nonce=0)

        # Create branch
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)

        # Branch should have cloned account
        assert "0xalice" in branch_state.accounts
        assert branch_state.accounts["0xalice"].balance == 1000.0

    def test_branch_state_isolation(self, branch_manager):
        """Test that branch state is isolated from main."""
        # Create branch
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)

        # Modify branch state
        branch_state.accounts["0xbob"] = Account(address="0xbob", balance=500.0, nonce=0)

        # Main state should be unchanged
        main_state = branch_manager.get_main_state()
        assert "0xbob" not in main_state.accounts


@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented yet")
class TestBranchTransactions:
    """Tests for submitting transactions to branches."""

    @pytest.mark.asyncio
    async def test_submit_tx_to_branch(self, branch_manager):
        """Test submitting transaction to a branch."""
        # Setup
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xalice"] = Account(address="0xalice", balance=1000.0, nonce=0)
        branch_state.accounts["0xbob"] = Account(address="0xbob", balance=0.0, nonce=0)

        # Submit transaction
        tx = AsyncTransaction(
            sender="0xalice",
            recipient="0xbob",
            value=100.0,
            nonce=0,
            gas_price=0.0,
            gas_limit=0,
        )

        ok, msg = await branch_manager.submit_tx_to_branch(branch_name, tx)

        assert ok is True
        assert branch_state.mempool.get_pending_count() == 1

    @pytest.mark.asyncio
    async def test_submit_tx_insufficient_balance_fails(self, branch_manager):
        """Test that tx with insufficient balance fails."""
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xalice"] = Account(address="0xalice", balance=50.0, nonce=0)

        tx = AsyncTransaction(
            sender="0xalice",
            recipient="0xbob",
            value=100.0,
            nonce=0,
            gas_price=0.0,
            gas_limit=0,
        )

        ok, msg = await branch_manager.submit_tx_to_branch(branch_name, tx)

        assert ok is False
        assert "balance" in msg.lower() or "insufficient" in msg.lower()

    @pytest.mark.asyncio
    async def test_submit_tx_to_nonexistent_branch_fails(self, branch_manager):
        """Test submitting to non-existent branch fails."""
        tx = AsyncTransaction(
            sender="0xalice",
            recipient="0xbob",
            value=100.0,
            nonce=0,
        )

        ok, msg = await branch_manager.submit_tx_to_branch("nonexistent-branch", tx)

        assert ok is False
        assert "not exist" in msg.lower() or "not found" in msg.lower()


@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented yet")
class TestBranchMining:
    """Tests for mining blocks on branches."""

    def test_mine_block_on_branch(self, branch_manager):
        """Test mining a block on a branch."""
        # Create branch with transaction
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xalice"] = Account(address="0xalice", balance=1000.0, nonce=0)
        branch_state.accounts["0xminer"] = Account(address="0xminer", balance=0.0, nonce=0)

        async def add_tx():
            tx = AsyncTransaction(
                sender="0xalice",
                recipient="0xminer",
                value=100.0,
                nonce=0,
                gas_price=0.0,
                gas_limit=0,
            )
            await branch_state.mempool.submit(tx)

        asyncio.run(add_tx())

        # Mine block
        block = branch_manager.mine_block_on_branch(branch_name, "0xminer")

        assert block is not None
        assert len(block.transactions) > 0  # At least coinbase

    def test_mine_block_updates_branch_state(self, branch_manager):
        """Test that mining updates branch state."""
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xminer"] = Account(address="0xminer", balance=0.0, nonce=0)

        initial_balance = branch_state.accounts["0xminer"].balance

        # Mine empty block
        block = branch_manager.mine_block_on_branch(branch_name, "0xminer")

        # Miner should receive coinbase reward
        assert branch_state.accounts["0xminer"].balance > initial_balance

    def test_mine_block_on_nonexistent_branch_fails(self, branch_manager):
        """Test mining on non-existent branch fails."""
        block = branch_manager.mine_block_on_branch("nonexistent-branch", "0xminer")
        assert block is None


@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented yet")
class TestBranchQueries:
    """Tests for querying branch state."""

    def test_list_branches(self, branch_manager):
        """Test listing all branches."""
        # Initially only main
        branches = branch_manager.list_branches()
        assert "main" in branches or "master" in branches

        # Create branches
        branch_manager.create_branch("0xalice")
        branch_manager.create_branch("0xbob")

        branches = branch_manager.list_branches()
        assert len(branches) >= 3  # main + 2 new

    def test_get_branch_state(self, branch_manager):
        """Test getting branch state."""
        branch_name = branch_manager.create_branch("0xalice")
        state = branch_manager.get_branch_state(branch_name)

        assert state is not None
        assert state.branch_name == branch_name
        assert isinstance(state.accounts, dict)

    def test_get_nonexistent_branch_state_returns_none(self, branch_manager):
        """Test getting non-existent branch returns None."""
        state = branch_manager.get_branch_state("nonexistent-branch")
        assert state is None

    def test_get_main_state(self, branch_manager):
        """Test getting main branch state."""
        main_state = branch_manager.get_main_state()

        assert main_state is not None
        assert isinstance(main_state.accounts, dict)


@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented yet")
class TestBranchMetadata:
    """Tests for branch metadata management."""

    def test_branch_metadata_stored(self, branch_manager):
        """Test that branch metadata is stored."""
        wallet = "0xalice123"
        branch_name = branch_manager.create_branch(wallet)

        # Get metadata from git
        metadata = branch_manager.git.get_branch_metadata(branch_name)

        assert metadata is not None
        assert "owner" in metadata
        assert metadata["owner"] == wallet

    def test_branch_metadata_includes_timestamp(self, branch_manager):
        """Test that metadata includes creation timestamp."""
        branch_name = branch_manager.create_branch("0xalice")
        metadata = branch_manager.git.get_branch_metadata(branch_name)

        assert "created_at" in metadata
        assert isinstance(metadata["created_at"], (int, float))

    def test_branch_metadata_includes_status(self, branch_manager):
        """Test that metadata includes status."""
        branch_name = branch_manager.create_branch("0xalice")
        metadata = branch_manager.git.get_branch_metadata(branch_name)

        assert "status" in metadata
        assert metadata["status"] == "active"


@pytest.mark.skipif(BranchManager is None or MergeResult is None or ResolutionStrategy is None,
                    reason="BranchManager or ConflictDetector not implemented yet")
class TestBranchMerge:
    """Tests for merging branches with conflict detection."""

    def test_merge_branch_no_conflicts_success(self, branch_manager):
        """Two branches with independent accounts — merge succeeds."""
        # Create source branch
        source = branch_manager.create_branch("0xalice")
        source_state = branch_manager.get_branch_state(source)
        source_state.accounts["0xalice"] = Account(address="0xalice", balance=100.0, nonce=0)

        # Merge into main
        result = branch_manager.merge_branch(source)

        assert result.success is True
        assert result.merge_commit is not None
        assert len(result.conflicts) == 0

        # Source branch state should be merged into target (main)
        main_state = branch_manager.get_main_state()
        assert "0xalice" in main_state.accounts
        assert main_state.accounts["0xalice"].balance == 100.0

    def test_merge_branch_updates_main_state(self, branch_manager):
        """After merge, main state reflects merged changes."""
        # Setup main with an account
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xbob"] = Account(address="0xbob", balance=500.0, nonce=0)

        # Create branch, modify account
        source = branch_manager.create_branch("0xbob")
        source_state = branch_manager.get_branch_state(source)
        source_state.accounts["0xbob"] = Account(address="0xbob", balance=300.0, nonce=1)
        source_state.accounts["0xalice"] = Account(address="0xalice", balance=200.0, nonce=0)

        # Merge with PREFER_SOURCE (balance conflict exists: 300 vs 500)
        result = branch_manager.merge_branch(source, strategy=ResolutionStrategy.PREFER_SOURCE)

        assert result.success is True

        # Main should have both accounts, with updated bob balance
        main_state = branch_manager.get_main_state()
        assert main_state.accounts["0xbob"].balance == 300.0
        assert main_state.accounts["0xalice"].balance == 200.0

    def test_merge_branch_with_conflicts_aborts(self, branch_manager):
        """Double-spend conflict — ABORT returns MergeResult with success=False."""
        # Setup: create UTXO in main
        main_state = branch_manager.get_main_state()
        main_state.utxo_set[("tx1", 0)] = UTXO(tx_id="tx1", output_index=0, address="0xalice", amount=100.0)

        # Create branch, spend the same UTXO in both
        source = branch_manager.create_branch("0xalice")
        source_state = branch_manager.get_branch_state(source)
        source_state.utxo_set[("tx1", 0)] = UTXO(tx_id="tx1", output_index=0, address="0xalice", amount=100.0)
        source_state.spent_utxos.add(("tx1", 0))
        main_state.spent_utxos.add(("tx1", 0))

        # Merge — should detect double-spend
        result = branch_manager.merge_branch(source, strategy=ResolutionStrategy.ABORT)

        assert result.success is False
        assert len(result.conflicts) > 0
        assert "utxo_double_spend" in result.conflicts[0].conflict_type.value

    def test_merge_branch_nonexistent_source_fails(self, branch_manager):
        """Merging non-existent branch fails gracefully."""
        result = branch_manager.merge_branch("nonexistent-branch")

        assert result.success is False
        assert "does not exist" in result.message.lower()

    def test_merge_branch_with_conflict_prefer_source(self, branch_manager):
        """PREFER_SOURCE strategy resolves conflict by choosing source values."""
        # Setup account with diverging balances
        main_state = branch_manager.get_main_state()
        main_state.accounts["0xalice"] = Account(address="0xalice", balance=1000.0, nonce=5)

        # Create branch with different balance
        source = branch_manager.create_branch("0xalice")
        source_state = branch_manager.get_branch_state(source)
        source_state.accounts["0xalice"] = Account(address="0xalice", balance=900.0, nonce=6)

        # Merge with PREFER_SOURCE
        result = branch_manager.merge_branch(source, strategy=ResolutionStrategy.PREFER_SOURCE)

        assert result.success is True
        assert len(result.conflicts) > 0  # Should detect balance mismatch

        # Source balance should win
        main_state = branch_manager.get_main_state()
        assert main_state.accounts["0xalice"].balance == 900.0

    def test_merge_branch_source_removed_after_merge(self, branch_manager):
        """Source branch is removed from BranchManager after merge."""
        source = branch_manager.create_branch("0xalice")
        assert source in branch_manager.branches

        result = branch_manager.merge_branch(source)
        assert result.success is True

        assert source not in branch_manager.branches



@pytest.mark.skipif(BranchManager is None, reason="BranchManager not implemented")
class TestMiningWithoutPoW:
    """Tests for block creation without Proof of Work."""

    def test_mine_block_without_pow_succeeds(self, branch_manager):
        """Block can be mined without PoW when skip_pow=True."""
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xminer"] = Account(address="0xminer", balance=0.0, nonce=0)

        block = branch_manager.mine_block_on_branch(branch_name, "0xminer", skip_pow=True)

        assert block is not None
        assert len(block.transactions) >= 1

    def test_mine_block_without_pow_updates_state(self, branch_manager):
        """State updates work without PoW."""
        branch_name = branch_manager.create_branch("0xalice")
        branch_state = branch_manager.get_branch_state(branch_name)
        branch_state.accounts["0xminer"] = Account(address="0xminer", balance=0.0, nonce=0)

        initial_height = branch_manager.git.get_chain_height()
        block = branch_manager.mine_block_on_branch(branch_name, "0xminer", skip_pow=True)

        assert block is not None
        assert branch_manager.git.get_chain_height() == initial_height + 1
        assert branch_state.accounts["0xminer"].balance > 0.0

    def test_mine_block_without_pow_on_nonexistent_branch(self, branch_manager):
        """skip_pow still returns None for nonexistent branch."""
        block = branch_manager.mine_block_on_branch(
            "nonexistent-branch", "0xminer", skip_pow=True
        )
        assert block is None
