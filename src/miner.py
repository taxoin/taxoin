"""
Proof-of-Work Miner.

Bitcoin-style mining: find a nonce such that
  SHA256(SHA256(block_header)) starts with N leading hex zeros.

The difficulty is the number of leading zeros required.
"""
from __future__ import annotations

import time
from typing import Optional

from .core import Block, BlockHeader, Transaction, sha256


def mine_block(header: BlockHeader, max_nonce: int = 2_000_000) -> BlockHeader:
    """Mine a block header by finding a valid nonce.

    Mutates header.nonce in place and returns it.
    """
    # If already meets difficulty, we're done (nonce=0)
    if header.meets_difficulty():
        return header

    for nonce in range(1, max_nonce + 1):
        header.nonce = nonce
        if header.meets_difficulty():
            return header

    raise RuntimeError(
        f"Failed to mine block: no valid nonce found in {max_nonce} attempts "
        f"(difficulty={header.difficulty})"
    )


def validate_pow(header: BlockHeader) -> bool:
    """Check that a block header meets its claimed difficulty."""
    return header.meets_difficulty()


def calculate_difficulty(
    current_difficulty: int,
    block_times: list[float],
    target_interval: float = 60.0,
) -> int:
    """Adjust difficulty based on recent block times (simplified).

    If blocks are coming faster than `target_interval`, increase difficulty.
    If slower, decrease difficulty. Never go below 1.
    """
    if len(block_times) < 2:
        return current_difficulty

    actual = block_times[-1] - block_times[0]
    n_intervals = len(block_times) - 1
    actual_avg = actual / n_intervals if n_intervals > 0 else target_interval

    ratio = target_interval / actual_avg if actual_avg > 0 else 1.0

    if ratio < 0.5:
        return max(1, current_difficulty - 1)
    elif ratio > 1.5:
        return current_difficulty + 1
    else:
        return current_difficulty
