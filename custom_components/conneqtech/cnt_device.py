
from .const import DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity


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
