"""Constants for the Conneqtech integration."""

import logging
from homeassistant.const import Platform
from datetime import datetime

DOMAIN = "conneqtech"
TOPIC_UPDATE: str = f"{DOMAIN}_update_{0}"

LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
]

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_DEVICE_ID = "device_id"


def parse_datetime(dt: str | None) -> datetime:
    if dt is None:
        return None
    try:
        return datetime.fromisoformat(dt)
    except ValueError:
        return None
    except TypeError:
        return None


def get_nested_value(obj, key):
    """Retrieve the value of a dot-separated key from a nested object."""
    keys = key.split('.')
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k)
        elif isinstance(obj, list):
            try:
                k = int(k)
                obj = obj[k]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return obj


def set_nested_value(obj, key, value) -> dict:
    """Set the value of a dot-separated key in a nested object."""
    keys = key.split('.')
    d = obj
    for k in keys[:-1]:
        if isinstance(d, dict):
            d = d.setdefault(k, {})
        elif isinstance(d, list):
            try:
                k = int(k)
                while len(d) <= k:
                    d.append({})
                d = d[k]
            except (ValueError, IndexError):
                return obj
        else:
            return obj
    if isinstance(d, dict):
        d[keys[-1]] = value
    elif isinstance(d, list):
        try:
            k = int(keys[-1])
            while len(d) <= k:
                d.append(None)
            d[k] = value
        except (ValueError, IndexError):
            return obj
    return obj
