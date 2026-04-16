"""
core/exceptions.py
------------------
Custom exception hierarchy for the Jyotish API.

Raise these from services — routers catch them and convert to HTTPException.
This keeps HTTP concerns out of the service layer.
"""


class JyotishBaseError(Exception):
    """Base for all application errors."""
    pass


class InvalidBirthDataError(JyotishBaseError):
    """Birth data failed validation (bad date, missing fields, etc.)."""
    pass


class ChartComputationError(JyotishBaseError):
    """Error during astrological chart computation."""
    pass


class InvalidPlanetError(JyotishBaseError):
    """Unknown or unsupported planet name supplied."""
    pass


class InvalidSignError(JyotishBaseError):
    """Unknown or unsupported zodiac sign supplied."""
    pass


class AuthenticationError(JyotishBaseError):
    """API key missing or not found in DB."""
    pass


class InactiveAccountError(JyotishBaseError):
    """API key exists but account is not active."""
    pass


class RateLimitExceededError(JyotishBaseError):
    """User has exceeded their daily API call limit."""
    pass


class DatabaseError(JyotishBaseError):
    """Unexpected database error."""
    pass
