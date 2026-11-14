# LifeQuest API prototype

LifeQuest helps students and other individuals manage tasks as RPG quests.
This repository implements its API prototype for Assignment 2 using Python and
FastAPI. The current implementation includes the application, shared JSON response
and error handling, quest schemas, and in-memory quest data. Quest endpoints,
mock authentication, and the HTML greeting page will be added in subsequent features.

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

Foundation tests use temporary routes to verify the shared handlers. These routes
are not part of the running API. Model tests check quest validation and mock data.

## Quest fields and mock data

Creation and PUT replacement will share the `QuestInput` schema:

| Field | Validation |
|---|---|
| `title` | Required string, 3-120 characters after trimming surrounding whitespace |
| `description` | Required string, 1-2000 characters after trimming surrounding whitespace |
| `deadline` | Required date, supplied as a `YYYY-MM-DD` string |
| `difficulty` | Required: `easy`, `medium`, or `hard` |
| `status` | `open` or `completed`; defaults to `open` if omitted |

Unknown fields are rejected. Clients cannot supply `id` or `ownerId`; the backend
will assign them on creation and preserve them on update. PUT replaces the editable
fields, so all four required fields must be included; omitting `status` resets it
to `open`. Past deadlines are allowed for overdue and completed quests.

`app/mock_data.py` stores quests in a plain dictionary. `quest_1` and `quest_2`
belong to `user-a`; `quest_3` and `quest_4` belong to `user-b`. An administrator
will be able to access all four once authentication is implemented. Use
`quest_999` as a non-existent ID in demonstrations.

There is no database. Mock data resets to these four quests when the server
restarts, so created quests and edits are not saved permanently.

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
