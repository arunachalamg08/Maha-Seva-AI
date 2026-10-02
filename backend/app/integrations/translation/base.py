from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTranslationProvider(ABC):
    """Abstract Base Class for Translation Providers."""
    
    @abstractmethod
    async def translate(self, text: str, source_language: str = "en", target_language: str = "mr") -> Dict[str, Any]:
        """Translate a single string from source to target language."""
        pass

    @abstractmethod
    async def batch_translate(self, texts: List[str], source_language: str = "en", target_language: str = "mr") -> List[Dict[str, Any]]:
        """Translate multiple strings in a single batch request."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass
