from slowapi import Limiter
from slowapi.util import get_remote_address

"""
Application rate limiter configuration.

Uses client IP address to identify request source
and apply request rate limits.
"""

limiter = Limiter(key_func=get_remote_address)
