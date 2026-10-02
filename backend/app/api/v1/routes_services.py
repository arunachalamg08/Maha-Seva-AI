from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ...core.data_loader import data_store
from ...models.schemas import ServiceBase

router = APIRouter(prefix="/services", tags=["RTS Act Services"])

@router.get("", response_model=List[ServiceBase])
def list_services(
    category: Optional[str] = Query(None, description="Filter by category (e.g. Certificates & Revenue, Land Records)"),
    department_id: Optional[str] = Query(None, description="Filter by department ID")
):
    services = data_store.get_services(category=category, department_id=department_id)
    return services

@router.get("/{service_id}", response_model=ServiceBase)
def get_service(service_id: str):
    service = data_store.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service with ID '{service_id}' not found.")
    return service
