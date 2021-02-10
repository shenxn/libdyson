"""Dyson Pure Cool Link fan."""

import json
import logging
import threading
from typing import Optional

from libdyson.const import (
    ENVIRONMENTAL_INIT,
    ENVIRONMENTAL_OFF,
    AirQualityTarget,
    FanMode,
    FanSpeed,
    MessageType,
)
from libdyson.exceptions import DysonNotConnected

from .dyson_device import TIMEOUT, DysonDevice
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
        self._air_quality_target = None
        self._continuous_monitoring = None
        self._error_code = None
        self._warning_code = None

        # Environmental
        self._humidity = None
        self._temperature = None
        self._volatile_organic_compounds = None
        self._particulars = None
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
    def continuous_monitoring(self) -> bool:
        """Return standby monitoring status."""
        return self._continuous_monitoring

    @property
    def air_quality_target(self) -> AirQualityTarget:
        """Return air quality target."""
        return self._air_quality_target

    @property
    def filter_life(self) -> int:
        """Return filter life in hours."""
        return self._filter_life

    @property
    def error_code(self) -> Optional[str]:
        """Return error code."""
        return self._error_code

    @property
    def warning_code(self) -> Optional[str]:
        """Return warning code."""
        return self._warning_code

    @property
    def humidity(self) -> int:
        """Return humidity in percentage."""
        return self._humidity

    @property
    def temperature(self) -> int:
        """Return temperature in kelvin."""
        return self._temperature

    @property
    def particulars(self) -> int:
        """Return particulars in unknown unit."""
        return self._particulars

    @property
    def volatile_organic_compounds(self) -> int:
        """Return VOCs in unknown unit."""
        return self._volatile_organic_compounds

    @property
    def sleep_timer(self) -> int:
        """Return sleep timer in minutes."""
        return self._sleep_timer

    @staticmethod
    def _get_field_value(state, field):
        return state[field][1] if isinstance(state[field], list) else state[field]

    @staticmethod
    def _get_environmental_field_value(state, field, divisor=1):
        value = DysonPureCoolLink._get_field_value(state, field)
        if value == "OFF":
            return ENVIRONMENTAL_OFF
        if value == "INIT":
            return ENVIRONMENTAL_INIT
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
        self._continuous_monitoring = self._get_field_value(state, "rhtm") == "ON"
        self._error_code = self._get_field_value(state, "ercd")
        self._warning_code = self._get_field_value(state, "wacd")

    def _update_environmental(self, payload: dict) -> None:
        data = payload["data"]
        self._humidity = self._get_environmental_field_value(data, "hact")
        self._temperature = self._get_environmental_field_value(
            data, "tact", divisor=10
        )
        self._particulars = self._get_environmental_field_value(data, "pact")
        self._volatile_organic_compounds = self._get_environmental_field_value(
            data, "vact"
        )
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

    def _request_first_data(self) -> bool:
        """Request and wait for first data."""
        self.request_current_status()
        self.request_environmental_data()
        status_available = self._status_data_available.wait(timeout=TIMEOUT)
        environmental_available = self._environmental_data_available.wait(
            timeout=TIMEOUT
        )
        return status_available and environmental_available

    def request_environmental_data(self):
        """Request environmental sensor data."""
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

    def set_continuous_monitoring(self, continuous_monitoring: bool) -> None:
        """Turn on/off continuous monitoring."""
        self._set_configuration(
            fmod=self._fan_mode.value,  # Seems fmod is required to make this work
            rhtm=self._bool_to_param(continuous_monitoring),
        )

    def set_air_quality_target(self, air_quality_target: AirQualityTarget) -> None:
        """Set air quality target."""
        self._set_configuration(qtar=air_quality_target.value)

    def set_sleep_timer(self, duration: int) -> None:
        """Set sleep timer."""
        if not 0 < duration <= 540:
            raise ValueError("Duration must be between 1 and 540")
        self._set_configuration(sltm="%04d" % duration)

    def disable_sleep_timer(self) -> None:
        """Disable sleep timer."""
        self._set_configuration(sltm="OFF")

    def reset_filter(self) -> None:
        """Reset filter life."""
        self._set_configuration(rstf="RSTF")
