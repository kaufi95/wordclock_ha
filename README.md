# WordClock Home Assistant Integration

A custom Home Assistant integration for controlling WordClock devices with real-time updates via Server-Sent Events.

https://github.com/kaufi95/wordclock

## Features

- 🎨 **RGB Color Control** - Full RGB color customization
- 🔆 **Brightness Control** - Adjustable brightness (1-255)
- ⚡ **Real-time Updates** - Instant synchronization via Server-Sent Events (SSE)
- 💡 **Super Bright Mode** - Toggle enhanced brightness mode
- 🎭 **Transition Effects** - Multiple animation options (None, Fade, Wipe, Sparkle)
- ⚙️ **Prefix Mode Control** - Configure time prefix behavior
- 🌍 **Language Support** - Switch between Dialekt and Deutsch
- 🔍 **Auto Discovery** - Automatic discovery via mDNS/Zeroconf
- 🌐 **Network Control** - HTTP-based communication
- 🔧 **Easy Setup** - Simple configuration flow

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kaufi95&repository=wordclock_ha&category=Integration)

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

Once configured, your WordClock will provide multiple entities in Home Assistant:

### Light Entity

- **Turn On/Off** - Control power state
- **Set Brightness** - Adjust brightness from 1-255 (same range as HA)
- **Change Color** - Pick any RGB color

### Switch Entity

- **Super Bright Mode** - Toggle enhanced brightness mode for maximum visibility

### Select Entities

- **Transition Effect** - Choose animation style (None, Fade, Wipe, Sparkle)
- **Prefix Mode** - Control time prefix behavior (Always, Random, Off)
- **Language** - Switch between Dialekt and Deutsch

### Number Entity

- **Transition Speed** - Adjust animation speed (0-4)

All entities update **instantly** via Server-Sent Events - changes made in the web interface appear immediately in Home Assistant and vice versa!

### Example Automations

**Morning Routine:**

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
      - service: select.select_option
        target:
          entity_id: select.wordclock_transition
        data:
          option: "Fade"
```

**Movie Mode:**

```yaml
automation:
  - alias: "WordClock Movie Mode"
    trigger:
      - platform: state
        entity_id: media_player.tv
        to: "playing"
    action:
      - service: light.turn_on
        target:
          entity_id: light.wordclock
        data:
          brightness: 50
          rgb_color: [255, 0, 0]
      - service: switch.turn_off
        target:
          entity_id: switch.wordclock_super_bright
```

## WordClock Device Requirements

Your WordClock device must support the following HTTP endpoints:

- `GET /status` - Returns current state
- `POST /update` - Accepts JSON payload to update state
- `GET /events` - Server-Sent Events stream for real-time updates

### Status Response Format

```json
{
  "red": 255,
  "green": 255,
  "blue": 255,
  "brightness": 60,
  "language": "deutsch",
  "enabled": true,
  "superBright": false,
  "transition": 1,
  "prefixMode": 1,
  "transitionSpeed": 1
}
```

### Update Request Format

Send a JSON payload with any of the above fields to `/update`:

```json
{
  "brightness": 80,
  "red": 255,
  "green": 100,
  "blue": 50,
  "superBright": true
}
```

### Server-Sent Events

The `/events` endpoint should stream updates with the `text/event-stream` content type:

```
event: settings
data: {"red":255,"green":100,"blue":50,"brightness":80,...}

```

Each change triggers a broadcast to all connected clients, enabling real-time synchronization.

## Troubleshooting

### Device Not Found

- Ensure your WordClock is on the same network as Home Assistant
- Verify the WordClock's IP address/hostname is correct
- Check that the WordClock HTTP API is responding on port 80

### Connection Issues

- Confirm your WordClock supports the required HTTP endpoints
- Check Home Assistant logs for detailed error messages
- Ensure no firewall is blocking communication

### Slow Updates

If updates aren't instant:

1. Check that the `/events` endpoint is working: `curl -N -H "Accept: text/event-stream" http://YOUR_IP/events`
2. Verify you see SSE connection messages in HA logs: Settings → System → Logs
3. Reload the integration: Settings → Devices & Services → WordClock → ⋮ → Reload

### Brightness Range

- Both Home Assistant and WordClock use the same 1-255 brightness range
- Values are passed directly without conversion
- Minimum brightness is 1, maximum is 255

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.wordclock: debug
```

Then: Settings → System → Logs → Reload

## Development

This integration follows Home Assistant development guidelines:

- Async/await patterns for non-blocking operations
- Server-Sent Events for real-time updates via `DataUpdateCoordinator`
- Proper error handling and automatic reconnection
- Config flow for user-friendly setup
- Zeroconf/mDNS discovery support
- Multiple entity types: Light, Switch, Select, Number
- IoT class: `local_push` (real-time updates, not polling)

### Architecture

- **Coordinator Pattern**: Central `WordClockCoordinator` manages SSE connection
- **Real-time Updates**: Changes broadcast via SSE to all entities simultaneously
- **Optimistic Updates**: UI updates immediately on user actions
- **Auto-reconnection**: 5-second retry on connection failures
- **Direct Brightness Control**: Both HA and WordClock use 1-255 range (no conversion needed)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
