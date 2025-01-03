
from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .conneqtechapi import ConneqtechApi
from .const import LOGGER, TOPIC_UPDATE, DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .device import ConneqtechDevice


class CntDevice(CoordinatorEntity):
    """Base class for Conneqtech entities."""
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.imei)},
            "name": self.coordinator.data.imei,
            "manufacturer": "Conneqtech",
            "model": self.coordinator.data.device_type,
            "sw_version": self.coordinator.data.firmware_version,
        }
