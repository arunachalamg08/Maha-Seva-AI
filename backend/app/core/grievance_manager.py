import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..config import settings
from ..models.schemas import GrievanceSubmission, GrievanceRecord, GrievanceTimelineEvent
from .data_loader import data_store

class GrievanceManager:
    def __init__(self):
        self.db_file = settings.DB_DIR / "grievances.json"
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(settings.DB_DIR, exist_ok=True)
        if not os.path.exists(self.db_file):
            # Seed with sample realistic grievances
            initial_data = [
                {
                    "token_id": "MH-GRV-2026-8492",
                    "citizen_name": "Ramesh Tukaram Patil",
                    "phone_number": "9822019482",
                    "email": "ramesh.patil@example.com",
                    "district": "Pune",
                    "taluka": "Haveli",
                    "department_id": "DEPT-REV",
                    "department_name": "Revenue and Forest Department",
                    "category": "Land Records / 7-12 Delay",
                    "subject": "Delay in mutation entry (Ferfar) for agricultural land",
                    "description": "Submitted online application for mutation entry 45 days ago at Haveli Tahsil office. Statutory RTS period is 30 days.",
                    "priority_level": "High",
                    "priority_score": 85,
                    "current_status": "Under Investigation",
                    "assigned_officer": "Naib Tahsildar (Revenue) Haveli",
                    "sla_target_days": 15,
                    "days_remaining": 4,
                    "created_at": (datetime.now() - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                    "timeline": [
                        {
                            "timestamp": (datetime.now() - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S"),
                            "stage": "Registered",
                            "status": "Submitted",
                            "officer_remark": "Grievance registered and assigned tracking token MH-GRV-2026-8492.",
                            "updated_by": "MahaSeva Automated System"
                        },
                        {
                            "timestamp": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"),
                            "stage": "Assigned",
                            "status": "In Review",
                            "officer_remark": "Assigned to Circle Officer Haveli for Talathi verification.",
                            "updated_by": "District Nodal Officer (Pune)"
                        },
                        {
                            "timestamp": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                            "stage": "Under Investigation",
                            "status": "Action In Progress",
                            "officer_remark": "Notice served to Talathi to complete pending ferfar within 5 working days.",
                            "updated_by": "Naib Tahsildar (Haveli)"
                        }
                    ]
                }
            ]
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _load_all(self) -> List[Dict[str, Any]]:
        with open(self.db_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_all(self, data: List[Dict[str, Any]]):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_grievance(self, sub: GrievanceSubmission) -> GrievanceRecord:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        token_num = random.randint(1000, 9999)
        token_id = f"MH-GRV-2026-{token_num}"

        # Determine department name
        dept = data_store.get_department_by_id(sub.department_id)
        dept_name = dept["name_en"] if dept else "General Administration Department"

        # Calculate priority
        desc_lower = sub.description.lower() + " " + sub.subject.lower()
        priority_score = 50
        priority_level = "Standard"

        critical_keywords = ["emergency", "corruption", "bribe", "hospital", "life", "accident", "suicide", "starvation"]
        high_keywords = ["delay", "rts", "pension", "ration", "water", "scholarship", "crop loss", "electricity"]

        if any(w in desc_lower for w in critical_keywords):
            priority_score = 95
            priority_level = "Critical"
        elif any(w in desc_lower for w in high_keywords):
            priority_score = 75
            priority_level = "High"

        sla_days = 7 if priority_level == "Critical" else (15 if priority_level == "High" else 30)

        record_dict = {
            "token_id": token_id,
            "citizen_name": sub.citizen_name,
            "phone_number": sub.phone_number,
            "email": sub.email,
            "district": sub.district,
            "taluka": sub.taluka or "District HQ",
            "department_id": sub.department_id,
            "department_name": dept_name,
            "category": sub.category,
            "subject": sub.subject,
            "description": sub.description,
            "priority_level": priority_level,
            "priority_score": priority_score,
            "current_status": "Registered",
            "assigned_officer": f"Nodal Officer ({dept_name}, {sub.district})",
            "sla_target_days": sla_days,
            "days_remaining": sla_days,
            "created_at": now_str,
            "updated_at": now_str,
            "timeline": [
                {
                    "timestamp": now_str,
                    "stage": "Registered",
                    "status": "Submitted",
                    "officer_remark": f"Grievance received under Maharashtra Citizen Redressal Framework. Token #{token_id} assigned.",
                    "updated_by": "MahaSeva Citizen Gateway"
                }
            ]
        }

        all_records = self._load_all()
        all_records.insert(0, record_dict)
        self._save_all(all_records)

        return GrievanceRecord(**record_dict)

    def get_by_token(self, token_id: str) -> Optional[GrievanceRecord]:
        all_records = self._load_all()
        for r in all_records:
            if r["token_id"].strip().upper() == token_id.strip().upper():
                return GrievanceRecord(**r)
        return None

    def list_all(self, limit: int = 50) -> List[GrievanceRecord]:
        all_records = self._load_all()
        return [GrievanceRecord(**r) for r in all_records[:limit]]

    def update_status(self, token_id: str, new_status: str, remark: str, updated_by: str) -> Optional[GrievanceRecord]:
        all_records = self._load_all()
        for r in all_records:
            if r["token_id"].strip().upper() == token_id.strip().upper():
                r["current_status"] = new_status
                r["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                r["timeline"].append({
                    "timestamp": r["updated_at"],
                    "stage": new_status,
                    "status": new_status,
                    "officer_remark": remark,
                    "updated_by": updated_by
                })
                self._save_all(all_records)
                return GrievanceRecord(**r)
        return None

grievance_manager = GrievanceManager()
