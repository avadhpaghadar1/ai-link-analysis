from .base import PlatformAdapter, PlatformError


class LinkedInAdapter(PlatformAdapter):
    name = "LinkedIn"

    def __init__(self, client, access_token: str | None, author_urn: str | None):
        super().__init__(client)
        self.access_token = access_token
        self.author_urn = author_urn

    async def post(self, message: str) -> str:
        if not self.access_token or not self.author_urn:
            raise PlatformError("LinkedIn credentials or author URN are not configured")
        response = await self.client.post(
            "https://api.linkedin.com/rest/posts",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "LinkedIn-Version": "202401",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
            },
            json={
                "author": self.author_urn,
                "commentary": message,
                "visibility": "PUBLIC",
                "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            },
        )
        if response.is_error:
            raise PlatformError(f"LinkedIn post failed ({response.status_code})")
        post_id = response.headers.get("x-restli-id")
        if not post_id:
            raise PlatformError("LinkedIn did not return a post identifier")
        return f"https://www.linkedin.com/feed/update/{post_id}/"
