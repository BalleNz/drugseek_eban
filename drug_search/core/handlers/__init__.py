from .assistant_handler import assistant_router
from .auth_handler import auth_router
from .drug_handler import drug_router
from .user_handler import user_router

__all__ = [
    "auth_router",
    "drug_router",
    "user_router",
    "assistant_router"
]