from .auth import auth_router
from .drug import drug_router
from .user import user_router

__all__ = ["auth_router", "drug_router", "user_router"]