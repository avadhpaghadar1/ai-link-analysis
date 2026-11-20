from __future__ import annotations

import re
from datetime import date as date_type, time as time_type
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)


class PostingRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value

    @model_validator(mode="after")
    def require_one_cta_url(self) -> "PostingRequest":
        urls = URL_PATTERN.findall(self.message)
        if len(urls) != 1:
            raise ValueError("message must contain exactly one CTA URL")
        candidate = urls[0].rstrip(".,!?;:")
        parsed = urlparse(candidate)
        try:
            HttpUrl(candidate)
        except Exception as exc:
            raise ValueError("CTA URL must be a valid HTTP or HTTPS URL") from exc
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            raise ValueError("CTA URL must be a valid HTTP or HTTPS URL")
        return self


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: HttpUrl | None = None
    public_access: bool
    date: date_type | None = None
    time: time_type | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
