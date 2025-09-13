# WordClock Home Assistant Integration

A custom Home Assistant integration for controlling WordClock devices.

https://github.com/kaufi95/wordclock

## Features

- 🎨 **RGB Color Control** - Full RGB color customization
- 🔆 **Brightness Control** - Adjustable brightness (0-255)
- 🔍 **Auto Discovery** - Automatic discovery via mDNS/Zeroconf
- 🌐 **Network Control** - HTTP-based communication
- ⚡  **Real-time Updates** - Live status monitoring
- 🔧 **Easy Setup** - Simple configuration flow

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Install "WordClock" from HACS
3. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/wordclock` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations → Add Integration → WordClock

## Configuration

The integration supports both automatic discovery and manual configuration:

### Automatic Discovery

WordClock devices broadcasting via mDNS will be automatically discovered and can be added with one click.

### Manual Setup

1. Go to Configuration → Integrations → Add Integration
2. Search for "WordClock"
3. Enter your WordClock's IP address or hostname (e.g., `wordclock.local`)
4. Give it a friendly name
5. Click Submit

## Usage

Once configured, your WordClock will appear as a light entity in Home Assistant:

- **Turn On/Off** - Control power state
- **Set Brightness** - Adjust brightness from 0-100%
- **Change Color** - Pick any RGB color
- **Automation Ready** - Use in automations and scenes

### Example Automation

```yaml
automation:
  - alias: "WordClock Morning"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.wordclock
        data:
          brightness: 180
          rgb_color: [255, 200, 100] # Warm white
```

## WordClock Device Requirements

Your WordClock device must support the following HTTP endpoints:

- `GET /status` - Returns current state (brightness, red, green, blue)
- `POST /update` - Accepts JSON payload to update state

### Expected JSON Format

```json
{
  "brightness": 128,
  "red": 255,
  "green": 255,
  "blue": 255,
  "language": "dialekt"
}
```

## Troubleshooting

### Device Not Found

- Ensure your WordClock is on the same network as Home Assistant
- Verify the WordClock's IP address/hostname is correct
- Check that the WordClock HTTP API is responding on port 80

### Connection Issues

- Confirm your WordClock supports the required HTTP endpoints
- Check Home Assistant logs for detailed error messages
- Ensure no firewall is blocking communication

## Development

This integration follows Home Assistant development guidelines:

- Async/await patterns for non-blocking operations
- Proper error handling and logging
- Config flow for user-friendly setup
- Zeroconf discovery support
- Standard light entity implementation

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
