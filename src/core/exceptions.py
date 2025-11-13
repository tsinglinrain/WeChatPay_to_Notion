"""Custom exceptions for the application."""


class Bill2NotionError(Exception):
    """Base exception for all Bill2Notion errors."""
    pass


class ConfigurationError(Bill2NotionError):
    """Raised when configuration is invalid or missing."""
    pass


class EmailError(Bill2NotionError):
    """Raised when email operations fail."""
    pass


class PasswordNotFoundError(EmailError):
    """Raised when password email cannot be found."""
    pass


class AttachmentNotFoundError(EmailError):
    """Raised when bill attachment cannot be found."""
    pass


class FileProcessingError(Bill2NotionError):
    """Raised when file processing operations fail."""
    pass


class ExtractionError(FileProcessingError):
    """Raised when file extraction fails."""
    pass


class DataProcessingError(Bill2NotionError):
    """Raised when data processing operations fail."""
    pass


class NotionUploadError(Bill2NotionError):
    """Raised when Notion upload operations fail."""
    pass
