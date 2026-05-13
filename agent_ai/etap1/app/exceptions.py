class AppError(Exception):
    """Base exception for application-specific errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class AIResponseError(AppError):
    """Raised when AI response is invalid or cannot be parsed."""
    pass


class ClassificationError(AppError):
    """Raised when classification process fails."""
    pass


class PromptLoadError(AppError):
    """Raised when prompt file cannot be loaded."""
    pass