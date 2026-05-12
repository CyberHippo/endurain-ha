from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EndurainApiClient, EndurainAuthError, EndurainConnectionError
from .const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, DOMAIN
from .coordinator import EndurainCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

type EndurainConfigEntry = ConfigEntry[EndurainCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: EndurainConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = EndurainApiClient(entry.data[CONF_URL], session)

    try:
        await client.authenticate(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    except EndurainAuthError as err:
        raise ConfigEntryAuthFailed(err) from err
    except EndurainConnectionError as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = EndurainCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EndurainConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
