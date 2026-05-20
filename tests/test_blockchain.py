"""Integration tests for BlockchainEngine."""
import asyncio
import os
import tempfile
import pytest

from src.blockchain import BlockchainEngine
from src.core import AsyncTransaction


@pytest.fixture
def engine():
    """Create a fresh blockchain engine in a temp dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        eng = BlockchainEngine(tmpdir)
        eng.load_state()
        yield eng


class TestBlockchainEngine:
    def test_init_creates_genesis(self, engine):
        status = engine.get_status()
        assert status["chain_height"] >= 1

    def test_create_account(self, engine):
        engine.create_account("0xalice", 1000.0)
        assert engine.get_balance("0xalice") == 1000.0

    def test_create_account_default_balance(self, engine):
        engine.create_account("0xbob")
        assert engine.get_balance("0xbob") == 0.0

    def test_submit_invalid_tx_no_account(self, engine):
        async def test():
            tx = AsyncTransaction(sender="0xnobody", recipient="0xbob", value=10, nonce=0)
            ok, msg = await engine.submit_async_transaction(tx)
            assert ok is False
            assert "does not exist" in msg

        asyncio.run(test())

    def test_submit_and_mine(self, engine):
        engine.create_account("0xalice", 100000.0)
        engine.create_account("0xminer", 0.0)

        async def submit():
            tx = AsyncTransaction(
                sender="0xalice", recipient="0xbob",
                value=50, nonce=0, gas_price=1,
            )
            ok, msg = await engine.submit_async_transaction(tx)
            assert ok is True

        asyncio.run(submit())
        assert engine.mempool.get_pending_count() == 1

        block = engine.mine_block("0xminer")
        assert block is not None
        assert engine.mempool.get_pending_count() == 0

    def test_get_accounts(self, engine):
        engine.create_account("0xalice", 100.0)
        engine.create_account("0xbob", 50.0)
        accounts = engine.get_accounts()
        assert len(accounts) == 2
        assert "0xalice" in accounts
        assert "0xbob" in accounts

    def test_verify_empty_chain(self, engine):
        assert engine.verify() is True

    def test_get_chain(self, engine):
        chain = engine.get_chain()
        assert isinstance(chain, list)
        assert len(chain) >= 1
        assert "commit" in chain[0]

    def test_mine_multiple_blocks(self, engine):
        engine.create_account("0xminer", 0.0)
        for i in range(3):
            block = engine.mine_block("0xminer")
            assert block is not None
        assert engine.git.get_chain_height() >= 4  # genesis + 3
