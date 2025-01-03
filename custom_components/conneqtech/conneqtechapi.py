"""The Conneqtech API."""

from __future__ import annotations


from typing import Any

from aiohttp import ClientSession, BasicAuth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from datetime import timedelta
from .device import ConneqtechDevice
from .const import LOGGER, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICE_ID, DOMAIN


class ConneqtechApi(DataUpdateCoordinator):
    """Conneqtech API class."""

    def __init__(
            self,
            hass: HomeAssistant,
            config_entry: ConfigEntry,
    ) -> None:
        """Initialize the Conneqtech API class."""
        self.hass: HomeAssistant = hass
        self.session: ClientSession = self.hass.helpers.aiohttp_client.async_get_clientsession()
        self.auth = BasicAuth(
            config_entry.data.get(CONF_CLIENT_ID),
            config_entry.data.get(CONF_CLIENT_SECRET),
        )
        self.config_entry = config_entry

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Set update method to get devices on first load.
            update_method=self.async_update_data,
            # Do not set a polling interval as data will be pushed.
            # You can remove this line but left here for explanatory purposes.
            update_interval=timedelta(seconds=15),
        )

    async def async_update_data(self) -> Any:
        return await self.async_get_device(self.config_entry.data.get(CONF_DEVICE_ID))

    async def async_init(self) -> None:
        """Initialize the Conneqtech API class."""
        resp = await self.session.get(
            "https://api.iot.conneq.tech/v2/device?query=imei:0&limit=0",
            auth=self.auth,
        )
        resp.raise_for_status()

    async def async_get_device(self, device_id: str) -> ConneqtechDevice:
        """Get device data."""
        resp = await self.session.get(
            f"https://api.iot.conneq.tech/v2/device/{device_id}",
            auth=self.auth,
        )
        resp.raise_for_status()
        return ConneqtechDevice(await resp.json())
