
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PAYGRID_API_KEY")
base_url = os.getenv("PAYGRID_BASE_URL", "").rstrip("/")

if not api_key or not base_url:
    raise RuntimeError("Paygrid settings are missing from .env")

recipient = input("Enter your test phone number (e.g. 2547XXXXXXXX): ").strip()

payload = {
    "recipient": [recipient],
    "message": "SCHOOL_TRACK sandbox test: SMS integration check.",
    "sender_id": "CommsGrid"
}

response = requests.post(
    f"{base_url}/sms/send",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=20
)

print("HTTP status:", response.status_code)
print("Response:", response.text)
