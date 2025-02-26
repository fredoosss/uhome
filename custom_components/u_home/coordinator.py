"""Data Coordinator for Uhome integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
from .uhome_api import UhomeAPI, UhomeDevice

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)


class UhomeUpdateCoordinator(DataUpdateCoordinator[list[UhomeDevice]]):
    """UhomeUpdateCoordinator implementation."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry[UhomeUpdateCoordinator],
        uhome_api: UhomeAPI,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="U home",
            config_entry=config_entry,
            update_interval=timedelta(
                minutes=config_entry.options.get(
                    CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                )
            ),
            always_update=True,
        )
        self.uhome_api = uhome_api
        self.devices = None

    async def _async_setup(self) -> None:
        """Fetch all devices from U home."""
        self.devices = await self.uhome_api.async_discover_devices()

    async def _async_update_data(self) -> list[UhomeDevice]:
        """Fetch state data for the U home devices."""
        await self.uhome_api.async_update_device_states(self.devices)
        return self.devices
