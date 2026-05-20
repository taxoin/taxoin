"""Tests for Attested Transactions and Balance Hold."""
import time
import pytest

from src.core import Account

try:
    from src.attested_tx import AttestedTransaction, BalanceHold, TX_TIMEOUT_BLOCKS
except ImportError:
    AttestedTransaction = None
    BalanceHold = None
    TX_TIMEOUT_BLOCKS = None


@pytest.mark.skipif(AttestedTransaction is None, reason="AttestedTransaction not implemented")
class TestAttestedTransaction:
    """Tests for attested transaction creation."""

    def test_create_attested_tx(self):
        tx = AttestedTransaction(
            consumer="0xalice",
            provider="0xbob",
            service_ref="sms:0xbob",
            amount=0.1,
            consumer_sig="alice_sig",
            provider_sig="bob_sig",
        )
        assert tx.consumer == "0xalice"
        assert tx.provider == "0xbob"
        assert tx.amount == 0.1
        assert tx.tx_id is not None
        assert len(tx.tx_id) > 0

    def test_requires_both_signatures(self):
        tx = AttestedTransaction(
            consumer="0xalice",
            provider="0xbob",
            service_ref="sms:0xbob",
            amount=0.1,
            consumer_sig="",
            provider_sig="bob_sig",
        )
        assert tx.is_valid() is False

    def test_both_signatures_present(self):
        tx = AttestedTransaction(
            consumer="0xalice",
            provider="0xbob",
            service_ref="sms:0xbob",
            amount=0.1,
            consumer_sig="alice_sig",
            provider_sig="bob_sig",
        )
        assert tx.is_valid() is True

    def test_positive_amount_required(self):
        tx = AttestedTransaction(
            consumer="0xalice",
            provider="0xbob",
            service_ref="sms:0xbob",
            amount=0.0,
            consumer_sig="alice_sig",
            provider_sig="bob_sig",
        )
        assert tx.is_valid() is False


@pytest.mark.skipif(BalanceHold is None, reason="BalanceHold not implemented")
class TestBalanceHold:
    """Tests for balance hold mechanism."""

    def setup_balances(self):
        return {"0xalice": 100.0, "0xbob": 10.0}

    def test_create_hold(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        ok = hold.create_hold("0xalice", 1.0, "tx001")
        assert ok is True
        assert balances["0xalice"] == 99.0  # available reduced
        assert hold.get_held("0xalice") == 1.0

    def test_hold_insufficient_balance(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        ok = hold.create_hold("0xalice", 200.0, "tx002")
        assert ok is False

    def test_release_hold(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        hold.create_hold("0xalice", 1.0, "tx001")
        hold.release_hold("tx001")
        assert hold.get_held("0xalice") == 0.0
        assert balances["0xalice"] == 100.0  # restored

    def test_claim_hold(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        hold.create_hold("0xalice", 1.0, "tx001")
        hold.claim_hold("tx001", "0xbob", balances)
        assert balances["0xalice"] == 99.0  # deducted
        assert balances["0xbob"] == 11.0   # credited
        assert hold.get_held("0xalice") == 0.0

    def test_multiple_holds_same_consumer(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        hold.create_hold("0xalice", 1.0, "tx001")
        hold.create_hold("0xalice", 2.0, "tx002")
        assert hold.get_held("0xalice") == 3.0
        assert balances["0xalice"] == 97.0

    def test_release_one_hold_keeps_others(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        hold.create_hold("0xalice", 1.0, "tx001")
        hold.create_hold("0xalice", 2.0, "tx002")
        hold.release_hold("tx001")
        assert hold.get_held("0xalice") == 2.0
        assert balances["0xalice"] == 98.0  # 100 - 1 - 2 + 1 = 98
        # Actually: 100 - 1 - 2 = 97. Release tx001: 97, held = 2
        # Release just restores the held amount to available

    def test_hold_nonexistent_tx(self):
        balances = self.setup_balances()
        hold = BalanceHold(balances)
        hold.release_hold("nonexistent")  # should not crash
        hold.claim_hold("nonexistent", "0xbob", balances)  # should not crash
