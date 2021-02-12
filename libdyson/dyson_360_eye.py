"""Dyson 360 Eye vacuum robot."""
from enum import Enum
from typing import Optional, Tuple

from .const import DEVICE_TYPE_360_EYE
from .dyson_device import DysonDevice


class VacuumState(Enum):
    """Dyson vacuum state."""

    FAULT_CALL_HELPLINE = "FAULT_CALL_HELPLINE"
    FAULT_CONTACT_HELPLINE = "FAULT_CONTACT_HELPLINE"
    FAULT_CRITICAL = "FAULT_CRITICAL"
    FAULT_GETTING_INFO = "FAULT_GETTING_INFO"
    FAULT_LOST = "FAULT_LOST"
    FAULT_ON_DOCK = "FAULT_ON_DOCK"
    FAULT_ON_DOCK_CHARGED = "FAULT_ON_DOCK_CHARGED"
    FAULT_ON_DOCK_CHARGING = "FAULT_ON_DOCK_CHARGING"
    FAULT_REPLACE_ON_DOCK = "FAULT_REPLACE_ON_DOCK"
    FAULT_RETURN_TO_DOCK = "FAULT_RETURN_TO_DOCK"
    FAULT_RUNNING_DIAGNOSTIC = "FAULT_RUNNING_DIAGNOSTIC"
    FAULT_USER_RECOVERABLE = "FAULT_USER_RECOVERABLE"
    FULL_CLEAN_ABANDONED = "FULL_CLEAN_ABANDONED"
    FULL_CLEAN_ABORTED = "FULL_CLEAN_ABORTED"
    FULL_CLEAN_CHARGING = "FULL_CLEAN_CHARGING"
    FULL_CLEAN_DISCOVERING = "FULL_CLEAN_DISCOVERING"
    FULL_CLEAN_FINISHED = "FULL_CLEAN_FINISHED"
    FULL_CLEAN_INITIATED = "FULL_CLEAN_INITIATED"
    FULL_CLEAN_NEEDS_CHARGE = "FULL_CLEAN_NEEDS_CHARGE"
    FULL_CLEAN_PAUSED = "FULL_CLEAN_PAUSED"
    FULL_CLEAN_RUNNING = "FULL_CLEAN_RUNNING"
    FULL_CLEAN_TRAVERSING = "FULL_CLEAN_TRAVERSING"
    INACTIVE_CHARGED = "INACTIVE_CHARGED"
    INACTIVE_CHARGING = "INACTIVE_CHARGING"
    INACTIVE_DISCHARGING = "INACTIVE_DISCHARGING"
    MAPPING_ABORTED = "MAPPING_ABORTED"
    MAPPING_CHARGING = "MAPPING_CHARGING"
    MAPPING_FINISHED = "MAPPING_FINISHED"
    MAPPING_INITIATED = "MAPPING_INITIATED"
    MAPPING_NEEDS_CHARGE = "MAPPING_NEEDS_CHARGE"
    MAPPING_PAUSED = "MAPPING_PAUSED"
    MAPPING_RUNNING = "MAPPING_RUNNING"


class VacuumPowerMode(Enum):
    """Dyson vacuum power mode."""

    QUIET = "halfPower"
    MAX = "fullPower"


class CleaningType(Enum):
    """Vacuum cleaning type."""

    IMMEDIATE = "immediate"
    MANUAL = "manual"
    Scheduled = "scheduled"


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
    def cleaning_type(self) -> Optional[CleaningType]:
        """Return the type of the current cleaning task."""
        cleaning_type = self._status["fullCleanType"]
        if cleaning_type == "":
            return None
        return CleaningType(cleaning_type)

    @property
    def cleaning_id(self) -> Optional[str]:
        """Return the id of the current cleaning task."""
        cleaning_id = self._status["cleanId"]
        if cleaning_id == "":
            return None
        return cleaning_id

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
            VacuumState.MAPPING_CHARGING,
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
