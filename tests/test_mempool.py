"""Tests for the async mempool."""
import pytest
from src.mempool import Mempool
from src.core import AsyncTransaction, Transaction, TxInput, TxOutput


@pytest.fixture
def mempool():
    return Mempool(max_size=10)


class TestMempool:
    @pytest.mark.asyncio
    async def test_submit_and_get(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=10, nonce=0)
        ok = await mempool.submit(tx)
        assert ok is True
        assert mempool.get_pending_count() == 1

    @pytest.mark.asyncio
    async def test_reject_duplicate(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=10, nonce=0)
        await mempool.submit(tx)
        ok = await mempool.submit(tx)
        assert ok is False  # duplicate

    @pytest.mark.asyncio
    async def test_remove_confirmed(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=10, nonce=0)
        await mempool.submit(tx)
        mempool.remove_confirmed({tx.tx_hash})
        assert mempool.get_pending_count() == 0

    def test_validate_tx_valid(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=10, nonce=0)
        # total cost = 10 + 1*21000 = 21010, need >= that
        valid, msg = mempool.validate_tx(tx, sender_balance=50000, sender_nonce=0)
        assert valid is True
        assert msg == "ok"

    def test_validate_tx_insufficient_balance(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=100, nonce=0)
        valid, msg = mempool.validate_tx(tx, sender_balance=10, sender_nonce=0)
        assert valid is False
        assert "insufficient" in msg

    def test_validate_tx_low_nonce(self, mempool):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=10, nonce=0)
        valid, msg = mempool.validate_tx(tx, sender_balance=100, sender_nonce=5)
        assert valid is False
        assert "nonce too low" in msg

    @pytest.mark.asyncio
    async def test_get_pending_transactions(self, mempool):
        txs = [
            AsyncTransaction(sender="0xa", recipient="0xb", value=i, nonce=i)
            for i in range(3)
        ]
        for tx in txs:
            await mempool.submit(tx)
        pending = mempool.get_pending_transactions(max_count=2)
        assert len(pending) == 2

    @pytest.mark.asyncio
    async def test_mempool_max_size(self, mempool):
        for i in range(15):
            tx = AsyncTransaction(sender="0xa", recipient="0xb", value=1, nonce=i)
            await mempool.submit(tx)
        assert mempool.get_pending_count() <= 10
