from .polish import router as polish_router
from .anti_ai import router as anti_ai_router
from .upload import router as upload_router
from .auth import router as auth_router

__all__ = ["polish_router", "anti_ai_router", "upload_router", "auth_router"]
