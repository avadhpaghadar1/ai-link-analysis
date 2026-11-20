from .base import PlatformAdapter, PlatformError


class MastodonAdapter(PlatformAdapter):
    name = "Mastodon"

    def __init__(self, client, base_url: str, access_token: str | None):
        super().__init__(client)
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token

    async def post(self, message: str) -> str:
        if not self.access_token:
            raise PlatformError("Mastodon credentials are not configured")
        response = await self.client.post(
            f"{self.base_url}/api/v1/statuses",
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"status": message, "visibility": "public"},
        )
        if response.is_error:
            raise PlatformError(f"Mastodon post failed ({response.status_code})")
        data = response.json()
        return data["url"]
