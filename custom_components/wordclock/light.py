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
        
        if ATTR_BRIGHTNESS in kwargs:
            # Convert HA brightness (0-255) to WordClock brightness (0-255)
            data["brightness"] = kwargs[ATTR_BRIGHTNESS]
        elif self._brightness is None or self._brightness == 0:
            # Default brightness if not set or currently off
            data["brightness"] = 128
        else:
            # Keep current brightness
            data["brightness"] = self._brightness

        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            data["red"] = rgb[0]
            data["green"] = rgb[1] 
            data["blue"] = rgb[2]
        elif self._rgb_color is not None:
            # Keep current color
            data["red"] = self._rgb_color[0]
            data["green"] = self._rgb_color[1]
            data["blue"] = self._rgb_color[2]
        else:
            # Default white color
            data["red"] = 255
            data["green"] = 255
            data["blue"] = 255

        # Always include language (keep current or default)
        data["language"] = "dialekt"

        await self._send_update(data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        data = {
            "brightness": 0,
            "red": self._rgb_color[0] if self._rgb_color else 255,
            "green": self._rgb_color[1] if self._rgb_color else 255,
            "blue": self._rgb_color[2] if self._rgb_color else 255,
            "language": "dialekt"
        }
        await self._send_update(data)

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                async with session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        self._brightness = data.get("brightness", 0)
                        self._rgb_color = (
                            data.get("red", 255),
                            data.get("green", 255),
                            data.get("blue", 255)
                        )
                        self._state = self._brightness > 0
                        self._available = True
                    else:
                        self._available = False
        except (aiohttp.ClientError, asyncio.TimeoutError):
            self._available = False
            _LOGGER.warning("Error updating WordClock status")

    async def _send_update(self, data: dict[str, Any]) -> None:
        """Send update to WordClock."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self._brightness = data["brightness"]
                        self._rgb_color = (data["red"], data["green"], data["blue"])
                        self._state = self._brightness > 0
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.error("Failed to update WordClock: %s", response.status)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            self._available = False
            _LOGGER.error("Error sending update to WordClock")