"""
Storage backend factory.
"""
from typing import Optional
from ..config.settings import StorageConfig
from .base import StorageBackend
from .sqlalchemy_storage import SQLAlchemyStorage
from ..utils.logging import get_logger

logger = get_logger(__name__)


def get_storage_backend(model_class=None) -> StorageBackend:
    """
    Get the appropriate storage backend based on configuration.
    
    Args:
        model_class: Deprecated - kept for backward compatibility, not used
    
    Returns:
        Storage backend instance (SQLAlchemy by default)
    """
    backend_type = StorageConfig.STORAGE_BACKEND.lower()
    
    # Default to SQLAlchemy storage
    if backend_type in ['database', 'sqlite', 'sqlalchemy']:
        logger.info("Using SQLAlchemyStorage backend")
        return SQLAlchemyStorage()
    elif backend_type == 'sheets':
        # TODO: Implement Google Sheets backend
        logger.warning("Google Sheets backend not yet implemented, falling back to SQLAlchemy")
        return SQLAlchemyStorage()
    elif backend_type == 'mongodb':
        # TODO: Implement MongoDB backend
        logger.warning("MongoDB backend not yet implemented, falling back to SQLAlchemy")
        return SQLAlchemyStorage()
    else:
        logger.warning(f"Unknown storage backend '{backend_type}', using SQLAlchemy")
        return SQLAlchemyStorage()

