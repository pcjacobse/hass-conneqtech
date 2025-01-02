"""The Conneqtech API."""

from __future__ import annotations


from typing import Any

from aiohttp import ClientSession, ClientResponseError, BasicAuth
from aiohttp.client_exceptions import ClientError

from homeassistant.core import HomeAssistant

from .device import ConneqtechDevice


class ConneqtechApi:
    """Conneqtech API class."""

    def __init__(
            self,
            hass: HomeAssistant,
            client_id: str,
            client_secret: str,
    ) -> None:
        """Initialize the Conneqtech API class."""
        self.hass: HomeAssistant = hass
        self.session: ClientSession = self.hass.helpers.aiohttp_client.async_get_clientsession()
        self.auth = BasicAuth(client_id, client_secret)

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
        data = await resp.json()

        return ConneqtechDevice(
            imei=data["imei"],
            params=data["params"],
            device_type=data["device_type"],
            firmware_version=data.get("payload_state", {}).get(
                "tracker", {}).get("config", {}).get("fwver"),
            latitude=data.get("payload_state", {}).get("tracker", {}).get(
                "loc", {}).get("geo", {}).get("coordinates", [None, None])[1],
            longitude=data.get("payload_state", {}).get("tracker", {}).get(
                "loc", {}).get("geo", {}).get("coordinates", [None, None])[0],
            battery_level=data.get("payload_state", {}).get(
                "tracker", {}).get("metric", {}).get("bbatp"),
            speed=data.get("payload_state", {}).get(
                "tracker", {}).get("loc", {}).get("sp"),
        )
