"""Uhome Base Entity."""

from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UhomeUpdateCoordinator
from .uhome_api import UhomeDevice

_LOGGER = logging.getLogger(__name__)


class UhomeEntity(CoordinatorEntity[UhomeUpdateCoordinator]):
    """Representation of a base U home Entity."""

    def __init__(
        self, coordinator: UhomeUpdateCoordinator, device: UhomeDevice
    ) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, device.id)
        self._device = device
        mac = device.id.split(":")
        self._attr_unique_id = f"{device.category}{mac[3]}{mac[4]}{mac[5]}"
        if self.device_class:
            self._attr_unique_id += f"_{self.device_class}"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._device.id)},
            "name": self._device.name,
            "manufacturer": self._device.device_info.manufacturer,
            "model": self._device.device_info.model,
            "hw_version": self._device.device_info.hardware_version,
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.status == "Online"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
        # Some devices will set assumed_state while waiting for the refresh
        self._device.assumed_state = False
