"""Dyson Pure Cool Link fan."""

import json

from libdyson.const import AirQualityTarget, FanMode, FanSpeed
from libdyson.exceptions import DysonException, DysonNotConnected

from .dyson_device import DysonDevice
from .utils import mqtt_time


class DysonPureCoolLink(DysonDevice):
    """Dyson Pure Cool Link device."""

    def __init__(self, serial: str, credential: str, device_type: str):
        """Initialize the device."""
        super().__init__(serial, credential)
        self._device_type = device_type
        self._fan_mode = None
        self._fan_state = None
        self._night_mode = None
        self._speed = None
        self._oscillation = None
        self._filter_life = None
        self._quality_target = None
        self._standby_monitoring = None

    @property
    def device_type(self) -> str:
        """Device type."""
        return self._device_type

    @property
    def _status_topic(self) -> str:
        """MQTT status topic."""
        return f"{self.device_type}/{self._serial}/status/current"

    @property
    def fan_mode(self) -> FanMode:
        """Return fan mode."""
        return FanMode(self._fan_mode)

    @property
    def is_on(self) -> bool:
        """Return if the device is on."""
        return self._fan_state == "FAN"

    @property
    def speed(self) -> FanSpeed:
        """Return fan speed."""
        return FanSpeed(self._speed)

    @property
    def auto_mode(self) -> bool:
        """Return auto mode status."""
        return self.fan_mode == FanMode.AUTO

    @property
    def oscillation(self) -> bool:
        """Return oscillation status."""
        return self._oscillation == "ON"

    @property
    def night_mode(self) -> bool:
        """Return night mode status."""
        return self._night_mode == "ON"

    @property
    def standby_monitoring(self) -> bool:
        """Return standby monitoring status."""
        return self._standby_monitoring == "ON"

    @property
    def air_quality_target(self) -> AirQualityTarget:
        """Return air quality target."""
        return AirQualityTarget(self._air_quality_target)

    @property
    def filter_life(self) -> int:
        """Return filter life in hours."""
        return int(self._filter_life)

    @staticmethod
    def _get_field_value(state, field):
        return state[field][1] if isinstance(state[field], list) else state[field]

    @staticmethod
    def _bool_to_param(value: bool) -> str:
        return "ON" if value else "OFF"

    def _update_state(self, data: dict) -> None:
        state = data["product-state"]
        self._fan_mode = self._get_field_value(state, "fmod")
        self._fan_state = self._get_field_value(state, "fnst")
        self._night_mode = self._get_field_value(state, "nmod")
        self._speed = self._get_field_value(state, "fnsp")
        self._oscillation = self._get_field_value(state, "oson")
        self._filter_life = self._get_field_value(state, "filf")
        self._air_quality_target = self._get_field_value(state, "qtar")
        self._standby_monitoring = self._get_field_value(state, "rhtm")

    def _set_configuration(self, **kwargs: dict) -> None:
        if not self.is_connected:
            raise DysonNotConnected
        payload = json.dumps(
            {
                "msg": "STATE-SET",
                "time": mqtt_time(),
                "mode-reason": "LAPP",
                "data": kwargs,
            }
        )
        self._mqtt_client.publish(self._command_topic, payload, 1)

    def turn_on(self) -> None:
        """Turn on the device."""
        self._set_configuration(fmod="FAN")

    def turn_off(self) -> None:
        """Turn off the device."""
        self._set_configuration(fmod="OFF")

    def set_speed(self, speed: int) -> None:
        """Set manual speed."""
        if speed < 1 or speed > 10:
            raise DysonException("Invalid speed %s", speed)
        self._set_configuration(fmod="FAN", fnsp="%04d" % speed)

    def set_auto_mode(self, auto_mode: bool) -> None:
        """Turn on/off auto mode."""
        if auto_mode:
            self._set_configuration(fmod="AUTO")
        else:
            self._set_configuration(fmod="FAN")

    def set_oscillation(self, oscillation: bool) -> None:
        """Turn on/off night mode."""
        self._set_configuration(oson=self._bool_to_param(oscillation))

    def set_night_mode(self, night_mode: bool) -> None:
        """Turn on/off auto mode."""
        self._set_configuration(nmod=self._bool_to_param(night_mode))

    def set_standby_monitoring(self, standby_monitoring: bool) -> None:
        """Turn on/off standby monitoring."""
        self._set_configuration(
            fmod=self._fan_mode,
            rhtm=self._bool_to_param(standby_monitoring),
        )

    def set_air_quality_target(self, air_quality_target: AirQualityTarget) -> None:
        """Set air quality target."""
        self._set_configuration(qtar=air_quality_target.value)

    def reset_filter(self) -> None:
        """Reset filter life."""
        self._set_configuration(rstf="RSTF")
