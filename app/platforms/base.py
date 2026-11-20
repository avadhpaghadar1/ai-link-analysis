from abc import ABC, abstractmethod

import httpx


class PlatformError(Exception):
    """An expected failure returned by a platform API."""


class PlatformAdapter(ABC):
    name: str

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def post(self, message: str) -> str:
        """Publish a message and return its public URL."""
