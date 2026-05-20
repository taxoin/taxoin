"""
Cryptographic utilities: key generation, signing, verification.
Uses ECDSA secp256k1 via the `cryptography` library.
"""
from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


# secp256k1 is the curve Bitcoin / Ethereum use
CURVE = ec.SECP256K1


def generate_keypair() -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    """Generate a new secp256k1 keypair."""
    private_key = ec.generate_private_key(CURVE)
    public_key = private_key.public_key()
    return private_key, public_key


def private_to_bytes(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_to_bytes(key: ec.EllipticCurvePublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def public_key_to_address(pub_key: ec.EllipticCurvePublicKey) -> str:
    """Derive a human-readable address from a public key.

    Similar to Ethereum: keccak256(public_key)[-20:] but using SHA256
    for simplicity, returning a hex string prefixed with '0x'.
    """
    raw = pub_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    h = hashlib.sha256(raw).hexdigest()[-40:]  # last 40 hex chars = 20 bytes
    return f"0x{h}"


def private_key_to_address(priv_key: ec.EllipticCurvePrivateKey) -> str:
    return public_key_to_address(priv_key.public_key())


def sign(private_key: ec.EllipticCurvePrivateKey, data: str) -> str:
    """Sign a string with the private key, return hex signature."""
    signature = private_key.sign(
        data.encode("utf-8"),
        ec.ECDSA(hashes.SHA256()),
    )
    return signature.hex()


def verify(public_key: ec.EllipticCurvePublicKey, data: str, signature_hex: str) -> bool:
    """Verify a signature against a public key."""
    try:
        public_key.verify(
            bytes.fromhex(signature_hex),
            data.encode("utf-8"),
            ec.ECDSA(hashes.SHA256()),
        )
        return True
    except InvalidSignature:
        return False


def private_key_from_pem(pem_data: str) -> ec.EllipticCurvePrivateKey:
    """Load a private key from PEM string."""
    return serialization.load_pem_private_key(
        pem_data.encode("utf-8"),
        password=None,
    )


def public_key_from_pem(pem_data: str) -> ec.EllipticCurvePublicKey:
    """Load a public key from PEM string."""
    return serialization.load_pem_public_key(
        pem_data.encode("utf-8"),
    )
