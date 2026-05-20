"""Tests for cryptographic utilities."""
import pytest
from src.crypto_utils import (
    generate_keypair, private_to_bytes, public_to_bytes,
    public_key_to_address, private_key_to_address,
    sign, verify,
)
from cryptography.hazmat.primitives.asymmetric import ec


class TestKeyGeneration:
    def test_generate_keypair(self):
        priv, pub = generate_keypair()
        assert isinstance(priv, ec.EllipticCurvePrivateKey)
        assert isinstance(pub, ec.EllipticCurvePublicKey)

    def test_public_key_to_address_format(self):
        _, pub = generate_keypair()
        addr = public_key_to_address(pub)
        assert addr.startswith("0x")
        assert len(addr) == 42  # 0x + 40 hex chars

    def test_private_key_to_address(self):
        priv, pub = generate_keypair()
        addr1 = private_key_to_address(priv)
        addr2 = public_key_to_address(pub)
        assert addr1 == addr2


class TestSigning:
    def test_sign_and_verify(self):
        priv, pub = generate_keypair()
        data = "hello blockchain"
        sig = sign(priv, data)
        assert verify(pub, data, sig) is True

    def test_verify_wrong_data(self):
        priv, pub = generate_keypair()
        sig = sign(priv, "correct data")
        assert verify(pub, "wrong data", sig) is False

    def test_verify_wrong_key(self):
        priv, _ = generate_keypair()
        _, wrong_pub = generate_keypair()
        sig = sign(priv, "test")
        assert verify(wrong_pub, "test", sig) is False

    def test_signatures_differ(self):
        priv, _ = generate_keypair()
        sig1 = sign(priv, "message")
        sig2 = sign(priv, "message")
        # ECDSA signatures have randomness, so they should differ
        # (unless the RNG produces the same k, which is extremely unlikely)
        assert sig1 != sig2
