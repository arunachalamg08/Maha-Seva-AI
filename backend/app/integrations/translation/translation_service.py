import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from ...config import settings
from .google_translate import GoogleCloudTranslationProvider

class TranslationService:
    """
    Production-grade translation service with persistent database caching,
    hash-based deduplication, batch translation, and admin audit management.
    """
    def __init__(self):
        self.provider = GoogleCloudTranslationProvider()
        self.cache_file = settings.DB_DIR / "translations_cache.json"
        self._ensure_cache_file()

    def _ensure_cache_file(self):
        os.makedirs(settings.DB_DIR, exist_ok=True)
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _load_cache(self) -> List[Dict[str, Any]]:
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_cache(self, items: List[Dict[str, Any]]):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _compute_hash(self, text: str, source_lang: str, target_lang: str) -> str:
        raw = f"{source_lang}:{target_lang}:{text.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def translate_text(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "mr",
        entity_type: str = "dynamic_text",
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "none",
                "cached": True
            }

        if source_language == target_language:
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "identity",
                "cached": True
            }

        source_hash = self._compute_hash(text, source_language, target_language)
        cache = self._load_cache()

        # Check in cache
        for item in cache:
            if item.get("source_hash") == source_hash:
                return {
                    "id": item.get("id"),
                    "translated_text": item.get("translated_text"),
                    "source_language": source_language,
                    "target_language": target_language,
                    "provider": item.get("provider", "cached"),
                    "cached": True,
                    "created_at": item.get("created_at")
                }

        # Cache miss: call translation provider
        res = await self.provider.translate(text, source_language, target_language)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cache_entry = {
            "id": f"TR-{len(cache) + 1:05d}",
            "entity_type": entity_type,
            "entity_id": entity_id or f"GEN-{source_hash[:8]}",
            "source_language": source_language,
            "target_language": target_language,
            "source_text": text,
            "source_hash": source_hash,
            "translated_text": res["translated_text"],
            "provider": res["provider"],
            "created_at": now_str,
            "updated_at": now_str,
            "status": "active"
        }

        cache.append(cache_entry)
        self._save_cache(cache)

        return {
            "id": cache_entry["id"],
            "translated_text": res["translated_text"],
            "source_language": source_language,
            "target_language": target_language,
            "provider": res["provider"],
            "cached": False,
            "created_at": now_str
        }

    async def batch_translate_texts(
        self,
        texts: List[str],
        source_language: str = "en",
        target_language: str = "mr"
    ) -> List[Dict[str, Any]]:
        results = []
        for text in texts:
            r = await self.translate_text(text, source_language, target_language)
            results.append(r)
        return results

    def get_all_cached_translations(self, limit: int = 100) -> List[Dict[str, Any]]:
        cache = self._load_cache()
        return cache[-limit:]

    def update_cached_translation(self, entry_id: str, new_translation: str) -> Optional[Dict[str, Any]]:
        cache = self._load_cache()
        for item in cache:
            if item.get("id") == entry_id:
                item["translated_text"] = new_translation
                item["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item["provider"] = "manual_reviewed"
                self._save_cache(cache)
                return item
        return None

    def delete_cached_translation(self, entry_id: str) -> bool:
        cache = self._load_cache()
        filtered = [item for item in cache if item.get("id") != entry_id]
        if len(filtered) != len(cache):
            self._save_cache(filtered)
            return True
        return False

translation_service = TranslationService()
