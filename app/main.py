import sys
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware
from fastapi_pagination import add_pagination
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings, DevPhase
from app.core.middleware import AuthenticationMiddleware, AuthBackend, LogMiddleware
from app.core.exceptions import CustomException

import logging
from pathlib import Path

logging.getLogger("uvicorn.access").disabled = True
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def init_routers(app: FastAPI):
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
def init_monkeypatch():
    ### Monkey patch serializers for custom types
    from pydantic.json import ENCODERS_BY_TYPE
    from app.schemas._unset import _UNSET
    ENCODERS_BY_TYPE[_UNSET] = lambda _: None

def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message
    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message}
    )

def make_middleware() -> List[Middleware]:
    return [
        *([Middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"]
        )] if settings.DEV_PHASE == DevPhase.DEV else []),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error
        ),
        Middleware(
            EventHandlerASGIMiddleware,
            handlers=[local_handler]
        ),
        Middleware(
            LogMiddleware, 
            logger=logger
        )
    ]

app = FastAPI(
    openapi_url=f"{ settings.API_V1_STR }/openapi.json",
    middleware=make_middleware()
)

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    content = { "error_code": exc.error_code, "message": exc.message }
    if settings.DEV_PHASE == DevPhase.DEV:
        content["stack"] = exc.stack
    return JSONResponse(
        status_code=exc.code,
        content=content,
    )

# if not settings.DISABLE_LOGGER:
    # logger = CustomizeLogger.make_logger(config_path)
    # app.logger = logger
    # app.add_middleware(LogMiddleware, logger=logger)
init_monkeypatch()
init_routers(app)
add_pagination(app)