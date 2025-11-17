"""Rate limiting utilities."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# Rate limit configurations
RATE_LIMITS = {
    "job_submit": "10/minute",
    "api_default": "100/hour",
    "auth": "5/minute"
}
