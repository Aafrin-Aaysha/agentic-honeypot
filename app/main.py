from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional
from app.models import IncomingRequest, ApiResponse, CallbackPayload, ExtractedIntelligence
from app.services.detector import detector
from app.services.agent import agent
from app.services.extractor import extractor
from app.services.callback import callback_service
from app.services.state import session_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("honey-pot")

app = FastAPI()

async def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.post("/api/v1/message", response_model=ApiResponse)
async def handle_message(request: IncomingRequest, api_key: str = Depends(verify_api_key)):
    session_id = request.sessionId
    logger.info(f"Processing message for session {session_id}")

    # 1. Initialize/Get Session & details
    session = session_manager.get_session(session_id)
    
    # 2. Increment Message Count
    session_manager.increment_message_count(session_id)
    
    # 3. Analyze content
    current_text = request.message.text
    full_text = current_text + " " + " ".join([m.text for m in (request.conversationHistory or [])])
    
    # 4. Scam Detection
    if detector.detect(full_text):
        session_manager.mark_scam_detected(session_id)
        logger.info(f"Scam detected for session {session_id}")

    # 5. Extract Intelligence & Accumulate (Only if not already completed strategies?)
    # Requirement: "Continue returning polite but disengaging responses... Do not attempt further intelligence extraction."
    if not session.conversationCompleted:
        intelligence_data = extractor.extract(full_text)
        session_manager.update_intelligence(session_id, intelligence_data)

    # 6. Check Completion Conditions
    # - Intelligence accumulated (At least one important field)
    has_intelligence = (len(session.bankAccounts) > 0 or 
                        len(session.upiIds) > 0 or 
                        len(session.phishingLinks) > 0 or 
                        len(session.phoneNumbers) > 0)
    
    # - Message limit
    limit_reached = session.totalMessages >= 6
    
    if (has_intelligence or limit_reached) and not session.conversationCompleted:
        session.conversationCompleted = True
        logger.info(f"Conversation marked COMPLETE for session {session_id}. Reasons: Intel={has_intelligence}, Limit={limit_reached}")

    # 7. Generate Agent Response (Pass session for adaptive logic)
    reply = agent.generate_response(current_text, session)
    
    # 8. Check Callback Trigger
    # Trigger ONLY if:
    # - Scam detected
    # - Conversation Completed
    # - Callback Not Sent
    
    should_send_callback = (
        session.scamDetected and 
        session.conversationCompleted and 
        not session.callbackSent
    )

    if should_send_callback:
        logger.info(f"Triggering callback for session {session_id}")
        
        final_intelligence = session_manager.get_intelligence_as_dict(session_id)
        total_exchanged = len(request.conversationHistory or []) + 2 
        
        payload = CallbackPayload(
            sessionId=session_id,
            scamDetected=True,
            totalMessagesExchanged=total_exchanged,
            extractedIntelligence=ExtractedIntelligence(**final_intelligence),
            agentNotes="Scam confirmed. Conversation completed."
        )
        
        if callback_service.send_result(payload):
            session_manager.mark_callback_sent(session_id)
    
    return ApiResponse(status="success", reply=reply)

@app.get("/")
def health_check():
    return {"status": "running"}
