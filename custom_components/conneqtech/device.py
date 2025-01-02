"""Conneqtech device"""

from __future__ import annotations
from attr import dataclass
from typing import Any, Optional
from datetime import datetime


@dataclass
class ConneqtechDevice:
    """Device class for Conneqtech integration."""
    imei: str
    params: dict[str, Any]
    device_type: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    last_connection_date: Optional[datetime] = None
    last_location_date: Optional[datetime] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[int] = None
    speed: Optional[float] = None
    altitude: Optional[float] = None
    course: Optional[float] = None

    async def async_add_listener(self, listener):
        """Add listener to device."""
        pass
