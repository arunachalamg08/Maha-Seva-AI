from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAIProvider(ABC):
    @abstractmethod
    def generate_response(self, query: str, language: str = "en", context_items: Optional[list] = None) -> Dict[str, Any]:
        """Generate conversational answer for citizen inquiry based on verified context."""
        pass

    @abstractmethod
    def analyze_document_text(self, document_type: str, content: str) -> Dict[str, Any]:
        """Analyze citizen uploaded document text and verify key fields."""
        pass
