"""Dyson Pure Cool Link fan."""

import json
import logging
import threading

from libdyson.const import AirQualityTarget, FanMode, FanSpeed, MessageType
from libdyson.exceptions import DysonNotConnected

from .dyson_device import DysonDevice
from .utils import mqtt_time

_LOGGER = logging.getLogger(__name__)


class DysonPureCoolLink(DysonDevice):
    """Dyson Pure Cool Link device."""

    def __init__(self, serial: str, credential: str, device_type: str):
        """Initialize the device."""
        super().__init__(serial, credential)
        self._device_type = device_type

        self._environmental_data_available = threading.Event()

        self._fan_mode = None
        self._fan_state = None
        self._night_mode = None
        self._speed = None
        self._oscillation = None
        self._filter_life = None
        self._quality_target = None
        self._standby_monitoring = None

        # Environmental
        self._humdity = None
        self._temperature = None
        self._volatil_organic_compounds = None
        self._dust = None
        self._sleep_timer = None

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
        return self._fan_mode

    @property
    def is_on(self) -> bool:
        """Return if the device is on."""
        return self._fan_state

    @property
    def speed(self) -> FanSpeed:
        """Return fan speed."""
        return self._speed

    @property
    def auto_mode(self) -> bool:
        """Return auto mode status."""
        return self.fan_mode == FanMode.AUTO

    @property
    def oscillation(self) -> bool:
        """Return oscillation status."""
        return self._oscillation

    @property
    def night_mode(self) -> bool:
        """Return night mode status."""
        return self._night_mode

    @property
    def standby_monitoring(self) -> bool:
        """Return standby monitoring status."""
        return self._standby_monitoring

    @property
    def air_quality_target(self) -> AirQualityTarget:
        """Return air quality target."""
        return self._air_quality_target

    @property
    def filter_life(self) -> int:
        """Return filter life in hours."""
        return self._filter_life

    @property
    def humidity(self) -> int:
        """Return humidity in percentage."""
        return self._humdity

    @property
    def temperature(self) -> int:
        """Return temperature in kelvin."""
        return self._temperature

    @property
    def dust(self) -> int:
        """Return dust level in unknown unit."""
        return self._dust

    @property
    def sleep_timer(self) -> int:
        """Return sleep timer."""
        return self._sleep_timer

    @staticmethod
    def _get_field_value(state, field):
        return state[field][1] if isinstance(state[field], list) else state[field]

    @staticmethod
    def _get_environmental_field_value(state, field, divisor=1):
        value = DysonPureCoolLink._get_field_value(state, field)
        if value == "OFF":
            return -1
        if divisor == 1:
            return int(value)
        return float(value) / divisor

    @staticmethod
    def _bool_to_param(value: bool) -> str:
        return "ON" if value else "OFF"

    def _handle_message(self, payload: dict) -> None:
        super()._handle_message(payload)
        if payload["msg"] == "ENVIRONMENTAL-CURRENT-SENSOR-DATA":
            _LOGGER.debug("New environmental state: %s", payload)
            self._update_environmental(payload)
            if not self._environmental_data_available.is_set():
                self._environmental_data_available.set()
            for callback in self._callbacks:
                callback(MessageType.ENVIRONMENTAL)

    def _update_state(self, payload: dict) -> None:
        state = payload["product-state"]
        self._fan_mode = FanMode(self._get_field_value(state, "fmod"))
        self._fan_state = self._get_field_value(state, "fnst") == "FAN"
        self._night_mode = self._get_field_value(state, "nmod") == "ON"
        self._speed = FanSpeed(self._get_field_value(state, "fnsp"))
        self._oscillation = self._get_field_value(state, "oson") == "ON"
        self._filter_life = int(self._get_field_value(state, "filf"))
        self._air_quality_target = AirQualityTarget(
            self._get_field_value(state, "qtar")
        )
        self._standby_monitoring = self._get_field_value(state, "rhtm") == "ON"

    def _update_environmental(self, payload: dict) -> None:
        data = payload["data"]
        self._humdity = self._get_environmental_field_value(data, "hact")
        self._temperature = self._get_environmental_field_value(
            data, "tact", divisor=10
        )
        self._dust = self._get_environmental_field_value(data, "pact")
        self._sleep_timer = self._get_environmental_field_value(data, "sltm")

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

    def request_environmental_state(self):
        """Request environmental state."""
        if not self.is_connected:
            raise DysonNotConnected
        payload = {
            "msg": "REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA",
            "time": mqtt_time(),
        }
        self._mqtt_client.publish(self._command_topic, json.dumps(payload))

    def turn_on(self) -> None:
        """Turn on the device."""
        self._set_configuration(fmod="FAN")

    def turn_off(self) -> None:
        """Turn off the device."""
        self._set_configuration(fmod="OFF")

    def set_speed(self, speed: FanSpeed) -> None:
        """Set manual speed."""
        if speed == FanSpeed.SPEED_AUTO:
            self.set_auto_mode(True)
            return
        self._set_configuration(fmod="FAN", fnsp=speed.value)

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
