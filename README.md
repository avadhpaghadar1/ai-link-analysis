# Automated Multi-Platform Posting System

FastAPI implementation of the Dxora Technologies practical test. `POST /posting`
validates one short message and publishes it independently to five platforms:

- **Bluesky** using the AT Protocol
- **Mastodon** using `POST /api/v1/statuses`
- **Reddit** using the OAuth password grant and `/api/submit`
- **DEV** using `POST /api/articles`
- **LinkedIn** using the REST Posts API

Each adapter is isolated. Missing credentials are reported as a platform failure,
and a failed platform never prevents the other adapters from running.

## Run locally

Requires Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Fill in the credentials for the platforms you want to use.
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open the generated OpenAPI UI at http://localhost:4000/docs.

## API

```http
POST http://localhost:4000/posting
Content-Type: application/json

{"message":"Check out our latest business platform: https://example.com"}
```

The message must be 1–200 characters and contain exactly one valid HTTP(S)
URL. A response includes `platform`, `status`, `posted_url`, `public_access`,
`date`, `time`, and `error` for every platform.

```json
{
  "success": true,
  "results": [
    {
      "platform": "Bluesky",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Bluesky credentials are not configured"
    }
  ]
}
```

`success` is true when at least one platform succeeds. In a real run, successful
platforms return the URL supplied by that platform.

## API credentials and safety

See `.env.example` for all variables. Never commit `.env` or access tokens.
The integrations use official APIs and the minimum write credentials needed by
each provider. A Reddit script application and subreddit are required; LinkedIn
requires a member access token and author URN.

## Verification

```powershell
pytest -q
```

The implementation was also tested with a live Mastodon credential. The
Mastodon API returned HTTP 200 for credential verification, and a real
`POST /posting` request published successfully. See
[docs/verification.log](docs/verification.log) for the non-sensitive test log.

## GitHub submission checklist

Before pushing this project:

1. Confirm `.env` is not staged; only `.env.example` should be uploaded.
2. Run `pytest -q`.
3. Push the project to a public GitHub repository.
4. Open `/docs` after starting the server and include a screenshot in the
   repository or submission email if requested.

The `.gitignore` file excludes credentials, virtual environments, caches, and
Python bytecode.

Official API references:

- https://docs.bsky.app/docs/api/com-atproto-repo-create-record
- https://docs.joinmastodon.org/methods/statuses/
- https://www.reddit.com/dev/api/
- https://developers.forem.com/api/v1
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
