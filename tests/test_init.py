from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.endurain.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, DOMAIN

MOCK_CONFIG = {
    CONF_URL: "http://endurain.local:8000",
    CONF_USERNAME: "testuser",
    CONF_PASSWORD: "testpass",
}

MOCK_USER = {"id": 1, "name": "Test User"}

MOCK_DATA = {
    "user": MOCK_USER,
    "last_activity": None,
    "weekly_distances": {},
    "monthly_distances": {},
    "latest_weight": None,
    "latest_steps": None,
    "latest_sleep": None,
}


@pytest.fixture
def mock_api():
    with patch("custom_components.endurain.EndurainApiClient") as mock_cls:
        client = mock_cls.return_value
        client.authenticate = AsyncMock()
        client.get_user_me = AsyncMock(return_value=MOCK_USER)
        client.get_last_activity = AsyncMock(return_value=None)
        client.get_weekly_distances = AsyncMock(return_value={})
        client.get_monthly_distances = AsyncMock(return_value={})
        client.get_latest_weight = AsyncMock(return_value=None)
        client.get_latest_steps = AsyncMock(return_value=None)
        client.get_latest_sleep = AsyncMock(return_value=None)
        yield client


async def test_setup_entry(hass: HomeAssistant, mock_api) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.LOADED


async def test_unload_entry(hass: HomeAssistant, mock_api) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED


try:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
except ImportError:
    from unittest.mock import MagicMock
    MockConfigEntry = MagicMock
