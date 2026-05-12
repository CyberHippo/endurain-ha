from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EndurainApiClient, EndurainAuthError, EndurainConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EndurainCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: EndurainApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            # user must be fetched first — it populates _user_id used by all other calls
            user = await self.client.get_user_me()
        except EndurainAuthError as err:
            raise ConfigEntryAuthFailed from err
        except EndurainConnectionError as err:
            raise UpdateFailed(f"Cannot connect to Endurain: {err}") from err

        results = await asyncio.gather(
            self.client.get_last_activity(),
            self.client.get_weekly_distances(),
            self.client.get_monthly_distances(),
            self.client.get_latest_weight(),
            self.client.get_latest_steps(),
            self.client.get_latest_sleep(),
            return_exceptions=True,
        )

        keys = (
            "last_activity",
            "weekly_distances",
            "monthly_distances",
            "latest_weight",
            "latest_steps",
            "latest_sleep",
        )

        data: dict[str, Any] = {"user": user}
        for key, result in zip(keys, results):
            if isinstance(result, EndurainAuthError):
                raise ConfigEntryAuthFailed from result
            if isinstance(result, Exception):
                _LOGGER.warning("Failed to fetch %s: %s", key, result)
                data[key] = None
            else:
                data[key] = result

        return data
