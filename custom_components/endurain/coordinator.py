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
            (
                user,
                last_activity,
                weekly,
                monthly,
                weight,
                steps,
                sleep,
            ) = await asyncio.gather(
                self.client.get_user_me(),
                self.client.get_last_activity(),
                self.client.get_weekly_distances(),
                self.client.get_monthly_distances(),
                self.client.get_latest_weight(),
                self.client.get_latest_steps(),
                self.client.get_latest_sleep(),
                return_exceptions=True,
            )
        except EndurainAuthError as err:
            raise ConfigEntryAuthFailed from err
        except EndurainConnectionError as err:
            raise UpdateFailed(f"Cannot connect to Endurain: {err}") from err

        def _unwrap(result: Any, name: str) -> Any:
            if isinstance(result, EndurainAuthError):
                raise ConfigEntryAuthFailed from result
            if isinstance(result, Exception):
                _LOGGER.warning("Failed to fetch %s: %s", name, result)
                return None
            return result

        return {
            "user": _unwrap(user, "user"),
            "last_activity": _unwrap(last_activity, "last_activity"),
            "weekly_distances": _unwrap(weekly, "weekly_distances"),
            "monthly_distances": _unwrap(monthly, "monthly_distances"),
            "latest_weight": _unwrap(weight, "latest_weight"),
            "latest_steps": _unwrap(steps, "latest_steps"),
            "latest_sleep": _unwrap(sleep, "latest_sleep"),
        }


