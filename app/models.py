from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Message(BaseModel):
    sender: Optional[str] = "user"
    text: str
    timestamp: Optional[str] = None
    
    class Config:
        populate_by_name = True

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class IncomingRequest(BaseModel):
    sessionId: Optional[str] = Field(default="global-session", alias="session_id")
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[Metadata] = None

    class Config:
        populate_by_name = True

class ApiResponse(BaseModel):
    status: str
    reply: str

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class CallbackPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str
