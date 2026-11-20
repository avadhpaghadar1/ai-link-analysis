from .base import PlatformAdapter, PlatformError


class BlueskyAdapter(PlatformAdapter):
    name = "Bluesky"

    def __init__(self, client, identifier: str | None, app_password: str | None):
        super().__init__(client)
        self.identifier = identifier
        self.app_password = app_password

    async def post(self, message: str) -> str:
        if not self.identifier or not self.app_password:
            raise PlatformError("Bluesky credentials are not configured")
        session = await self.client.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": self.identifier, "password": self.app_password},
        )
        if session.is_error:
            raise PlatformError(f"Bluesky authentication failed ({session.status_code})")
        data = session.json()
        record = await self.client.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {data['accessJwt']}"},
            json={
                "repo": data["did"],
                "collection": "app.bsky.feed.post",
                "record": {"$type": "app.bsky.feed.post", "text": message, "createdAt": _now_iso()},
            },
        )
        if record.is_error:
            raise PlatformError(f"Bluesky post failed ({record.status_code})")
        uri = record.json()["uri"]
        rkey = uri.rsplit("/", 1)[-1]
        return f"https://bsky.app/profile/{data['handle']}/post/{rkey}"


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
