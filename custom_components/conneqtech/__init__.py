"""Conneqtech IOT integration."""

from .conneqtechapi import ConneqtechApi, Coordinator
from .const import DOMAIN, LOGGER, PLATFORMS, CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from dataclasses import dataclass

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from collections.abc import Callable


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator
    cancel_update_listener: Callable


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Conneqtech IOT platform."""
    hass.data.setdefault(DOMAIN, {})
    LOGGER.debug(f"Setting up Conneqtech IOT platform for {DOMAIN}")

    device_id = entry.data.get(CONF_DEVICE_ID)

    conneqtechApi = ConneqtechApi(
        hass,
        client_id=entry.data.get("client_id"),
        client_secret=entry.data.get("client_secret"),
        device_id=device_id,
    )
    await conneqtechApi.async_init()

    coordinator = Coordinator(hass, entry, conneqtechApi)
    await coordinator.async_config_entry_first_refresh()
    cancel_update_listener = entry.add_update_listener(_async_update_listener)

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(
            entry, unique_id=f"conneqtech-{device_id}")

    hass.data[DOMAIN][entry.entry_id] = RuntimeData(
        coordinator, cancel_update_listener)

    entry.async_create_background_task(
        hass,
        coordinator.async_connect(),
        name="Conneqtech IOT connection"
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle config options update."""
    # Reload the integration when the options change.
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    LOGGER.debug("Unloading Conneqtech IOT platform")

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return True
