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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the UPS Over Network sensor."""
    # Get data from config entry
    config = config_entry.data
    options = config_entry.options

    # Merge data and options
    combined_config = {**config}
    if options:
        # Prioritize settings from options
        for key, value in options.items():
            combined_config[key] = value

    # Use the combined config directly
    ups_id = combined_config.get(CONF_ID)
    ups_name = combined_config.get(CONF_NAME)
    ups_host = combined_config.get(CONF_HOST)
    ups_port = combined_config.get(CONF_PORT)
    ups_protocol = combined_config.get(CONF_PROTOCOL, "Megatec/Q1")
    scan_interval = timedelta(seconds=combined_config.get(CONF_SCAN_INTERVAL))
    low_battery_voltage = combined_config.get("low_battery_voltage")
    full_battery_voltage = combined_config.get("full_battery_voltage")

    coordinator = UPSDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="UPS Sensor",
        update_interval=scan_interval,
        ups_host=ups_host,
        ups_port=ups_port,
        ups_protocol=ups_protocol,
        low_battery_voltage=low_battery_voltage,
        full_battery_voltage=full_battery_voltage,
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for sensor_type, sensor_definition in SENSOR_DEFINITIONS.items():
        sensors.append(
            UPSSensor(
                coordinator, ups_id, ups_name, sensor_type, *sensor_definition
            )
        )

    async_add_entities(sensors, True)


class UPSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching UPS data."""

    def __init__(
        self,
        hass,
        logger,
        name,
        update_interval,
        ups_host,
        ups_port,
        ups_protocol,
        low_battery_voltage,
        full_battery_voltage,
    ):
        """Initialize."""
        self.ups_host = ups_host
        self.ups_port = ups_port
        self.ups_protocol = ups_protocol
        self.low_battery_voltage = low_battery_voltage
        self.full_battery_voltage = full_battery_voltage

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
            "battery_level": int(
                max(
                    0,
                    min(
                        1,
                        (float(values[5]) - self.low_battery_voltage)
                        / (self.full_battery_voltage - self.low_battery_voltage),
                    ),
                )
                * 10000
            )
            / 100,
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
        self._attr_unique_id = f"{self._ups_id}_{self._sensor_type}"
        self._attr_name = f"{self._ups_name} {self._sensor_name}"
        self._attr_device_info = {
            "identifiers": {("ups_over_network", self._ups_id)},
            "name": self._ups_name,
            "manufacturer": "UPS Over Network",
            "model": "Generic UPS",
        }
        if self._sensor_type == "raw":
            self._attr_entity_registry_enabled_default = False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data and self._sensor_type in self.coordinator.data

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.available:
            return self.coordinator.data.get(self._sensor_type)
        return None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._sensor_type == "battery_level":
            if self.state == 100:
                return "mdi:battery"
            if self.state is not None and self.state < 10:
                return "mdi:battery-alert-variant-outline"
            if self.state is not None:
                return f"mdi:battery-{int(self.state / 10) * 10}"
        return self._sensor_icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_unit
