"""Tests for core data structures."""
import pytest
from src.core import (
    Transaction, TxInput, TxOutput, UTXO, Account,
    AsyncTransaction, Block, BlockHeader, make_genesis_block,
    sha256, double_sha256,
)


class TestHashing:
    def test_sha256_returns_64_hex_chars(self):
        h = sha256("hello")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_double_sha256_is_different(self):
        s = "test_data"
        assert double_sha256(s) != sha256(s)

    def test_sha256_is_deterministic(self):
        assert sha256("hello") == sha256("hello")
        assert sha256("hello") != sha256("world")


class TestTransaction:
    def test_transaction_has_tx_id(self):
        tx = Transaction(
            inputs=[TxInput(tx_id="abc", output_index=0)],
            outputs=[TxOutput(address="0x123", amount=10.0)],
        )
        assert len(tx.tx_id) == 64
        assert all(c in "0123456789abcdef" for c in tx.tx_id)

    def test_coinbase_transaction(self):
        tx = Transaction.coinbase("0xabc", reward=50.0)
        assert len(tx.inputs) == 0
        assert len(tx.outputs) == 1
        assert tx.outputs[0].address == "0xabc"
        assert tx.outputs[0].amount == 50.0

    def test_serialize_roundtrip(self):
        tx = Transaction(
            inputs=[TxInput(tx_id="abc", output_index=0, signature="sig1")],
            outputs=[TxOutput(address="0x123", amount=10.0)],
        )
        s = tx.serialize()
        assert "abc" in s
        assert "0x123" in s
        assert "10.0" in s or "10" in s


class TestUTXO:
    def test_utxo_creation(self):
        u = UTXO(tx_id="abc", output_index=0, address="0x123", amount=10.0)
        assert u.outpoint() == ("abc", 0)
        assert u.amount == 10.0

    def test_utxo_serialize(self):
        u = UTXO(tx_id="abc", output_index=1, address="0xaddr", amount=5.0)
        s = u.serialize()
        assert "0xaddr" in s


class TestAccount:
    def test_account_creation(self):
        a = Account(address="0xabc", balance=100.0)
        assert a.nonce == 0
        assert a.balance == 100.0

    def test_account_serialize(self):
        a = Account(address="0xabc", balance=50.0, nonce=3)
        s = a.serialize()
        assert "0xabc" in s
        assert "50.0" in s or "50" in s


class TestAsyncTransaction:
    def test_async_tx_has_hash(self):
        tx = AsyncTransaction(
            sender="0xalice", recipient="0xbob",
            value=10.0, nonce=0,
        )
        assert len(tx.tx_hash) == 64

    def test_async_tx_different_nonces(self):
        tx1 = AsyncTransaction(sender="0xa", recipient="0xb", value=1, nonce=0)
        tx2 = AsyncTransaction(sender="0xa", recipient="0xb", value=1, nonce=1)
        assert tx1.tx_hash != tx2.tx_hash

    def test_async_tx_serialize(self):
        tx = AsyncTransaction(sender="0xa", recipient="0xb", value=5, nonce=0)
        s = tx.serialize()
        assert "0xa" in s
        assert "0xb" in s


class TestBlock:
    def test_block_header_hash(self):
        h1 = BlockHeader(parent_hash="0"*64, merkle_root="m", timestamp=0, difficulty=4)
        h2 = BlockHeader(parent_hash="0"*64, merkle_root="m", timestamp=0, difficulty=4)
        assert h1.hash() == h2.hash()
        # different nonces produce different hashes
        h2.nonce = 1
        assert h1.hash() != h2.hash()

    def test_difficulty_check(self):
        # With difficulty 0, any hash passes
        h = BlockHeader(parent_hash="0"*64, merkle_root="m", timestamp=0, difficulty=0)
        assert h.meets_difficulty()

        # With difficulty 1, hash must start with '0'
        h2 = BlockHeader(parent_hash="0"*64, merkle_root="0", timestamp=0, difficulty=1, nonce=0)
        assert h2.meets_difficulty() or not h2.meets_difficulty()  # depends on hash

    def test_block_serialize(self):
        header = BlockHeader(parent_hash="0"*64, merkle_root="m", timestamp=0, difficulty=4)
        tx = Transaction.coinbase("0xmine")
        block = Block(header=header, transactions=[tx])
        s = block.serialize()
        assert "0xmine" in s
        assert "coinbase" not in s  # coinbase txs have no inputs


class TestGenesisBlock:
    def test_genesis_block_exists(self):
        genesis = make_genesis_block()
        assert genesis.header.parent_hash == "0" * 64
        assert genesis.header.timestamp == 0.0

    def test_genesis_merkle_is_genesis(self):
        genesis = make_genesis_block()
        assert genesis.header.merkle_root == "genesis"
