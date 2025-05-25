# pynjspc

A Python asyncio client for [nodejs-poolController](https://github.com/tagyoureit/nodejs-poolController).

---

`pynjspc` provides an async, Pythonic interface to monitor and control your pool equipment via the njsPC API. It is suitable for use in automation systems, scripts, and integrations.

## Features

- **Async connection**: Maintains a persistent Socket.IO connection to njsPC.
- **Automatic reconnection**: Handles connection drops and reconnects automatically.
- **Event subscription**: Subscribe to real-time events with `.on(event_name, callback)` and `.once(event_name, callback)`.
- **State management**: Fetch the full controller state with `fetch_full_state()`.
- **Clean async lifecycle**: Use `connect()`, `disconnect()`, and `wait_until_connected()`.
- **Context manager support**: Use with `async with` for automatic cleanup.
- **Comprehensive logging**: Detailed logs of connection state and events.
- **Type hints**: Full typing support for modern Python development.

## Installation

Install from PyPI:

```bash
pip install pynjspc
```

Or install the latest version from GitHub:

```bash
pip install git+https://github.com/celestinjr/pynjspc.git
```

## Requirements

- Python 3.9 or higher
- `python-socketio[asyncio]`
- `aiohttp`

## Quickstart

```python
import asyncio
from pynjspc import NjsPCClient, EVENT_STATE_UPDATE

async def main():
    async with NjsPCClient(host="192.168.1.100", port=4200) as client:
        async def on_state_update(data):
            print(f"State update: {data}")
        client.on(EVENT_STATE_UPDATE, on_state_update)
        state = await client.fetch_full_state()
        print(f"Controller state: {state}")
        await asyncio.sleep(60)  # Listen for events

if __name__ == "__main__":
    asyncio.run(main())
```

## API Overview

### NjsPCClient

#### Constructor

```python
NjsPCClient(
    host: str,
    port: int = None,
    request_timeout: float = None,
    path: str = None,
    throttle_rate: float = None,
)
```

#### Properties
- `connected`: Returns True if the client is currently connected.

#### Methods
- `connect(timeout: float = 10.0)`: Connect to the njsPC controller.
- `disconnect()`: Disconnect from the controller.
- `fetch_full_state(timeout: float = None)`: Fetch the full state from the controller.

##### Event Handling
- `on(event: str, callback: Callable)`: Register an event handler for a specific event.
- `remove(event: Optional[str] = None)`: Remove all handlers for an event, or all events if no event is given.

##### Circuit Commands
- `set_circuit_state(circuit_id: int, is_on: bool)`: Set a circuit on or off.

## Constants

Event name constants are available:

```python
from pynjspc import EVENT_GET_FULL_STATE, EVENT_FULL_STATE, EVENT_STATE_UPDATE
```

## Exceptions

The following exceptions are available from `pynjspc.exceptions`:

- `NjsPCError`: Base class for njsPC client errors.
- `ConnectionError`: Raised when a connection error occurs.
- `ConnectionTimeoutError`: Raised when a connection attempt times out.
- `NotConnectedError`: Raised when an operation is attempted before the client is connected.
- `InvalidStateError`: Raised when the client or server is in an invalid state for an operation.
- `RequestTimeoutError`: Raised when a request to the server times out.
- `ValidationError`: Raised when validation of a parameter or state data fails.
- `EquipmentNotFoundError`: Raised when a requested piece of equipment cannot be found.
- `CommandError`: Raised when a command to the equipment fails.
- `StateNotAvailableError`: Raised when state data is requested but not available.
- `UnsupportedFeatureError`: Raised when an operation is attempted on an unsupported feature.
- `ConfigurationError`: Raised when there's an issue with the controller's configuration.

## License

MIT License. See [LICENSE](LICENSE).