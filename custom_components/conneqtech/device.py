"""Conneqtech device"""

from __future__ import annotations
from attr import dataclass
from typing import Any, Optional
from datetime import datetime

from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import TOPIC_UPDATE, DOMAIN


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


class CntDevice(Entity):
    def __init__(self, hass, config_entry, device: ConneqtechDevice):
        self.hass = hass
        self.config_entry = config_entry
        self.device = device
        self.topic_update = TOPIC_UPDATE.format(device.imei)
        self.topic_update_listener = None

    async def async_added_to_hass(self):
        @callback
        def update():
            self.update_from_latest_data()
            self.async_write_ha_state()

        await super().async_added_to_hass()
        self.topic_update_listener = async_dispatcher_connect(
            self.hass, self.topic_update, update)
        self.async_on_remove(self.topic_update_listener)
        self.update_from_latest_data()

    @property
    def available(self) -> bool:
        return not not self.device

    @property
    def should_poll(self) -> bool:
        return True  # temp switch to False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.imei)},
            "name": self.device.imei,
            "manufacturer": "Conneqtech",
            "model": self.device.device_type,
            "sw_version": self.device.firmware_version,
        }

    @callback
    def update_from_latest_data(self):
        self.device = self.hass.data[DOMAIN][self.config_entry.entry_id]["device"]
