from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_PATH = "/api/v1"
# Web client: login returns access_token + refresh_token in body directly (no PKCE exchange needed)
CLIENT_TYPE_HEADER = {"X-Client-Type": "web"}


class EndurainAuthError(Exception):
    pass


class EndurainConnectionError(Exception):
    pass


class EndurainApiClient:
    def __init__(self, url: str, session: aiohttp.ClientSession) -> None:
        self._base = url.rstrip("/") + API_PATH
        self._session = session
        self._access_token: str | None = None
        self._refresh_token: str | None = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    async def authenticate(self, username: str, password: str) -> None:
        url = f"{self._base}/auth/login"
        data = {"username": username, "password": password}
        try:
            async with self._session.post(
                url, data=data, headers=CLIENT_TYPE_HEADER
            ) as resp:
                if resp.status in (401, 403):
                    raise EndurainAuthError("Invalid credentials")
                resp.raise_for_status()
                body = await resp.json()
                # Web login returns access_token directly; refresh token is in a cookie
                self._access_token = body["access_token"]
                # Store CSRF token for refresh calls if present
                self._csrf_token = body.get("csrf_token")
        except aiohttp.ClientConnectionError as err:
            raise EndurainConnectionError(str(err)) from err

    async def _refresh(self) -> None:
        url = f"{self._base}/auth/refresh"
        headers = {**CLIENT_TYPE_HEADER}
        if self._csrf_token:
            headers["X-CSRF-Token"] = self._csrf_token
        try:
            async with self._session.post(url, headers=headers) as resp:
                if resp.status in (401, 403):
                    raise EndurainAuthError("Refresh token expired")
                resp.raise_for_status()
                body = await resp.json()
                self._access_token = body["access_token"]
                self._csrf_token = body.get("csrf_token", self._csrf_token)
        except aiohttp.ClientConnectionError as err:
            raise EndurainConnectionError(str(err)) from err

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------

    async def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self._base}{path}"
        headers = {**CLIENT_TYPE_HEADER, "Authorization": f"Bearer {self._access_token}"}
        try:
            async with self._session.get(url, headers=headers, params=params) as resp:
                if resp.status == 401:
                    await self._refresh()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    async with self._session.get(
                        url, headers=headers, params=params
                    ) as retry:
                        retry.raise_for_status()
                        return await retry.json()
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientConnectionError as err:
            raise EndurainConnectionError(str(err)) from err

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    async def get_user_me(self) -> dict:
        return await self._get("/users/me")

    async def get_last_activity(self) -> dict | None:
        data = await self._get("/activities/", params={"page_num": 1, "num_records": 1})
        records = data.get("records") or []
        return records[0] if records else None

    async def get_weekly_distances(self) -> dict:
        return await self._get("/activities/distances/weekly")

    async def get_monthly_distances(self) -> dict:
        return await self._get("/activities/distances/monthly")

    async def get_latest_weight(self) -> dict | None:
        data = await self._get("/health/weight/", params={"page_num": 1, "num_records": 1})
        records = data.get("records") or []
        return records[0] if records else None

    async def get_latest_steps(self) -> dict | None:
        data = await self._get("/health/steps/", params={"page_num": 1, "num_records": 1})
        records = data.get("records") or []
        return records[0] if records else None

    async def get_latest_sleep(self) -> dict | None:
        data = await self._get("/health/sleep/", params={"page_num": 1, "num_records": 1})
        records = data.get("records") or []
        return records[0] if records else None
