"""Platform for select integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import WordClockCoordinator

_LOGGER = logging.getLogger(__name__)

TRANSITION_OPTIONS = {
    0: "None",
    1: "Fade",
    2: "Wipe",
    3: "Sparkle"
}

PREFIX_MODE_OPTIONS = {
    0: "Always",
    1: "Random",
    2: "Off"
}

LANGUAGE_OPTIONS = {
    "dialekt": "Dialekt",
    "deutsch": "Deutsch"
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WordClock Select platform."""
    coordinator: WordClockCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    name = config_entry.data[CONF_NAME]

    async_add_entities([
        WordClockTransitionSelect(coordinator, name),
        WordClockPrefixModeSelect(coordinator, name),
        WordClockLanguageSelect(coordinator, name),
    ])


class WordClockTransitionSelect(CoordinatorEntity, SelectEntity):
    """Representation of WordClock transition animation selector."""

    def __init__(self, coordinator: WordClockCoordinator, name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._name = name

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Transition"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator._host}_wordclock_transition"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data is None:
            return None
        transition_value = self.coordinator.data.get("transition")
        if transition_value is not None:
            return TRANSITION_OPTIONS.get(transition_value)
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(TRANSITION_OPTIONS.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the key for the selected option
        transition_value = None
        for key, value in TRANSITION_OPTIONS.items():
            if value == option:
                transition_value = key
                break

        if transition_value is None:
            _LOGGER.error("Invalid transition option: %s", option)
            return

        data = {"transition": transition_value}
        await self.coordinator.async_send_update(data)


class WordClockPrefixModeSelect(CoordinatorEntity, SelectEntity):
    """Representation of WordClock prefix mode selector."""

    def __init__(self, coordinator: WordClockCoordinator, name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._name = name

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Prefix Mode"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator._host}_wordclock_prefix_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data is None:
            return None
        prefix_mode_value = self.coordinator.data.get("prefixMode")
        if prefix_mode_value is not None:
            return PREFIX_MODE_OPTIONS.get(prefix_mode_value)
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(PREFIX_MODE_OPTIONS.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the key for the selected option
        prefix_mode_value = None
        for key, value in PREFIX_MODE_OPTIONS.items():
            if value == option:
                prefix_mode_value = key
                break

        if prefix_mode_value is None:
            _LOGGER.error("Invalid prefix mode option: %s", option)
            return

        data = {"prefixMode": prefix_mode_value}
        await self.coordinator.async_send_update(data)


class WordClockLanguageSelect(CoordinatorEntity, SelectEntity):
    """Representation of WordClock language selector."""

    def __init__(self, coordinator: WordClockCoordinator, name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._name = name

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Language"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator._host}_wordclock_language"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data is None:
            return None
        language_value = self.coordinator.data.get("language")
        if language_value is not None:
            return LANGUAGE_OPTIONS.get(language_value)
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(LANGUAGE_OPTIONS.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the key for the selected option
        language_value = None
        for key, value in LANGUAGE_OPTIONS.items():
            if value == option:
                language_value = key
                break

        if language_value is None:
            _LOGGER.error("Invalid language option: %s", option)
            return

        data = {"language": language_value}
        await self.coordinator.async_send_update(data)
