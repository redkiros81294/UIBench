"""
UIBench backend application.

Usage:
    uvicorn backend.app.main:app --reload
"""
from backend.app.main import create_app

__all__ = ["create_app"]
