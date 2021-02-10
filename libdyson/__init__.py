"""Dyson Python library."""

from typing import Optional

from .const import (
    DEVICE_TYPE_360_EYE,
    DEVICE_TYPE_PURE_COOL_LINK_DESK,
    DEVICE_TYPE_PURE_COOL_LINK_TOWER,
)
from .const import MessageType  # noqa: F401
from .discovery import DysonDiscovery  # noqa: F401
from .dyson_360_eye import Dyson360Eye
from .dyson_360_eye import Dyson360EyePowerMode  # noqa: F401
from .dyson_360_eye import Dyson360EyeState  # noqa: F401
from .dyson_device import DysonDevice
from .dyson_pure_cool_link import DysonPureCoolLink, FanMode, FanSpeed  # noqa: F401


def get_device(serial: str, credential: str, device_type: str) -> Optional[DysonDevice]:
    """Get a new DysonDevice instance."""
    if device_type == DEVICE_TYPE_360_EYE:
        return Dyson360Eye(serial, credential)
    if device_type in [
        DEVICE_TYPE_PURE_COOL_LINK_DESK,
        DEVICE_TYPE_PURE_COOL_LINK_TOWER,
    ]:
        return DysonPureCoolLink(serial, credential, device_type)
    return None
