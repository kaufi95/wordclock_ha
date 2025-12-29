"""WordClock data update coordinator using Server-Sent Events."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

RECONNECT_DELAY = 5  # seconds


class WordClockCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage WordClock SSE connection and state updates."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"WordClock {name}",
            update_interval=None,  # We don't use polling, only SSE events
        )
        self._host = host
        self._session: aiohttp.ClientSession = async_get_clientsession(hass)
        self._sse_task: asyncio.Task | None = None
        self._shutdown = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint (fallback method)."""
        try:
            async with async_timeout.timeout(5):
                async with self._session.get(f"http://{self._host}/status") as response:
                    if response.status == 200:
                        return await response.json()
                    raise UpdateFailed(f"Error fetching data: {response.status}")
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout fetching data") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_start(self) -> None:
        """Start the SSE listener."""
        # Get initial state
        await self.async_refresh()

        # Start SSE listener
        self._shutdown = False
        self._sse_task = asyncio.create_task(self._listen_sse())

    async def async_stop(self) -> None:
        """Stop the SSE listener."""
        self._shutdown = True
        if self._sse_task:
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
            self._sse_task = None

    async def _listen_sse(self) -> None:
        """Listen to Server-Sent Events from the wordclock."""
        while not self._shutdown:
            try:
                _LOGGER.info("Connecting to SSE endpoint at http://%s/events", self._host)
                async with self._session.get(
                    f"http://{self._host}/events",
                    headers={
                        "Accept": "text/event-stream",
                        "Cache-Control": "no-cache",
                    },
                    timeout=aiohttp.ClientTimeout(total=None),  # No timeout for SSE
                ) as response:
                    if response.status != 200:
                        _LOGGER.warning(
                            "SSE connection failed with status %s, retrying in %s seconds",
                            response.status,
                            RECONNECT_DELAY,
                        )
                        await asyncio.sleep(RECONNECT_DELAY)
                        continue

                    _LOGGER.info("Successfully connected to WordClock SSE stream at %s", self._host)

                    # Read SSE stream line by line
                    event_type = None
                    event_data = None

                    async for line in response.content:
                        if self._shutdown:
                            break

                        line = line.decode("utf-8").rstrip("\r\n")

                        _LOGGER.debug("SSE raw line: %r", line)

                        # Empty line signals end of event
                        if not line:
                            if event_data:
                                try:
                                    import json
                                    data = json.loads(event_data)
                                    _LOGGER.info("Received SSE event (type=%s): %s", event_type, data)

                                    # Update coordinator data and notify listeners
                                    self.async_set_updated_data(data)

                                except json.JSONDecodeError as err:
                                    _LOGGER.warning("Failed to parse SSE data: %s - Data was: %s", err, event_data)

                                # Reset for next event
                                event_type = None
                                event_data = None
                            continue

                        # Parse SSE fields
                        if line.startswith("event:"):
                            event_type = line[6:].strip()
                        elif line.startswith("data:"):
                            event_data = line[5:].strip()

            except aiohttp.ClientError as err:
                if not self._shutdown:
                    _LOGGER.warning(
                        "SSE connection error: %s, retrying in %s seconds",
                        err,
                        RECONNECT_DELAY,
                    )
                    await asyncio.sleep(RECONNECT_DELAY)
            except asyncio.CancelledError:
                _LOGGER.debug("SSE listener cancelled")
                raise
            except Exception as err:
                if not self._shutdown:
                    _LOGGER.exception("Unexpected error in SSE listener: %s", err)
                    await asyncio.sleep(RECONNECT_DELAY)

        _LOGGER.debug("SSE listener stopped")

    async def async_send_update(self, data: dict[str, Any]) -> bool:
        """Send update to WordClock."""
        try:
            async with async_timeout.timeout(5):
                async with self._session.post(
                    f"http://{self._host}/update",
                    json=data,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        # SSE will update us, but we can optimistically update
                        # to avoid UI lag
                        current_data = self.data or {}
                        updated_data = {**current_data, **data}
                        self.async_set_updated_data(updated_data)
                        return True
                    _LOGGER.warning("Failed to update WordClock: HTTP %s", response.status)
                    return False
        except asyncio.TimeoutError:
            _LOGGER.info("WordClock at %s not responding to update", self._host)
            return False
        except aiohttp.ClientError as err:
            _LOGGER.info("Cannot send update to WordClock at %s: %s", self._host, err)
            return False
