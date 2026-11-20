from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import PlatformAdapter, PlatformError
from app.schemas import PostingRequest
from app.services.posting_service import PostingService


class SuccessfulAdapter(PlatformAdapter):
    name = "Working"

    async def post(self, message: str) -> str:
        return "https://example.com/post/1"


class FailingAdapter(PlatformAdapter):
    name = "Broken"

    async def post(self, message: str) -> str:
        raise PlatformError("test failure")


def test_message_requires_exactly_one_valid_url():
    with pytest.raises(ValueError):
        PostingRequest(message="no link")
    with pytest.raises(ValueError):
        PostingRequest(message="https://one.example https://two.example")
    request = PostingRequest(message="Read this: https://example.com/product")
    assert request.message.endswith("/product")


@pytest.mark.asyncio
async def test_one_platform_failure_does_not_stop_other_platforms():
    service = PostingService([SuccessfulAdapter(None), FailingAdapter(None)])
    results = await service.post_to_all("Read this: https://example.com/product")
    assert [result.status for result in results] == ["success", "failed"]
    assert str(results[0].posted_url) == "https://example.com/post/1"
    assert results[1].error == "test failure"


def test_endpoint_rejects_invalid_message():
    with TestClient(app) as client:
        response = client.post("/posting", json={"message": "missing CTA"})
    assert response.status_code == 422
