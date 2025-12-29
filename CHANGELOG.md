# Changelog

All notable changes to this project will be documented in this file.

## [2.1.1] - 2025-12-29

### Changed
- Reverted brightness range back to 1-255 (matching Home Assistant's internal range)
- Removed brightness conversion logic for direct pass-through
- Updated default last brightness from 50 to 128

## [2.1.0] - 2025-12-29

### Added
- Super Bright mode toggle via new Switch entity
- Support for brightness range 5-100% with automatic conversion from HA's 0-255 range

### Changed
- Updated brightness handling with conversion between HA (0-255) and WordClock (5-100)

## [2.0.0] - 2025-12-29

### Added
- Real-time updates via Server-Sent Events (SSE)
- New `WordClockCoordinator` class managing SSE connection and state distribution
- Automatic SSE reconnection with 5-second retry delay
- Optimistic updates for immediate UI responsiveness

### Changed
- All entities now extend `CoordinatorEntity` instead of managing individual HTTP calls
- IoT class changed from `local_polling` to `local_push`
- Removed polling-based updates in favor of push-based SSE updates
- Updated all platform files (light, number, select) to use coordinator pattern

### Fixed
- Added proper SSE headers (`Accept: text/event-stream`, `Cache-Control: no-cache`)
- Instant synchronization between Home Assistant and WordClock web interface

## [1.2.0] - Previous version

### Features
- Basic light control (on/off, brightness, RGB color)
- Number entity for transition speed
- Select entities for transition, prefix mode, and language
- Polling-based updates via `/status` endpoint
- Config flow with manual and automatic (mDNS) discovery
