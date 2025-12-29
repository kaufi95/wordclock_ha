"""Platform for switch integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up the WordClock Switch platform."""
    coordinator: WordClockCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    name = config_entry.data[CONF_NAME]

    async_add_entities([WordClockSuperBrightSwitch(coordinator, name)])


class WordClockSuperBrightSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of WordClock Super Bright mode switch."""

    def __init__(self, coordinator: WordClockCoordinator, name: str) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._name = name

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Super Bright"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator._host}_wordclock_superbright"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("superBright", False)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb-outline"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        data = {"superBright": True}
        await self.coordinator.async_send_update(data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        data = {"superBright": False}
        await self.coordinator.async_send_update(data)
