"""Dyson 360 Eye vacuum robot."""
from enum import Enum
from typing import Optional, Tuple

from libdyson.const import DEVICE_TYPE_360_EYE
from libdyson.dyson_device import DysonDevice


class VacuumState(Enum):
    """Dyson vacuum state."""

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


class VacuumPowerMode(Enum):
    """Dyson vacuum power mode."""

    QUIET = "halfPower"
    MAX = "fullPower"


class Dyson360Eye(DysonDevice):
    """Dyson 360 Eye device."""

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return DEVICE_TYPE_360_EYE

    @property
    def _status_topic(self) -> str:
        """MQTT status topic."""
        return f"{self.device_type}/{self._serial}/status"

    @property
    def state(self) -> VacuumPowerMode:
        """State of the device."""
        return VacuumState(
            self._status["state"]
            if "state" in self._status
            else self._status["newstate"]
        )

    @property
    def power_mode(self) -> VacuumPowerMode:
        """Power mode of the device."""
        return VacuumPowerMode(self._status["currentVacuumPowerMode"])

    @property
    def full_clean_type(self) -> str:
        """Full clean type of the device."""
        return self._status["fullCleanType"]

    @property
    def clean_id(self) -> str:
        """Clean id of the device."""
        return self._status["cleanId"]

    @property
    def battery_level(self) -> int:
        """Battery level of the device in percentage."""
        return self._status["batteryChargeLevel"]

    @property
    def position(self) -> Optional[Tuple[int, int]]:
        """Position (x, y) of the device."""
        if (
            "globalPosition" in self._status
            and len(self._status["globalPosition"]) == 2
        ):
            return tuple(self._status["globalPosition"])
        return None

    @property
    def is_charging(self) -> bool:
        """Whether the device is charging."""
        return self.state in [
            VacuumState.INACTIVE_CHARGING,
            VacuumState.INACTIVE_CHARGED,
            VacuumState.FULL_CLEAN_CHARGING,
        ]

    def _update_status(self, payload: dict) -> None:
        self._status = payload

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

    def set_power_mode(self, power_mode: VacuumPowerMode) -> None:
        """Set power mode."""
        self._send_command(
            "STATE-SET",
            {"data": {"defaultVacuumPowerMode": power_mode.value}},
        )
