from .patients import router as patients_router
from .chat import router as chat_router
from .audit import router as audit_router

__all__ = [
    "patients_router",
    "chat_router",
    "audit_router"
]
