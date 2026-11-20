# LifeQuest API reference

Run the backend using the root README. The local base URL is
`http://127.0.0.1:8000`. For executable examples, use **Try it out** at
`/docs`. Choose **Authorize** and enter the mock token without the
`Bearer` prefix. The HTTP examples below show the headers sent by the client.
Examples assume the server has just started and run in the order shown.
Restarting restores the original four quests.

| Token | Role | Access |
|---|---|---|
| `user-a-token` | Regular user A | Own quests, initially `quest_1` and `quest_2` |
| `user-b-token` | Regular user B | Own quests, initially `quest_3` and `quest_4` |
| `admin-token` | Administrator | All quests |

All quest routes require `Authorization: Bearer <token>`. Requests with a JSON
body use `Content-Type: application/json`. A regular user accessing another
user's quest receives `403` to distinguish insufficient permission from a
missing quest, which receives `404`.

## Quest request body

| Field | Rule |
|---|---|
| `title` | Required string, 3–120 characters after trimming |
| `description` | Required string, 1–2,000 characters after trimming |
| `deadline` | Required calendar date in `YYYY-MM-DD` format. Past dates are allowed. |
| `difficulty` | Required. One of `easy`, `medium`, or `hard`. |
| `status` | Optional. One of `open` or `completed`. Defaults to `open`. |

Unknown fields, including `id` and `ownerId`, fail validation.

## GET /api/v1/quests

Any authenticated role can list the quests it can access. There is no path
parameter or body. Optional integer query parameters are `page` (at least 1,
default 1) and `perPage` (1–100, default 10). Access filtering happens before
pagination. A page past the end returns an empty `data` array with `200`.

Errors are `400 VALIDATION_ERROR` for invalid pagination and
`401 UNAUTHORIZED` for missing or invalid authentication.

```http
GET /api/v1/quests?page=1&perPage=1 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Quests retrieved successfully.",
  "data": [
    {
      "title": "Review REST API notes",
      "description": "Revise resources, HTTP methods, and status codes.",
      "deadline": "2026-11-20",
      "difficulty": "easy",
      "status": "open",
      "id": "quest_1",
      "ownerId": "user-a"
    }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "perPage": 1
  }
}
```

## GET /api/v1/quests/{quest_id}

Any authenticated role can retrieve an accessible quest. Supply the quest ID
as a string in the path. There are no query parameters or request body.

Errors are `401 UNAUTHORIZED`, `403 FORBIDDEN` for another user's quest, and
`404 NOT_FOUND` for an unknown ID.

```http
GET /api/v1/quests/quest_1 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Quest retrieved successfully.",
  "data": {
    "title": "Review REST API notes",
    "description": "Revise resources, HTTP methods, and status codes.",
    "deadline": "2026-11-20",
    "difficulty": "easy",
    "status": "open",
    "id": "quest_1",
    "ownerId": "user-a"
  }
}
```

## PUT /api/v1/quests/{quest_id}

The owner or an administrator can replace a quest's editable fields. Supply the
quest ID in the path and a JSON body matching the table above. There are no
query parameters. All required fields must be sent and omitting `status` sets
it to `open`. The ID and owner are preserved.

Errors are `400 VALIDATION_ERROR`, `401 UNAUTHORIZED`, `403 FORBIDDEN`, and
`404 NOT_FOUND`.

```http
PUT /api/v1/quests/quest_1 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
Content-Type: application/json

{
  "title": "Review REST API notes",
  "description": "Review resources and HTTP status codes.",
  "deadline": "2026-11-25",
  "difficulty": "medium",
  "status": "completed"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Quest updated successfully.",
  "data": {
    "title": "Review REST API notes",
    "description": "Review resources and HTTP status codes.",
    "deadline": "2026-11-25",
    "difficulty": "medium",
    "status": "completed",
    "id": "quest_1",
    "ownerId": "user-a"
  }
}
```

## DELETE /api/v1/quests/{quest_id}

The owner or an administrator can delete a quest. Supply the quest ID in the
path. There are no query parameters or request body. A successful response
returns `200` with `data: null`.

Errors are `401 UNAUTHORIZED`, `403 FORBIDDEN`, and `404 NOT_FOUND`. A second
deletion of the same ID returns `404`.

```http
DELETE /api/v1/quests/quest_2 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Quest deleted successfully.",
  "data": null
}
```

## GET /api/v1/greeting

Public route with no required headers, parameters, or body. Returns the HTML
greeting and a list of registered API routes.

```http
GET /api/v1/greeting HTTP/1.1
Host: 127.0.0.1:8000
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!-- Selected excerpt -->
<h1>LifeQuest</h1>
```

## Error examples

All API errors use `success: false` and an `error` object. Only validation
errors include field-level `details`. An unsupported method returns
`405 METHOD_NOT_ALLOWED` with an `Allow` header. An unexpected server failure
returns `500 INTERNAL_SERVER_ERROR` with a generic message.

### 400 · Invalid pagination

```http
GET /api/v1/quests?page=0 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [
      {
        "field": "page",
        "message": "Input should be greater than or equal to 1"
      }
    ]
  }
}
```

### 401 · Missing token

```http
GET /api/v1/quests HTTP/1.1
Host: 127.0.0.1:8000
```

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
WWW-Authenticate: Bearer

{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "A valid Bearer token is required."
  }
}
```

### 403 · Another user's quest

```http
GET /api/v1/quests/quest_3 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You cannot access another user's quest."
  }
}
```

### 404 · Missing quest

```http
GET /api/v1/quests/quest_999 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
```

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Quest not found."
  }
}
```

### 405 · Unsupported method

```http
POST /api/v1/greeting HTTP/1.1
Host: 127.0.0.1:8000
```

```http
HTTP/1.1 405 Method Not Allowed
Content-Type: application/json
Allow: GET

{
  "success": false,
  "error": {
    "code": "METHOD_NOT_ALLOWED",
    "message": "Method Not Allowed"
  }
}
```

## POST /api/v1/quests · Planned

Quest creation is scheduled for a separate implementation commit. The intended
contract accepts the JSON body described above with any valid mock token, uses no
path or query parameters, and returns `201 Created` with the new quest in
`data`. The server generates the ID and uses the authenticated user as owner.
Invalid body fields are expected to return `400 VALIDATION_ERROR`. Missing or
invalid tokens are expected to return `401 UNAUTHORIZED`.

Example request for the planned route

```http
POST /api/v1/quests HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer user-a-token
Content-Type: application/json

{
  "title": "Prepare API demo",
  "description": "Practice showing quest creation and access checks.",
  "deadline": "2026-11-25",
  "difficulty": "medium"
}
```

After the creation route merges, replace this planned section with the verified
request and response, including the actual ID format and status codes.
