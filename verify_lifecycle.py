import requests
import json
import time
import random
import string
import datetime

URL = "http://127.0.0.1:8000/api/v1/message"
HEADERS = {
    "x-api-key": "secret-key",
    "Content-Type": "application/json"
}

def generate_session_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def get_timestamp(offset_minutes=0):
    t = datetime.datetime.utcnow() + datetime.timedelta(minutes=offset_minutes)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")

def send_message(session_id, text, history, description):
    print(f"\n--- {description} ---")
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": get_timestamp()
        },
        "conversationHistory": history,
        "metadata": {"channel": "SMS"}
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print("Status: 200 OK")
            print(f"Agent Reply: {data['reply']}")
            return data['reply']
        else:
            print(f"Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_lifecycle():
    session_id = generate_session_id()
    print(f"Testing Lifecycle Session: {session_id}")
    history = []
    
    # 1. Start: Scam Trigger (Turn 1)
    # Expect: Confusion (Confusion response)
    reply = send_message(session_id, "Your bank acct blocked. Urgent.", history, "Turn 1: Trigger Scam")
    history.append({"sender": "scammer", "text": "Your bank acct blocked...", "timestamp": get_timestamp(0)})
    history.append({"sender": "user", "text": reply, "timestamp": get_timestamp(1)})
    
    # 2. Scammer insists (Turn 2)
    # Expect: More Confusion
    reply = send_message(session_id, "Verify now or lose money.", history, "Turn 2: Insist")
    history.append({"sender": "scammer", "text": "Verify now...", "timestamp": get_timestamp(2)})
    history.append({"sender": "user", "text": reply, "timestamp": get_timestamp(3)})

    # 3. Scammer sends partial info (Turn 3)
    # Expect: Agent probing for missing info (e.g. UPI)
    # We haven't sent intelligence yet.
    reply = send_message(session_id, "Just pay fine.", history, "Turn 3: Probing Phase")
    history.append({"sender": "scammer", "text": "Just pay fine.", "timestamp": get_timestamp(4)})
    history.append({"sender": "user", "text": reply, "timestamp": get_timestamp(5)})

    # 4. Scammer sends UPI (Turn 4) -> Intelligence Extraction
    # Conditions: Intelligence found.
    # Expect: Completion Logic Trigger -> CALLBACK SENT -> Agent Disengages
    print("\n[EXPECTATION] Callback should trigger NOW (Intelligence provided):")
    reply = send_message(session_id, "Pay to scammer@upi immediately.", history, "Turn 4: Intelligence Given")
    history.append({"sender": "scammer", "text": "Pay to scammer@upi...", "timestamp": get_timestamp(6)})
    history.append({"sender": "user", "text": reply, "timestamp": get_timestamp(7)})

    # 5. Post-Completion (Turn 5)
    # Expect: Agent disengages ("Need time to think"), No Callback
    print("\n[EXPECTATION] Callback should NOT trigger (Completed + Idempotency):")
    reply = send_message(session_id, "Did you pay?", history, "Turn 5: Post-Completion")

if __name__ == "__main__":
    time.sleep(2)
    test_lifecycle()
