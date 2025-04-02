import json
from fastapi import Request, HTTPException
import sys
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)
from app.core.middleware.logger import LogMiddleware


class MockApp:
    def __init__(self):
        self.logger = MockLogger()

class MockLogger:
    def info(self, log_data):
        pass

    def error(self, log_data):
        pass
           
class MockResponse:
    def __init__(self, status_code=200, body=b'{"key": "value"}'):
        self.status_code = status_code
        self.body_iterator = [body]

async def mock_call_next(request):
    return MockResponse()

async def mock_call_next_with_error(request):
    # Simulate an error scenario
    raise HTTPException(status_code=500, detail="Internal Server Error")

async def test_successful_request_logging():
    request = Request({"type": "http", "method": "GET", "url": "http://example.com"})
    middleware = LogMiddleware(MockApp())

    response = await middleware.dispatch(request, mock_call_next)

    assert isinstance(response, MockResponse)

    assert isinstance(middleware.log_data, dict)
    assert "req" in middleware.log_data
    assert "res" in middleware.log_data

    assert middleware.log_data["req"]["method"] == "GET"
    assert middleware.log_data["res"]["status_code"] == 200

    assert "GET" in str(middleware.log_data)

    json.dumps(middleware.log_data)

    middleware.log_data = None

async def test_error_logging():
    request_error = Request({"type": "http", "method": "GET", "url": "http://example.com"})
    middleware_error = LogMiddleware(MockApp())

    try:
        await middleware_error.dispatch(request_error, mock_call_next_with_error)
    except HTTPException:
        pass  # Expected exception

    # Add assertions for error logging
    assert isinstance(middleware_error.log_data, dict)
    assert "req" in middleware_error.log_data
    assert "res" in middleware_error.log_data

    assert middleware_error.log_data["req"]["method"] == "GET"
    assert middleware_error.log_data["res"]["status_code"] == 500

    assert "GET" in str(middleware_error.log_data)
    assert "Internal Server Error" in str(middleware_error.log_data)

    json.dumps(middleware_error.log_data)

    middleware_error.log_data = None

