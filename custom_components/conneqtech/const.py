"""Constants for the Conneqtech integration."""

import logging
from homeassistant.const import Platform

DOMAIN = "conneqtech"
TOPIC_UPDATE: str = f"{DOMAIN}_update_{0}"

LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER,
    # Platform.SENSOR,
    # Platform.BINARY_SENSOR,
]

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_DEVICE_ID = "device_id"
