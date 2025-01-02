"""Conneqtech IOT integration."""

from .conneqtechapi import ConneqtechApi
from .const import DOMAIN, LOGGER, PLATFORMS, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Conneqtech IOT platform."""
    hass.data.setdefault(DOMAIN, {})
    LOGGER.debug(f"Setting up Conneqtech IOT platform for {DOMAIN}")

    client_id = entry.data.get(CONF_CLIENT_ID)
    client_secret = entry.data.get(CONF_CLIENT_SECRET)
    device_id = entry.data.get(CONF_DEVICE_ID)

    conneqtechApi = ConneqtechApi(hass, client_id, client_secret)
    await conneqtechApi.async_init()
    device = await conneqtechApi.async_get_device(device_id)
    if entry.unique_id is None:
        hass.config_entries.async_update_entry(
            entry, unique_id=f"conneqtech-{device_id}")

    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "api": conneqtechApi,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    LOGGER.debug("Unloading Conneqtech IOT platform")

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return True
