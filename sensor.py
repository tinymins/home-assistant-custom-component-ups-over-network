import asyncio
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_RESOURCES,
    ELECTRIC_POTENTIAL_VOLT,
    FREQUENCY_HERTZ,
    TEMP_CELSIUS,
    PERCENTAGE
)

_LOGGER = logging.getLogger(__name__)

# 定义传感器的类型和单位
SENSOR_DEFINITIONS = {
    "raw": ["Raw", "", "mdi:text-box-outline"],
    "input_voltage": ["Input Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:flash"],
    "fault_voltage": ["Fault Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:flash-off"],
    "output_voltage": ["Output Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:flash"],
    "load": ["Load", PERCENTAGE, "mdi:gauge"],
    "frequency": ["Frequency", FREQUENCY_HERTZ, "mdi:current-ac"],
    "battery_voltage": ["Battery Voltage", ELECTRIC_POTENTIAL_VOLT, "mdi:battery"],
    "temperature": ["Temperature", TEMP_CELSIUS, "mdi:thermometer"],
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the UPS sensor."""
    ups_id = config[CONF_ID]
    ups_name = config[CONF_NAME]
    ups_host = config[CONF_HOST]
    ups_port = config[CONF_PORT]
    ups_protocol = config[CONF_PROTOCOL]
    resources = config[CONF_RESOURCES]

    sensors = []

    for sensor_type in resources:
        sensor_definition = SENSOR_DEFINITIONS.get(sensor_type)
        if sensor_definition:
            sensors.append(UPSSensor(ups_id, ups_name, ups_host, ups_port, ups_protocol, sensor_type, *sensor_definition))

    async_add_entities(sensors, True)

class UPSSensor(Entity):
    """Implementation of a UPS sensor."""

    def __init__(self, ups_id, ups_name, ups_host, ups_port, ups_protocol, sensor_type, sensor_name, sensor_unit, sensor_icon):
        """Initialize the sensor."""
        self._ups_id = ups_id
        self._ups_name = ups_name
        self._ups_host = ups_host
        self._ups_port = ups_port
        self._ups_protocol = ups_protocol
        self._sensor_type = sensor_type
        self._sensor_name = sensor_name
        self._sensor_unit = sensor_unit
        self._sensor_icon = sensor_icon
        self._sensor_state = None

    @property
    def id(self):
        """Return the id of the sensor."""
        return "{}_{}".format(self._ups_id, self._sensor_type)

    @property
    def unique_id(self):
        """Return the unique_id of the sensor."""
        return "{}_{}".format(self._ups_id, self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._ups_name, self._sensor_name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._sensor_state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._sensor_icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_unit

    async def async_update_megatec_q1(self, reader, writer):
        # 发送Q1命令
        writer.write(b'Q1\r')
        await writer.drain()

        # 读取响应
        data = await reader.read(1024)
        response = data.decode('utf-8').strip()

        # 关闭连接
        writer.close()
        await writer.wait_closed()

        # 解析响应
        if response.startswith('(') and len(response) > 46:
            values = response[1:-1].split(' ') # 去除括号
            if self._sensor_type == "raw":
                self._sensor_state = response
            elif self._sensor_type == "input_voltage":
                self._sensor_state = float(values[0])
            elif self._sensor_type == "fault_voltage":
                self._sensor_state = float(values[1])
            elif self._sensor_type == "output_voltage":
                self._sensor_state = float(values[2])
            elif self._sensor_type == "load":
                self._sensor_state = float(values[3])
            elif self._sensor_type == "frequency":
                self._sensor_state = float(values[4])
            elif self._sensor_type == "battery_voltage":
                self._sensor_state = float(values[5])
            elif self._sensor_type == "temperature":
                self._sensor_state = float(values[6])

    async def async_update(self):
        """Get the latest data from the UPS and updates the states."""
        try:
            reader, writer = await asyncio.open_connection(self._ups_host, self._ups_port)

            if self._ups_protocol == "Megatec/Q1":
                await self.async_update_megatec_q1(reader, writer)

        except Exception as e:
            _LOGGER.error(f"Error fetching data from UPS: {e}")
            self._sensor_state = None
