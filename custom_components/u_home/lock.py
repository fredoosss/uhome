"""Platform for Uhome lock integration."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import UhomeUpdateCoordinator
from .entity import UhomeEntity
from .uhome_api import UhomeAPI, UhomeSmartLock

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry[UhomeAPI], async_add_entities
):
    """Set up the lock entries."""
    coordinator = entry.runtime_data
    async_add_entities(
        UhomeLock(coordinator, device)
        for device in coordinator.devices
        if device.category == "SmartLock"
    )


class UhomeLock(UhomeEntity, LockEntity):
    """Representation of a Uhome lock."""

    def __init__(
        self, coordinator: UhomeUpdateCoordinator, device: UhomeSmartLock
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, device)
        self._attr_name = None

    @property
    def is_locked(self) -> bool:
        """Return the locked state."""
        return self._device.lock_state == "Locked"

    @property
    def is_unlocked(self) -> bool:
        """Return the unlocked state."""
        return self._device.lock_state == "Unlocked"

    @property
    def is_jammed(self) -> bool:
        """Return the jammed state."""
        return self._device.lock_state == "Jammed"

    async def async_lock(self, **kwargs) -> None:
        """Lock the device."""
        delta = await self.coordinator.uhome_api.async_lock_device(self._device)
        self._device.assumed_state = True
        self._device.lock_state = "Locked"
        self.async_write_ha_state()
        await asyncio.sleep(delta.total_seconds())
        await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs) -> None:
        """Unlock the device."""
        delta = await self.coordinator.uhome_api.async_unlock_device(self._device)
        self._device.assumed_state = True
        self._device.lock_state = "Unlocked"
        self.async_write_ha_state()
        await asyncio.sleep(delta.total_seconds())
        await self.coordinator.async_request_refresh()
