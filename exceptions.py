"""Custom exceptions for GDPR/CCPA Compliance Checker."""


class ComplianceCheckerError(Exception):
    """Base exception for all compliance checker errors."""
    pass


class ScanError(ComplianceCheckerError):
    """Raised when a website scan fails."""
    pass


class NetworkError(ScanError):
    """Raised when network request fails."""
    pass


class InvalidURLError(ComplianceCheckerError):
    """Raised when URL is invalid or malformed."""
    pass


class DatabaseError(ComplianceCheckerError):
    """Raised when database operation fails."""
    pass


class AIServiceError(ComplianceCheckerError):
    """Raised when AI service call fails."""
    pass


class ConfigurationError(ComplianceCheckerError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(ComplianceCheckerError):
    """Raised when input validation fails."""
    pass
