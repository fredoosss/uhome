"""Application credentials platform for the U home integration."""

from __future__ import annotations

from uhomepy import AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT

from homeassistant.components.application_credentials import AuthorizationServer
from homeassistant.core import HomeAssistant


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url=AUTHORIZE_ENDPOINT,
        token_url=TOKEN_ENDPOINT,
    )
