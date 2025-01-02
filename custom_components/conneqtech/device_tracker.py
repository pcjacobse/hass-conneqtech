"""ConnectTech device tracker entity."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, LOGGER, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICE_ID
from .conneqtechapi import ConneqtechApi
from .device import ConneqtechDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the device tracker entities."""
    LOGGER.debug(f"Setting up device tracker entities for {DOMAIN}")

    device: ConneqtechDevice = hass.data[DOMAIN][entry.entry_id]["device"]
    LOGGER.debug(f"Setting up device tracker entity for {device.imei}")
    api: ConneqtechApi = hass.data[DOMAIN][entry.entry_id]["api"]
    async_add_entities([ConneqtechDeviceTracker(api, device)])


class ConneqtechDeviceTracker(TrackerEntity):
    """Conneqtech device tracker entity."""

    def __init__(self, api: ConneqtechApi, device: ConneqtechDevice):
        """Initialize the entity."""
        self._device = device
        self._api = api

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"conneqtech-location-{self._device.imei}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{self._device.imei} Location"

    @property
    def source_type(self) -> str:
        """Return the source type of the entity."""
        return SourceType.GPS

    @property
    def should_poll(self) -> bool:
        """Return whether the entity should be polled."""
        return True

    async def async_update(self):
        """Update the entity."""
        LOGGER.debug(f"Updating device tracker entity {self._device.imei}")
        self._device = await self._api.async_get_device(self._device.imei)
        LOGGER.debug(f"Updated device tracker entity values: {self._device}")

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self._device.latitude

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self._device.longitude

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:crosshairs-gps"

    @property
    def battery_level(self) -> int:
        """Return the battery level of the device."""
        return self._device.battery_level
