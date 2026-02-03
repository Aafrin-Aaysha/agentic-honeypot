from typing import Dict, Set, List, Optional
from pydantic import BaseModel, Field

class SessionState(BaseModel):
    sessionId: str
    totalMessages: int = 0
    lastMessage: str = ""
    callbackSent: bool = False
    scamDetected: bool = False
    # Use sets for unique accumulation (converted to list on export)
    # We can't use set directly in Pydantic v1 without config, but v2 is fine. 
    # For safety with simple Pydantic, let's use Sets internally but store as Lists or Sets in a plain class? 
    # Let's stick to Pydantic for structure but use a helper to manage it.
    bankAccounts: Set[str] = Field(default_factory=set)
    upiIds: Set[str] = Field(default_factory=set)
    phishingLinks: Set[str] = Field(default_factory=set)
    phoneNumbers: Set[str] = Field(default_factory=set)
    suspiciousKeywords: Set[str] = Field(default_factory=set)
    conversationCompleted: bool = False

    class Config:
        arbitrary_types_allowed = True

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(sessionId=session_id)
        return self.sessions[session_id]

    def update_intelligence(self, session_id: str, new_data: Dict[str, List[str]]):
        session = self.get_session(session_id)
        if "bankAccounts" in new_data:
            session.bankAccounts.update(new_data["bankAccounts"])
        if "upiIds" in new_data:
            session.upiIds.update(new_data["upiIds"])
        if "phishingLinks" in new_data:
            session.phishingLinks.update(new_data["phishingLinks"])
        if "phoneNumbers" in new_data:
            session.phoneNumbers.update(new_data["phoneNumbers"])
        if "suspiciousKeywords" in new_data:
            session.suspiciousKeywords.update(new_data["suspiciousKeywords"])

    def mark_scam_detected(self, session_id: str):
        session = self.get_session(session_id)
        session.scamDetected = True

    def increment_message_count(self, session_id: str, last_message: str = ""):
        if session_id in self.sessions:
            self.sessions[session_id].totalMessages += 1
            self.sessions[session_id].lastMessage = last_message

    def mark_callback_sent(self, session_id: str):
        session = self.get_session(session_id)
        session.callbackSent = True

    def get_intelligence_as_dict(self, session_id: str) -> Dict[str, List[str]]:
        session = self.get_session(session_id)
        return {
            "bankAccounts": list(session.bankAccounts),
            "upiIds": list(session.upiIds),
            "phishingLinks": list(session.phishingLinks),
            "phoneNumbers": list(session.phoneNumbers),
            "suspiciousKeywords": list(session.suspiciousKeywords),
        }

# Singleton
    def get_stats(self):
        total_scams = 0
        total_intel_items = 0
        recent_intel = []
        
        for sid, session in self.sessions.items():
            if session.scamDetected:
                total_scams += 1
            
            # Count collected items
            intel_count = len(session.bankAccounts) + len(session.upiIds) + len(session.phishingLinks) + len(session.phoneNumbers)
            total_intel_items += intel_count
            
            # If has intel OR is a detected scam, add to recent list
            if intel_count > 0 or session.scamDetected:
                recent_intel.append({
                    "session_id": sid,
                    "last_message": session.lastMessage,
                    "phones": session.phoneNumbers,
                    "upis": session.upiIds,
                    "links": session.phishingLinks
                })
        
        return {
            "active_sessions": len(self.sessions),
            "scams_detected": total_scams,
            "intel_items": total_intel_items,
            "recent_intel": recent_intel[-10:] # Last 10
        }

session_manager = SessionManager()
