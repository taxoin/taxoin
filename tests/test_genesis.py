"""Tests for Genesis module (Proof of Personhood)."""
import time
import pytest

try:
    from src.genesis import GenesisRegistry, GenesisAttestation, GENESIS_REWARD, MAX_GENESIS_SUPPLY
except ImportError:
    GenesisRegistry = None
    GenesisAttestation = None
    GENESIS_REWARD = None
    MAX_GENESIS_SUPPLY = None


@pytest.mark.skipif(GenesisRegistry is None, reason="GenesisRegistry not implemented")
class TestGenesisConstants:
    """Test genesis parameters."""

    def test_genesis_reward(self):
        assert GENESIS_REWARD == 50.0

    def test_max_supply(self):
        assert MAX_GENESIS_SUPPLY == 21_000_000.0

    def test_max_participants(self):
        assert MAX_GENESIS_SUPPLY / GENESIS_REWARD == 420_000


@pytest.mark.skipif(GenesisRegistry is None, reason="GenesisRegistry not implemented")
class TestGenesisRegistry:
    """Test genesis registry operations."""

    def test_create_registry(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        assert len(reg.validators) == 3
        assert reg.get_total_genesis_supply() == 0.0

    def test_add_attestation(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        addr = "0xnewbie"
        reg.add_attestation(addr, "0xval1")
        assert not reg.is_attestation_complete(addr)
        assert reg.get_attestation_count(addr) == 1

    def test_three_attestations_complete(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        addr = "0xnewbie"
        reg.add_attestation(addr, "0xval1")
        reg.add_attestation(addr, "0xval2")
        reg.add_attestation(addr, "0xval3")
        assert reg.is_attestation_complete(addr)
        assert reg.get_attestation_count(addr) == 3

    def test_genesis_credited_after_complete(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        addr = "0xnewbie"
        reg.add_attestation(addr, "0xval1")
        reg.add_attestation(addr, "0xval2")
        reg.add_attestation(addr, "0xval3")
        assert reg.is_genesis_done(addr) is True
        assert reg.get_total_genesis_supply() == GENESIS_REWARD

    def test_double_genesis_rejected(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        addr = "0xnewbie"
        reg.add_attestation(addr, "0xval1")
        reg.add_attestation(addr, "0xval2")
        reg.add_attestation(addr, "0xval3")
        assert reg.is_genesis_done(addr) is True
        # Second genesis for same address should not increase supply
        prev = reg.get_total_genesis_supply()
        reg.add_attestation(addr, "0xval1")
        assert reg.get_total_genesis_supply() == prev

    def test_duplicate_validator_attestation(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        addr = "0xnewbie"
        reg.add_attestation(addr, "0xval1")
        reg.add_attestation(addr, "0xval1")  # same validator twice
        assert reg.get_attestation_count(addr) == 1  # not counted twice

    def test_supply_cap(self):
        validators = ["0xval1", "0xval2", "0xval3"]
        reg = GenesisRegistry(validators)
        # Simulate distributing to many addresses
        for i in range(500_000):
            addr = f"0x{i:08x}"
            for v in validators:
                reg.add_attestation(addr, v)
            if reg.get_total_genesis_supply() >= MAX_GENESIS_SUPPLY:
                break
        # Supply should never exceed the cap
        assert reg.get_total_genesis_supply() <= MAX_GENESIS_SUPPLY
