from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import api_v1_router
from .core.data_loader import data_store
from .core.search_engine import search_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="One Intelligent Digital Gateway for Maharashtra Government Services — Prototype Platform",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "online",
        "rts_act_support": settings.RTS_ACT_NAME,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "dataset_summary": {
            "schemes_loaded": len(data_store.schemes),
            "services_loaded": len(data_store.services),
            "departments_loaded": len(data_store.departments),
            "districts_loaded": len(data_store.districts)
        },
        "disclaimer": "This platform is an AI-powered prototype citizen-service gateway for Maharashtra. For official submissions, citizens are directed to Aaple Sarkar and MahaDBT portals."
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "search_index_size": len(search_engine.doc_metadata)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
