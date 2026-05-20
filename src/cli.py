"""
CLI for Gitchain — Blockchain on Git.

Usage:
  gitchain init                 Initialize the chain
  gitchain status               Show chain status
  gitchain balance <address>    Show balance for an address
  gitchain accounts             List all accounts
  gitchain send <from> <to> <value>  Submit an async transaction
  gitchain mine <address>       Mine a new block (coinbase to address)
  gitchain chain                Show the full chain
  gitchain verify               Verify chain integrity
  gitchain wallet new           Generate a new wallet keypair
  gitchain wallet address       Show wallet address
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import click

from .blockchain import BlockchainEngine
from .core import AsyncTransaction, Account
from .crypto_utils import (
    generate_keypair, private_key_to_address, public_key_to_address,
    private_to_bytes, public_to_bytes,
)

WALLET_DIR = ".gitchain"
WALLET_FILE = "wallet.json"


def _get_engine() -> BlockchainEngine:
    engine = BlockchainEngine(".")
    engine.load_state()
    return engine


def _load_wallet() -> dict | None:
    path = Path(WALLET_DIR) / WALLET_FILE
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def _save_wallet(wallet: dict) -> None:
    path = Path(WALLET_DIR) / WALLET_FILE
    path.parent.mkdir(exist_ok=True)
    with open(path, "w") as f:
        json.dump(wallet, f, indent=2)


# ── Commands ───────────────────────────────────────────────────────────

@click.group()
def cli():
    """Gitchain — Blockchain on Git."""
    pass


@cli.command()
def init():
    """Initialize a new blockchain."""
    engine = _get_engine()
    height = engine.git.get_chain_height()
    click.echo(f"✓ Chain initialized at .gitchain/")
    click.echo(f"  Genesis block at height {height}")
    click.echo(f"  Difficulty: {engine.difficulty}")


@cli.command()
def status():
    """Show chain status."""
    engine = _get_engine()
    status = engine.get_status()

    click.echo("─" * 40)
    click.echo(f"Chain height:    {status['chain_height']}")
    click.echo(f"Latest hash:     {status['latest_hash'][:16]}...")
    click.echo(f"Difficulty:      {status['difficulty']}")
    click.echo(f"Mempool size:    {status['mempool_size']}")
    click.echo(f"UTXO count:      {status['utxo_count']}")
    click.echo(f"Account count:   {status['account_count']}")
    click.echo("─" * 40)


@cli.command()
@click.argument("address")
def balance(address: str):
    """Show balance for an address."""
    engine = _get_engine()
    bal = engine.get_balance(address)
    nonce = engine.get_nonce(address)
    click.echo(f"Address: {address}")
    click.echo(f"Balance: {bal}")
    click.echo(f"Nonce:   {nonce}")


@cli.command()
def accounts():
    """List all accounts."""
    engine = _get_engine()
    accounts = engine.get_accounts()
    if not accounts:
        click.echo("No accounts found.")
        return

    click.echo(f"{'Address':<44} {'Balance':<12} {'Nonce':<6}")
    click.echo("─" * 64)
    for addr, acct in sorted(accounts.items()):
        click.echo(f"{addr:<44} {acct.balance:<12.2f} {acct.nonce:<6}")


@cli.command()
@click.argument("sender")
@click.argument("recipient")
@click.argument("value", type=float)
@click.option("--gas-price", default=1.0, help="Gas price")
@click.option("--nonce", default=None, type=int, help="Transaction nonce (auto if not set)")
def send(sender, recipient, value, gas_price, nonce):
    """Submit an async transaction."""
    async def _send(_nonce=nonce):
        engine = _get_engine()
        if _nonce is None:
            _nonce = engine.get_nonce(sender)

        tx = AsyncTransaction(
            sender=sender,
            recipient=recipient,
            value=value,
            nonce=_nonce,
            gas_price=gas_price,
        )
        ok, msg = await engine.submit_async_transaction(tx)
        if ok:
            click.echo(f"✓ Tx submitted: {tx.tx_hash}")
        else:
            click.echo(f"✗ Failed: {msg}")
        return ok

    asyncio.run(_send())


@cli.command()
@click.argument("address")
def mine(address: str):
    """Mine a new block. Coinbase reward goes to ADDRESS."""
    engine = _get_engine()
    engine.create_account(address)

    click.echo(f"Mining block... (difficulty={engine.difficulty})")
    block = engine.mine_block(address)

    if block:
        click.echo(f"✓ Block mined!")
        click.echo(f"  Hash:       {block.hash}")
        click.echo(f"  Nonce:      {block.header.nonce}")
        click.echo(f"  Txs:        {len(block.transactions)}")
        click.echo(f"  Difficulty: {block.header.difficulty}")
        click.echo(f"  Height:     {engine.git.get_chain_height()}")
    else:
        click.echo("✗ Mining failed (no valid nonce found)")


@cli.command()
def chain():
    """Show the full blockchain."""
    engine = _get_engine()
    chain = engine.get_chain()

    if not chain:
        click.echo("Chain is empty.")
        return

    click.echo(f"{'Height':<8} {'Commit':<12} {'Block Hash':<20} {'Nonce':<8} {'Txs':<6}")
    click.echo("─" * 60)

    for i, entry in enumerate(chain):
        click.echo(
            f"{i:<8} "
            f"{entry['commit'][:10]:<12} "
            f"{entry['hash'][:16]:<20} "
            f"{str(entry['nonce']):<8} "
            f"{entry['tx_count']:<6}"
        )


@cli.command()
def verify():
    """Verify blockchain integrity."""
    engine = _get_engine()
    valid = engine.verify()
    if valid:
        click.echo("✓ Chain integrity verified.")
    else:
        click.echo("✗ Chain integrity BROKEN!")


@cli.group()
def wallet():
    """Wallet management."""
    pass


@wallet.command()
def new():
    """Generate a new wallet keypair."""
    priv, pub = generate_keypair()
    address = public_key_to_address(pub)
    wallet_data = {
        "address": address,
        "private_key": private_to_bytes(priv).decode(),
        "public_key": public_to_bytes(pub).decode(),
    }
    _save_wallet(wallet_data)
    click.echo(f"✓ New wallet created!")
    click.echo(f"  Address: {address}")
    click.echo(f"  Keys saved to: {WALLET_DIR}/{WALLET_FILE}")


@wallet.command()
def address():
    """Show the wallet address."""
    wallet_data = _load_wallet()
    if wallet_data:
        click.echo(f"Address: {wallet_data['address']}")
    else:
        click.echo("No wallet found. Create one with: gitchain wallet new")


if __name__ == "__main__":
    cli()
