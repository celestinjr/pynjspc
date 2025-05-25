"""pynjspc - Asynchronous Python client for njsPC pool controller."""

from .client import NjsPCClient
from .exceptions import (
    NjsPCError,
    ConnectionError,
    ConnectionTimeoutError,
    NotConnectedError,
)
from .const import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_AUTO_RECONNECT,
    DEFAULT_RECONNECT_DELAY,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_WATCHDOG_TIMEOUT,
    DEFAULT_FALLBACK_WATCHDOG_SLEEP,
    DEFAULT_UNKNOWN_EVENTS_LOG,
    ApiEndpoints,
    SocketIOEventsInbound,
    # SocketIOEventsOutbound,
)

__version__ = "0.1.0"
VERSION = (0, 1, 0)

__all__ = [
    "__version__",
    "VERSION",
    "NjsPCClient",
    "NjsPCError",
    "ConnectionError",
    "ConnectionTimeoutError",
    "NotConnectedError",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_AUTO_RECONNECT",
    "DEFAULT_RECONNECT_DELAY",
    "DEFAULT_MAX_RECONNECT_ATTEMPTS",
    "DEFAULT_WATCHDOG_TIMEOUT",
    "DEFAULT_FALLBACK_WATCHDOG_SLEEP",
    "DEFAULT_UNKNOWN_EVENTS_LOG",
    "ApiEndpoints",
    "SocketIOEventsInbound",
    # "SocketIOEventsOutbound",
]
