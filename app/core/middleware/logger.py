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

    def __init__(self, app: FastAPI, *, logger) -> None:
        self._logger = logger
        super().__init__(app)

    # https://github.com/tiangolo/fastapi/issues/394#issuecomment-927272627
    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request, call_next):
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

        # urlStr = str(request.url)
        # if urlStr[-5:] != "/docs":
            # self._logger.info(
            #     {
            #         "req": {
            #             "method": request.method, 
            #             "url": str(request.url),
            #             # "body": req_body,
            #             "user": request.user.onyen if hasattr(request.user, "onyen") else None,
            #         },
            #         "res": {
            #             "status_code": response.status_code
            #             # "response_time": f"{round((time.time() - start_time) * 1000)} ms",
            #             # "body": resp_body
            #         }
            #     }
            # )
        self._logger.info(logging_dict)

        return response
    
    async def _create_request_log(self, request: Request) -> str:

        path = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        request_log_dict = {
            "method": request.method
        }

        try:
            body = await request.json()
            request_log_dict["body"] = body
        except:
            body = None

        return request_log_dict
    
    async def _create_response_log(self,
                            call_next: Callable,
                            request: Request,
                            request_id: str
                            ) -> Response:

        start_time = time.perf_counter()
        response = await self._execute_request(call_next, request, request_id)
        finish_time = time.perf_counter()

        execution_time = finish_time - start_time

        response_log_dict = {
            "status_code": response.status_code,
            "execution_time": f"{execution_time:0.4f}s"
        }

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

        try:
            resp_body = json.loads(resp_body[0].decode())
        except:
            resp_body = str(resp_body)

        response_log_dict["body"] = resp_body

        return response, response_log_dict

    async def _execute_request(self,
                               call_next: Callable,
                               request: Request,
                               request_id: str
                               ) -> Response:
        try:
            response: Response = await call_next(request)

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
    