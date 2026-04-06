class LCDError(Exception):
    """Base exception for all lcd-content-formatter errors."""


class FrameRowNotFoundError(LCDError, KeyError):
    """Raised when a requested FrameRow ID does not exist in the Frame."""


class DuplicateFrameRowError(LCDError, ValueError):
    """Raised when adding a FrameRow with an ID that already exists."""


class I2CError(LCDError, OSError):
    """Raised when an I2C communication error occurs."""
