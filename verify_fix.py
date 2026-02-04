import requests
import json

URL = "http://127.0.0.1:8000/api/v1/message"
HEADERS = {
    "x-api-key": "secret-key",
    "Content-Type": "application/json"
}

def test_scenario(name, payload=None, use_json=True):
    print(f"\n>>> Scenario: {name}")
    try:
        if use_json:
            response = requests.post(URL, json=payload, headers=HEADERS)
        else:
            response = requests.post(URL, data=payload, headers=HEADERS)
            
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Scenarios to test
    results = []
    
    # 1. Empty dict
    results.append(test_scenario("Empty Object", {}))
    
    # 2. None/Empty Body
    # In requests, json=None sends nothing or null depending on version. 
    # Let's try sending literal empty string as data
    results.append(test_scenario("Empty Body", payload="", use_json=False))
    
    # 3. Flat string
    # results.append(test_scenario("Flat String", "Hello World")) # This might fail JSON parsing if not quoted
    results.append(test_scenario("Quoted String", "Direct Message"))
    
    # 4. Standard Structured (Regression check)
    standard_payload = {
        "sessionId": "reg-test-123",
        "message": {"text": "Is this a scam?"}
    }
    results.append(test_scenario("Standard Structured", standard_payload))

    if all(results):
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
