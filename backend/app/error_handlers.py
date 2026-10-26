"""Give every error response the same shape: {"detail": "message"}.

HTTPException (401, 404, 409, ...) already uses it. These handlers bring the two
exceptions into line: validation errors, which also list each field's problem,
and unexpected errors, which FastAPI would otherwise send as plain text.
No error response includes the rejected input or an exception's message.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """422 with a message per invalid field, for example {"field": "body.password"}."""
    errors = [
        # Only the location and message: Pydantic's "input" would echo back
        # the rejected value, including a rejected password
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Invalid request", "errors": errors},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """500 for a bug. The exception's message could reveal internals, so it stays
    out of the response. Starlette re-raises exc afterwards, so it's still logged.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Install the handlers on an app. Separate so tests can use them on a test app."""
    # Starlette types every handler as taking a plain Exception, though it only
    # ever passes this one a RequestValidationError
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)
