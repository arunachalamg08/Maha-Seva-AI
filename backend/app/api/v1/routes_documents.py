from fastapi import APIRouter
from typing import Dict, Any
from ...core.data_loader import data_store
from ...models.schemas import DocumentAnalysisRequest, DocumentAnalysisResponse
from ...ai.providers import ai_provider

router = APIRouter(prefix="/documents", tags=["Document Intelligence"])

@router.get("/master")
def get_master_documents() -> Dict[str, Any]:
    return data_store.get_documents_master()

@router.post("/pre-screen", response_model=DocumentAnalysisResponse)
def pre_screen_document(req: DocumentAnalysisRequest):
    res = ai_provider.analyze_document_text(
        document_type=req.document_type,
        content=req.content_text
    )
    return DocumentAnalysisResponse(**res)
