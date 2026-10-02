from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ...core.data_loader import data_store
from ...core.search_engine import search_engine
from ...models.schemas import DepartmentInfo, DistrictInfo

router = APIRouter(prefix="/directory", tags=["Departments & Setu Directory"])

@router.get("/departments", response_model=List[DepartmentInfo])
def get_departments():
    return data_store.get_departments()

@router.get("/departments/{dept_id}", response_model=DepartmentInfo)
def get_department(dept_id: str):
    dept = data_store.get_department_by_id(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

@router.get("/districts", response_model=List[DistrictInfo])
def get_districts():
    return data_store.get_districts()

@router.get("/districts/{district_id}", response_model=DistrictInfo)
def get_district(district_id: str):
    dist = data_store.get_district_by_id(district_id)
    if not dist:
        raise HTTPException(status_code=404, detail="District not found")
    return dist

@router.get("/search")
def global_search(q: str = Query(..., min_length=1)):
    results = search_engine.search(q, top_k=8)
    return {
        "query": q,
        "total_results": len(results),
        "results": [r["meta"] for r in results]
    }
