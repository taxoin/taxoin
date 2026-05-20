"""Tests for Service Registry module."""
import json
import os
import tempfile
import time
import pytest

from src.core import Account

try:
    from src.service_registry import ServiceRegistration, ServiceRegistry, SERVICE_TYPES
except ImportError:
    ServiceRegistration = None
    ServiceRegistry = None
    SERVICE_TYPES = None


@pytest.mark.skipif(ServiceRegistry is None, reason="ServiceRegistry not implemented")
class TestServiceRegistry:
    """Tests for service registration and discovery."""

    def test_register_service(self):
        reg = ServiceRegistry()
        service = ServiceRegistration(
            provider="0xalice",
            service_type="sms",
            price_per_unit=0.1,
            description="SMS gateway",
            endpoint="https://sms.alice.com",
        )
        ok = reg.register(service, validator_sig="0xval1_sig")
        assert ok is True

    def test_list_services_empty(self):
        reg = ServiceRegistry()
        assert reg.list_services() == []

    def test_list_services_after_register(self):
        reg = ServiceRegistry()
        s1 = ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                  description="SMS", endpoint="https://a.com")
        s2 = ServiceRegistration(provider="0xbob", service_type="gpu", price_per_unit=5.0,
                                  description="GPU farm", endpoint="https://b.com")
        reg.register(s1)
        reg.register(s2)
        services = reg.list_services()
        assert len(services) == 2

    def test_filter_by_type(self):
        reg = ServiceRegistry()
        reg.register(ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                          description="SMS", endpoint="https://a.com"))
        reg.register(ServiceRegistration(provider="0xbob", service_type="gpu", price_per_unit=5.0,
                                          description="GPU", endpoint="https://b.com"))
        sms_list = reg.list_services(service_type="sms")
        assert len(sms_list) == 1
        assert sms_list[0].provider == "0xalice"

    def test_get_service(self):
        reg = ServiceRegistry()
        reg.register(ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                          description="SMS", endpoint="https://a.com"))
        s = reg.get_service("0xalice")
        assert s is not None
        assert s.service_type == "sms"

    def test_get_nonexistent_service(self):
        reg = ServiceRegistry()
        assert reg.get_service("0xnobody") is None

    def test_register_duplicate_provider(self):
        reg = ServiceRegistry()
        reg.register(ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                          description="SMS", endpoint="https://a.com"))
        ok = reg.register(ServiceRegistration(provider="0xalice", service_type="gpu", price_per_unit=5.0,
                                               description="GPU", endpoint="https://b.com"))
        assert ok is False

    def test_service_types_defined(self):
        assert SERVICE_TYPES is not None
        assert "sms" in SERVICE_TYPES
        assert "gpu" in SERVICE_TYPES

    def test_rating_default_zero(self):
        s = ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                 description="SMS", endpoint="https://a.com")
        assert s.rating == 0.0
        assert s.total_tx == 0


@pytest.mark.skipif(ServiceRegistry is None, reason="ServiceRegistry not implemented")
class TestServiceRegistryPersistence:
    """Tests for service registry persistence to disk."""

    def test_save_and_load_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "services.json")
            reg = ServiceRegistry(store_path=path)
            reg2 = ServiceRegistry(store_path=path)
            assert reg2.list_services() == []

    def test_save_and_load_with_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "services.json")
            reg = ServiceRegistry(store_path=path)
            reg.register(ServiceRegistration(provider="0xalice", service_type="sms",
                                              price_per_unit=0.1, description="SMS",
                                              endpoint="https://a.com"))
            reg.register(ServiceRegistration(provider="0xbob", service_type="gpu",
                                              price_per_unit=5.0, description="GPU",
                                              endpoint="https://b.com"))
            reg2 = ServiceRegistry(store_path=path)
            assert len(reg2.list_services()) == 2

    def test_preserves_data_across_instances(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "services.json")
            reg = ServiceRegistry(store_path=path)
            reg.register(ServiceRegistration(provider="0xalice", service_type="sms",
                                              price_per_unit=0.1, description="SMS",
                                              endpoint="https://a.com"))
            reg2 = ServiceRegistry(store_path=path)
            loaded = reg2.get_service("0xalice")
            assert loaded is not None
            assert loaded.price_per_unit == 0.1
