from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTemperature,
    PERCENTAGE,
)

# Define sensor types and units
SENSOR_DEFINITIONS = {
    "raw": ["Raw", "", "mdi:text-box-outline"],
    "input_voltage": ["Input Voltage", UnitOfElectricPotential.VOLT, "mdi:flash"],
    "fault_voltage": ["Fault Voltage", UnitOfElectricPotential.VOLT, "mdi:flash-off"],
    "output_voltage": ["Output Voltage", UnitOfElectricPotential.VOLT, "mdi:flash"],
    "load": ["Load", PERCENTAGE, "mdi:gauge"],
    "frequency": ["Frequency", UnitOfFrequency.HERTZ, "mdi:current-ac"],
    "battery_voltage": ["Battery Voltage", UnitOfElectricPotential.VOLT, "mdi:battery"],
    "temperature": ["Temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer"],
}
