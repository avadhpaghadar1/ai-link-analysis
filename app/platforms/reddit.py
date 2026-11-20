from .base import PlatformAdapter, PlatformError


class RedditAdapter(PlatformAdapter):
    name = "Reddit"

    def __init__(self, client, client_id, client_secret, username, password, subreddit):
        super().__init__(client)
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.subreddit = subreddit

    async def post(self, message: str) -> str:
        if not all((self.client_id, self.client_secret, self.username, self.password, self.subreddit)):
            raise PlatformError("Reddit credentials or subreddit are not configured")
        token = await self.client.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "password", "username": self.username, "password": self.password},
            headers={"User-Agent": "automated-posting-system/1.0"},
        )
        if token.is_error:
            raise PlatformError(f"Reddit authentication failed ({token.status_code})")
        access_token = token.json().get("access_token")
        result = await self.client.post(
            "https://oauth.reddit.com/api/submit",
            headers={"Authorization": f"Bearer {access_token}", "User-Agent": "automated-posting-system/1.0"},
            data={"sr": self.subreddit, "kind": "self", "title": message[:80], "text": message, "resubmit": "true"},
        )
        if result.is_error:
            raise PlatformError(f"Reddit post failed ({result.status_code})")
        data = result.json()["json"]["data"]
        return f"https://www.reddit.com{data['url']}"
