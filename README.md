# LifeQuest API prototype

LifeQuest helps students and other individuals manage tasks as RPG quests.
This repository implements its API prototype for Assignment 2 using Python and
FastAPI. The current implementation includes the application, shared JSON response
and error handling, quest schemas, in-memory quest data, and mock authentication
and access helpers, plus quest listing and retrieval. Quest creation, updating,
deletion, and the HTML greeting page will be added in subsequent features.

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
The quest GET endpoints are registered; a request to `/` returns a structured `404`.

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
can access all four through the shared access helper. Use
`quest_999` as a non-existent ID in demonstrations.

There is no database. Mock data resets to these four quests when the server
restarts, so created quests and edits are not saved permanently.

## Mock authentication and access control

No login, passwords, JWTs, or external authentication service are needed. The
assignment uses these predefined tokens:

| Token | User ID | Permissions |
|---|---|---|
| `user-a-token` | `user-a` | Own quests only |
| `user-b-token` | `user-b` | Own quests only |
| `admin-token` | `admin` | All quests |

Protected endpoints will use `Depends(get_current_user)` from `app/auth.py`.
Send the token in the header, for example:

```http
Authorization: Bearer user-a-token
```

Missing, malformed, and invalid tokens return `401 UNAUTHORIZED` with a
`WWW-Authenticate: Bearer` header. Tokens are case-sensitive.

`get_accessible_quest` returns `404 NOT_FOUND` for a missing quest and
`403 FORBIDDEN` for another user's quest. We choose `403` to clearly explain an
authenticated user's lack of permission, as permitted by the assignment. Quest
reading, updating, and deletion will reuse this check. Collection endpoints will
use `can_access_quest` to filter results before calculating pagination metadata.

The authentication helpers are connected to both GET quest endpoints. Isolated
helper tests and actual endpoint tests verify their behavior.

## Quest GET endpoints

Both endpoints require `Authorization: Bearer <token>` and return the standard
JSON envelope. No request body is needed.

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/quests` | List the caller's quests; administrators see all quests |
| GET | `/api/v1/quests/{quest_id}` | Retrieve one quest, subject to ownership checks |

The list accepts integer queries `page` (minimum 1, default 1) and `perPage`
(1-100, default 10). Results follow the mock dictionary's insertion order.
Access filtering happens before pagination; `meta.total` counts only visible
quests. A page beyond the results returns an empty array with HTTP 200.

Example in Windows PowerShell (or replace `curl.exe` with `curl` on Linux/macOS):

```powershell
curl.exe -H "Authorization: Bearer user-b-token" "http://127.0.0.1:8000/api/v1/quests?page=2&perPage=1"
curl.exe -H "Authorization: Bearer user-a-token" "http://127.0.0.1:8000/api/v1/quests/quest_1"
```

Both return 200 on success. The list response includes `data` as an array and
`meta` with `total`, `page`, and `perPage`; the single response contains the quest
object in `data`. Invalid pagination returns 400 `VALIDATION_ERROR`. Missing or
invalid tokens return 401 `UNAUTHORIZED`. Single-quest requests can also return
403 `FORBIDDEN` or 404 `NOT_FOUND`. Unexpected server errors use the shared 500
`INTERNAL_SERVER_ERROR` response.

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
