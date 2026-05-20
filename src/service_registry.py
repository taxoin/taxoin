"""Service Registry — on-chain service discovery with persistence."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

SERVICE_TYPES = ["sms", "gpu", "compute", "taxi", "api", "storage", "bandwidth", "expertise"]


@dataclass
class ServiceRegistration:
    provider: str
    service_type: str
    price_per_unit: float
    description: str
    endpoint: str
    attested_by: list[str] = field(default_factory=list)
    rating: float = 0.0
    total_tx: int = 0
    created_at: float = 0.0


class ServiceRegistry:
    """On-chain registry of available services.

    Persists to a JSON file when store_path is provided.
    Data survives restarts.
    """

    def __init__(self, store_path: str | None = None):
        self._services: dict[str, ServiceRegistration] = {}
        self._store_path = store_path
        if store_path and os.path.exists(store_path):
            self._load()

    def _save(self) -> None:
        if not self._store_path:
            return
        data = {
            addr: asdict(svc)
            for addr, svc in self._services.items()
        }
        with open(self._store_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self) -> None:
        if not self._store_path or not os.path.exists(self._store_path):
            return
        with open(self._store_path) as f:
            data = json.load(f)
        for addr, svc_data in data.items():
            svc_data["attested_by"] = list(svc_data.get("attested_by", []))
            self._services[addr] = ServiceRegistration(**svc_data)

    def register(
        self,
        registration: ServiceRegistration,
        validator_sig: str | None = None,
    ) -> bool:
        """Register a new service."""
        if registration.provider in self._services:
            return False
        registration.created_at = time.time()
        if validator_sig:
            registration.attested_by.append(validator_sig)
        self._services[registration.provider] = registration
        self._save()
        return True

    def list_services(
        self,
        service_type: str | None = None,
        min_rating: float = 0.0,
    ) -> list[ServiceRegistration]:
        """List all services, optionally filtered."""
        services = list(self._services.values())
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        if min_rating > 0.0:
            services = [s for s in services if s.rating >= min_rating]
        return services

    def get_service(self, provider: str) -> Optional[ServiceRegistration]:
        """Get a specific service by provider address."""
        return self._services.get(provider)
