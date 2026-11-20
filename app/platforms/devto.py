from .base import PlatformAdapter, PlatformError


class DevToAdapter(PlatformAdapter):
    name = "DEV"

    def __init__(self, client, api_key: str | None):
        super().__init__(client)
        self.api_key = api_key

    async def post(self, message: str) -> str:
        if not self.api_key:
            raise PlatformError("DEV API key is not configured")
        response = await self.client.post(
            "https://dev.to/api/articles",
            headers={"api-key": self.api_key},
            json={"article": {"title": message[:80], "body_markdown": message, "published": False}},
        )
        if response.is_error:
            raise PlatformError(f"DEV post failed ({response.status_code})")
        return response.json()["url"]
