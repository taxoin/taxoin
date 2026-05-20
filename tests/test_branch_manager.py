"""
Tests for BranchManager.

Tests for TODO-0002 Phase 1.3: BranchManager Implementation
"""
import asyncio
import tempfile
import time
import pytest

from src.core import Account, AsyncTransaction, Block, BlockHeader
from src.git_backend import GitBlockchain
from src.mempool import Mempool


# Import will fail until we create branch_manager.py
try:
    from src.branch_manager import BranchManager
except ImportError:
    BranchManager = None


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
