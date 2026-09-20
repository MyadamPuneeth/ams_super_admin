from uuid import uuid4
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class ApiError(Exception):
    def __init__(self, status: int, message: str): self.status, self.message = status, message

def body(status: int, message: str, request: Request) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(status_code=status, content={"statusCode": status, "message": message, "requestId": request_id})

async def api_error(request: Request, error: ApiError): return body(error.status, error.message, request)
async def http_error(request: Request, error: StarletteHTTPException): return body(error.status_code, str(error.detail), request)
async def validation_error(request: Request, error: RequestValidationError):
    message = "; ".join(item["msg"] for item in error.errors())
    return body(400, message, request)
async def unexpected_error(request: Request, error: Exception):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    print({"requestId": request_id, "event": "request.failed", "errorType": type(error).__name__})
    return body(500, "Something went wrong. Please try again.", request)
