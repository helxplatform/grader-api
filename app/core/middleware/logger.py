import json
import logging
import time
from typing import Callable
from uuid import uuid4
from fastapi import FastAPI, Response
from starlette.types import Message
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.utils.async_iterator_wrapper import AsyncIteratorWrapper

class LogMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI, *, logger: logging.Logger, file_logger: logging.Logger = None) -> None:
        self._logger = logger
        self._file_logger = file_logger
        super().__init__(app)

    # https://github.com/tiangolo/fastapi/issues/394#issuecomment-927272627
    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/v1/health"):
            response = await self._execute_request(call_next, request)
            return response
        
        request_id: str = str(uuid4())
        logging_dict = {
            "X-API-REQUEST-ID": request_id  # X-API-REQUEST-ID maps each request-response to a unique ID
        }

        await self.set_body(request)
        response, response_dict = await self._create_response_log(
            call_next,
            request,
            request_id
        )
        request_dict = await self._create_request_log(request)
        logging_dict["req"] = request_dict
        logging_dict["res"] = response_dict

        self._logger.info(logging_dict)
        if self._file_logger is not None:
            resp_body = [section async for section in response.__dict__["body_iterator"]]
            response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

            try:
                resp_body = json.loads(resp_body[0])
            except:
                resp_body = str(resp_body)

            response_dict["body"] = resp_body
            logging_dict["res"] = response_dict

            self._file_logger.debug(logging_dict)

        return response
    
    async def _create_request_log(self, request: Request) -> str:

        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        request_log_dict = {
            "method": request.method,
            "endpoint": path,
            "user": request.user.onyen if hasattr(request.user, "onyen") else None,
        }

        try:
            body = await request.json()
            request_log_dict["body"] = body
        except:
            body = None
            request_log_dict["body"] = None

        return request_log_dict
    
    async def _create_response_log(self,
                            call_next: Callable,
                            request: Request,
                            request_id
                            ) -> Response:

        start_time = time.perf_counter()
        response = await self._execute_request(call_next, request, request_id)
        finish_time = time.perf_counter()

        execution_time = finish_time - start_time

        response_log_dict = {
            "status_code": response.status_code,
            "execution_time": f"{execution_time:0.4f}s",
        }

        return response, response_log_dict

    async def _execute_request(self,
                               call_next: Callable,
                               request: Request,
                               request_id: str = None
                               ) -> Response:
        try:
            response: Response = await call_next(request)

            if request_id is not None:
                response.headers["X-API-Request-ID"] = request_id
            return response

        except Exception as e:
            self._logger.exception(
                {
                    "path": request.url.path,
                    "method": request.method,
                    "reason": e
                }
            )
    