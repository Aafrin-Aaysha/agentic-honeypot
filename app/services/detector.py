class ScamDetector:
    def __init__(self):
        # Heuristic keywords for initial version
        self.keywords = [
            "bank account", "verify immediately", "blocked", "suspended",
            "cancel your order", "lottery", "winner", "urgent", "credit card",
            "kyc", "electricity bill", "upi id", "otp"
        ]

    def detect(self, text: str) -> bool:
        """
        Detects if the message text contains scam indicators.
        In the future, this can be swapped with an LLM call.
        """
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword in text_lower:
                return True
        return False

# Singleton instance
detector = ScamDetector()
