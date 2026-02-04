from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADERS = {"x-api-key": "secret-key", "Content-Type": "application/json"}

results = {}

print('Running quick in-process tests...')
# Empty object
r = client.post('/api/v1/message', json={}, headers=HEADERS)
print('Empty Object:', r.status_code, r.json())
results['empty_object'] = (r.status_code, r.json())
# No body
r = client.post('/api/v1/message', headers=HEADERS)
print('No Body:', r.status_code, r.json())
results['no_body'] = (r.status_code, r.json())
# Quoted string
r = client.post('/api/v1/message', data='"Direct Message"', headers=HEADERS)
print('Quoted String:', r.status_code, r.json())
results['quoted_string'] = (r.status_code, r.json())
# Structured
standard_payload = {"sessionId": "reg-test-123", "message": {"text": "Is this a scam?"}}
r = client.post('/api/v1/message', json=standard_payload, headers=HEADERS)
print('Structured:', r.status_code, r.json())
results['structured'] = (r.status_code, r.json())

# Simple verify scenario
payload = {
    "sessionId": "test-session-123",
    "message": {"sender": "scammer", "text": "Your bank account will be blocked today.", "timestamp": "2026-01-21T10:15:30Z"},
    "conversationHistory": [],
    "metadata": {"channel": "SMS"}
}
r = client.post('/api/v1/message', json=payload, headers=HEADERS)
print('verify scenario:', r.status_code, r.json())
results['verify'] = (r.status_code, r.json())

# session sequence
session_id = 'session-test-xyz'
r1 = client.post('/api/v1/message', json={"sessionId": session_id, "message": {"sender": "scammer", "text": "Your account blocked.", "timestamp": "2026-01-21T10:00:00Z"}, "conversationHistory": [], "metadata": {"channel": "SMS"}}, headers=HEADERS)
print('seq 1:', r1.status_code, r1.json())
r2 = client.post('/api/v1/message', json={"sessionId": session_id, "message": {"sender": "scammer", "text": "Send UPI ID 123@upi immediately.", "timestamp": "2026-01-21T10:02:00Z"}, "conversationHistory": [{"sender":"user","text":"Agent Reply 1","timestamp":"2026-01-21T10:01:00Z"}], "metadata": {"channel": "SMS"}}, headers=HEADERS)
print('seq 2:', r2.status_code, r2.json())
r3 = client.post('/api/v1/message', json={"sessionId": session_id, "message": {"sender": "scammer", "text": "Why are you waiting? Urgent.", "timestamp": "2026-01-21T10:03:30Z"}, "conversationHistory": [{"sender":"scammer","text":"Your account blocked...","timestamp":"2026-01-21T10:00:00Z"}, {"sender":"user","text":"Agent Reply 1","timestamp":"2026-01-21T10:01:00Z"}], "metadata": {"channel": "SMS"}}, headers=HEADERS)
print('seq 3:', r3.status_code, r3.json())

print('\nSummary:')
for k,v in results.items():
    print(k, '->', v)

all_ok = all(v[0]==200 for v in results.values())
print('\nALL OK' if all_ok else '\nSOME FAIL')
