"""
REST API for Epochal Capital.

Provides FastAPI-based endpoints for:
- Company management
- Deal pipeline
- Investment tracking
- Alerts
- Research
- Portfolio analytics
"""

from epochal.api.app import create_app, app
from epochal.api.routes import router

__all__ = [
    "create_app",
    "app",
    "router",
]
