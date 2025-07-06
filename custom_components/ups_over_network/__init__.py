"""The UPS Over Network integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
    CONF_HOST,
    CONF_PORT,
)
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config):
    """Set up the UPS Over Network component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up UPS Over Network from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get configuration
    config = entry.data
    options = entry.options
    combined_config = {**config}
    if options:
        for key, value in options.items():
            combined_config[key] = value

    ups_host = combined_config.get(CONF_HOST)
    ups_port = combined_config.get(CONF_PORT)

    # Test UPS connection before setting up platforms
    try:
        _LOGGER.debug("Testing UPS connection to %s:%s", ups_host, ups_port)
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ups_host, ups_port),
            timeout=10.0
        )
        writer.close()
        await writer.wait_closed()
        _LOGGER.debug("UPS connection test successful")
    except Exception as err:
        _LOGGER.error("Failed to connect to UPS at %s:%s: %s", ups_host, ups_port, err)
        raise ConfigEntryNotReady(f"Unable to connect to UPS at {ups_host}:{ups_port}: {err}") from err

    # Store the config entry data in hass.data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
