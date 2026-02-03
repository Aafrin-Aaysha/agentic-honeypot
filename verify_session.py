import requests
import json
import time
import random
import string

URL = "http://127.0.0.1:8000/api/v1/message"
HEADERS = {
    "x-api-key": "secret-key",
    "Content-Type": "application/json"
}

def generate_session_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def send_message(session_id, text, history, description):
    print(f"\n--- {description} ---")
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": "2026-01-21T10:00:00Z"
        },
        "conversationHistory": history,
        "metadata": {"channel": "SMS"}
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            print("Status: 200 OK")
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_session_gating():
    session_id = generate_session_id()
    print(f"Testing Session: {session_id}")
    
    history = []
    
    # Message 1: Scam Trigger
    send_message(session_id, "Your account blocked. Verify blocked account now.", history, "Msg 1: Trigger Scam")
    history.append({
        "sender": "scammer", 
        "text": "Your account blocked...",
        "timestamp": "2026-01-21T10:00:00Z"
    })
    history.append({
        "sender": "user", 
        "text": "Agent Reply 1",
        "timestamp": "2026-01-21T10:01:00Z"
    }) # Simulated reply in history
    
    # Message 2: Follow up
    send_message(session_id, "Send UPI ID 123@upi immediately.", history, "Msg 2: Follow Up")
    history.append({
        "sender": "scammer", 
        "text": "Send UPI ID...",
        "timestamp": "2026-01-21T10:02:00Z"
    })
    history.append({
        "sender": "user", 
        "text": "Agent Reply 2",
        "timestamp": "2026-01-21T10:03:00Z"
    })

    # Message 3: Threshold Reach -> Should Trigger Callback
    print("\n[EXPECTATION] Callback should trigger NOW:")
    send_message(session_id, "Why are you waiting? Urgent.", history, "Msg 3: Threshold Reached")
    
    # Message 4: Post-Threshold -> No Callback
    print("\n[EXPECTATION] Callback should NOT trigger (Idempotency):")
    send_message(session_id, "Hello? Answer me.", history, "Msg 4: Post-Threshold")

if __name__ == "__main__":
    # Wait for server to potentially restart/reload
    time.sleep(2)
    test_session_gating()
