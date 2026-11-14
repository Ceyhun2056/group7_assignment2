# LifeQuest API prototype

LifeQuest helps students and other individuals manage tasks as RPG quests.
This repository implements its API prototype for Assignment 2 using Python and
FastAPI. The current foundation includes the application and shared JSON response
and error handling. Quest CRUD, mock users/data, and the HTML greeting page will
be added in subsequent features.

## Run locally

Requires Python 3.10 or newer. From the repository directory:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install and start the backend:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.
No business endpoints are registered in this foundation yet; a request to `/`
returns a structured `404`.

## Run tests

```bash
python -m pytest -q
```

Tests use temporary routes to verify the shared handlers. These routes are not
part of the running API.

## Response conventions

Success responses contain `success`, `message`, and `data`. List endpoints will
also include `meta` containing `total`, `page`, and `perPage`.

Errors contain `success: false` and an `error` object with `code` and `message`.
Request validation errors return HTTP `400`, code `VALIDATION_ERROR`, and a
`details` array containing `field` and `message`. Other errors omit `details`.
Unexpected server errors return a generic message without internal details.

The assignment refers to an error-code table that is not present in the supplied
document. This prototype uses the following fixed codes:

| HTTP status | Error code |
|---|---|
| 400 | `BAD_REQUEST`, or `VALIDATION_ERROR` for request validation |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 405 | `METHOD_NOT_ALLOWED` |
| 409 | `CONFLICT` |
| 500 | `INTERNAL_SERVER_ERROR` |

FastAPI's `/docs`, `/redoc`, and `/openapi.json` are documentation endpoints;
the JSON envelope convention applies to business responses and API errors.
