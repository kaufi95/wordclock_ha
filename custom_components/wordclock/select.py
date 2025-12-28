"""Platform for select integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]

    async_add_entities([
        WordClockTransitionSelect(hass, host, name),
        WordClockPrefixModeSelect(hass, host, name),
        WordClockLanguageSelect(hass, host, name),
    ], True)


class WordClockTransitionSelect(SelectEntity):
    """Representation of WordClock transition animation selector."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._host = host
        self._name = name
        self._current_option = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Transition"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wordclock_transition"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self._current_option

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(TRANSITION_OPTIONS.values())

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

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

        try:
            session = async_get_clientsession(self.hass)
            data = {"transition": transition_value}
            async with async_timeout.timeout(5):
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self._current_option = option
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.warning("Failed to update transition: HTTP %s", response.status)
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s not responding to update", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("Cannot send update to WordClock at %s: %s", self._host, err)
            self._available = False

    async def async_update(self) -> None:
        """Fetch new state data."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):
                async with session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        transition_value = data.get("transition")
                        if transition_value is not None:
                            self._current_option = TRANSITION_OPTIONS.get(transition_value)
                        self._available = True
                    else:
                        self._available = False
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s is not responding", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("WordClock at %s is unreachable: %s", self._host, err)
            self._available = False


class WordClockPrefixModeSelect(SelectEntity):
    """Representation of WordClock prefix mode selector."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._host = host
        self._name = name
        self._current_option = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Prefix Mode"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wordclock_prefix_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self._current_option

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(PREFIX_MODE_OPTIONS.values())

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

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

        try:
            session = async_get_clientsession(self.hass)
            data = {"prefixMode": prefix_mode_value}
            async with async_timeout.timeout(5):
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self._current_option = option
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.warning("Failed to update prefix mode: HTTP %s", response.status)
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s not responding to update", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("Cannot send update to WordClock at %s: %s", self._host, err)
            self._available = False

    async def async_update(self) -> None:
        """Fetch new state data."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):
                async with session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        prefix_mode_value = data.get("prefixMode")
                        if prefix_mode_value is not None:
                            self._current_option = PREFIX_MODE_OPTIONS.get(prefix_mode_value)
                        self._available = True
                    else:
                        self._available = False
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s is not responding", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("WordClock at %s is unreachable: %s", self._host, err)
            self._available = False


class WordClockLanguageSelect(SelectEntity):
    """Representation of WordClock language selector."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._host = host
        self._name = name
        self._current_option = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Language"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wordclock_language"

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self._current_option

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(LANGUAGE_OPTIONS.values())

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

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

        try:
            session = async_get_clientsession(self.hass)
            data = {"language": language_value}
            async with async_timeout.timeout(5):
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self._current_option = option
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.warning("Failed to update language: HTTP %s", response.status)
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s not responding to update", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("Cannot send update to WordClock at %s: %s", self._host, err)
            self._available = False

    async def async_update(self) -> None:
        """Fetch new state data."""
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):
                async with session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        language_value = data.get("language")
                        if language_value is not None:
                            self._current_option = LANGUAGE_OPTIONS.get(language_value)
                        self._available = True
                    else:
                        self._available = False
        except asyncio.TimeoutError:
            if self._available:
                _LOGGER.info("WordClock at %s is not responding", self._host)
            self._available = False
        except aiohttp.ClientError as err:
            if self._available:
                _LOGGER.info("WordClock at %s is unreachable: %s", self._host, err)
            self._available = False
