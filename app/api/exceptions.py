from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from fastapi.exceptions import (
    RequestValidationError as ReqValid,
    ResponseValidationError as RespValid,
)



class AppException(Exception):
    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail



def setup_exceptions(app: FastAPI) -> None:
    """Глобальные обработчики исключений."""

    @app.exception_handler(AppException)
    async def app_err(req: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content={"detail": exc.detail,},
        )


    @app.exception_handler(HTTPException)
    async def http_err(req: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail,},
        )


    @app.exception_handler(ReqValid)
    async def req_err(req: Request, exc: ReqValid) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
            },
        )


    @app.exception_handler(RespValid)
    async def res_err(req: Request, exc: RespValid) -> JSONResponse:
        logger.exception(f"Response error: {req.method} {req.url.path}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Server error",},
        )


    @app.exception_handler(Exception)
    async def any_err(req: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Critical: {req.method} {req.url.path}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal error",},
        )