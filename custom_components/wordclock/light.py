"""Platform for light integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WordClock Light platform."""
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]
    
    async_add_entities([WordClockLight(hass, host, name)], True)


class WordClockLight(LightEntity):
    """Representation of a WordClock Light."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize a WordClock Light."""
        self.hass = hass
        self._host = host
        self._name = name
        self._state = None
        self._brightness = None
        self._rgb_color = None
        self._available = True
        self._last_brightness = 128  # Store last non-zero brightness

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wordclock"

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        return self._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the RGB color value."""
        return self._rgb_color

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        return ColorMode.RGB

    @property
    def supported_color_modes(self) -> set[str]:
        """Flag supported color modes."""
        return {ColorMode.RGB}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        data = {}

        # Only send brightness if it's being changed
        if ATTR_BRIGHTNESS in kwargs:
            new_brightness = kwargs[ATTR_BRIGHTNESS]
            if new_brightness != self._brightness:
                data["brightness"] = new_brightness
        elif self._brightness is None or self._brightness == 0:
            # Device is off, set to last known brightness
            data["brightness"] = self._last_brightness

        # Only send RGB if it's being changed
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            if self._rgb_color != rgb:
                data["red"] = rgb[0]
                data["green"] = rgb[1]
                data["blue"] = rgb[2]
        elif self._rgb_color is None:
            # No color set yet, use default white
            data["red"] = 255
            data["green"] = 255
            data["blue"] = 255

        # Only send enabled if device is currently off
        if not self._state:
            data["enabled"] = True

        # Only send if there are changes
        if data:
            await self._send_update(data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        # Only send enabled=false if device is currently on
        if self._state:
            data = {"enabled": False}
            await self._send_update(data)

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):  # Reduced timeout to 5 seconds
                async with session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        self._brightness = data.get("brightness", 0)
                        # Store last non-zero brightness for restoration
                        if self._brightness > 0:
                            self._last_brightness = self._brightness
                        self._rgb_color = (
                            data.get("red", 255),
                            data.get("green", 255),
                            data.get("blue", 255)
                        )
                        # Use enabled state from firmware
                        self._state = data.get("enabled", self._brightness > 0)
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.debug("WordClock returned status %s", response.status)
        except asyncio.TimeoutError:
            # Device is likely powered off or unreachable
            if self._available:  # Only log once when becoming unavailable
                _LOGGER.info("WordClock at %s is not responding (device may be powered off)", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            # Network errors
            if self._available:  # Only log once when becoming unavailable
                _LOGGER.info("WordClock at %s is unreachable: %s", self._host, err)
            self._available = False

    async def _send_update(self, data: dict[str, Any]) -> None:
        """Send update to WordClock."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):  # Reduced timeout to 5 seconds
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        # Store last non-zero brightness for restoration
                        if "brightness" in data and data["brightness"] > 0:
                            self._last_brightness = data["brightness"]

                        # Update current state with what was sent
                        if "brightness" in data:
                            self._brightness = data["brightness"]
                        if "red" in data and "green" in data and "blue" in data:
                            self._rgb_color = (data["red"], data["green"], data["blue"])
                        if "enabled" in data:
                            self._state = data["enabled"]
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.warning("Failed to update WordClock: HTTP %s", response.status)
        except asyncio.TimeoutError:
            # Device is likely powered off or unreachable
            if self._available:  # Only log once when becoming unavailable
                _LOGGER.info("WordClock at %s not responding to update (device may be powered off)", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            # Network errors
            if self._available:  # Only log once when becoming unavailable
                _LOGGER.info("Cannot send update to WordClock at %s: %s", self._host, err)
            self._available = False