from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    FREQUENCY_HERTZ,
    TEMP_CELSIUS,
    PERCENTAGE
)

# Define sensor types and units
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
