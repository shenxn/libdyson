"""Dyson 360 Eye vacuum robot."""
from enum import Enum
from typing import Optional, Tuple

from libdyson.const import DEVICE_TYPE_360_EYE
from libdyson.dyson_device import DysonDevice


class Dyson360EyeState(Enum):
    """360 Eye state."""

    INACTIVE_CHARGING = "INACTIVE_CHARGING"
    INACTIVE_CHARGED = "INACTIVE_CHARGED"
    FULL_CLEAN_INITIATED = "FULL_CLEAN_INITIATED"
    FULL_CLEAN_RUNNING = "FULL_CLEAN_RUNNING"
    FULL_CLEAN_PAUSED = "FULL_CLEAN_PAUSED"
    FULL_CLEAN_ABORTED = "FULL_CLEAN_ABORTED"
    FULL_CLEAN_FINISHED = "FULL_CLEAN_FINISHED"
    FULL_CLEAN_NEEDS_CHARGE = "FULL_CLEAN_NEEDS_CHARGE"
    FULL_CLEAN_CHARGING = "FULL_CLEAN_CHARGING"
    FAULT_USER_RECOVERABLE = "FAULT_USER_RECOVERABLE"
    FAULT_REPLACE_ON_DOCK = "FAULT_REPLACE_ON_DOCK"


class Dyson360EyePowerMode(Enum):
    """360 Eye power mode."""

    QUIET = "halfPower"
    MAX = "fullPower"


class Dyson360Eye(DysonDevice):
    """Dyson 360 Eye device."""

    def __init__(self, serial: str, credential: str):
        """Initialize the device."""
        super().__init__(serial, credential)
        self._state = None
        self._power_mode = None
        self._full_clean_type = None
        self._position = None
        self._clean_id = None
        self._battery_level = None

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return DEVICE_TYPE_360_EYE

    @property
    def _status_topic(self) -> str:
        """MQTT status topic."""
        return f"{self.device_type}/{self._serial}/status"

    @property
    def state(self) -> Optional[Dyson360EyeState]:
        """State of the device."""
        return self._state

    @property
    def power_mode(self) -> Optional[Dyson360EyePowerMode]:
        """Power mode of the device."""
        return self._power_mode

    @property
    def full_clean_type(self) -> Optional[str]:
        """Full clean type of the device."""
        return self._full_clean_type

    @property
    def clean_id(self) -> Optional[str]:
        """Clean id of the device."""
        return self._clean_id

    @property
    def battery_level(self) -> Optional[int]:
        """Battery level of the device in percentage."""
        return self._battery_level

    @property
    def position(self) -> Optional[Tuple[int, int]]:
        """Position (x, y) of the device."""
        return self._position

    @property
    def is_charging(self) -> Optional[bool]:
        """Whether the device is charging."""
        if self.state is None:
            return None
        return self.state in [
            Dyson360EyeState.INACTIVE_CHARGING,
            Dyson360EyeState.INACTIVE_CHARGED,
            Dyson360EyeState.FULL_CLEAN_CHARGING,
        ]

    def _update_state(self, payload: dict) -> None:
        state = payload["state"] if "state" in payload else payload["newstate"]
        self._set_enum_attr(state, "state", Dyson360EyeState)
        self._set_enum_attr(
            payload["currentVacuumPowerMode"],
            "power_mode",
            Dyson360EyePowerMode,
        )
        self._full_clean_type = payload["fullCleanType"]
        self._clean_id = payload["cleanId"]
        self._battery_level = payload["batteryChargeLevel"]
        if "globalPosition" in payload and len(payload["globalPosition"]) == 2:
            self._position = tuple(payload["globalPosition"])

    def start(self) -> None:
        """Start cleaning."""
        self._send_command("START", {"fullCleanType": "immediate"})

    def pause(self) -> None:
        """Pause cleaning."""
        self._send_command("PAUSE")

    def resume(self) -> None:
        """Resume cleaning."""
        self._send_command("RESUME")

    def abort(self) -> None:
        """Abort cleaning."""
        self._send_command("ABORT")

    def set_power_mode(self, power_mode: Dyson360EyePowerMode) -> None:
        """Set power mode."""
        self._send_command(
            "STATE-SET",
            {"data": {"defaultVacuumPowerMode": power_mode.value}},
        )
