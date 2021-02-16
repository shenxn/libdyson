"""Test Dyson Python library."""
from typing import Type

import pytest

from libdyson import (
    DEVICE_TYPE_360_EYE,
    DEVICE_TYPE_PURE_COOL,
    DEVICE_TYPE_PURE_COOL_DESK,
    DEVICE_TYPE_PURE_COOL_LINK,
    DEVICE_TYPE_PURE_COOL_LINK_DESK,
    DEVICE_TYPE_PURE_HOT_COOL_LINK,
    DEVICE_TYPE_PURE_HUMIDITY_COOL,
    Dyson360Eye,
    DysonDevice,
    DysonPureCool,
    DysonPureCoolLink,
    get_device,
)
from libdyson.dyson_pure_hot_cool_link import DysonPureHotCoolLink

from . import CREDENTIAL, SERIAL


@pytest.mark.parametrize(
    "device_type,class_type",
    [
        (DEVICE_TYPE_360_EYE, Dyson360Eye),
        (DEVICE_TYPE_PURE_COOL_LINK_DESK, DysonPureCoolLink),
        (DEVICE_TYPE_PURE_COOL_LINK, DysonPureCoolLink),
        (DEVICE_TYPE_PURE_COOL, DysonPureCool),
        (DEVICE_TYPE_PURE_COOL_DESK, DysonPureCool),
        (DEVICE_TYPE_PURE_HUMIDITY_COOL, DysonPureCool),
        (DEVICE_TYPE_PURE_HOT_COOL_LINK, DysonPureHotCoolLink),
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
