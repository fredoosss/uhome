"""API for Uhome bound to Home Assistant OAuth."""

from __future__ import annotations

import datetime
import logging

from aiohttp import ClientSession
from uhomepy import UhomeOpenAPI

from homeassistant.helpers import config_entry_oauth2_flow

_LOGGER = logging.getLogger(__name__)


class UhomeDeviceInfo:
    """Represents the Uhome deviceInfo."""

    def __init__(self, device_info: dict) -> None:
        """Normalize the properties into Python names."""
        self.manufacturer = device_info["manufacturer"]
        self.model = device_info["model"]
        self.hardware_version = device_info["hwVersion"]


class UhomeDeviceBatteryStatus:
    """Represents a Uhome BatteryLevelRange and st.batteryLevel."""

    def __init__(self, battery_info: dict) -> None:
        """Normalize the properties into Python names."""
        self.min = battery_info["min"]
        self.max = battery_info["max"]
        self.step = battery_info["step"]
        self.level = None  # st.batteryLevel

    def update_state(self, states: dict) -> None:
        """Update the battery state."""
        self.level = next(
            (
                state["value"]
                for state in states
                if state["capability"] == "st.batteryLevel"
            ),
            None,
        )


class UhomeDevice:
    """Represent a Uhome base device."""

    def __init__(self, device: dict) -> None:
        """Normalize the properties into Python names."""
        self.id = device["id"]
        self.name = device["name"]
        self.category = device["category"]
        self.device_info = UhomeDeviceInfo(device["deviceInfo"])
        self.status = None  # st.healthCheck

    def update_state(self, states: dict) -> None:
        """Update the device state."""
        self.status = next(
            (
                state["value"]
                for state in states
                if state["capability"] == "st.healthCheck"
            ),
            None,
        )


class UhomeSmartLock(UhomeDevice):
    """Represent a Uhome device of category SmartLock."""

    def __init__(self, device: dict) -> None:
        """Normalize the properties into Python names."""
        if device["category"] != "SmartLock":
            raise TypeError(f"Device {device['id']} is not a SmartLock")
        super().__init__(device)
        self.handle_type = device["handleType"]
        self.battery_status = UhomeDeviceBatteryStatus(
            device["attributes"]["batteryLevelRange"]
        )
        self.lock_state = None

    def update_state(self, states: dict) -> None:
        """Update the device state."""
        super().update_state(states)
        self.battery_status.update_state(states)
        self.lock_state = next(
            (state["value"] for state in states if state["capability"] == "st.lock"),
            None,
        )


class UhomeAPI(UhomeOpenAPI):
    """An implmentation of the UhomeOpenAPI that works for Home Assistant."""

    def __init__(
        self,
        session: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize Uhome auth."""
        super().__init__(session, "1")
        self._oauth_session = oauth_session

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()
        return self._oauth_session.token["access_token"]

    async def async_discover_devices(self) -> list[UhomeDevice]:
        """Call the discovery API and return the device array."""
        data = await super().async_discover_devices()
        payload = data.get("payload", {})
        devices = payload.get("devices", [])
        uhome_devices = []
        for device in devices:
            if device["category"] == "SmartLock":
                uhome_devices.append(UhomeSmartLock(device))
            else:
                uhome_devices.append(UhomeDevice(device))
            _LOGGER.info(
                "Discovered %s %s (%s)",
                device["category"],
                device["name"],
                device["id"],
            )
        return uhome_devices

    async def async_update_device_states(self, devices: list[UhomeDevice]) -> None:
        """Call the get API and return the device array."""
        device_ids = [device.id for device in devices]
        data = await self.async_query_devices(device_ids)
        payload = data.get("payload", {})
        for device in devices:
            for payload_device in payload.get("devices", []):
                if device.id == payload_device["id"]:
                    device.update_state(payload_device["states"])
                    _LOGGER.info(
                        "Updated device state for %s (%s): %s",
                        device.name,
                        device.id,
                        payload_device["states"],
                    )
                    break

    def _get_deferred_response(
        self, device: UhomeSmartLock, data: dict
    ) -> datetime.timedelta:
        """Return the deferred response time."""
        payload_devices = data.get("payload", {}).get("devices", [])
        states = next(
            (
                payload_device["states"]
                for payload_device in payload_devices
                if payload_device["id"] == device.id
            ),
            {},
        )
        deferred_response = next(
            (
                state["value"]
                for state in states
                if state["capability"] == "st.deferredResponse"
            ),
            None,
        )

        if deferred_response is None:
            pass  # THROW!

        return datetime.timedelta(seconds=deferred_response)

    async def async_lock_device(self, device: UhomeSmartLock) -> datetime.timedelta:
        """Lock the specified device."""
        data = await self.async_lock_devices([device.id])
        return self._get_deferred_response(device, data)

    async def async_unlock_device(self, device: UhomeSmartLock) -> datetime.timedelta:
        """Unlock the specified device."""
        data = await self.async_unlock_devices([device.id])
        return self._get_deferred_response(device, data)
