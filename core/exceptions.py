class ExamAPIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(ExamAPIException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class ValidationError(ExamAPIException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 400)


class NotFoundError(ExamAPIException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class BusinessLogicError(ExamAPIException):
    def __init__(self, message: str = "Business logic error"):
        super().__init__(message, 422)