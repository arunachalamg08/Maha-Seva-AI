import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .data_loader import data_store

# Multilingual cross-lingual synonym & entity expansion map
CROSS_LINGUAL_SYNONYMS = {
    # Marathi / Hindi / English cross mappings
    "शेतकरी": ["farmer", "agriculture", "shetkari", "krishi", "namo shetkari", "shettale"],
    "शेतकऱ्यांसाठी": ["farmer", "agriculture", "shetkari", "krishi", "namo shetkari"],
    "किसान": ["farmer", "agriculture", "kisan", "krishi", "namo shetkari"],
    "महिला": ["women", "female", "ladki bahin", "girl child", "lek ladki", "kanya"],
    "बहीण": ["ladki bahin", "sister", "women", "mahila"],
    "विद्यार्थी": ["student", "scholarship", "education", "ebc", "shishyavrutti", "swadhar", "hostel"],
    "छात्र": ["student", "scholarship", "education", "ebc", "shishyavrutti"],
    "उत्पन्न": ["income", "tahsildar", "certificate", "utpanna"],
    "दाखला": ["certificate", "income", "caste", "domicile", "rts", "dakhla"],
    "प्रमाण पत्र": ["certificate", "income", "caste", "domicile", "rts"],
    "जात": ["caste", "caste certificate", "sc", "st", "obc", "vjnt"],
    "जाति": ["caste", "caste certificate", "sc", "st", "obc"],
    "अधिवास": ["domicile", "nationality", "15 years residence"],
    "आरोग्य": ["health", "mjpjay", "medical", "cashless", "ayushman"],
    "स्वास्थ्य": ["health", "mjpjay", "medical", "cashless"],
    "सातबारा": ["7/12", "satbara", "land record", "utara", "mahabhumi"],
    "७/१२": ["7/12", "satbara", "land record", "utara", "mahabhumi"],
    "रेशन": ["ration", "ration card", "food", "mahafood", "annapurna"],
    "पेन्शन": ["pension", "sanjay gandhi", "shravanbal", "niradhar", "elderly"],
    "तक्रार": ["grievance", "complaint", "redressal", "lokshahi", "status"]
}

class SemanticSearchEngine:
    def __init__(self):
        self.documents = []
        self.doc_metadata = []
        self._build_index()

    def _build_index(self):
        self.documents = []
        self.doc_metadata = []

        # Index schemes
        for s in data_store.schemes:
            text = f"{s['name_en']} {s['name_mr']} {s['name_hi']} {s['category']} {s['department_name']} {s['short_description']} {s['target_beneficiary']} {s['financial_benefit']} " + " ".join(s['required_documents']) + " " + " ".join(s['eligibility']['criteria_points'])
            self.documents.append(text)
            self.doc_metadata.append({
                "type": "scheme",
                "id": s["id"],
                "title_en": s["name_en"],
                "title_mr": s["name_mr"],
                "title_hi": s["name_hi"],
                "category": s["category"],
                "benefit": s["financial_benefit"],
                "data": s
            })

        # Index services
        for s in data_store.services:
            req_docs = " ".join([d["name"] + " " + " ".join(d["options"]) for d in s["required_documents"]])
            proc = " ".join(s["procedure_steps"])
            text = f"{s['name_en']} {s['name_mr']} {s['name_hi']} {s['category']} {s['department_name']} {s['short_description']} {s['issuing_authority']} {req_docs} {proc}"
            self.documents.append(text)
            self.doc_metadata.append({
                "type": "service",
                "id": s["id"],
                "title_en": s["name_en"],
                "title_mr": s["name_mr"],
                "title_hi": s["name_hi"],
                "category": s["category"],
                "rts_days": s["statutory_rts_days"],
                "data": s
            })

        # Index departments
        for d in data_store.departments:
            text = f"{d['name_en']} {d['name_mr']} {d['name_hi']} {d['description']} {d['nodal_officer']} {d['helpline']}"
            self.documents.append(text)
            self.doc_metadata.append({
                "type": "department",
                "id": d["id"],
                "title_en": d["name_en"],
                "title_mr": d["name_mr"],
                "title_hi": d["name_hi"],
                "category": "Department",
                "data": d
            })

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None, max_features=8000)
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        cleaned_query = query.strip()
        expanded_terms = [cleaned_query]

        # Cross-lingual expansion
        for key, syns in CROSS_LINGUAL_SYNONYMS.items():
            if key in cleaned_query:
                expanded_terms.extend(syns)

        full_query = " ".join(expanded_terms)
        query_vec = self.vectorizer.transform([full_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        results = []
        for idx, score in enumerate(similarities):
            meta = self.doc_metadata[idx]
            boost = 0.0
            q_lower = cleaned_query.lower()

            # Exact keyword containment checks in English, Marathi, Hindi titles
            if meta["title_en"].lower() in q_lower or any(t.lower() in meta["title_en"].lower() for t in q_lower.split()):
                boost += 0.3
            if meta["title_mr"] in cleaned_query or any(w in meta["title_mr"] for w in cleaned_query.split() if len(w) > 2):
                boost += 0.4
            if meta["title_hi"] in cleaned_query or any(w in meta["title_hi"] for w in cleaned_query.split() if len(w) > 2):
                boost += 0.4

            final_score = float(score + boost)
            if final_score > 0.03:
                results.append({
                    "score": round(final_score, 4),
                    "meta": meta
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

search_engine = SemanticSearchEngine()
