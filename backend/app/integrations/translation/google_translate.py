import httpx
import re
from typing import List, Dict, Any
from .base import BaseTranslationProvider
from ...config import settings

class GoogleCloudTranslationProvider(BaseTranslationProvider):
    """
    Google Cloud Translation API Provider.
    Calls Google Translate v2 REST API when TRANSLATION_API_KEY is configured,
    with graceful fallback to offline dictionary translation.
    """
    def __init__(self):
        self.api_key = settings.TRANSLATION_API_KEY
        self.endpoint = "https://translation.googleapis.com/language/translate/v2"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def translate(self, text: str, source_language: str = "en", target_language: str = "mr") -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "google" if self.is_available() else "local_fallback"
            }

        if source_language == target_language:
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "identity"
            }

        # If API key is available, call Google Cloud Translation API
        if self.is_available():
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    payload = {
                        "q": text,
                        "source": source_language,
                        "target": target_language,
                        "format": "text",
                        "key": self.api_key
                    }
                    response = await client.post(self.endpoint, params={"key": self.api_key}, json={"q": text, "source": source_language, "target": target_language, "format": "text"})
                    if response.status_code == 200:
                        data = response.json()
                        translated_text = data["data"]["translations"][0]["translatedText"]
                        return {
                            "translated_text": translated_text,
                            "source_language": source_language,
                            "target_language": target_language,
                            "provider": "google"
                        }
            except Exception:
                # Log and fallback gracefully
                pass

        # Local fallback translation
        translated = self._local_translate(text, source_language, target_language)
        return {
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language,
            "provider": "local_fallback"
        }

    async def batch_translate(self, texts: List[str], source_language: str = "en", target_language: str = "mr") -> List[Dict[str, Any]]:
        if not texts:
            return []

        if self.is_available():
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    payload = {
                        "q": texts,
                        "source": source_language,
                        "target": target_language,
                        "format": "text"
                    }
                    response = await client.post(self.endpoint, params={"key": self.api_key}, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        translations = data["data"]["translations"]
                        return [
                            {
                                "translated_text": item["translatedText"],
                                "source_language": source_language,
                                "target_language": target_language,
                                "provider": "google"
                            }
                            for item in translations
                        ]
            except Exception:
                pass

        results = []
        for t in texts:
            res = await self.translate(t, source_language, target_language)
            results.append(res)
        return results

    def _local_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Rule-based dictionary fallback for essential government service terms."""
        terms = {
            "mr": {
                "Government Services": "शासकीय सेवा",
                "Home": "मुख्यपृष्ठ",
                "Schemes": "योजना",
                "Services": "सेवा",
                "Eligibility": "पात्रता",
                "Assistant": "सहाय्यक",
                "Grievances": "तक्रार निवारण",
                "Directory": "निर्देशिका",
                "Officer": "अधिकारी कक्ष",
                "One Digital Gateway for Maharashtra Government Services": "महाराष्ट्र शासन नागरिक सेवांसाठी एक डिजिटल गेटवे",
                "Income Certificate": "उत्पन्नाचे प्रमाणपत्र",
                "Domicile Certificate": "अधिवास प्रमाणपत्र",
                "Caste Certificate": "जात प्रमाणपत्र",
                "Non-Creamy Layer Certificate": "नॉन-क्रिमी लेयर प्रमाणपत्र",
                "7/12 Satbara Extract": "७/१२ सातबारा उतारा",
                "Ration Card": "रेशन कार्ड",
                "Revenue Department": "महसूल विभाग",
                "Agriculture Department": "कृषी विभाग",
                "Public Health Department": "सार्वजनिक आरोग्य विभाग",
                "Women and Child Development": "महिला व बालविकास विभाग",
                "Social Justice": "सामाजिक न्याय विभाग",
                "Submit": "सबमिट करा",
                "Search": "शोधा",
                "Track Status": "स्थिती तपासा",
                "Apply Online": "ऑनलाइन अर्ज करा",
                "Eligible": "पात्र",
                "Not Eligible": "अपात्र"
            },
            "hi": {
                "Government Services": "सरकारी सेवाएं",
                "Home": "होम",
                "Schemes": "योजनाएं",
                "Services": "सेवाएं",
                "Eligibility": "पात्रता",
                "Assistant": "सहायक",
                "Grievances": "शिकायत निवारण",
                "Directory": "निर्देशिका",
                "Officer": "अधिकारी कक्ष",
                "One Digital Gateway for Maharashtra Government Services": "महाराष्ट्र सरकारी सेवाओं के लिए एक डिजिटल गेटवे",
                "Income Certificate": "आय प्रमाण पत्र",
                "Domicile Certificate": "अधिवास प्रमाण पत्र",
                "Caste Certificate": "जाति प्रमाण पत्र",
                "Non-Creamy Layer Certificate": "नॉन-क्रीमी लेयर प्रमाण पत्र",
                "7/12 Satbara Extract": "7/12 खतौनी",
                "Ration Card": "राशन कार्ड",
                "Revenue Department": "राजस्व विभाग",
                "Agriculture Department": "कृषि विभाग",
                "Public Health Department": "सार्वजनिक स्वास्थ्य विभाग",
                "Women and Child Development": "महिला एवं बाल विकास विभाग",
                "Social Justice": "सामाजिक न्याय विभाग",
                "Submit": "सबमिट करें",
                "Search": "खोजें",
                "Track Status": "स्थिति जांचें",
                "Apply Online": "ऑनलाइन आवेदन करें",
                "Eligible": "पात्र",
                "Not Eligible": "अपात्र"
            }
        }

        # Check exact dictionary match
        if target_lang in terms and text in terms[target_lang]:
            return terms[target_lang][text]

        return text
