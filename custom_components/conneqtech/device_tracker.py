"""ConnectTech device tracker entity."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, LOGGER
from .conneqtechapi import ConneqtechApi
from .device import ConneqtechDevice
from .cnt_device import CntDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the device tracker entities."""
    LOGGER.debug(f"Setting up device tracker entities for {DOMAIN}")

    coordinator: ConneqtechApi = hass.data[DOMAIN][
        entry.entry_id
    ].coordinator

    LOGGER.debug(f"Setting up device tracker entity for {
                 coordinator.data.imei}")
    async_add_entities([ConneqtechDeviceTracker(coordinator)])


class ConneqtechDeviceTracker(CntDevice, TrackerEntity):
    """Conneqtech device tracker entity."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"conneqtech-location-{self.coordinator.data.imei}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{self.coordinator.data.imei} Location"

    @property
    def source_type(self) -> str:
        """Return the source type of the entity."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self.coordinator.data.latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self.coordinator.data.longitude

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:crosshairs-gps"

    @property
    def battery_level(self) -> int:
        """Return the battery level of the device."""
        return self.coordinator.data.battery_level
