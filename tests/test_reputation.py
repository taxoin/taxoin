"""Tests for Reputation system."""
import tempfile
import pytest

try:
    from src.reputation import ReputationTracker
except ImportError:
    ReputationTracker = None


@pytest.mark.skipif(ReputationTracker is None, reason="ReputationTracker not implemented")
class TestReputation:
    """Tests for reputation tracking."""

    def test_new_address_starts_at_zero(self):
        rep = ReputationTracker()
        assert rep.get_rating("0xalice") == 0.0

    def test_successful_tx_increases_rating(self):
        rep = ReputationTracker()
        rep.record_successful_tx("0xalice")
        assert rep.get_rating("0xalice") > 0.0

    def test_dispute_penalty(self):
        rep = ReputationTracker()
        rep.record_successful_tx("0xalice")
        rep.record_successful_tx("0xalice")
        before = rep.get_rating("0xalice")
        rep.record_dispute("0xalice", guilty=True)
        assert rep.get_rating("0xalice") < before

    def test_wrongful_dispute_no_penalty(self):
        rep = ReputationTracker()
        rep.record_successful_tx("0xalice")
        before = rep.get_rating("0xalice")
        rep.record_dispute("0xalice", guilty=False)
        assert rep.get_rating("0xalice") == before

    def test_multiple_providers_independent(self):
        rep = ReputationTracker()
        rep.record_successful_tx("0xalice")
        rep.record_successful_tx("0xalice")
        rep.record_successful_tx("0xalice")
        rep.record_successful_tx("0xbob")
        assert rep.get_rating("0xalice") != rep.get_rating("0xbob")

    def test_rating_capped_at_max(self):
        rep = ReputationTracker()
        for _ in range(1000):
            rep.record_successful_tx("0xalice")
        assert rep.get_rating("0xalice") <= 5.0

    def test_zero_tx_no_dispute(self):
        rep = ReputationTracker()
        assert rep.get_dispute_count("0xalice") == 0
        assert rep.get_successful_tx_count("0xalice") == 0

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/reputation.json"
            rep = ReputationTracker(store_path=path)
            rep.record_successful_tx("0xalice")
            rep.record_successful_tx("0xalice")

            rep2 = ReputationTracker(store_path=path)
            assert rep2.get_rating("0xalice") > 0.0
            assert rep2.get_successful_tx_count("0xalice") == 2

    def test_leaderboard_ordering(self):
        rep = ReputationTracker()
        rep.record_successful_tx("0xbob")
        rep.record_successful_tx("0xbob")
        rep.record_successful_tx("0xbob")
        rep.record_successful_tx("0xalice")
        rep.record_successful_tx("0xalice")

        leaders = rep.get_leaderboard()
        assert len(leaders) >= 2
        assert leaders[0][0] == "0xbob"  # higher rating first
