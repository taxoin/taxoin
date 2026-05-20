"""Tests for git backend."""
import os
import tempfile
import pytest

from src.git_backend import GitBlockchain, GitBackendError
from src.core import Block, BlockHeader, Transaction, make_genesis_block


@pytest.fixture
def temp_repo():
    """Create a temporary directory for each test (no chdir needed)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestGitBlockchain:
    def test_init_creates_git_repo(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        assert os.path.exists(os.path.join(temp_repo, ".git"))
        assert os.path.exists(os.path.join(temp_repo, ".taxoin"))

    def test_init_creates_genesis_block(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        assert chain.get_chain_height() >= 1

    def test_add_block_increases_height(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        h1 = chain.get_chain_height()

        header = BlockHeader(
            parent_hash="0"*64, merkle_root="test",
            timestamp=100, difficulty=4, nonce=0,
        )
        block = Block(header=header, transactions=[Transaction.coinbase("0xtest")])
        chain.add_block(block)

        assert chain.get_chain_height() == h1 + 1

    def test_get_latest_block_returns_block(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        block = chain.get_latest_block()
        assert block is not None

    def test_get_chain_summary_returns_list(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        summary = chain.get_chain_summary()
        assert isinstance(summary, list)
        assert len(summary) >= 1

    def test_verify_chain_valid(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        assert chain.verify_chain() is True

    def test_get_block_by_hash(self, temp_repo):
        chain = GitBlockchain(temp_repo)
        summary = chain.get_chain_summary()
        if summary:
            commit_hash = summary[0]["commit"]
            block_data = chain.get_block_by_hash(commit_hash)
            assert block_data is not None
            assert "header" in block_data
