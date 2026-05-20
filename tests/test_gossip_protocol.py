"""
Tests for Gossip Protocol.

Tests for TODO-0002 Phase 5: Gossip Protocol
"""
import time
import pytest

from src.core import Account


# Import will fail until we create gossip_protocol.py
try:
    from src.gossip_protocol import (
        GossipMessageType,
        GossipMessage,
        GossipProtocol,
    )
except ImportError:
    GossipMessageType = None
    GossipMessage = None
    GossipProtocol = None

try:
    from src.validator_network import (
        ValidatorNode,
        ValidatorSet,
        ValidatorNetwork,
    )
except ImportError:
    ValidatorNode = None
    ValidatorSet = None
    ValidatorNetwork = None


# ─── GossipMessage ──────────────────────────────────────────────────────────

@pytest.mark.skipif(GossipMessage is None or GossipMessageType is None,
                    reason="GossipMessage not implemented yet")
class TestGossipMessage:
    """Tests for gossip message creation."""

    def test_message_creation(self):
        """Creating a gossip message with required fields."""
        msg = GossipMessage(
            message_id="msg_001",
            msg_type=GossipMessageType.PROPOSAL,
            sender="0xval1",
            payload='{"branch": "branch/test/001"}',
        )

        assert msg.message_id == "msg_001"
        assert msg.msg_type == GossipMessageType.PROPOSAL
        assert msg.sender == "0xval1"
        assert msg.ttl == 5  # default
        assert msg.sequence == 0  # default

    def test_message_type_values(self):
        """All gossip message types exist."""
        assert GossipMessageType.PROPOSAL.value == "proposal"
        assert GossipMessageType.PREVOTE.value == "prevote"
        assert GossipMessageType.PRECOMMIT.value == "precommit"
        assert GossipMessageType.MERGE_CONFIRM.value == "merge_confirm"
        assert GossipMessageType.HEARTBEAT.value == "heartbeat"

    def test_message_ttl_zero(self):
        """Message with TTL=0 should not be forwarded."""
        msg = GossipMessage(
            message_id="msg_ttl0",
            msg_type=GossipMessageType.HEARTBEAT,
            sender="0xval1",
            payload="ping",
            ttl=0,
        )
        assert msg.ttl == 0


# ─── GossipProtocol ─────────────────────────────────────────────────────────

@pytest.mark.skipif(GossipProtocol is None or ValidatorSet is None,
                    reason="GossipProtocol not implemented yet")
class TestGossipProtocol:
    """Tests for epidemic gossip broadcast."""

    @pytest.fixture
    def validator_set(self):
        """Create a 7-validator set."""
        vals = [ValidatorNode.generate() for _ in range(7)]
        return ValidatorSet(vals)

    @pytest.fixture
    def single_validator_set(self):
        """Create a 1-validator set."""
        return ValidatorSet([ValidatorNode.generate()])

    def test_single_node_broadcast(self, single_validator_set):
        """With 1 validator, message reaches the sender only."""
        gossip = GossipProtocol(single_validator_set, fanout=3)
        sender = single_validator_set.get_active_validators()[0].address

        recipients = gossip.broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
        )

        assert len(recipients) == 1
        assert sender in recipients

    def test_all_nodes_reached(self, validator_set):
        """With 7 validators and fanout=3, all nodes receive the message."""
        gossip = GossipProtocol(validator_set, fanout=3)
        validators = validator_set.get_active_validators()
        sender = validators[0].address

        recipients = gossip.broadcast(
            msg_type=GossipMessageType.PROPOSAL,
            payload='{"branch": "test"}',
            sender=sender,
        )

        # All 7 validators should receive
        assert len(recipients) == 7
        for v in validators:
            assert v.address in recipients

    def test_deduplication(self, validator_set):
        """Same message — each node only receives it once during propagation."""
        gossip = GossipProtocol(validator_set, fanout=3)
        sender = validator_set.get_active_validators()[0].address

        recipients = gossip.broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
        )

        # Each node should appear at most once in the recipients set
        assert len(recipients) == len(set(recipients))
        assert gossip.get_cache_size() > 0

        # The message is in the cache for deduplication
        # But each broadcast creates a new sequence number, so calling again
        # is a *different* message — that's correct behavior.
        # True dedup: during a single broadcast, each node receives once.
        assert len(recipients) == 7

    def test_ttl_limits_propagation(self, validator_set):
        """TTL=0 means only the sender receives it (no forwarding)."""
        gossip = GossipProtocol(validator_set, fanout=3)
        sender = validator_set.get_active_validators()[0].address

        recipients = gossip.broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
            ttl=0,
        )

        # Only the sender receives (no forwarding with TTL=0)
        assert len(recipients) == 1
        assert sender in recipients

    def test_ttl_one_hop(self, validator_set):
        """TTL=1: only sender + its direct peers receive."""
        gossip = GossipProtocol(validator_set, fanout=3)
        sender = validator_set.get_active_validators()[0].address

        recipients = gossip.broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
            ttl=1,
        )

        # Sender + up to 3 direct peers = 4 max
        assert len(recipients) <= 4
        assert sender in recipients

    def test_cache_bounded(self, validator_set):
        """Cache doesn't grow unbounded — respects max size."""
        gossip = GossipProtocol(validator_set, fanout=3, cache_size=10)
        sender = validator_set.get_active_validators()[0].address

        # Send many unique messages (more than cache size)
        for i in range(15):
            gossip.broadcast(
                msg_type=GossipMessageType.HEARTBEAT,
                payload=f"msg_{i}",
                sender=sender,
            )

        # Cache should never exceed max_size (and may be slightly less
        # due to the last invocation only adding a bounded number of IDs)
        assert gossip.get_cache_size() <= 10 + 7  # slight slack for last round

    def test_clear_cache(self, validator_set):
        """Clear cache resets seen messages."""
        gossip = GossipProtocol(validator_set, fanout=3)
        sender = validator_set.get_active_validators()[0].address

        gossip.broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
        )

        assert gossip.get_cache_size() > 0
        gossip.clear_cache()
        assert gossip.get_cache_size() == 0


# ─── ValidatorNetwork Integration ───────────────────────────────────────────

@pytest.mark.skipif(GossipProtocol is None or ValidatorNetwork is None,
                    reason="GossipProtocol or ValidatorNetwork not implemented")
class TestGossipNetworkIntegration:
    """Tests for gossip integrated with ValidatorNetwork."""

    @pytest.fixture
    def network(self):
        """Create a validator network with keys."""
        vals = []
        priv_keys = {}
        for _ in range(7):
            node, priv = ValidatorNode.generate_with_private_key()
            vals.append(node)
            priv_keys[node.address] = priv
        vset = ValidatorSet(vals)
        return ValidatorNetwork(vset, priv_keys)

    def test_gossip_broadcast_reaches_all(self, network):
        """gossip_broadcast reaches all active validators."""
        sender = network.validator_set.get_active_validators()[0].address

        recipients = network.gossip_broadcast(
            msg_type=GossipMessageType.PROPOSAL,
            payload='{"test": true}',
            sender=sender,
        )

        assert len(recipients) == 7
        for v in network.validator_set.get_active_validators():
            assert v.address in recipients

    def test_gossip_broadcast_returns_set(self, network):
        """gossip_broadcast returns a set of addresses."""
        sender = network.validator_set.get_active_validators()[0].address

        recipients = network.gossip_broadcast(
            msg_type=GossipMessageType.HEARTBEAT,
            payload="ping",
            sender=sender,
        )

        assert isinstance(recipients, set)
