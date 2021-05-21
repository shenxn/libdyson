"""Dyson 360 Heurist cloud client."""

from datetime import datetime
from typing import List

import attr
from dateutil import parser

from .cloud_device import DysonCloudDevice


@attr.s(auto_attribs=True, frozen=True)
class Zone:
    """Represent a zone within a persistent map."""

    id: str
    name: str
    icon: str
    area: float  # In square meters

    @classmethod
    def from_raw(cls, raw: dict):
        return cls(
            raw["id"],
            raw["name"],
            raw["icon"],
            raw["area"],
        )


@attr.s(auto_attribs=True, frozen=True)
class PersistentMap:
    """Represent a persistent map created by the user."""

    id: str
    name: str
    last_visited: datetime  # UTC
    zones_definition_last_updated_date: datetime  # UTC
    zones: List[Zone]

    @classmethod
    def from_raw(cls, raw: dict):
        """Parse raw data from cloud API."""
        return cls(
            raw["id"],
            raw["name"],
            parser.isoparse(raw["lastVisited"]),
            parser.isoparse(raw["zonesDefinitionLastUpdatedDate"]),
            [Zone.from_raw(raw) for raw in raw["zones"]],
        )


class DysonCloud360Heurist(DysonCloudDevice):
    """Dyson 360 Heurist cloud client."""

    def get_persistent_maps(self) -> List[PersistentMap]:
        """Get the persistent maps from the cloud."""
        response = self._account.request(
            "GET",
            f"/v1/app/{self._serial}/persistent-map-metadata",
        )
        return [PersistentMap.from_raw(raw) for raw in response.json()]
