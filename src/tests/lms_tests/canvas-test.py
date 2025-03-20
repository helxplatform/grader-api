import json
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Assuming you have stored your Canvas LMS API key securely
CANVAS_API_KEY = ""
CANVAS_API_URL = "https://uncch.instructure.com/api/v1"

headers = {
    "Authorization": f"Bearer {CANVAS_API_KEY}"
}

url = f"{CANVAS_API_URL}/accounts"

response = requests.get(url, headers=headers)
print(response.json())


# Test the Assignment API

url = f"{CANVAS_API_URL}/courses/47558/assignments"

response = requests.get(url, headers=headers);
print(json.dumps(response.json(), indent = 4))


