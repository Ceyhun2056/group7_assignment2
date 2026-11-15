"""Application entry point: python -m uvicorn app.main:app --reload."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.responses import error_response
from app.quest_routes import router as quest_router

app = FastAPI(
    title="LifeQuest API",
    description="A mocked quest-management API for the LifeQuest prototype.",
    version="1.0.0",
)
app.include_router(quest_router)

# The assignment references an error-code table that is absent from the file.
# These fixed codes cover its listed HTTP errors and unexpected server failures.
ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = []
    for error in exc.errors():
        # Exclude raw inputs and exception context from public responses.
        location = error["loc"]
        if location and location[0] in {"body", "query", "path", "header", "cookie"}:
            location = location[1:]
        field = ".".join(str(part) for part in location) or "body"
        message = error["msg"]
        if error["type"] == "json_invalid":
            field, message = "body", "Request body must contain valid JSON."
        details.append({"field": field, "message": message})
    return JSONResponse(
        status_code=400,
        content=error_response(
            "VALIDATION_ERROR",
            "The request contains invalid or missing fields.",
            details=details,
        ),
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code >= 500:
        code, message = "INTERNAL_SERVER_ERROR", "An unexpected server error occurred."
    else:
        code = ERROR_CODES.get(exc.status_code, "HTTP_ERROR")
        message = (
            exc.detail if isinstance(exc.detail, str)
            else HTTPStatus(exc.status_code).phrase
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code, message),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_response(
            "INTERNAL_SERVER_ERROR", "An unexpected server error occurred."
        ),
    )
