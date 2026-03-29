import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small-3.1-24b-instruct:free")

print(f"Testing with model: {model}")
print(f"API Key present: {bool(api_key)}")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Respond ONLY with a JSON object."},
        {"role": "user", "content": "Open WhatsApp"}
    ],
    "response_format": {"type": "json_object"}
}

try:
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
