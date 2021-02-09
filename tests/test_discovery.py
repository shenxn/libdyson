"""Test discovery."""
import socket
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

from libdyson import DysonDiscovery
from libdyson.discovery import TYPE_DYSON_360_EYE, TYPE_DYSON_FAN
from libdyson.dyson_device import DysonDevice

from . import CREDENTIAL, HOST, SERIAL


@pytest.fixture(autouse=True)
def zeroconf_mock() -> MagicMock:
    """Return zeroconf mock."""
    zeroconf = MagicMock(spec=Zeroconf)
    with patch("libdyson.discovery.Zeroconf", return_value=zeroconf) as mocked:
        yield mocked


@pytest.fixture()
def service_browser_mock() -> MagicMock:
    """Return service browser mock."""
    service_browser = MagicMock(spec=ServiceBrowser)
    type(service_browser).zc = MagicMock()
    with patch(
        "libdyson.discovery.ServiceBrowser",
        return_value=service_browser,
    ) as mocked:
        yield mocked


@pytest.mark.parametrize("zeroconf_instance", [None, MagicMock(spec=Zeroconf)])
def test_discovery(
    service_browser_mock: MagicMock,
    zeroconf_mock: MagicMock,
    zeroconf_instance: Optional[Zeroconf],
):
    """Test discovery."""
    discovery = DysonDiscovery()
    device = DysonDevice(SERIAL, CREDENTIAL)
    discovery.start_discovery(zeroconf_instance)
    service_browser = service_browser_mock.return_value
    zeroconf = service_browser_mock.call_args.args[0]
    listener = service_browser_mock.call_args.args[2]

    if zeroconf_instance is None:
        zeroconf_mock.assert_called_once()
    else:
        zeroconf_mock.assert_not_called()

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
    service_browser.zc.close.assert_called_once()


def test_stop_runtime_error():
    """Test ServiceBrowser.cancel RuntimeError handling."""
    service_browser = MagicMock(spec=ServiceBrowser)
    type(service_browser).zc = MagicMock()
    type(service_browser).cancel = MagicMock(side_effect=RuntimeError)
    with patch(
        "libdyson.discovery.ServiceBrowser",
        return_value=service_browser,
    ):
        discovery = DysonDiscovery()
        discovery.start_discovery()
        discovery.stop_discovery()
        service_browser.cancel.assert_called_once()
        service_browser.zc.close.assert_called_once()
