"""Asynchronous Python client for njsPC pool controller."""

import asyncio
import json
import logging
import socket
import time
from typing import Callable, Dict, Set, Optional, Any, Union
from pathlib import Path

import socketio
import aiohttp

from pynjspc.const import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_AUTO_RECONNECT,
    DEFAULT_RECONNECT_DELAY,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_WATCHDOG_TIMEOUT,
    DEFAULT_UNKNOWN_EVENTS_LOG,
    ApiEndpoints,
    SocketIOEventsInbound,
    # SocketIOEventsOutbound,
)

from .exceptions import (
    ConnectionError as NjsPCConnectionError,
    ConnectionTimeoutError,
    NotConnectedError,
)

_LOGGER = logging.getLogger(__name__)


class NjsPCClient:
    """nodejs-poolController API client."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
        request_timeout: Optional[float] = None,
        auto_reconnect: Optional[bool] = None,
        reconnect_delay: Optional[float] = None,
        max_reconnect_attempts: Optional[int] = None,
        watchdog_timeout: Optional[float] = None,
        unknown_events_log: Optional[Union[str, Path]] = None,
    ):
        self.host: str = str(host or DEFAULT_HOST)
        self.port: int = int(port or DEFAULT_PORT)
        self._request_timeout: float = (
            float(request_timeout)
            if request_timeout is not None
            else float(DEFAULT_REQUEST_TIMEOUT)
        )
        self._auto_reconnect: bool = (
            bool(auto_reconnect)
            if auto_reconnect is not None
            else bool(DEFAULT_AUTO_RECONNECT)
        )
        self._reconnect_delay: float = (
            float(reconnect_delay)
            if reconnect_delay is not None
            else float(DEFAULT_RECONNECT_DELAY)
        )
        self._max_reconnect_attempts: Optional[int] = (
            int(max_reconnect_attempts)
            if max_reconnect_attempts is not None
            else DEFAULT_MAX_RECONNECT_ATTEMPTS
        )
        self._watchdog_timeout: float = (
            float(watchdog_timeout)
            if watchdog_timeout is not None
            else float(DEFAULT_WATCHDOG_TIMEOUT)
        )
        if unknown_events_log is not None and unknown_events_log != "":
            self._unknown_events_log: Optional[Union[str, Path]] = str(
                unknown_events_log
            )
        else:
            self._unknown_events_log = DEFAULT_UNKNOWN_EVENTS_LOG
        self._connected: bool = False
        self._event_callbacks: Dict[str, Set[Callable[[Any], None]]] = {}
        self._reconnect_attempts: int = 0
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_stop: bool = False
        self._last_activity: Optional[float] = None
        self._socket: Optional[socketio.AsyncClient] = None
        self._handlers_registered = False

    def _update_activity(self) -> None:
        """Update the last activity timestamp for watchdog monitoring."""
        _LOGGER.debug("Updating last activity timestamp")
        self._last_activity = time.monotonic()

    def _register_socket_handlers(self):
        if self._socket is None or self._handlers_registered:
            return

        # Register a generic event handler for all events
        async def _on_any_event(event: str, data: Optional[Any] = None) -> None:
            self._handle_event(event, data)

        self._socket.on("*", _on_any_event)

        # Register connection and disconnection handlers
        async def _on_connect() -> None:
            if not self._connected:
                self._connected = True
                self._update_activity()
                _LOGGER.info("Connected to njsPC server")

        self._socket.on("connect", _on_connect)

        async def _on_disconnect() -> None:
            if self._connected:
                self._connected = False
                self._update_activity()
                _LOGGER.warning("Disconnected from njsPC server")

        self._socket.on("disconnect", _on_disconnect)
        self._handlers_registered = True

    def _get_host_url(self, port: Optional[int] = None) -> str:
        """Helper to resolve host to IP and construct base URL."""
        try:
            ip = socket.gethostbyname(self.host)
        except socket.gaierror as e:
            _LOGGER.error(f"Failed to resolve host {self.host}: {e}")
            raise NjsPCConnectionError(f"Cannot resolve host: {self.host}")
        return f"http://{ip}:{port or self.port}"

    async def connect(self, timeout: float = 10.0) -> None:
        """Establish connection to the controller. Starts connection monitor if enabled. Enforces timeout."""
        self._socket = socketio.AsyncClient()
        self._connected = False
        self._handlers_registered = False
        self._register_socket_handlers()
        url = self._get_host_url()
        try:
            await asyncio.wait_for(self._socket.connect(url), timeout=timeout)
            # Only reset reconnect attempts if we actually connected
            self._reconnect_attempts = 0
        except asyncio.TimeoutError:
            self._connected = False
            _LOGGER.error(
                f"Connection attempt timed out after {timeout} seconds. Will attempt to reconnect."
            )
        except Exception as e:
            self._connected = False
            _LOGGER.error(
                f"Failed to connect to njsPC server: {e}. Will attempt to reconnect."
            )
        if self._auto_reconnect and (
            self._monitor_task is None or self._monitor_task.done()
        ):
            self._monitor_stop = False
            self._start_connection_monitor()

    async def disconnect(self) -> None:
        """Disconnect from the controller. Stops connection monitor and closes the socket."""
        if self._socket is not None:
            try:
                await self._socket.disconnect()
            except Exception as e:
                _LOGGER.warning(f"Exception during socket disconnect: {e}")
            self._socket = None

        self._connected = False
        self._monitor_stop = True
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

    async def async_close(self) -> None:
        """Asynchronously close the socket connection and clean up resources."""
        if self._socket is not None:
            try:
                await self._socket.disconnect()
            except Exception as e:
                _LOGGER.warning(f"Exception during socket disconnect in async_close: {e}")
            self._socket = None
        self._connected = False
        self._monitor_stop = True
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

    async def _cleanup_socket(self) -> None:
        """Internal method to clean up socket connection without stopping monitor."""
        if self._socket is not None:
            try:
                await self._socket.disconnect()
            except Exception as e:
                _LOGGER.warning(f"Exception during socket disconnect: {e}")
            self._socket = None
        self._connected = False

    # async def emit(self, event: SocketIOEventsOutbound, data: Optional[Dict[str, Any]] = None) -> None:
    #     """Emit an event to the controller."""
    #     if not self._connected or self._socket is None:
    #         raise NotConnectedError("Not connected to njsPC server.")

    #     if not SocketIOEventsOutbound.is_known_event(event.value):
    #         raise ValueError(f"Unknown event '{event}'")

    #     # Encode data as JSON string
    #     if data is not None and not isinstance(data, dict):
    #         raise ValueError(f"Data must be a dictionary, got {type(data).__name__}")
    #     if data is not None and not isinstance(data, dict):
    #         raise ValueError(f"Data must be a dictionary, got {type(data).__name__}")
    #     try:
    #         # Validate that data can be serialized to JSON
    #         json_data = json.dumps(data or {})
    #     except TypeError as e:
    #         raise ValueError(f"Data could not be serialized to JSON: {e}")

    #     try:
    #         _LOGGER.debug(f"Emitting event '{event.value}' with data: {json_data}")
    #         await self._socket.emit(event.value, json_data)
    #     except Exception as e:
    #         _LOGGER.error(f"Emit failed for event '{event}': {e}")
    #         raise

    async def fetch_full_state(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Fetch the full controller state via HTTP GET request to ApiEndpoints.STATE_ALL endpoint."""
        if not self._connected:
            raise NotConnectedError("Not connected to njsPC server.")
        if timeout is None:
            timeout = self._request_timeout

        url = f"{self._get_host_url()}/{ApiEndpoints.STATE_ALL.value}"

        try:
            _LOGGER.debug(f"Fetching full state from {url}")
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise NjsPCConnectionError(
                            f"HTTP {response.status}: Failed to fetch state from {url}"
                        )

                    state = await response.json()
                    _LOGGER.debug(f"Fetched full state: {state}")
        except asyncio.TimeoutError:
            raise ConnectionTimeoutError(
                f"fetch_full_state timed out after {timeout} seconds"
            )
        except aiohttp.ClientError as e:
            raise NjsPCConnectionError(f"Failed to fetch full state: {e}")
        except Exception as e:
            _LOGGER.error(f"Failed to fetch full state: {e}")
            raise

        if state is None:
            state = {}

        self._update_activity()
        return state

    async def send_command(
        self,
        endpoint: ApiEndpoints,
        data: Optional[Dict[str, Any]] = None,
        method: str = "PUT",
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Send a command to the controller via HTTP API.

        Args:
            endpoint: The API endpoint to send the command to
            data: The command data/payload to send
            method: HTTP method to use (GET, POST, PUT, DELETE)
            timeout: Request timeout in seconds

        Returns:
            Dict containing the response from the server

        Raises:
            NjsPCConnectionError: If the HTTP request fails
            ConnectionTimeoutError: If the request times out
            ValueError: If the data cannot be serialized to JSON
        """
        if not self._connected:
            raise NotConnectedError("Not connected to njsPC server.")
        if timeout is None:
            timeout = self._request_timeout

        url = f"{self._get_host_url()}/{endpoint.value}"

        # Validate data can be serialized to JSON if provided
        if data is not None:
            if not isinstance(data, dict):
                raise ValueError(
                    f"Data must be a dictionary, got {type(data).__name__}"
                )
            try:
                json.dumps(data)
            except TypeError as e:
                raise ValueError(f"Data could not be serialized to JSON: {e}")

        try:
            _LOGGER.debug(f"Sending {method} command to {url} with data: {data}")
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.request(method, url, json=data) as response:
                    if response.status not in [200, 201, 202]:
                        response_text = await response.text()
                        raise NjsPCConnectionError(
                            f"HTTP {response.status}: Command failed at {url}. Response: {response_text}"
                        )

                    # Try to parse JSON response, fallback to text if not JSON
                    try:
                        result = await response.json()
                        _LOGGER.debug(f"Command response: {result}")
                    except Exception:
                        result = {"response": await response.text()}
                        _LOGGER.debug(f"Command response (text): {result}")

        except asyncio.TimeoutError:
            raise ConnectionTimeoutError(
                f"send_command timed out after {timeout} seconds"
            )
        except aiohttp.ClientError as e:
            raise NjsPCConnectionError(f"Failed to send command to {url}: {e}")
        except Exception as e:
            _LOGGER.error(f"Failed to send command: {e}")
            raise

        self._update_activity()
        return result

    def on(self, event: SocketIOEventsInbound, callback: Callable) -> None:
        """Register an event handler for a specific event. Supports multiple callbacks per event."""
        if event.value not in self._event_callbacks:
            self._event_callbacks[event.value] = set()
        _LOGGER.debug(f"Registering callback for event '{event.value}'")
        self._event_callbacks[event.value].add(callback)

    def off(self, event: SocketIOEventsInbound, callback: Callable) -> None:
        """Unregister an event handler."""
        if event.value in self._event_callbacks:
            self._event_callbacks[event.value].discard(callback)
            if not self._event_callbacks[event.value]:
                del self._event_callbacks[event.value]

    def remove(self, event: Optional[SocketIOEventsInbound] = None) -> None:
        """Remove all handlers for a specific event, or all events if no event is given."""
        if event is not None:
            self._event_callbacks.pop(event.value, None)
        else:
            self._event_callbacks.clear()

    def _handle_event(self, event: str, data: Any) -> None:
        """Internal: Call all registered callbacks for an event.
        This should be called by the event loop or socket handler when an event is received.
        """
        _LOGGER.debug(f"Handling event '{event}' with data: {data}")
        self._update_activity()
        for callback in self._event_callbacks.get(event, set()):
            try:
                _LOGGER.debug(f"Calling callback for event '{event}'")
                callback(data)
            except Exception as e:
                _LOGGER.error(f"Error in event callback for '{event}': {e}")

        # Log the event if it's not a known event
        if not SocketIOEventsInbound.is_known_event(event):
            _LOGGER.warning(f"Unknown event '{event}' received with data: {data}")
            if self._unknown_events_log:
                with open(self._unknown_events_log, "a") as log_file:
                    log_file.write(
                        f"Unknown event '{event}' received with data: {data}\n"
                    )

    async def _connection_monitor(self) -> None:
        """Background task to monitor connection health and handle reconnections."""
        try:
            while not self._monitor_stop:
                _LOGGER.debug("Connection monitor checking status")
                now = time.monotonic()
                if self._last_activity is None:
                    _LOGGER.debug("Undefined last activity. Forcing reconnect.")
                    await self._cleanup_socket()
                elif self._connected and (
                    now - self._last_activity > self._watchdog_timeout
                ):
                    _LOGGER.debug(
                        f"No activity detected for {self._watchdog_timeout} seconds. Testing HTTP connection."
                    )
                    # Use test_connection instead of inline HTTP code
                    result = await self.test_connection()
                    if result:
                        _LOGGER.debug("HTTP connection check succeeded.")
                        self._update_activity()
                        _LOGGER.debug("Connection is healthy after test_connection.")
                    else:
                        _LOGGER.warning("HTTP connection check failed. Cleaning up socket.")
                        await self._cleanup_socket()

                if self._connected:
                    _LOGGER.debug("Connection is healthy")
                else:
                    self._reconnect_attempts = 0
                    while (
                        not self._connected
                        and (
                            self._max_reconnect_attempts is None
                            or self._reconnect_attempts < self._max_reconnect_attempts
                        )
                        and not self._monitor_stop
                    ):
                        _LOGGER.warning(
                            f"Connection lost. Attempting to reconnect "
                            f"({self._reconnect_attempts+1}/{self._max_reconnect_attempts or 'inf'}) "
                            f"in {self._reconnect_delay} seconds..."
                        )
                        await asyncio.sleep(self._reconnect_delay)
                        try:
                            await self.connect(timeout=self._request_timeout)
                        except Exception as e:
                            _LOGGER.error(f"Reconnect attempt failed: {e}")
                        self._reconnect_attempts += 1

                    if not self._connected:
                        _LOGGER.error("Max reconnect attempts reached. Giving up.")
                # Sleep until last_activity would be considered stale
                if self._last_activity is not None:
                    elapsed = time.monotonic() - self._last_activity
                    sleep_time = max(1, self._watchdog_timeout - elapsed)
                    _LOGGER.debug(f"Sleeping for {sleep_time} seconds")
                    await asyncio.sleep(sleep_time)
                else:
                    # If no activity, sleep a default interval to avoid tight loop
                    await asyncio.sleep(self._watchdog_timeout)
        except asyncio.CancelledError:
            pass

    def _start_connection_monitor(self):
        """Schedule the connection monitor to run in the background."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_stop = False
            self._monitor_task = asyncio.create_task(self._connection_monitor())

    # Convenience methods for common HTTP commands

    async def set_circuit_state(self, circuit_id: int, state: bool) -> Dict[str, Any]:
        """Set the state of a circuit via HTTP API.

        Args:
            circuit_id: The ID of the circuit to control
            state: True to turn on, False to turn off

        Returns:
            Dict containing the response from the server
        """
        if not self._connected:
            raise NotConnectedError("Not connected to njsPC server.")
        data = {"id": circuit_id, "state": state}
        return await self.send_command(ApiEndpoints.CIRCUIT_SETSTATE, data)

    async def test_connection(self, timeout: float = 5.0) -> bool:
        """Test HTTP connection to the controller. Returns True if successful, False otherwise."""
        url = f"{self._get_host_url()}/{ApiEndpoints.STATE_STATUS.value}"
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.get(url) as response:
                    return response.status == 200
        except Exception:
            return False

    @property
    def connected(self) -> bool:
        """Return True if the client is currently connected."""
        return self._connected


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    print("For examples, see the 'examples' directory.")
