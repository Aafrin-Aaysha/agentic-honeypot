from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.models import IncomingRequest, ApiResponse, CallbackPayload, ExtractedIntelligence
from app.services.detector import detector
from app.services.agent import agent
from app.services.extractor import extractor
from app.services.callback import callback_service
from app.services.state import session_manager
from app.dashboard import DASHBOARD_HTML
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("honey-pot")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    return DASHBOARD_HTML

@app.get("/api/stats")
async def get_stats():
    return session_manager.get_stats()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    body = await request.body()
    try:
        body_str = body.decode()
    except:
        body_str = "unable to decode"
    
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "INVALID_REQUEST_BODY",
            "detail": exc.errors(),
            "received_body": body_str
        },
    )

async def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.post("/api/v1/message", response_model=ApiResponse)
async def handle_message(request: IncomingRequest, api_key: str = Depends(verify_api_key)):
    session_id = request.sessionId
    
    # Extract message text from multiple possible locations
    current_text = None
    if request.text:
        current_text = request.text
    elif request.message:
        if isinstance(request.message, str):
            current_text = request.message
        elif hasattr(request.message, 'text'):
            current_text = request.message.text
            
    if not current_text:
        logger.warning(f"No text content found in request for session {session_id}")
        current_text = "" # Default to empty string instead of failing
        
    logger.info(f"Processing message for session {session_id}: {current_text[:50]}...")

    # 1. Initialize/Get Session & details
    session = session_manager.get_session(session_id)
    
    # 2. Increment Message Count
    session_manager.increment_message_count(session_id, current_text)
    
    # 3. Analyze content
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
