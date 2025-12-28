"""Platform for number integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.number import NumberEntity
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
    """Set up the WordClock Number platform."""
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]

    async_add_entities([WordClockTransitionSpeed(hass, host, name)], True)


class WordClockTransitionSpeed(NumberEntity):
    """Representation of WordClock transition speed control."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize the number entity."""
        self.hass = hass
        self._host = host
        self._name = name
        self._value = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the display name."""
        return f"{self._name} Transition Speed"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._host}_wordclock_transition_speed"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self._value

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return 0

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return 4

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return 1

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            session = async_get_clientsession(self.hass)
            data = {"transitionSpeed": int(value)}
            async with async_timeout.timeout(5):
                async with session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self._value = int(value)
                        self._available = True
                    else:
                        self._available = False
                        _LOGGER.warning("Failed to update transition speed: HTTP %s", response.status)
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
                        self._value = data.get("transitionSpeed")
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
