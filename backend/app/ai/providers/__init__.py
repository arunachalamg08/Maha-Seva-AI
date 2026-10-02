from .base_provider import BaseAIProvider
from .gemini_provider import GeminiAIProvider
from .fallback_provider import LocalFallbackProvider

ai_provider = GeminiAIProvider()
