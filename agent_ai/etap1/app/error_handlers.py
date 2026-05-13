from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import AppError

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Unexpected server error",
            "details": None,
        },
    )

async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []

    for error in exc.errors():
        field = ".".join(str(part) for part in error.get("loc", []) if part != "body")

        details.append(
            {
                "field": field,
                "message": error.get("msg"),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": details,
        },
    )