"""The WordClock integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, Platform
from homeassistant.core import HomeAssistant

from .coordinator import WordClockCoordinator

DOMAIN = "wordclock"
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WordClock from a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    # Create coordinator
    coordinator = WordClockCoordinator(hass, host, name)

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start SSE listener
    await coordinator.async_start()

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop SSE listener
    coordinator: WordClockCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_stop()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok