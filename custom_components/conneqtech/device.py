"""Conneqtech device"""

from __future__ import annotations
from attr import dataclass
from typing import Any, Optional
from datetime import datetime

from .const import parse_datetime


@dataclass
class ConneqtechDevice:
    """Device class for Conneqtech integration."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw

    @property
    def imei(self) -> str:
        return self.raw.get("imei")

    @property
    def params(self) -> dict[str, Any]:
        return self.raw.get("params")

    @property
    def device_type(self) -> str:
        return self.raw.get("device_type")

    @property
    def longitude(self) -> Optional[float]:
        return self.raw.get("payload_state", {}).get("tracker", {}).get(
            "loc", {}).get("geo", {}).get("coordinates", [None, None])[0]

    @property
    def latitude(self) -> Optional[float]:
        return self.raw.get("payload_state", {}).get("tracker", {}).get(
            "loc", {}).get("geo", {}).get("coordinates", [None, None])[1]

    @property
    def last_connection_date(self) -> Optional[datetime]:
        return parse_datetime(self.raw.get("payload_state", {}).get("dts"))

    @property
    def last_location_date(self) -> Optional[datetime]:
        return parse_datetime(self.raw.get("payload_state", {}).get(
            "tracker", {}).get("loc", {}).get("dtg"))

    @property
    def firmware_version(self) -> Optional[str]:
        return self.raw.get("payload_state", {}).get(
            "tracker", {}).get("config", {}).get("fwver")

    @property
    def battery_level(self) -> Optional[int]:
        return self.raw.get("payload_state", {}).get(
            "tracker", {}).get("metric", {}).get("bbatp")

    @property
    def speed(self) -> Optional[float]:
        return self.raw.get("payload_state", {}).get(
            "tracker", {}).get("loc", {}).get("sp")

    @property
    def altitude(self) -> Optional[float]:
        return self.raw.get("payload_state", {}).get("tracker", {}).get(
            "loc", {}).get("alt")

    @property
    def course(self) -> Optional[float]:
        return self.raw.get("payload_state", {}).get("tracker", {}).get(
            "loc", {}).get("ang")

    raw: Optional[dict[str, Any]] = None
