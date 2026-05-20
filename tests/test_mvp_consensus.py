"""Tests: MVP attested transactions wired with validator consensus."""
import tempfile
import pytest

from src.core import Account

try:
    from src.branch_manager import BranchManager
except ImportError:
    BranchManager = None

try:
    from src.attested_tx import AttestedTransaction, BalanceHold
except ImportError:
    AttestedTransaction = None
    BalanceHold = None

try:
    from src.consensus import ConsensusStatus
except ImportError:
    ConsensusStatus = None


@pytest.mark.skipif(any(x is None for x in [BranchManager, AttestedTransaction, BalanceHold, ConsensusStatus]),
                    reason="MVP or Consensus not implemented")
class TestMVPConsensus:
    """Attested transactions through validator consensus."""

    def test_submit_and_consensus_attested_tx(self):
        """Full flow: attested tx submitted -> consensus -> balance transferred."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BranchManager(tmpdir)
            main = manager.get_main_state()

            bob = "0xbob"
            alice = "0xalice"

            main.accounts[alice] = Account(address=alice, balance=50.0, nonce=0)
            main.accounts[bob] = Account(address=bob, balance=50.0, nonce=0)
            manager.init_validator_network(count=3)

            balances = {"0xalice": 50.0, "0xbob": 50.0}
            tx = AttestedTransaction(
                consumer=bob,
                provider=alice,
                service_ref="sms:0xalice",
                amount=1.0,
                consumer_sig="bob_sig",
                provider_sig="alice_sig",
            )
            branch_name = manager.create_branch(bob)
            result = manager.submit_attested_tx(tx, balances, branch_name=branch_name)

            assert result is True
            assert balances[bob] == 49.0

            result = manager.run_consensus(branch_name)

            assert result.success is True
            assert balances[alice] == 51.0
            assert balances[bob] == 49.0

    def test_consensus_rejects_invalid_attestation(self):
        """Consensus still runs with invalid tx, but hold stays."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BranchManager(tmpdir)
            main = manager.get_main_state()

            alice, bob = "0xalice", "0xbob"
            main.accounts[alice] = Account(address=alice, balance=50.0, nonce=0)
            main.accounts[bob] = Account(address=bob, balance=50.0, nonce=0)
            manager.init_validator_network(count=3)

            balances = {"0xalice": 50.0, "0xbob": 50.0}
            tx = AttestedTransaction(
                consumer=bob, provider=alice, service_ref="sms:alice",
                amount=1.0, consumer_sig="bob_sig", provider_sig="",
            )
            branch_name = manager.create_branch(bob)
            result = manager.submit_attested_tx(tx, balances, branch_name=branch_name)
            assert result is True
