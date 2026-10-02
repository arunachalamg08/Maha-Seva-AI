from fastapi import APIRouter
from .routes_schemes import router as schemes_router
from .routes_services import router as services_router
from .routes_eligibility import router as eligibility_router
from .routes_assistant import router as assistant_router
from .routes_grievance import router as grievance_router
from .routes_directory import router as directory_router
from .routes_documents import router as documents_router
from .routes_admin import router as admin_router
from .routes_translation import router as translation_router

api_v1_router = APIRouter()
api_v1_router.include_router(schemes_router)
api_v1_router.include_router(services_router)
api_v1_router.include_router(eligibility_router)
api_v1_router.include_router(assistant_router)
api_v1_router.include_router(grievance_router)
api_v1_router.include_router(directory_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(translation_router)
