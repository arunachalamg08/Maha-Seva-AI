import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.search_engine import search_engine

client = TestClient(app)

def test_translation_translate_endpoint():
    payload = {
        "text": "Government Services",
        "source_language": "en",
        "target_language": "mr"
    }
    res = client.post("/api/v1/translation/translate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "translated_text" in data
    assert data["target_language"] == "mr"
    assert "शासकीय सेवा" in data["translated_text"] or len(data["translated_text"]) > 0

def test_translation_batch_endpoint():
    payload = {
        "texts": ["Home", "Services", "Eligibility", "Grievances"],
        "source_language": "en",
        "target_language": "mr"
    }
    res = client.post("/api/v1/translation/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    assert len(data["translations"]) == 4

def test_translation_cache_management():
    # 1. Translate string to ensure it gets cached
    t_res = client.post("/api/v1/translation/translate", json={
        "text": "Income Certificate",
        "source_language": "en",
        "target_language": "mr",
        "entity_type": "service_name",
        "entity_id": "SRV-MH-001"
    })
    assert t_res.status_code == 200
    cache_item = t_res.json()
    assert "id" in cache_item
    entry_id = cache_item["id"]

    # 2. Query cache list
    c_res = client.get("/api/v1/translation/cache")
    assert c_res.status_code == 200
    cache_list = c_res.json()
    assert cache_list["total"] >= 1

    # 3. Update cache entry
    u_res = client.put(f"/api/v1/translation/cache/{entry_id}", json={
        "new_translation": "उत्पन्नाचा अधिकृत दाखला (RTS)"
    })
    assert u_res.status_code == 200
    assert u_res.json()["translated_text"] == "उत्पन्नाचा अधिकृत दाखला (RTS)"

    # 4. Next translate call should return the updated cached text
    re_res = client.post("/api/v1/translation/translate", json={
        "text": "Income Certificate",
        "source_language": "en",
        "target_language": "mr"
    })
    assert re_res.status_code == 200
    assert re_res.json()["cached"] is True
    assert re_res.json()["translated_text"] == "उत्पन्नाचा अधिकृत दाखला (RTS)"

def test_cross_lingual_marathi_search():
    # Searching in Marathi should find farmer schemes
    results_farmer = search_engine.search("शेतकऱ्यांसाठी योजना", top_k=5)
    assert len(results_farmer) > 0
    top_ids = [r["meta"]["id"] for r in results_farmer]
    assert "SCH-MH-002" in top_ids or "SCH-MH-008" in top_ids  # Namo Shetkari or Magel Tyala Shettale

    # Searching for income certificate in Marathi
    results_cert = search_engine.search("उत्पन्न दाखला", top_k=5)
    assert len(results_cert) > 0
    top_service_ids = [r["meta"]["id"] for r in results_cert]
    assert "SRV-MH-001" in top_service_ids

def test_ai_assistant_multilingual_responses():
    # Test Marathi response
    res_mr = client.post("/api/v1/assistant/ask", json={
        "query": "लाडकी बहीण योजनेची माहिती द्या",
        "language": "mr"
    })
    assert res_mr.status_code == 200
    assert "लाडकी बहीण" in res_mr.json()["answer"] or "योजना" in res_mr.json()["answer"]

    # Test Hindi response
    res_hi = client.post("/api/v1/assistant/ask", json={
        "query": "लाड़की बहिन योजना की पात्रता क्या है?",
        "language": "hi"
    })
    assert res_hi.status_code == 200
    assert "योजना" in res_hi.json()["answer"] or "पात्रता" in res_hi.json()["answer"]

    # Test English response
    res_en = client.post("/api/v1/assistant/ask", json={
        "query": "Tell me about Ladki Bahin Yojana",
        "language": "en"
    })
    assert res_en.status_code == 200
    assert "Ladki Bahin" in res_en.json()["answer"] or "Department" in res_en.json()["answer"]
