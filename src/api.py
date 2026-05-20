"""Taxoin REST API — FastAPI server for external integrations.

Usage:
    python3 -m src.api --port 47780
    # or via Docker: docker compose up
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .attested_tx import AttestedTransaction, BalanceHold
from .branch_manager import BranchManager
from .core import Account
from .crypto_utils import generate_keypair, public_key_to_address, private_to_bytes, public_to_bytes
from .genesis import GenesisRegistry
from .reputation import ReputationTracker
from .service_registry import ServiceRegistration, ServiceRegistry

app = FastAPI(title="Taxoin API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/web", StaticFiles(directory="web", html=True), name="web")

# ── Internal state (singletons, persisted) ──────────────────────────────

_taxoin_dir = os.environ.get("TAXOIN_DIR", ".taxoin")
_manager: BranchManager | None = None
_service_reg: ServiceRegistry | None = None
_reputation: ReputationTracker | None = None
_balances: dict[str, float] = {}


def _get_manager() -> BranchManager:
    global _manager
    if _manager is None:
        _manager = BranchManager(_taxoin_dir)
    return _manager


def _get_service_registry() -> ServiceRegistry:
    global _service_reg
    if _service_reg is None:
        path = os.path.join(_taxoin_dir, "services.json")
        _service_reg = ServiceRegistry(store_path=path)
    return _service_reg


def _get_reputation() -> ReputationTracker:
    global _reputation
    if _reputation is None:
        path = os.path.join(_taxoin_dir, "reputation.json")
        _reputation = ReputationTracker(store_path=path)
    return _reputation


def _get_balance(address: str) -> float:
    return _balances.get(address, 0.0)


# ── Request/Response models ─────────────────────────────────────────────

class WalletResponse(BaseModel):
    address: str
    private_key: str
    public_key: str

class BalanceResponse(BaseModel):
    address: str
    balance: float

class TxSendRequest(BaseModel):
    consumer: str
    provider: str
    amount: float
    service_ref: str = ""
    consumer_sig: str = ""
    provider_sig: str = ""
    description: str = ""

class TxResponse(BaseModel):
    tx_id: str
    status: str
    amount: float
    consumer: str
    provider: str

class ServiceRegisterRequest(BaseModel):
    provider: str
    service_type: str
    price_per_unit: float
    description: str
    endpoint: str = ""

class ServiceResponse(BaseModel):
    provider: str
    service_type: str
    price_per_unit: float
    description: str
    rating: float
    total_tx: int

class StatusResponse(BaseModel):
    network: str = "taxoin"
    status: str = "running"
    validators: int = 0
    blocks: int = 0
    services: int = 0
    total_supply: float = 0.0


# ── Endpoints ───────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status", response_model=StatusResponse)
def get_status():
    manager = _get_manager()
    branches = manager.list_branches()
    services = _get_service_registry().list_services()
    return StatusResponse(
        validators=len(branches),
        blocks=manager.git.get_chain_height(),
        services=len(services),
        total_supply=_get_balance("genesis"),
    )

@app.post("/api/wallet", response_model=WalletResponse)
def create_wallet():
    priv, pub = generate_keypair()
    address = public_key_to_address(pub)
    return WalletResponse(
        address=address,
        private_key=private_to_bytes(priv).decode(),
        public_key=public_to_bytes(pub).decode(),
    )

@app.get("/api/balance/{address}", response_model=BalanceResponse)
def get_balance(address: str):
    manager = _get_manager()
    main = manager.get_main_state()
    acct = main.accounts.get(address)
    balance = acct.balance if acct else _get_balance(address)
    return BalanceResponse(address=address, balance=balance)

@app.post("/api/tx/send", response_model=TxResponse)
def send_tx(req: TxSendRequest):
    tx = AttestedTransaction(
        consumer=req.consumer,
        provider=req.provider,
        service_ref=req.service_ref or f"svc:{req.provider}",
        amount=req.amount,
        consumer_sig=req.consumer_sig,
        provider_sig=req.provider_sig,
        description=req.description,
    )
    return TxResponse(
        tx_id=tx.tx_id,
        status="pending" if tx.is_valid() else "invalid",
        amount=tx.amount,
        consumer=tx.consumer,
        provider=tx.provider,
    )

@app.get("/api/services", response_model=list[ServiceResponse])
def list_services(service_type: str | None = None, min_rating: float = 0.0):
    reg = _get_service_registry()
    services = reg.list_services(service_type=service_type, min_rating=min_rating)
    return [
        ServiceResponse(
            provider=s.provider,
            service_type=s.service_type,
            price_per_unit=s.price_per_unit,
            description=s.description,
            rating=_get_reputation().get_rating(s.provider),
            total_tx=_get_reputation().get_successful_tx_count(s.provider),
        )
        for s in services
    ]

@app.post("/api/service/register")
def register_service(req: ServiceRegisterRequest):
    reg = _get_service_registry()
    svc = ServiceRegistration(
        provider=req.provider,
        service_type=req.service_type,
        price_per_unit=req.price_per_unit,
        description=req.description,
        endpoint=req.endpoint,
    )
    ok = reg.register(svc)
    if not ok:
        raise HTTPException(400, "Service already registered for this provider")
    return {"status": "ok", "provider": req.provider}

@app.get("/api/reputation/{address}")
def get_reputation(address: str):
    rep = _get_reputation()
    return {
        "address": address,
        "rating": rep.get_rating(address),
        "successful_tx": rep.get_successful_tx_count(address),
        "disputes": rep.get_dispute_count(address),
    }

@app.get("/api/validators", response_model=list[str])
def get_validators():
    manager = _get_manager()
    try:
        return manager.list_branches()
    except Exception:
        return ["main"]



@app.post("/api/testnet/faucet")
def faucet(data: dict):
    """Get 100 free Ⓣ for testing (testnet only)."""
    from .core import Account
    address = data.get("address", "")
    if not address:
        raise HTTPException(400, "Missing address")
    manager = _get_manager()
    main = manager.get_main_state()
    acct = main.accounts.get(address)
    if acct:
        acct.balance += 100.0
    else:
        main.accounts[address] = Account(address=address, balance=100.0)
    return {"status": "ok", "address": address, "amount": 100.0}


# ── CLI runner ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Taxoin API server")
    parser.add_argument("--port", type=int, default=47780)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    import uvicorn
    print(f"₿ Taxoin API starting on http://{args.host}:{args.port}")
    print(f"₿ OpenAPI docs at http://{args.host}:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
