"""Tests for real ECDSA signatures in attested transactions."""
import pytest

from src.core import Account
from src.crypto_utils import generate_keypair, public_key_to_address, sign, verify, private_key_from_pem, public_key_from_pem, private_to_bytes, public_to_bytes

try:
    from src.attested_tx import AttestedTransaction
except ImportError:
    AttestedTransaction = None


@pytest.mark.skipif(AttestedTransaction is None, reason="AttestedTransaction not implemented")
class TestRealSignatures:
    """AttestedTransaction with real ECDSA signatures."""

    def test_consumer_signs_tx(self):
        """Consumer signs the attested transaction with their key."""
        priv, pub = generate_keypair()
        address = public_key_to_address(pub)
        priv_pem = private_to_bytes(priv).decode()
        pub_pem = public_to_bytes(pub).decode()

        tx = AttestedTransaction(
            consumer=address,
            provider="0xbob",
            service_ref="sms:0xbob",
            amount=1.0,
            consumer_sig="",
            provider_sig="",
        )
        data = f"{tx.consumer}:{tx.provider}:{tx.amount}:{tx.service_ref}"
        tx.consumer_sig = sign(priv, data)

        assert len(tx.consumer_sig) > 0
        assert verify(pub, data, tx.consumer_sig) is True

    def test_provider_signs_tx(self):
        """Provider signs the attested transaction with their key."""
        c_priv, c_pub = generate_keypair()
        p_priv, p_pub = generate_keypair()
        consumer = public_key_to_address(c_pub)
        provider = public_key_to_address(p_pub)

        tx = AttestedTransaction(
            consumer=consumer,
            provider=provider,
            service_ref="sms:provider",
            amount=1.0,
            consumer_sig="",
            provider_sig="",
        )

        # Consumer signs
        data = f"{tx.consumer}:{tx.provider}:{tx.amount}:{tx.service_ref}"
        tx.consumer_sig = sign(c_priv, data)

        # Provider signs
        data2 = f"attest:{tx.tx_id}:{tx.provider}"
        tx.provider_sig = sign(p_priv, data2)

        assert tx.is_valid() is True
        assert verify(c_pub, data, tx.consumer_sig) is True
        assert verify(p_pub, data2, tx.provider_sig) is True

    def test_wrong_key_rejected(self):
        """Verification with wrong key fails."""
        c_priv, c_pub = generate_keypair()
        w_priv, w_pub = generate_keypair()  # wrong key
        address = public_key_to_address(c_pub)

        tx = AttestedTransaction(
            consumer=address,
            provider="0xbob",
            service_ref="sms:bob",
            amount=1.0,
            consumer_sig="",
            provider_sig="",
        )
        data = f"{tx.consumer}:{tx.provider}:{tx.amount}:{tx.service_ref}"
        tx.consumer_sig = sign(c_priv, data)

        # Wrong key can't verify
        assert verify(w_pub, data, tx.consumer_sig) is False

    def test_tampered_data_rejected(self):
        """Signature verification on tampered data fails."""
        priv, pub = generate_keypair()
        address = public_key_to_address(pub)

        tx = AttestedTransaction(
            consumer=address,
            provider="0xbob",
            service_ref="sms:bob",
            amount=1.0,
            consumer_sig="",
            provider_sig="",
        )
        data = f"{tx.consumer}:{tx.provider}:{tx.amount}:{tx.service_ref}"
        tx.consumer_sig = sign(priv, data)

        # Tampered data
        tampered = f"0xhacker:0xbob:99.0:sms"
        assert verify(pub, tampered, tx.consumer_sig) is False
