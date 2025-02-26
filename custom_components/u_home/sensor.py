"""Platform for Uhome lock integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from .entity import UhomeEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the lock entries."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            UhomeBatterySensor(coordinator, device)
            for device in coordinator.devices
            if hasattr(device, "battery_status")
        ]
    )


class UhomeBatterySensor(UhomeEntity, SensorEntity):
    """Representation of a Uhome lock battery sensor."""

    def __init__(self, coordinator, device) -> None:
        """Pass coordinator to CoordinatorEntity."""
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 0
        super().__init__(coordinator, device)

    @property
    def native_value(self) -> float:
        """Return the battery level."""
        max_battery_level = float(self._device.battery_status.max)
        return float(self._device.battery_status.level) * (100.0 / max_battery_level)
