"""
Rate limiting setup.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def setup_rate_limit(app):
    app.state.limiter = limiter
