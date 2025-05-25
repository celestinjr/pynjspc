"""Custom exceptions for the njsPC API client."""

class NjsPCError(Exception):
    """Base class for njsPC client errors."""
    pass

class ConnectionError(NjsPCError):
    """Raised when a connection error occurs."""
    pass

class ConnectionTimeoutError(ConnectionError):
    """Raised when a connection attempt times out."""
    pass

class NotConnectedError(NjsPCError):
    """Raised when an operation is attempted before the client is connected."""
    pass
