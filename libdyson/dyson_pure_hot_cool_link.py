"""Dyson Pure Hot+Cool Link device."""

from .dyson_pure_cool_link import DysonPureCoolLink


class DysonPureHotCoolLink(DysonPureCoolLink):
    """Dyson Pure Hot+Cool Link device."""

    @property
    def tilt(self) -> bool:
        """Return tilt status."""
        return self._get_field_value(self._status, "tilt") == "TILT"

    @property
    def focus_mode(self) -> bool:
        """Return if fan focus mode is on."""
        return self._get_field_value(self._status, "ffoc") == "ON"

    @property
    def heat_target(self) -> float:
        """Return heat target in kelvin."""
        return int(self._get_field_value(self._status, "hmax")) / 10

    @property
    def heat_mode_is_on(self) -> bool:
        """Return if heat mode is set to on."""
        return self._get_field_value(self._status, "hmod") == "HEAT"

    @property
    def heat_status_is_on(self) -> bool:
        """Return if the device is currently heating."""
        return self._get_field_value(self._status, "hsta") == "HEAT"

    def set_heat_target(self, heat_target: float) -> None:
        """Set heat target in kelvin."""
        if not 274 <= heat_target <= 310:
            raise ValueError("Heat target must be between 274 and 310 kelvin")
        self._set_configuration(
            hmod="HEAT",
            hmax=f"{round(heat_target * 10):04d}",
        )

    def enable_heat_mode(self) -> None:
        """Enable heat mode."""
        self._set_configuration(hmod="HEAT")

    def disable_heat_mode(self) -> None:
        """Disable heat mode."""
        self._set_configuration(hmod="OFF")

    def enable_focus_mode(self) -> None:
        """Enable fan focus mode."""
        self._set_configuration(ffoc="ON")

    def disable_focus_mode(self) -> None:
        """Disable fan focus mode."""
        self._set_configuration(ffoc="OFF")
