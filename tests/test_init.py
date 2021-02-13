"""Test Dyson Python library."""
from typing import Type

import pytest

from libdyson import (
    DEVICE_TYPE_360_EYE,
    DEVICE_TYPE_PURE_COOL_LINK_DESKTOP,
    DEVICE_TYPE_PURE_COOL_LINK_TOWER,
    Dyson360Eye,
    DysonDevice,
    DysonPureCool,
    DysonPureCoolLink,
    get_device,
)
from libdyson.const import (
    DEVICE_TYPE_PURE_COOL,
    DEVICE_TYPE_PURE_COOL_DESKTOP,
    DEVICE_TYPE_PURE_COOL_HUMIDITY,
)

from . import CREDENTIAL, SERIAL


@pytest.mark.parametrize(
    "device_type,class_type",
    [
        (DEVICE_TYPE_360_EYE, Dyson360Eye),
        (DEVICE_TYPE_PURE_COOL_LINK_DESKTOP, DysonPureCoolLink),
        (DEVICE_TYPE_PURE_COOL_LINK_TOWER, DysonPureCoolLink),
        (DEVICE_TYPE_PURE_COOL, DysonPureCool),
        (DEVICE_TYPE_PURE_COOL_DESKTOP, DysonPureCool),
        (DEVICE_TYPE_PURE_COOL_HUMIDITY, DysonPureCool),
    ],
)
def test_get_device(device_type: str, class_type: Type[DysonDevice]):
    """Test get_device."""
    device = get_device(SERIAL, CREDENTIAL, device_type)
    assert isinstance(device, class_type)
    assert device.serial == SERIAL


def test_get_device_unknown():
    """Test get_device with unknown type."""
    device = get_device(SERIAL, CREDENTIAL, "unknown")
    assert device is None
