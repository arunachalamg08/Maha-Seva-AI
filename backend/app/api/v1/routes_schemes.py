from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ...core.data_loader import data_store
from ...models.schemas import SchemeBase

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])

@router.get("", response_model=List[SchemeBase])
def list_schemes(
    category: Optional[str] = Query(None, description="Filter by category (e.g. Agriculture, Education, Women & Child)"),
    department_id: Optional[str] = Query(None, description="Filter by department ID")
):
    schemes = data_store.get_schemes(category=category, department_id=department_id)
    return schemes

@router.get("/categories", response_model=List[str])
def get_scheme_categories():
    categories = list(set([s["category"] for s in data_store.schemes]))
    categories.sort()
    return categories

@router.get("/{scheme_id}", response_model=SchemeBase)
def get_scheme(scheme_id: str):
    scheme = data_store.get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme with ID '{scheme_id}' not found.")
    return scheme
