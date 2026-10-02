from fastapi import APIRouter
from ...models.schemas import AssistantQuery, AssistantResponse
from ...ai.providers import ai_provider

router = APIRouter(prefix="/assistant", tags=["MahaSeva AI Assistant"])

@router.post("/ask", response_model=AssistantResponse)
def ask_assistant(payload: AssistantQuery):
    res = ai_provider.generate_response(
        query=payload.query,
        language=payload.language or "en"
    )
    
    return AssistantResponse(
        answer=res["answer"],
        language=payload.language or "en",
        suggested_schemes=res.get("suggested_schemes", []),
        suggested_services=res.get("suggested_services", []),
        source_citations=res.get("citations", []),
        confidence_score=res.get("confidence", 0.95),
        disclaimer="MahaSeva AI Citizen Assistant provides verified guidance under Maharashtra RTS Act standards. Always cross-verify on official portals."
    )

@router.get("/suggestions")
def get_sample_questions(lang: str = "en"):
    if lang == "mr":
        return [
            "माझी लाडकी बहीण योजनेची पात्रता आणि कागदपत्रे काय आहेत?",
            "नमो शेतकरी महासन्मान निधीसाठी कसा अर्ज करावा?",
            "तहसीलदारांकडून उत्पन्नाचा दाखला काढण्यासाठी किती दिवस लागतात?",
            "महात्मा फुले जन आरोग्य योजनेत किती लाखांचे मोफत उपचार मिळतात?",
            "डिजिटल ७/१२ उतारा ऑनलाइन कसा काढायचा?"
        ]
    elif lang == "hi":
        return [
            "माझी लाड़की बहिन योजना की पात्रता एवं आवश्यक दस्तावेज क्या हैं?",
            "नमो शेतकरी महासम्मान निधि के लिए आवेदन कैसे करें?",
            "आय प्रमाण पत्र प्राप्त करने में कितने दिन लगते हैं?",
            "महात्मा फुले जन आरोग्य योजना में कितना स्वास्थ्य बीमा मिलता है?",
            "डिजिटल 7/12 खतौनी ऑनलाइन कैसे निकालें?"
        ]
    else:
        return [
            "What are the eligibility criteria for Mukhyamantri Majhi Ladki Bahin Yojana?",
            "How to apply for Namo Shetkari Mahasanman Nidhi for farmers?",
            "What is the statutory RTS delivery timeline for Income Certificate?",
            "How much cashless coverage is provided under MJPJAY Health Scheme?",
            "How can I download a digitally signed 7/12 Satbara extract online?"
        ]
