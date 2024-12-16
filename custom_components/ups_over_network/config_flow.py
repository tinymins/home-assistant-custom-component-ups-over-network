import voluptuous as vol
from datetime import timedelta
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
)
from homeassistant.helpers import config_validation as cv
from .const import SENSOR_DEFINITIONS

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_PROTOCOL): cv.string,
        vol.Required(CONF_RESOURCES): vol.All(
            cv.ensure_list, [vol.In(SENSOR_DEFINITIONS.keys())]
        ),
        vol.Optional("low_battery_voltage", default=24): cv.positive_int,
        vol.Optional("full_battery_voltage", default=27): cv.positive_int,
        vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=30)): cv.time_period,
    },
    extra=vol.ALLOW_EXTRA,
)
