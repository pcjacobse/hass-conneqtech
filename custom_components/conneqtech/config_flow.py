"""Config flow for Conneqtech integration."""
from __future__ import annotations
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_DEVICE_ID
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from aiohttp import ClientResponseError

from .const import DOMAIN, LOGGER
from .conneqtechapi import ConneqtechApi

import voluptuous as vol

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): str,
        vol.Required(CONF_CLIENT_SECRET): str,
    }
)
STEP_DEVICE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
    }
)


async def validate_device_input(hass, data: ConfigEntry) -> ConfigEntry:
    """Validate the user's device input allows us to connect."""
    if not data[CONF_DEVICE_ID].isdigit():
        raise HomeAssistantError("invalid_device_id")
    return data


class ConneqtechConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Conneqtech."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._existing_entry: config_entries.ConfigEntry | None = None
        self.reauth_mode = False

    async def async_step_device(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle a flow initialized by the device."""
        LOGGER.debug("async_step_device")
        if user_input is None:
            return self.async_show_form(
                step_id="device",
                data_schema=STEP_DEVICE_DATA_SCHEMA,
            )
        try:
            user_input = await validate_device_input(self.hass, user_input)
            device_id = user_input[CONF_DEVICE_ID]
            await self.conneqtechApi.async_get_device(device_id)
            self.user_input_data[CONF_DEVICE_ID] = device_id
        except ClientResponseError as e:
            err = e.args[0]
            if e.status == 404:
                err = "device_not_found"
            return self.async_show_form(
                step_id="device",
                data_schema=STEP_DEVICE_DATA_SCHEMA,
                errors={"base": err},
            )
        except Exception as e:
            LOGGER.error(f"Error: {e}")
            return self.async_show_form(
                step_id="device",
                data_schema=STEP_DEVICE_DATA_SCHEMA,
                errors={"base": e.args[0]},
            )

        await self.async_set_unique_id(f"conneqtech-{device_id}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=device_id,
            data=self.user_input_data
        )

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        client_id = user_input[CONF_CLIENT_ID]
        client_secret = user_input[CONF_CLIENT_SECRET]
        try:
            LOGGER.debug("create ConneqtechApi")
            self.conneqtechApi = ConneqtechApi(
                self.hass,
                client_id=client_id,
                client_secret=client_secret,
                device_id=None,
            )
            await self.conneqtechApi.async_init()
            if self.reauth_mode:
                self.hass.config_entries.async_update_entry(
                    self._existing_entry,
                    options={CONF_CLIENT_ID: client_id,
                             CONF_CLIENT_SECRET: client_secret},
                )
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self._existing_entry.entry_id))
                return self.async_abort(reason="reauth_successful")
        except ClientResponseError as e:
            if e.status == 403:
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors={"base": "invalid_auth"},
                )
        except Exception as e:
            LOGGER.error(f"Error: {e}")
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": e.args[0]},
            )
        self.user_input_data = user_input
        return await self.async_step_device(None)

    async def async_step_reauth(self, user_input: ConfigEntry) -> FlowResult:
        """Handle re-auth."""
        self.reauth_mode = True
        self._existing_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"])

        return await self.async_step_user(user_input)
