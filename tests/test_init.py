"""Test Dyson Python library."""
from typing import Type

import pytest

from libdyson import (
    DEVICE_TYPE_360_EYE,
    DEVICE_TYPE_PURE_COOL_LINK_DESK,
    DEVICE_TYPE_PURE_COOL_LINK_TOWER,
    get_device,
)
from libdyson.dyson_360_eye import Dyson360Eye
from libdyson.dyson_device import DysonDevice
from libdyson.dyson_pure_cool_link import DysonPureCoolLink

from . import CREDENTIAL, SERIAL


@pytest.mark.parametrize(
    "device_type,class_type",
    [
        (DEVICE_TYPE_360_EYE, Dyson360Eye),
        (DEVICE_TYPE_PURE_COOL_LINK_DESK, DysonPureCoolLink),
        (DEVICE_TYPE_PURE_COOL_LINK_TOWER, DysonPureCoolLink),
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
