"""
GossipProtocol: Epidemic message propagation for validator network.

Part of TODO-0002 Phase 5: Gossip Protocol
"""
from __future__ import annotations

import hashlib
import random
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GossipMessageType(Enum):
    PROPOSAL = "proposal"
    PREVOTE = "prevote"
    PRECOMMIT = "precommit"
    MERGE_CONFIRM = "merge_confirm"
    HEARTBEAT = "heartbeat"


@dataclass
class GossipMessage:
    """A message propagated through the gossip network."""

    message_id: str
    msg_type: GossipMessageType
    sender: str
    payload: str
    ttl: int = 5
    sequence: int = 0
    timestamp: float = 0.0


class GossipProtocol:
    """Epidemic gossip protocol for message dissemination.

    Simulates epidemic (gossip) propagation through a set of validators:
    - Each node forwards each unique message to F random peers (fanout)
    - Deduplication via bounded message cache
    - TTL limits propagation distance (number of hops)
    - Converges to all nodes receiving the message in O(log N) rounds
    """

    def __init__(
        self,
        validator_set: "ValidatorSet",  # noqa: F821
        fanout: int = 3,
        cache_size: int = 1000,
    ):
        self.validator_set = validator_set
        self.fanout = fanout
        self._cache: set[str] = set()
        self._cache_max_size = cache_size
        self._sequence_counters: dict[str, int] = {}

    def _get_next_sequence(self, sender: str) -> int:
        """Get next sequence number for a sender."""
        seq = self._sequence_counters.get(sender, 0)
        self._sequence_counters[sender] = seq + 1
        return seq

    @staticmethod
    def _generate_id(msg_type: GossipMessageType, sender: str, sequence: int) -> str:
        """Generate a deterministic unique message ID."""
        raw = f"{msg_type.value}:{sender}:{sequence}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _add_to_cache(self, message_id: str) -> None:
        """Add message ID to cache, evicting oldest if at capacity."""
        if len(self._cache) >= self._cache_max_size:
            # Evict a random entry (simulated bounded cache)
            self._cache.pop()
        self._cache.add(message_id)

    def get_cache_size(self) -> int:
        """Get current number of cached message IDs."""
        return len(self._cache)

    def clear_cache(self) -> None:
        """Reset the message cache."""
        self._cache.clear()

    def broadcast(
        self,
        msg_type: GossipMessageType,
        payload: str,
        sender: str,
        ttl: int = 5,
    ) -> set[str]:
        """Broadcast a message through the gossip network.

        Simulates epidemic propagation:
        - Starts from the sender
        - Each hop: each recipient forwards to F random peers
        - Deduplication: already-seen messages not forwarded
        - Stops when TTL expires or no new nodes reached

        Args:
            msg_type: Type of message
            payload: Message content string
            sender: Address of the sending validator
            ttl: Initial time-to-live (max hops)

        Returns:
            Set of all validator addresses that received the message
        """
        sequence = self._get_next_sequence(sender)
        message_id = self._generate_id(msg_type, sender, sequence)

        # Quick dedup check
        if message_id in self._cache:
            return set()

        self._add_to_cache(message_id)

        active = self.validator_set.get_active_validators()
        all_addresses = {v.address for v in active}
        received: set[str] = {sender}

        # BFS-style epidemic propagation
        frontier: set[str] = {sender}
        current_ttl = ttl

        while frontier and current_ttl > 0:
            next_frontier: set[str] = set()

            for node_addr in frontier:
                # Pick up to fanout random peers that haven't received yet
                candidates = list(all_addresses - received - {node_addr})

                if not candidates:
                    continue

                # Shuffle to get random selection
                random.shuffle(candidates)
                peers = candidates[:min(self.fanout, len(candidates))]

                for peer in peers:
                    if peer not in received:
                        received.add(peer)
                        next_frontier.add(peer)

            frontier = next_frontier
            current_ttl -= 1

            # If all validators received, we're done
            if received == all_addresses:
                break

        return received
