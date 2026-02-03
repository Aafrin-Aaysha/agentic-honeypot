import random
from typing import List
from app.models import Message
from app.services.state import SessionState

class AgentService:
    def __init__(self):
        self.persona = "Naive Elderly Person"
        
        # Responses by category
        self.confusion_responses = [
            "Oh dear, I don't understand. Why is this happening?",
            "My grandson usually helps me with this. Can you explain slowly?",
            "I am very worried. Will I lose my money?",
            "Is there a fee to verify? I am confused."
        ]
        
        self.probing_responses = {
            "missing_upi": [
                "I have my UPI app open. What ID should I send it to?",
                "Can you give me the UPI address again? I can't find it.",
                "Where do I send the money? Is there a UPI ID?"
            ],
            "missing_phone": [
                "Is there a number I can call for help? I'm having trouble typing.",
                "Can I speak to a human? Please give me a phone number.",
                "It's hard to text. Do you have a helpline number?"
            ],
            "missing_link": [
                "You mentioned a link? I don't see one properly.",
                "Is there a website I should go to?",
                "My screen is small. Can you send the link again?"
            ],
            "general": [
                "What details do you need exactly? I have my passbook.",
                "Please don't block my account, I need to pay for my medicine.",
                "I am ready to verify. What should I do next?"
            ]
        }
        
        self.disengage_responses = [
            "I need to ask my son about this when he gets home.",
            "I am feeling dizzy. I need to rest a bit.",
            "Let me look for my glasses. I'll reply later.",
            "I need time to think about this.",
            "Please wait, someone is at the door."
        ]

    def generate_response(self, message_text: str, session: SessionState) -> str:
        """
        Generates an adaptive response based on session state and turns.
        """
        # If conversation is already marked complete, disengage
        if session.conversationCompleted:
            return random.choice(self.disengage_responses)

        # Turn-based strategy
        if session.totalMessages <= 2:
            return random.choice(self.confusion_responses)
        
        elif 3 <= session.totalMessages <= 5:
            # Check what intelligence we are missing
            if not session.upiIds:
                return random.choice(self.probing_responses["missing_upi"])
            elif not session.phoneNumbers:
                return random.choice(self.probing_responses["missing_phone"])
            elif not session.phishingLinks:
                return random.choice(self.probing_responses["missing_link"])
            else:
                return random.choice(self.probing_responses["general"])
        
        else:
            # Turn 6+: Stall/Disengage
            return random.choice(self.disengage_responses)

agent = AgentService()
