import requests
import logging
from app.models import CallbackPayload

logger = logging.getLogger("uvicorn")

class CallbackService:
    def __init__(self):
        self.endpoint = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

    def send_result(self, payload: CallbackPayload):
        """
        Sends the final result to the GUVI evaluation endpoint.
        """
        try:
            data = payload.dict()
            logger.info(f"Sending callback to {self.endpoint} with payload: {data}")
            
            # Using a mock for now if we don't want to actually hit the server during dev/test without real data
            # But the requirement says "Must send".
            # Ensure timeout is set as per problem statement example
            response = requests.post(self.endpoint, json=data, timeout=5)
            
            if response.status_code == 200:
                logger.info("Callback successful")
                return True
            else:
                logger.error(f"Callback failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Callback exception: {e}")
            return False

callback_service = CallbackService()
