"""Custom domain exceptions."""


class DomainError(Exception):
    """Base class for all domain-specific exceptions."""


class ValidationError(DomainError):
    """Raised when input data is invalid."""


class NotFoundError(DomainError):
    """Raised when an entity is not found."""


class InvalidStateTransitionError(DomainError):
    """Raised when an invalid lifecycle transition is requested."""


class ResourceUnavailableError(DomainError):
    """Raised when a resource cannot be used right now."""


class PaymentError(DomainError):
    """Raised when payment processing fails."""
