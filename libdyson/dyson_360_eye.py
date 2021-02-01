"""Dyson 360 Eye vacuum robot."""
from enum import Enum, auto
from typing import List, Optional, Tuple

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

    def __init__(self, serial: str, credentials: str):
        super().__init__(serial, credentials)
        self._state = None
        self._power_mode = None
        self._full_clean_type = None
        self._position = None
        self._clean_id = None
        self._battery_level = None

    @property
    def _device_type(self) -> str:
        return DEVICE_TYPE_360_EYE

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
            Dyson360EyeState.FULL_CLEAN_CHARGING,
        ]

    def _update_state(self, data: dict) -> None:
        state = data["state"] if "state" in data else data["newstate"]
        self._set_enum_attr(state, "state", Dyson360EyeState)
        self._set_enum_attr(
            data["currentVacuumPowerMode"],
            "power_mode",
            Dyson360EyePowerMode,
        )
        self._full_clean_type = data["fullCleanType"]
        self._clean_id = data["cleanId"]
        self._battery_level = data["batteryChargeLevel"]
        if "globalPosition" in data and len(data["globalPosition"]) == 2:
            self._position = tuple(data["globalPosition"])

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
