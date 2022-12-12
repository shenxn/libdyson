"""Dyson Pure Hot+Cool device."""

from typing import Optional

from .dyson_device import DysonHeatingDevice
from .dyson_pure_cool import DysonPureCool

class DysonPureHotCool(DysonPureCool, DysonHeatingDevice):
    """Dyson Pure Hot+Cool device."""

class DysonPureHotCoolFormaldehyde(DysonPureHotCool):
    """Dyson Pure Hot+Cool Formaldehyde device."""

    @property
    def formaldehyde(self) -> Optional[int]:
        """Return formaldehyde reading."""
        return self._get_environmental_field_value("hcho")
