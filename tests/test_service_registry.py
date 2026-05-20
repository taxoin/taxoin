"""Tests for Service Registry module."""
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
        assert ok is False  # can't register twice

    def test_service_types_defined(self):
        assert SERVICE_TYPES is not None
        assert "sms" in SERVICE_TYPES
        assert "gpu" in SERVICE_TYPES

    def test_rating_default_zero(self):
        s = ServiceRegistration(provider="0xalice", service_type="sms", price_per_unit=0.1,
                                 description="SMS", endpoint="https://a.com")
        assert s.rating == 0.0
        assert s.total_tx == 0
