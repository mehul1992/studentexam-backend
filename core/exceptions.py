"""
Custom exceptions for the application.
Follows Interface Segregation Principle by providing specific exception types.
"""


class ExamAPIException(Exception):
    """Base exception for exam-related API errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(ExamAPIException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class ValidationError(ExamAPIException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 400)


class NotFoundError(ExamAPIException):
    """Raised when a resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class BusinessLogicError(ExamAPIException):
    """Raised when business logic constraints are violated."""
    def __init__(self, message: str = "Business logic error"):
        super().__init__(message, 422)
