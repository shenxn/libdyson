"""Dyson Pure Humidity+Cool device."""

from .const import WaterHardness
from .dyson_pure_cool import DysonPureCool

WATER_HARDNESS_ENUM_TO_STR = {
    WaterHardness.SOFT: "2025",
    WaterHardness.MEDIUM: "1350",
    WaterHardness.HARD: "0675",
}
WATER_HARDNESS_STR_TO_ENUM = {
    str_: enum for enum, str_ in WATER_HARDNESS_ENUM_TO_STR.items()
}


class DysonPureHumidityCool(DysonPureCool):
    """Dyson Pure Humidity+Cool device."""

    @property
    def humidification(self) -> bool:
        """Return if humidification is on."""
        return self._get_field_value(self._status, "hume") == "HUMD"

    @property
    def humidification_auto_mode(self) -> bool:
        """Return if humidification auto mode is on."""
        return self._get_field_value(self._status, "haut") == "ON"

    @property
    def humidity_target(self) -> int:
        """Return humidity target in percentage."""
        return int(self._get_field_value(self._status, "humt"))

    @property
    def auto_humidity_target(self) -> int:
        """Return humidification auto mode humidity target."""
        return int(self._get_field_value(self._status, "rect"))

    @property
    def water_hardness(self) -> WaterHardness:
        """Return the water hardness setting."""
        return WATER_HARDNESS_STR_TO_ENUM[self._get_field_value(self._status, "wath")]

    def enable_humidification(self) -> None:
        """Enable humidification."""
        self._set_configuration(hume="HUMD")

    def disable_humidification(self) -> None:
        """Disable humidification."""
        self._set_configuration(hume="OFF")

    def enable_humidification_auto_mode(self) -> None:
        """Enable humidification auto mode."""
        self._set_configuration(haut="ON")

    def disable_humidification_auto_mode(self) -> None:
        """Disable humidification auto mode."""
        self._set_configuration(haut="OFF")

    def set_humidity_target(self, humidity_target: int) -> None:
        """Set humidity target."""
        self._set_configuration(humt=f"{humidity_target:04d}")

    def set_water_hardness(self, water_hardness: WaterHardness) -> None:
        """Set water hardness."""
        self._set_configuration(wath=WATER_HARDNESS_ENUM_TO_STR[water_hardness])
