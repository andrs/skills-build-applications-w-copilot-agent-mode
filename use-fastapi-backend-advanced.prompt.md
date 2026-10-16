# Using the Advanced FastAPI Prompt

Use the following request in Copilot Chat:

```text
Use `.github/prompts/fastapi-backend-advanced.prompt.md` to add a weekly
leaderboard endpoint to the existing AndresFit FastAPI backend.

Requirements:

- Add `GET /api/v1/leaderboard/weekly`.
- Return users ranked by calories burned during the last 7 days.
- Keep the API -> Service -> Repository -> Model architecture.
- Add the repository query using async SQLAlchemy and `select()`.
- Add the service method and response schema.
- Inject the service through dependencies.
- Add tests using `AsyncMock` and `httpx.AsyncClient`.
- Inspect existing files first and preserve current behavior.
- Do not use synchronous SQLAlchemy or `session.query()`.
- Run the backend test suite and report changed files and test results.
```

## Example For Another Feature

Replace the requested behavior while keeping the same implementation rules:

```text
Use `.github/prompts/fastapi-backend-advanced.prompt.md` to add
`PATCH /api/v1/users/{user_id}` for updating a user's full name and email.

Follow the existing architecture, validation, exception handling, and testing
patterns. Inspect the existing files first, preserve current behavior, run all
backend tests, and report changed files and test results.
```