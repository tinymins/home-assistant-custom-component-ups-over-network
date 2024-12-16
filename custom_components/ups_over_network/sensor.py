import asyncio
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_RESOURCES,
    CONF_SCAN_INTERVAL,
)
from .const import SENSOR_DEFINITIONS
from .config_flow import PLATFORM_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the UPS sensor."""
    # Explicitly validate the configuration against the PLATFORM_SCHEMA
    config = PLATFORM_SCHEMA(config)

    ups_id = config[CONF_ID]
    ups_name = config[CONF_NAME]
    ups_host = config[CONF_HOST]
    ups_port = config[CONF_PORT]
    ups_protocol = config[CONF_PROTOCOL]
    resources = config[CONF_RESOURCES]
    scan_interval = config.get(CONF_SCAN_INTERVAL, timedelta(seconds=30))

    coordinator = UPSDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="UPS Sensor",
        update_interval=scan_interval,
        ups_host=ups_host,
        ups_port=ups_port,
        ups_protocol=ups_protocol,
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for sensor_type in resources:
        sensor_definition = SENSOR_DEFINITIONS.get(sensor_type)
        if sensor_definition:
            sensors.append(
                UPSSensor(
                    coordinator, ups_id, ups_name, sensor_type, *sensor_definition
                )
            )

    async_add_entities(sensors, True)


class UPSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching UPS data."""

    def __init__(
        self, hass, logger, name, update_interval, ups_host, ups_port, ups_protocol
    ):
        """Initialize."""
        self.ups_host = ups_host
        self.ups_port = ups_port
        self.ups_protocol = ups_protocol

        super().__init__(hass, logger, name=name, update_interval=update_interval)

    async def _async_update_data_megatec_q1(self, reader, writer):
        # Send Q1 command
        writer.write(b"Q1\r")
        await writer.drain()

        # Read response
        data = await reader.read(1024)
        response = data.decode("utf-8").strip()

        # Close connection
        writer.close()
        await writer.wait_closed()

        # Parse the response
        # Remove the parentheses
        values = response[1:-1].split(" ")
        # Validate response
        if not response.startswith("(") or len(values) < 6:
            raise UpdateFailed(f"Invalid response from UPS: {response}")

        return {
            "raw": response,
            "input_voltage": float(values[0]),
            "fault_voltage": float(values[1]),
            "output_voltage": float(values[2]),
            "load": float(values[3]),
            "frequency": float(values[4]),
            "battery_voltage": float(values[5]),
            "temperature": float(values[6]),
        }

    async def _async_update_data(self):
        """Fetch data from UPS."""
        try:
            reader, writer = await asyncio.open_connection(self.ups_host, self.ups_port)

            if self.ups_protocol == "Megatec/Q1":
                return await self._async_update_data_megatec_q1(reader, writer)

        except Exception as e:
            raise UpdateFailed(f"Error communicating with UPS: {e}")


class UPSSensor(CoordinatorEntity, Entity):
    """Implementation of a UPS sensor."""

    def __init__(
        self,
        coordinator,
        ups_id,
        ups_name,
        sensor_type,
        sensor_name,
        sensor_unit,
        sensor_icon,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._ups_id = ups_id
        self._ups_name = ups_name
        self._sensor_type = sensor_type
        self._sensor_name = sensor_name
        self._sensor_unit = sensor_unit
        self._sensor_icon = sensor_icon

    @property
    def id(self):
        """Return the id of the sensor."""
        return f"{self._ups_id}_{self._sensor_type}"

    @property
    def unique_id(self):
        """Return the unique_id of the sensor."""
        return f"{self._ups_id}_{self._sensor_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._ups_name} {self._sensor_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type)

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._sensor_icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_unit
