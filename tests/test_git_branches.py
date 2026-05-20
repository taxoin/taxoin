"""
Tests for Git Backend branch management extensions.

Tests for TODO-0002 Phase 1.1: Git Backend Extensions
"""
import os
import tempfile
import pytest

from src.git_backend import GitBlockchain, GitBackendError
from src.core import make_genesis_block


@pytest.fixture
def git_blockchain():
    """Create a fresh GitBlockchain in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        blockchain = GitBlockchain(tmpdir)
        yield blockchain


class TestBranchManagement:
    """Tests for branch creation, switching, and management."""

    def test_create_branch(self, git_blockchain):
        """Test creating a new branch from main."""
        branch_name = "branch/0xalice/1716172800_001"

        # Create branch
        result = git_blockchain.create_branch(branch_name, from_ref="HEAD")

        assert result == branch_name
        assert branch_name in git_blockchain.list_branches()

    def test_create_branch_from_specific_commit(self, git_blockchain):
        """Test creating a branch from a specific commit."""
        # Get current HEAD
        head = git_blockchain._current_head()

        branch_name = "branch/0xbob/1716172801_001"
        result = git_blockchain.create_branch(branch_name, from_ref=head)

        assert result == branch_name
        assert branch_name in git_blockchain.list_branches()

    def test_create_branch_duplicate_fails(self, git_blockchain):
        """Test that creating duplicate branch fails."""
        branch_name = "branch/0xalice/1716172800_001"

        git_blockchain.create_branch(branch_name)

        # Second creation should fail
        with pytest.raises(GitBackendError):
            git_blockchain.create_branch(branch_name)

    def test_switch_branch(self, git_blockchain):
        """Test switching between branches."""
        branch_name = "branch/0xalice/1716172800_001"
        git_blockchain.create_branch(branch_name)

        # Switch to new branch
        git_blockchain.switch_branch(branch_name)

        # Verify we're on the new branch
        current = git_blockchain.get_current_branch()
        assert current == branch_name

    def test_switch_to_nonexistent_branch_fails(self, git_blockchain):
        """Test switching to non-existent branch fails."""
        with pytest.raises(GitBackendError):
            git_blockchain.switch_branch("nonexistent-branch")

    def test_list_branches(self, git_blockchain):
        """Test listing all branches."""
        # Initially should have master/main
        branches = git_blockchain.list_branches()
        assert len(branches) >= 1
        assert any(b in ["master", "main"] for b in branches)

        # Create new branches
        git_blockchain.create_branch("branch/0xalice/001")
        git_blockchain.create_branch("branch/0xbob/001")

        branches = git_blockchain.list_branches()
        assert "branch/0xalice/001" in branches
        assert "branch/0xbob/001" in branches
        assert len(branches) >= 3

    def test_get_current_branch(self, git_blockchain):
        """Test getting current branch name."""
        current = git_blockchain.get_current_branch()
        assert current in ["master", "main"]

        # Switch to new branch
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)
        git_blockchain.switch_branch(branch_name)

        current = git_blockchain.get_current_branch()
        assert current == branch_name

    def test_delete_branch(self, git_blockchain):
        """Test deleting a branch."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)

        # Switch back to main before deleting
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        git_blockchain.switch_branch(main_branch)

        # Delete branch
        git_blockchain.delete_branch(branch_name)

        assert branch_name not in git_blockchain.list_branches()

    def test_delete_current_branch_fails(self, git_blockchain):
        """Test that deleting current branch fails."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)
        git_blockchain.switch_branch(branch_name)

        # Cannot delete current branch
        with pytest.raises(GitBackendError):
            git_blockchain.delete_branch(branch_name)

    def test_delete_nonexistent_branch_fails(self, git_blockchain):
        """Test deleting non-existent branch fails."""
        with pytest.raises(GitBackendError):
            git_blockchain.delete_branch("nonexistent-branch")

    def test_get_branch_head(self, git_blockchain):
        """Test getting commit SHA at branch head."""
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        head = git_blockchain.get_branch_head(main_branch)

        assert head is not None
        assert len(head) == 40  # SHA-1 hash
        assert all(c in "0123456789abcdef" for c in head)

    def test_get_branch_head_nonexistent_fails(self, git_blockchain):
        """Test getting head of non-existent branch fails."""
        with pytest.raises(GitBackendError):
            git_blockchain.get_branch_head("nonexistent-branch")


class TestBranchMetadata:
    """Tests for branch metadata storage via git notes."""

    def test_set_branch_metadata(self, git_blockchain):
        """Test storing metadata for a branch."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)

        metadata = {
            "owner": "0xalice123",
            "created_at": 1716172800,
            "status": "active",
        }

        git_blockchain.set_branch_metadata(branch_name, metadata)

        # Should not raise
        assert True

    def test_get_branch_metadata(self, git_blockchain):
        """Test retrieving metadata for a branch."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)

        metadata = {
            "owner": "0xalice123",
            "created_at": 1716172800,
            "status": "active",
        }

        git_blockchain.set_branch_metadata(branch_name, metadata)
        retrieved = git_blockchain.get_branch_metadata(branch_name)

        assert retrieved == metadata
        assert retrieved["owner"] == "0xalice123"
        assert retrieved["created_at"] == 1716172800

    def test_get_metadata_nonexistent_branch_returns_empty(self, git_blockchain):
        """Test getting metadata for non-existent branch returns empty dict."""
        metadata = git_blockchain.get_branch_metadata("nonexistent-branch")
        assert metadata == {}

    def test_update_branch_metadata(self, git_blockchain):
        """Test updating existing metadata."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)

        # Set initial metadata
        metadata = {"owner": "0xalice123", "status": "active"}
        git_blockchain.set_branch_metadata(branch_name, metadata)

        # Update metadata
        updated = {"owner": "0xalice123", "status": "merged", "merged_at": 1716173000}
        git_blockchain.set_branch_metadata(branch_name, updated)

        retrieved = git_blockchain.get_branch_metadata(branch_name)
        assert retrieved["status"] == "merged"
        assert retrieved["merged_at"] == 1716173000


