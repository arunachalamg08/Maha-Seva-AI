from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["platform"] == "MahaSeva AI"
    assert "dataset_summary" in data

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_schemes_list():
    res = client.get("/api/v1/schemes")
    assert res.status_code == 200
    schemes = res.json()
    assert len(schemes) >= 10
    assert any("Ladki Bahin" in s["name_en"] for s in schemes)

def test_services_list():
    res = client.get("/api/v1/services")
    assert res.status_code == 200
    services = res.json()
    assert len(services) >= 5

def test_eligibility_check_endpoint():
    payload = {
        "age": 28,
        "gender": "Female",
        "annual_income": 180000,
        "category": "Open",
        "district": "Pune",
        "is_farmer": False,
        "has_disability": False,
        "is_student": False
    }
    res = client.post("/api/v1/eligibility/check", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["eligible_count"] >= 1
    # Majhi Ladki Bahin should be eligible
    matches = {m["scheme_id"]: m["eligible"] for m in data["matches"]}
    assert matches.get("SCH-MH-001") is True

def test_assistant_query():
    payload = {
        "query": "What is Majhi Ladki Bahin Yojana?",
        "language": "en"
    }
    res = client.post("/api/v1/assistant/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 20

def test_grievance_submission_and_tracking():
    sub = {
        "citizen_name": "Suresh Kale",
        "phone_number": "9876543210",
        "district": "Nagpur",
        "department_id": "DEPT-REV",
        "category": "Ration Card Delay",
        "subject": "Delay in issuing new Ration Card",
        "description": "Applied 40 days ago, no status update from DSO office.",
        "preferred_language": "en"
    }
    res = client.post("/api/v1/grievance/submit", json=sub)
    assert res.status_code == 200
    grv = res.json()
    assert "token_id" in grv
    token = grv["token_id"]

    # Track it
    track_res = client.get(f"/api/v1/grievance/track/{token}")
    assert track_res.status_code == 200
    assert track_res.json()["found"] is True

def test_directory_departments_and_districts():
    res_dept = client.get("/api/v1/directory/departments")
    assert res_dept.status_code == 200
    assert len(res_dept.json()) >= 8

    res_dist = client.get("/api/v1/directory/districts")
    assert res_dist.status_code == 200
    assert len(res_dist.json()) >= 6
