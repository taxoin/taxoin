"""Tests for Proof-of-Work mining."""
from src.miner import mine_block, validate_pow, calculate_difficulty
from src.core import BlockHeader


class TestMiner:
    def test_mine_difficulty_0(self):
        header = BlockHeader(
            parent_hash="0" * 64, merkle_root="test",
            timestamp=100, difficulty=0,
        )
        result = mine_block(header)
        assert validate_pow(result)

    def test_mine_difficulty_1(self):
        header = BlockHeader(
            parent_hash="0" * 64, merkle_root="pow_test_1",
            timestamp=200, difficulty=1,
        )
        result = mine_block(header)
        assert validate_pow(result)
        assert result.nonce >= 0
        assert result.hash().startswith("0")

    def test_mine_difficulty_2(self):
        header = BlockHeader(
            parent_hash="0" * 64, merkle_root="pow_test_2_unique",
            timestamp=300, difficulty=2,
        )
        result = mine_block(header)
        assert validate_pow(result)
        assert result.nonce >= 0
        assert result.hash().startswith("00")

    def test_validate_pow_valid(self):
        header = BlockHeader(
            parent_hash="0" * 64, merkle_root="test",
            timestamp=0, difficulty=0, nonce=0,
        )
        assert validate_pow(header)

    def test_validate_pow_invalid(self):
        header = BlockHeader(
            parent_hash="0" * 64, merkle_root="test_invalid",
            timestamp=0, difficulty=100, nonce=0,
        )
        # Very high difficulty with nonce=0 should not work
        assert not validate_pow(header)


class TestDifficultyAdjustment:
    def test_difficulty_stays_same(self):
        d = calculate_difficulty(4, [0, 60], target_interval=60)
        assert d == 4  # exactly on target

    def test_difficulty_increases_when_fast(self):
        d = calculate_difficulty(4, [0, 10], target_interval=60)
        assert d == 5  # too fast -> harder

    def test_difficulty_decreases_when_slow(self):
        d = calculate_difficulty(4, [0, 200], target_interval=60)
        assert d == 3  # too slow -> easier

    def test_not_enough_data(self):
        d = calculate_difficulty(4, [0], target_interval=60)
        assert d == 4  # no change with 1 data point