class TestBranchMerging:
    """Tests for merging branches."""

    def test_merge_branches_fast_forward(self, git_blockchain):
        """Test fast-forward merge."""
        # Create and switch to new branch
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)
        git_blockchain.switch_branch(branch_name)

        # Add a block on the branch
        from src.core import Block, BlockHeader
        block = Block(
            header=BlockHeader(
                parent_hash="0" * 64,
                merkle_root="test",
                timestamp=1716172800,
                difficulty=4,
                nonce=0,
            ),
            transactions=[],
            state_snapshot={},
        )
        git_blockchain.add_block(block)

        # Switch back to main
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        git_blockchain.switch_branch(main_branch)

        # Merge branch into main
        result = git_blockchain.merge_branches(branch_name, main_branch)

        assert result is not None
        assert len(result) == 40  # commit SHA

    def test_merge_branches_returns_commit_sha(self, git_blockchain):
        """Test that merge returns commit SHA."""
        branch_name = "branch/0xalice/001"
        git_blockchain.create_branch(branch_name)

        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        result = git_blockchain.merge_branches(branch_name, main_branch)

        assert result is not None
        assert len(result) == 40

    def test_merge_nonexistent_branch_fails(self, git_blockchain):
        """Test merging non-existent branch fails."""
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"

        with pytest.raises(GitBackendError):
            git_blockchain.merge_branches("nonexistent-branch", main_branch)


class TestBranchDivergence:
    """Tests for checking branch divergence."""

    def test_get_divergence_same_branch(self, git_blockchain):
        """Test divergence of branch with itself is (0, 0)."""
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"

        ahead, behind = git_blockchain.get_divergence(main_branch, main_branch)

        assert ahead == 0
        assert behind == 0

    def test_get_divergence_new_branch(self, git_blockchain):
        """Test divergence of newly created branch."""
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        branch_name = "branch/0xalice/001"

        git_blockchain.create_branch(branch_name)

        ahead, behind = git_blockchain.get_divergence(branch_name, main_branch)

        # New branch has no commits ahead or behind
        assert ahead == 0
        assert behind == 0

    def test_get_divergence_with_commits(self, git_blockchain):
        """Test divergence after adding commits to branch."""
        main_branch = "master" if "master" in git_blockchain.list_branches() else "main"
        branch_name = "branch/0xalice/001"

        # Create branch and add commit
        git_blockchain.create_branch(branch_name)
        git_blockchain.switch_branch(branch_name)

        from src.core import Block, BlockHeader
        block = Block(
            header=BlockHeader(
                parent_hash="0" * 64,
                merkle_root="test",
                timestamp=1716172800,
                difficulty=4,
                nonce=0,
            ),
            transactions=[],
            state_snapshot={},
        )
        git_blockchain.add_block(block)

        # Check divergence
        ahead, behind = git_blockchain.get_divergence(branch_name, main_branch)

        # Branch is 1 commit ahead
        assert ahead == 1
        assert behind == 0
