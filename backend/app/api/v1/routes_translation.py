from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...integrations.translation import translation_service

router = APIRouter(prefix="/translation", tags=["Translation API"])

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "mr"
    entity_type: Optional[str] = "dynamic_text"
    entity_id: Optional[str] = None

class BatchTranslationRequest(BaseModel):
    texts: List[str]
    source_language: str = "en"
    target_language: str = "mr"

class TranslationUpdatePayload(BaseModel):
    new_translation: str

@router.post("/translate")
async def translate_single(payload: TranslationRequest):
    return await translation_service.translate_text(
        text=payload.text,
        source_language=payload.source_language,
        target_language=payload.target_language,
        entity_type=payload.entity_type or "dynamic_text",
        entity_id=payload.entity_id
    )

@router.post("/batch")
async def translate_batch(payload: BatchTranslationRequest):
    results = await translation_service.batch_translate_texts(
        texts=payload.texts,
        source_language=payload.source_language,
        target_language=payload.target_language
    )
    return {
        "total": len(results),
        "translations": results
    }

@router.get("/cache")
def get_translation_cache(limit: int = Query(100, ge=1, le=500)):
    items = translation_service.get_all_cached_translations(limit=limit)
    return {
        "total": len(items),
        "entries": items
    }

@router.put("/cache/{entry_id}")
def update_translation_cache_entry(entry_id: str, payload: TranslationUpdatePayload):
    updated = translation_service.update_cached_translation(entry_id, payload.new_translation)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Translation entry '{entry_id}' not found.")
    return updated

@router.delete("/cache/{entry_id}")
def delete_translation_cache_entry(entry_id: str):
    deleted = translation_service.delete_cached_translation(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Translation entry '{entry_id}' not found.")
    return {"success": True, "message": f"Translation entry '{entry_id}' deleted."}
