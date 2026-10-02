import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import settings

class DataLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_all_data()
        return cls._instance

    def _load_all_data(self):
        data_dir = settings.DATA_DIR
        
        with open(data_dir / "schemes.json", "r", encoding="utf-8") as f:
            self.schemes: List[Dict[str, Any]] = json.load(f)

        with open(data_dir / "services.json", "r", encoding="utf-8") as f:
            self.services: List[Dict[str, Any]] = json.load(f)

        with open(data_dir / "departments.json", "r", encoding="utf-8") as f:
            self.departments: List[Dict[str, Any]] = json.load(f)

        with open(data_dir / "districts_kendras.json", "r", encoding="utf-8") as f:
            self.districts: List[Dict[str, Any]] = json.load(f)

        with open(data_dir / "documents_master.json", "r", encoding="utf-8") as f:
            self.documents_master: Dict[str, Any] = json.load(f)

    def get_schemes(self, category: Optional[str] = None, department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self.schemes
        if category and category.lower() != "all":
            results = [s for s in results if category.lower() in s["category"].lower()]
        if department_id:
            results = [s for s in results if s["department_id"] == department_id]
        return results

    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for s in self.schemes:
            if s["id"].lower() == scheme_id.lower():
                return s
        return None

    def get_services(self, category: Optional[str] = None, department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self.services
        if category and category.lower() != "all":
            results = [s for s in results if category.lower() in s["category"].lower()]
        if department_id:
            results = [s for s in results if s["department_id"] == department_id]
        return results

    def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        for s in self.services:
            if s["id"].lower() == service_id.lower():
                return s
        return None

    def get_departments(self) -> List[Dict[str, Any]]:
        return self.departments

    def get_department_by_id(self, dept_id: str) -> Optional[Dict[str, Any]]:
        for d in self.departments:
            if d["id"].lower() == dept_id.lower():
                return d
        return None

    def get_districts(self) -> List[Dict[str, Any]]:
        return self.districts

    def get_district_by_id(self, district_id: str) -> Optional[Dict[str, Any]]:
        for d in self.districts:
            if d["district_id"].lower() == district_id.lower() or d["district_name_en"].lower() == district_id.lower():
                return d
        return None

    def get_documents_master(self) -> Dict[str, Any]:
        return self.documents_master

data_store = DataLoader()
