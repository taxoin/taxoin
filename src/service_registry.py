"""Service Registry — on-chain service discovery."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
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
    """On-chain registry of available services."""

    def __init__(self):
        self._services: dict[str, ServiceRegistration] = {}

    def register(
        self,
        registration: ServiceRegistration,
        validator_sig: str | None = None,
    ) -> bool:
        """Register a new service.

        Each provider can only register one service.
        Validator signature is required for production but optional in tests.

        Args:
            registration: Service details
            validator_sig: Signature from a validator verifying the service

        Returns:
            True if registered, False if provider already has a service
        """
        if registration.provider in self._services:
            return False
        registration.created_at = time.time()
        if validator_sig:
            registration.attested_by.append(validator_sig)
        self._services[registration.provider] = registration
        return True

    def list_services(
        self,
        service_type: str | None = None,
        min_rating: float = 0.0,
    ) -> list[ServiceRegistration]:
        """List all services, optionally filtered by type and minimum rating."""
        services = list(self._services.values())
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        if min_rating > 0.0:
            services = [s for s in services if s.rating >= min_rating]
        return services

    def get_service(self, provider: str) -> Optional[ServiceRegistration]:
        """Get a specific service by provider address."""
        return self._services.get(provider)
