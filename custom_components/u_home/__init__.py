"""The U home integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow

from .coordinator import UhomeUpdateCoordinator
from .uhome_api import UhomeAPI

_PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[UhomeAPI]
) -> bool:
    """Set up the U home integration from the config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, config_entry
        )
    )

    oauth2_session = config_entry_oauth2_flow.OAuth2Session(
        hass, config_entry, implementation
    )

    uhome_api = UhomeAPI(aiohttp_client.async_get_clientsession(hass), oauth2_session)
    coordinator = UhomeUpdateCoordinator(hass, config_entry, uhome_api)
    config_entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: ConfigEntry[UhomeAPI]
) -> bool:
    """Unload the U home integration."""
    return await hass.config_entries.async_unload_platforms(config_entry, _PLATFORMS)
