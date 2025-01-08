"""The Conneqtech API."""

from __future__ import annotations


from typing import Any, Callable, Optional

from aiohttp import ClientSession, BasicAuth, ClientTimeout
from aiohttp.client_exceptions import ClientConnectionError
from aiohttp_sse_client2 import client as sse_client
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
# from datetime import timedelta
from .device import ConneqtechDevice
from .const import LOGGER, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICE_ID, DOMAIN, set_nested_value
import json


class Coordinator(DataUpdateCoordinator):
    """Conneqtech API class."""

    def __init__(
            self,
            hass: HomeAssistant,
            config_entry: ConfigEntry,
            api: ConneqtechApi,
    ) -> None:
        """Initialize the Conneqtech API class."""
        self.api = api
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Set update method to get devices on first load.
            update_method=self.api.async_update_data,
            # Do not set a polling interval as data will be pushed.
            # You can remove this line but left here for explanatory purposes.
            update_interval=None,  # timedelta(seconds=15),
        )

    async def async_connect(self) -> None:
        """Connect to the Conneqtech API."""
        await self.api.async_connect(self.update_data)

    def update_data(self, key: str, val: Any) -> None:
        """Update the data."""

        self.data.raw = set_nested_value(self.data.raw, key, val)
        self.async_set_updated_data(self.data)


class ConneqtechApi:
    """Conneqtech API class."""

    def __init__(
            self,
            hass: HomeAssistant,
            client_id: str,
            client_secret: str,
            device_id: Optional[str],
    ) -> None:
        """Initialize the Conneqtech API class."""
        LOGGER.debug(f"Initializing Conneqtech API for {device_id}")

        self.hass: HomeAssistant = hass
        self.session: ClientSession = self.hass.helpers.aiohttp_client.async_get_clientsession()
        self.auth = BasicAuth(
            client_id,
            client_secret,
        )
        self.device_id = device_id

    async def async_connect(self, callback: Callable[[str, Any], None]) -> None:
        """Connect to the Conneqtech API."""
        imei = self.device_id

        while True:
            LOGGER.debug(f"Connecting to Conneqtech API for {imei}")
            async with sse_client.EventSource(
                f"https://api.iot.conneq.tech/v2/es/device?imeis={imei}",
                session=ClientSession(timeout=ClientTimeout(total=None)),
                auth=self.auth,
            ) as event_source:
                try:
                    async for event in event_source:
                        data = json.loads(event.data)
                        if data.get("type") == "updated":
                            for key, val in data.get("changes").items():
                                LOGGER.debug(f"Received event {
                                    imei} change: {key} - {val}")
                                if callback is not None:
                                    callback(key, val)
                except ClientConnectionError as e:
                    LOGGER.error(f"Connection error {imei}: {e}")
                except Exception as e:
                    LOGGER.error(f"Error {imei}: {e}")
                LOGGER.debug(f"Connection closed for {imei}")

    async def async_update_data(self) -> Any:
        return await self.async_get_device(self.device_id)

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
