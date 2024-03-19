import voluptuous as vol
from homeassistant.helpers import config_validation as cv

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_ID): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Required(CONF_PROTOCOL): cv.string,
    vol.Required(CONF_RESOURCES): vol.All(cv.ensure_list, [vol.In(SENSOR_DEFINITIONS.keys())]),
    vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=30)): cv.time_period,
}, extra=vol.ALLOW_EXTRA)
