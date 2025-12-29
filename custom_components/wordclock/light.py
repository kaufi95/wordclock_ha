"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import WordClockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WordClock Light platform."""
    coordinator: WordClockCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    name = config_entry.data[CONF_NAME]

    async_add_entities([WordClockLight(coordinator, name)])


class WordClockLight(CoordinatorEntity, LightEntity):
    """Representation of a WordClock Light."""

    def __init__(self, coordinator: WordClockCoordinator, name: str) -> None:
        """Initialize a WordClock Light."""
        super().__init__(coordinator)
        self._name = name
        self._last_brightness = 128  # Store last brightness (in range 1-255)

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator._host}_wordclock"

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data is None:
            return None
        # WordClock uses 1-255 range, same as HA
        brightness = self.coordinator.data.get("brightness", 0)
        if brightness > 0:
            self._last_brightness = brightness
        return brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the RGB color value."""
        if self.coordinator.data is None:
            return None
        return (
            self.coordinator.data.get("red", 255),
            self.coordinator.data.get("green", 255),
            self.coordinator.data.get("blue", 255),
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("enabled", self.brightness and self.brightness > 0)

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        return ColorMode.RGB

    @property
    def supported_color_modes(self) -> set[str]:
        """Flag supported color modes."""
        return {ColorMode.RGB}

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        attributes = {}
        if (transition := self.coordinator.data.get("transition")) is not None:
            attributes["transition"] = transition
        if (prefix_mode := self.coordinator.data.get("prefixMode")) is not None:
            attributes["prefix_mode"] = prefix_mode
        if (transition_speed := self.coordinator.data.get("transitionSpeed")) is not None:
            attributes["transition_speed"] = transition_speed
        if (language := self.coordinator.data.get("language")) is not None:
            attributes["language"] = language
        if (superbright := self.coordinator.data.get("superBright")) is not None:
            attributes["superbright"] = superbright
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        data = {}
        current_brightness = self.brightness
        current_rgb = self.rgb_color

        # Only send brightness if it's being changed
        if ATTR_BRIGHTNESS in kwargs:
            # WordClock uses 1-255 range, same as HA
            new_brightness = kwargs[ATTR_BRIGHTNESS]
            brightness = max(1, min(255, new_brightness))  # Clamp to 1-255
            if new_brightness != current_brightness:
                data["brightness"] = brightness
        elif current_brightness is None or current_brightness == 0:
            # Device is off, set to last known brightness
            data["brightness"] = self._last_brightness

        # Only send RGB if it's being changed
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            if current_rgb != rgb:
                data["red"] = rgb[0]
                data["green"] = rgb[1]
                data["blue"] = rgb[2]
        elif current_rgb is None:
            # No color set yet, use default white
            data["red"] = 255
            data["green"] = 255
            data["blue"] = 255

        # Only send enabled if device is currently off
        if not self.is_on:
            data["enabled"] = True

        # Only send if there are changes
        if data:
            await self.coordinator.async_send_update(data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        # Only send enabled=false if device is currently on
        if self.is_on:
            data = {"enabled": False}
            await self.coordinator.async_send_update(data)