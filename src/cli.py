"""CLI for Taxoin — Blockchain on Git.

Usage:
  taxoin init                 Initialize the chain
  taxoin status               Show chain status
  taxoin balance <address>    Show balance for an address
  taxoin accounts             List all accounts
  taxoin send <from> <to> <value>  Submit an async transaction
  taxoin mine <address>       Mine a new block (coinbase to address)
  taxoin chain                Show the full chain
  taxoin verify               Verify chain integrity
  taxoin wallet new           Generate a new wallet keypair
  taxoin wallet address       Show wallet address
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import click

from .blockchain import BlockchainEngine
from .branch_manager import BranchManager
from .core import AsyncTransaction, Account
from .crypto_utils import (
    generate_keypair, private_key_to_address, public_key_to_address,
    private_to_bytes, public_to_bytes,
)

WALLET_DIR = ".taxoin"
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
    """Taxoin — Blockchain on Git."""
    pass


@cli.command()
def init():
    """Initialize a new blockchain."""
    engine = _get_engine()
    height = engine.git.get_chain_height()
    click.echo(f"✓ Chain initialized at .taxoin/")
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
        click.echo("No wallet found. Create one with: taxoin wallet new")


# ── Branch Commands ──────────────────────────────────────────────────────

@cli.group()
def branch():
    """Branch management (parallel transaction branches)."""
    pass


@branch.command()
@click.argument("wallet")
def create(wallet: str):
    """Create a new transaction branch for a wallet."""
    manager = BranchManager(".")
    branch_name = manager.create_branch(wallet)
    click.echo(f"✓ Branch created: {branch_name}")


@branch.command(name="list")
def list_branches():
    """List all branches."""
    manager = BranchManager(".")
    branches = manager.list_branches()
    if not branches:
        click.echo("No branches found.")
        return

    click.echo("Branches:")
    for b in sorted(branches):
        click.echo(f"  • {b}")


@branch.command()
@click.argument("branch_name")
def merge(branch_name: str):
    """Merge a branch via validator consensus."""
    manager = BranchManager(".")
    manager.init_validator_network(count=7)

    click.echo(f"Running consensus for {branch_name}...")
    result = manager.run_consensus(branch_name)

    if result.success:
        click.echo(f"✓ Merged: {result.merge_commit[:16]}...")
    else:
        click.echo(f"✗ Failed: {result.message}")
        if result.conflicts:
            click.echo(f"  Conflicts: {len(result.conflicts)}")
            for c in result.conflicts:
                click.echo(f"    - {c.detail}")


@branch.command()
@click.argument("branch_name")
def status(branch_name: str):
    """Show branch status and state info."""
    manager = BranchManager(".")
    state = manager.get_branch_state(branch_name)

    if not state:
        click.echo(f"Branch '{branch_name}' does not exist.")
        return

    click.echo(f"Branch:       {state.branch_name}")
    click.echo(f"Parent hash:  {state.parent_hash[:20]}...")
    click.echo(f"Accounts:     {len(state.accounts)}")
    click.echo(f"UTXOs:        {len(state.utxo_set)}")
    click.echo(f"Transactions: {state.transaction_count}")
    click.echo(f"Spent UTXOs:  {len(state.spent_utxos)}")
    click.echo(f"Nonce tracks: {len(state.used_nonces)}")
    click.echo(f"Created:      {state.created_at}")


# ── Validator Commands ───────────────────────────────────────────────────

@cli.group()
def validator():
    """Validator network management."""
    pass


@validator.command()
@click.option("--count", default=7, help="Number of validators (default: 7)")
def init(count: int):
    """Initialize the validator network."""
    manager = BranchManager(".")
    manager.init_validator_network(count=count)
    validators = manager.get_validators()
    click.echo(f"✓ Validator network initialized with {len(validators)} validators")
    for v in validators:
        click.echo(f"  {v.address} (power={v.voting_power})")


@validator.command(name="list")
def list_validators():
    """List all validators."""
    manager = BranchManager(".")
    validators = manager.get_validators()

    if not validators:
        click.echo("No validators. Run: taxoin validator init")
        return

    click.echo(f"{'Address':<44} {'Power':<8} {'Status':<12}")
    click.echo("─" * 66)
    for v in validators:
        click.echo(f"{v.address:<44} {v.voting_power:<8} {v.status.value:<12}")


if __name__ == "__main__":
    cli()
