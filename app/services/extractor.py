import re
from typing import List, Dict

class IntelligenceExtractor:
    def __init__(self):
        self.upi_pattern = re.compile(r"[\w\.\-_]+@[\w]+")
        # Simplified regex for demo; strict validation can be added
        self.phone_pattern = re.compile(r"(\+91[\-\s]?)?[6-9]\d{9}")
        self.url_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        self.bank_keywords = ["account", "verify", "pay", "deposit", "transfer"]

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts intelligence from the text.
        """
        intelligence = {
            "bankAccounts": [],  # High false positive rate with regex, better with LLM or specific format (IFSC + Acc)
            "upiIds": self.upi_pattern.findall(text),
            "phishingLinks": self.url_pattern.findall(text),
            "phoneNumbers": self.phone_pattern.findall(text),
            "suspiciousKeywords": [kw for kw in self.bank_keywords if kw in text.lower()]
        }
        
        # Simple heuristic for potential account numbers (usually 9-18 digits)
        # Needs to be careful not to pick up phone numbers.
        # This is a placeholder for more advanced NER.
        potential_accounts = re.findall(r"\b\d{9,18}\b", text)
        # Filter out things that look like phone numbers (10 digits starting with 6-9)
        intelligence["bankAccounts"] = [
            acc for acc in potential_accounts 
            if not (len(acc) == 10 and int(acc[0]) >= 6)
        ]

        return intelligence

extractor = IntelligenceExtractor()
