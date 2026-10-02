from typing import Dict, Any, Optional, List
from .base_provider import BaseAIProvider
from ...core.search_engine import search_engine

class LocalFallbackProvider(BaseAIProvider):
    """
    Zero-hallucination, 100% local and offline AI reasoning provider.
    Synthesizes verified answers purely from Maharashtra Government dataset records.
    """
    def generate_response(self, query: str, language: str = "en", context_items: Optional[list] = None) -> Dict[str, Any]:
        results = search_engine.search(query, top_k=3)
        
        if not results:
            if language == "mr":
                ans = "माफ करा, मला या विषयावर थेट माहिती मिळाली नाही. कृपया आपले सरकार पोर्टल किंवा संबंधित जिल्हा सेतू केंद्राशी संपर्क साधा."
            elif language == "hi":
                ans = "क्षमा करें, मुझे इस विषय पर सटीक जानकारी नहीं मिली। कृपया आपले सरकार पोर्टल अथवा संबंधित जिला सेतु केंद्र से संपर्क करें।"
            else:
                ans = "I could not find exact matched government services for your specific query. Please consult the nearest Setu Suvidha Kendra or check the Aaple Sarkar portal (aaplesarkar.mahaonline.gov.in)."
            return {
                "answer": ans,
                "suggested_schemes": [],
                "suggested_services": [],
                "citations": ["Maharashtra Right to Public Services Act (RTS), 2015"],
                "confidence": 0.5
            }

        top_match = results[0]["meta"]
        suggested_schemes = []
        suggested_services = []
        citations = []

        for r in results:
            meta = r["meta"]
            if meta["type"] == "scheme":
                suggested_schemes.append(meta["data"])
                citations.append(meta["data"].get("source_gr", "Maharashtra Govt Resolution"))
            elif meta["type"] == "service":
                suggested_services.append(meta["data"])
                citations.append(f"RTS Statutory Delivery: {meta['data'].get('statutory_rts_days', 15)} days")

        # Synthesize multilingual response
        if top_match["type"] == "scheme":
            data = top_match["data"]
            if language == "mr":
                ans = f"**{data['name_mr']}** ({data['name_en']})\n\n" \
                      f"• **विभाग:** {data['department_name']}\n" \
                      f"• **आर्थिक लाभ:** {data['financial_benefit']}\n" \
                      f"• **पात्रता:** {data['target_beneficiary']}\n" \
                      f"• **आवश्यक कागदपत्रे:** {', '.join(data['required_documents'][:3])}\n" \
                      f"• **अर्ज करण्याची पद्धत:** {data['application_mode']}\n" \
                      f"• **अधिकृत पोर्टल:** {data['official_portal']}\n" \
                      f"• **शासन निर्णय:** {data['source_gr']}"
            elif language == "hi":
                ans = f"**{data['name_hi']}** ({data['name_en']})\n\n" \
                      f"• **विभाग:** {data['department_name']}\n" \
                      f"• **वित्तीय लाभ:** {data['financial_benefit']}\n" \
                      f"• **पात्रता:** {data['target_beneficiary']}\n" \
                      f"• **आवश्यक दस्तावेज:** {', '.join(data['required_documents'][:3])}\n" \
                      f"• **आवेदन प्रक्रिया:** {data['application_mode']}\n" \
                      f"• **आधिकारिक पोर्टल:** {data['official_portal']}\n" \
                      f"• **शासनादेश (GR):** {data['source_gr']}"
            else:
                ans = f"**{data['name_en']}** ({data['name_mr']})\n\n" \
                      f"• **Department:** {data['department_name']}\n" \
                      f"• **Benefit:** {data['financial_benefit']}\n" \
                      f"• **Target Group:** {data['target_beneficiary']}\n" \
                      f"• **Key Documents:** {', '.join(data['required_documents'][:3])}\n" \
                      f"• **Application Mode:** {data['application_mode']}\n" \
                      f"• **Official Portal:** {data['official_portal']}\n" \
                      f"• **Government Resolution:** {data['source_gr']}"

        elif top_match["type"] == "service":
            data = top_match["data"]
            steps = " -> ".join([s.split('.')[0] for s in data["procedure_steps"][:3]])
            if language == "mr":
                ans = f"**{data['name_mr']}** ({data['name_en']})\n\n" \
                      f"• **सक्षम प्राधिकारी:** {data['issuing_authority']}\n" \
                      f"• **आरटीएस हमी कालावधी:** {data['statutory_rts_days']} कामकाजाचे दिवस\n" \
                      f"• **शासकीय शुल्क:** {data['government_fee']}\n" \
                      f"• **वैधता:** {data['validity']}\n" \
                      f"• **थोडक्यात प्रक्रिया:** {steps}\n" \
                      f"• **ऑनलाइन अर्ज करा:** {data['portal_url']}"
            elif language == "hi":
                ans = f"**{data['name_hi']}** ({data['name_en']})\n\n" \
                      f"• **सक्षम अधिकारी:** {data['issuing_authority']}\n" \
                      f"• **आरटीएस वितरण अवधि:** {data['statutory_rts_days']} कार्य दिवस\n" \
                      f"• **सरकारी शुल्क:** {data['government_fee']}\n" \
                      f"• **प्रक्रिया:** {steps}\n" \
                      f"• **ऑनलाइन आवेदन:** {data['portal_url']}"
            else:
                ans = f"**{data['name_en']}** ({data['name_mr']})\n\n" \
                      f"• **Issuing Authority:** {data['issuing_authority']}\n" \
                      f"• **Statutory RTS Timeline:** {data['statutory_rts_days']} working days\n" \
                      f"• **Government Fee:** {data['government_fee']}\n" \
                      f"• **Validity:** {data['validity']}\n" \
                      f"• **Procedure Overview:** {steps}\n" \
                      f"• **Apply Online:** {data['portal_url']}"
        else:
            data = top_match["data"]
            ans = f"**{data['name_en']}** ({data['name_mr']})\n\n" \
                  f"• **Description:** {data['description']}\n" \
                  f"• **Nodal Officer:** {data['nodal_officer']}\n" \
                  f"• **Citizen Helpline:** {data['helpline']}\n" \
                  f"• **Website:** {data['website']}"

        return {
            "answer": ans,
            "suggested_schemes": suggested_schemes,
            "suggested_services": suggested_services,
            "citations": list(set(citations)),
            "confidence": 0.95
        }

    def analyze_document_text(self, document_type: str, content: str) -> Dict[str, Any]:
        text_lower = content.lower()
        missing = []
        entities = {}

        if "income" in document_type.lower() or "उत्पन्न" in document_type:
            if "tahsildar" not in text_lower and "तहसीलदार" not in text_lower and "revenue" not in text_lower:
                missing.append("Tahsildar / Revenue Seal & Signature declaration")
            if "rs" not in text_lower and "₹" not in text_lower and "lakh" not in text_lower and "rupees" not in text_lower:
                missing.append("Total Annual Family Income amount in words and figures")
            entities["detected_type"] = "Revenue Income Certificate"

        elif "caste" in document_type.lower() or "जात" in document_type:
            if "sub-divisional" not in text_lower and "sdo" not in text_lower and "उपविभागीय" not in text_lower:
                missing.append("Competent Authority (SDO / Deputy Collector) order number")
            entities["detected_type"] = "Caste / Tribe Certificate"

        elif "domicile" in document_type.lower() or "अधिवास" in document_type:
            if "15 years" not in text_lower and "resident" not in text_lower and "महाराष्ट्र" not in text_lower:
                missing.append("Explicit statement of 15 years continuous residence in Maharashtra")
            entities["detected_type"] = "Domicile & Nationality Certificate"

        status = "Pre-Screening Passed" if len(missing) == 0 else "Action Required / Missing Elements"

        return {
            "document_type": document_type,
            "is_valid_format": len(missing) == 0,
            "extracted_entities": entities,
            "detected_missing_fields": missing,
            "checklist_status": status,
            "recommended_next_steps": [
                "Verify digital signature / Barcode at Aaple Sarkar verification link",
                "Ensure applicant name matches 10th marksheet and Aadhaar exact spelling",
                "Submit within the valid financial year window"
            ]
        }
