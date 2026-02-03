import requests
import json
import time

URL = "http://127.0.0.1:8000/api/v1/message"
HEADERS = {
    "x-api-key": "secret-key",
    "Content-Type": "application/json"
}

def test_scam_message():
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print("Sending scam message 1...")
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print("Status Code:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Error:", e)

def test_followup_message():
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension.",
            "timestamp": "2026-01-21T10:17:10Z"
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": "2026-01-21T10:15:30Z"
            },
            {
                "sender": "user",
                "text": "Why will my account be blocked?",
                "timestamp": "2026-01-21T10:16:10Z"
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }

    print("\nSending follow-up message...")
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        print("Status Code:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2) 
    test_scam_message()
    test_followup_message()
