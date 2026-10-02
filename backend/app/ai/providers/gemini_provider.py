import httpx
from typing import Dict, Any, Optional
from .base_provider import BaseAIProvider
from .fallback_provider import LocalFallbackProvider
from ...config import settings

class GeminiAIProvider(BaseAIProvider):
    def __init__(self):
        self.fallback = LocalFallbackProvider()
        self.api_key = settings.GEMINI_API_KEY or None
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_response(self, query: str, language: str = "en", context_items: Optional[list] = None) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.generate_response(query, language, context_items)

        try:
            # Build context from local search
            local_fallback_res = self.fallback.generate_response(query, language, context_items)
            
            system_prompt = (
                "You are MahaSeva AI, an intelligent, factual digital citizen-service assistant for Maharashtra Government schemes and services. "
                "You MUST adhere strictly to verified government records. NEVER fabricate schemes, eligibility criteria, fees, or timelines. "
                f"Respond in {language.upper()} language (use Marathi Devanagari script for 'mr', Hindi Devanagari for 'hi', English for 'en'). "
                f"Reference context: {local_fallback_res['answer']}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\nCitizen Query: {query}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 800
                }
            }

            with httpx.Client(timeout=8.0) as client:
                res = client.post(f"{self.endpoint}?key={self.api_key}", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "answer": ai_text,
                        "suggested_schemes": local_fallback_res["suggested_schemes"],
                        "suggested_services": local_fallback_res["suggested_services"],
                        "citations": local_fallback_res["citations"],
                        "confidence": 0.98
                    }
        except Exception:
            pass

        return self.fallback.generate_response(query, language, context_items)

    def analyze_document_text(self, document_type: str, content: str) -> Dict[str, Any]:
        return self.fallback.analyze_document_text(document_type, content)
