import requests
import time

URL = "https://agentic-honeypot-7h39.onrender.com/"
EXPECTED_VERSION = "v1.2-robust-api"

print("🔍 Monitoring Render deployment...\n")

for i in range(20):  # Check for up to 2 minutes
    try:
        response = requests.get(URL, timeout=10)
        data = response.json()
        
        if "version" in data and data["version"] == EXPECTED_VERSION:
            print(f"✅ NEW VERSION DEPLOYED: {data}")
            print("\n🎉 The fix is now live! You can test with GUVI now.")
            break
        else:
            print(f"⏳ Attempt {i+1}: Still old version - {data}")
    except Exception as e:
        print(f"⏳ Attempt {i+1}: Waiting for deployment... ({e})")
    
    time.sleep(6)
else:
    print("\n⚠️ Deployment taking longer than expected. Check Render dashboard manually.")
