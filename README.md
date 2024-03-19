# UPS over Network

This is a HomeAssistant plugin for collecting UPS information on the network. The UPS serial port is connected to the network via a serial-to-WiFi module, allowing the plugin to communicate directly with the UPS, collecting and displaying its status information in real-time.

## Demo configuration

```yaml
sensor:
  - platform: ups_over_network
    id: nas_ups
    name: NAS UPS
    host: 10.254.0.62
    port: 502
    scan_interval: 1
    protocol: Megatec/Q1
    resources:
      - raw
      - input_voltage
      - fault_voltage
      - output_voltage
      - load
      - frequency
      - battery_voltage
      - temperature
```

## Demo screenshot

![image](https://github.com/tinymins/home-assistant-custom-component-ups-over-network/assets/1808990/2022558e-8dda-41d4-afee-0bdac28248d1)
