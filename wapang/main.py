from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from wapang.api import api_router
from wapang.app.orders.exceptions import InvalidFieldFormatException
from wapang.common.exceptions import (
    WapangException,
    MissingRequiredFieldException
)

app = FastAPI()

app.include_router(api_router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error["type"] == "missing":
            raise MissingRequiredFieldException()
        elif error["type"] == "enum":
            raise InvalidFieldFormatException()
    return await request_validation_exception_handler(request, exc)

@app.exception_handler(WapangException)
async def wapang_exception_handler(request: Request, exc: WapangException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "error_msg": exc.error_msg
        }
    )