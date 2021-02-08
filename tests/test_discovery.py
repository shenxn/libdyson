"""Test discovery."""
import socket
from unittest.mock import MagicMock, patch

import pytest
from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf

from libdyson import DysonDiscovery
from libdyson.discovery import TYPE_DYSON_360_EYE, TYPE_DYSON_FAN
from libdyson.dyson_device import DysonDevice

from . import CREDENTIAL, HOST, SERIAL


def _mocked_service_browser(
    zeroconf: Zeroconf, type: list, listener: ServiceListener
) -> ServiceBrowser:
    service_browser = MagicMock(spec=ServiceBrowser)
    service_browser.zc = zeroconf
    service_browser.listener = listener
    return service_browser


@pytest.fixture(autouse=True)
def _zeroconf():
    zeroconf = MagicMock(spec=Zeroconf)
    with patch("libdyson.discovery.Zeroconf", return_value=zeroconf) as mocked:
        yield mocked


@pytest.fixture(autouse=True)
def _service_browser():
    with patch(
        "libdyson.discovery.ServiceBrowser", side_effect=_mocked_service_browser
    ) as mocked:
        yield mocked


def test_discovery():
    """Test discovery."""
    discovery = DysonDiscovery()
    device = DysonDevice(SERIAL, CREDENTIAL)
    discovery.start_discovery()
    service_browser = discovery._browser
    zeroconf = service_browser.zc
    listener = service_browser.listener

    # 360 Eye, discovered before registered
    name = f"360EYE-{SERIAL}.{TYPE_DYSON_360_EYE}"
    address = socket.inet_aton(HOST)
    service_info = ServiceInfo(TYPE_DYSON_360_EYE, name, addresses=[address])
    zeroconf.get_service_info = MagicMock(return_value=service_info)
    listener.add_service(zeroconf, TYPE_DYSON_360_EYE, name)
    callback = MagicMock()
    discovery.register_device(device, callback)
    callback.assert_called_once_with(HOST)

    # Pure Cool Link, registered before discovered
    serial = "NK6-CN-HAA0000A"
    device = DysonDevice(serial, CREDENTIAL)
    callback = MagicMock()
    discovery.register_device(device, callback)
    name = f"475_{serial}.{TYPE_DYSON_FAN}"
    service_info = ServiceInfo(TYPE_DYSON_FAN, name, addresses=[address])
    zeroconf.get_service_info = MagicMock(return_value=service_info)
    listener.add_service(zeroconf, TYPE_DYSON_FAN, name)
    callback.assert_called_once_with(HOST)

    # Stop discovery
    discovery.stop_discovery()
    service_browser.cancel.assert_called_once()
    zeroconf.close.assert_called_once()
