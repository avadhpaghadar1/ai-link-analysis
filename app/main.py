from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.config import get_settings
from app.platforms.bluesky import BlueskyAdapter
from app.platforms.devto import DevToAdapter
from app.platforms.linkedin import LinkedInAdapter
from app.platforms.mastodon import MastodonAdapter
from app.platforms.reddit import RedditAdapter
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True) as client:
        app.state.posting_service = PostingService([
            BlueskyAdapter(client, settings.bluesky_identifier, settings.bluesky_app_password),
            MastodonAdapter(client, settings.mastodon_base_url, settings.mastodon_access_token),
            RedditAdapter(client, settings.reddit_client_id, settings.reddit_client_secret, settings.reddit_username,
                          settings.reddit_password, settings.reddit_subreddit),
            DevToAdapter(client, settings.dev_api_key),
            LinkedInAdapter(client, settings.linkedin_access_token, settings.linkedin_author_urn),
        ])
        yield


app = FastAPI(title="Automated Multi-Platform Posting System", version="1.0.0", lifespan=lifespan)


@app.post("/posting", response_model=PostingResponse)
async def create_posting(request: PostingRequest) -> PostingResponse:
    results = await app.state.posting_service.post_to_all(request.message)
    return PostingResponse(success=any(result.status == "success" for result in results), results=results)
