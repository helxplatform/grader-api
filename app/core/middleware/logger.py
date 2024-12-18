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

    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path.startswith("/api/v1/health"):
            response = await self._execute_request(call_next, request)
            return response

        await self.set_body(request)

        request_id = str(uuid4())
        response, response_dict = await self._create_response_log(
            call_next,
            request,
            request_id
        )

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

        try:
            resp_body = json.loads(resp_body[0])
        except:
            resp_body = str(resp_body)

        if "error_code" in resp_body:
            # If the response contains an error code, that means an exception happened
            # and we need to log it. So just log the exception and return, don't log
            # the request as you would normally.
            request_log = {
                "path": request.url.path,
                "method": request.method,
            }
            if type(resp_body) is dict:
                request_log["error_code"] = resp_body["error_code"]
                request_log["message"] = resp_body["message"]
                self._logger.error(request_log)
            elif type(resp_body) is str:
                # If the resp_body is of type str because the above json.loads() failed, 
                # don't add the fields above, just use the whole resp_body
                request_log["resp_body"] = resp_body
                self._logger.error(request_log)
            return response

        logging_dict = {
            "X-API-REQUEST-ID": request_id,  # X-API-REQUEST-ID maps each request-response to a unique ID
            "req": await self._create_request_log(request),
            "res": response_dict
        }
        self._logger.info(logging_dict)

        if self._file_logger is not None:
            response_dict["body"] = resp_body
            logging_dict["res"] = response_dict

            self._file_logger.debug(logging_dict)

        return response
    
    async def _create_request_log(self, request: Request) -> str:

        request_log_dict = {
            "method": request.method,
            "endpoint": request.url.path,
            "user": request.user.onyen if hasattr(request.user, "onyen") else None,
        }

        try:
            if request.url.path not in self._get_endpoints_to_not_log_req_body():
                body = await request.json()
                request_log_dict["body"] = body
        except Exception as e:
            request_log_dict["body"] = None

        return request_log_dict
    
    async def _create_response_log(
        self,
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

    async def _execute_request(
        self,
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
            # If we hit an exception here, it is a non-HTTP error, i.e., it is an internal server error.
            exception_log = {
                "path": request.url.path,
                "method": request.method,
                "reason": e
            }
            self._logger.error(exception_log)
            # Starlette will log the internal traceback for us automatically.
            raise e
    
    def _get_endpoints_to_not_log_req_body(self) -> list[str]:
        return [
            "/api/v1/login",
            "/api/v1/refresh"
        ]