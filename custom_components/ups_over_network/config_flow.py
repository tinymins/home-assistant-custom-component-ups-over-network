"""Config flow for UPS Over Network integration."""
import voluptuous as vol
from datetime import timedelta
import logging

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 3
DEFAULT_LOW_BATTERY_VOLTAGE = 24
DEFAULT_FULL_BATTERY_VOLTAGE = 27

class UpsOverNetworkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UPS Over Network."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate user input
            try:
                # Connection test logic can be added here
                # await self.hass.async_add_executor_job(
                #     self._test_connection, user_input[CONF_HOST], user_input[CONF_PORT]
                # )

                # Create unique ID to prevent duplicate entries
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}_{user_input[CONF_PORT]}_{user_input[CONF_ID]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.error("Error connecting to UPS: %s", ex)
                errors["base"] = "cannot_connect"

        # If no user input or there are errors, show the form
        # Removed resource_schema as we'll enable all sensors

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=502): int,
                vol.Required(CONF_ID): str,
                vol.Required(CONF_PROTOCOL, default="Megatec/Q1"): vol.In(["Megatec/Q1"]),
                vol.Optional("low_battery_voltage", default=DEFAULT_LOW_BATTERY_VOLTAGE): cv.positive_int,
                vol.Optional("full_battery_voltage", default=DEFAULT_FULL_BATTERY_VOLTAGE): cv.positive_int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                # Removed resource_schema from here
            }),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return UpsOverNetworkOptionsFlow(config_entry)

    # def _test_connection(self, host, port):
    #     """Test connectivity to the UPS."""
    #     # Implement connection test logic
    #     pass


class UpsOverNetworkOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # No longer need to process resource selection as all sensors will be enabled

            # Update configuration
            options = {
                # Removed CONF_RESOURCES from here
                "low_battery_voltage": user_input.get("low_battery_voltage", DEFAULT_LOW_BATTERY_VOLTAGE),
                "full_battery_voltage": user_input.get("full_battery_voltage", DEFAULT_FULL_BATTERY_VOLTAGE),
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            }

            return self.async_create_entry(title="", data=options)

        # Prepare current configuration
        options = self.config_entry.options
        data = self.config_entry.data

        # No longer need resource selection form

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "low_battery_voltage",
                    default=options.get("low_battery_voltage", data.get("low_battery_voltage", DEFAULT_LOW_BATTERY_VOLTAGE))
                ): cv.positive_int,
                vol.Optional(
                    "full_battery_voltage",
                    default=options.get("full_battery_voltage", data.get("full_battery_voltage", DEFAULT_FULL_BATTERY_VOLTAGE))
                ): cv.positive_int,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=options.get(CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
                ): int,
                # Removed resource_schema from here
            }),
        )
