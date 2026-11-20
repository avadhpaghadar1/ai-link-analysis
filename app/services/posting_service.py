import asyncio
from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import PlatformAdapter, PlatformError
from app.schemas import PlatformResult


class PostingService:
    def __init__(self, adapters: list[PlatformAdapter]):
        self.adapters = adapters

    async def post_to_all(self, message: str) -> list[PlatformResult]:
        results = await asyncio.gather(*(self._post_one(adapter, message) for adapter in self.adapters))
        return list(results)

    async def _post_one(self, adapter: PlatformAdapter, message: str) -> PlatformResult:
        now = datetime.now(timezone.utc)
        try:
            url = await adapter.post(message)
            return PlatformResult(
                platform=adapter.name, status="success", posted_url=url, public_access=True,
                date=now.date(), time=now.time().replace(microsecond=0),
            )
        except (PlatformError, httpx.HTTPError, KeyError) as exc:
            return PlatformResult(
                platform=adapter.name, status="failed", posted_url=None, public_access=False,
                date=None, time=None, error=str(exc),
            )
