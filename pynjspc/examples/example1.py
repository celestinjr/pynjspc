import asyncio
import logging
import os
from pynjspc import NjsPCClient, SocketIOEventsInbound
from pynjspc.const import ApiEndpoints

logging.basicConfig(level=logging.DEBUG)

async def monitor_all(**kwargs):
    client = NjsPCClient(**kwargs)
    def make_handler(event_name):
        def handler(data):
            print(f"Received event: {event_name}")
        return handler
    try:
        await client.connect()
        for event in SocketIOEventsInbound:
            client.on(event, make_handler(event.value))
        while True:
            await asyncio.sleep(3600)
    finally:
        await client.disconnect()

async def monitor_pump(**kwargs):
    client = NjsPCClient(**kwargs)
    def make_handler(event_name):
        def handler(data):
            print(f"Received event: {event_name} | Data: {data}")
        return handler
    try:
        await client.connect()
        event = SocketIOEventsInbound.PUMP
        client.on(event, make_handler(event.value))
        while True:
            await asyncio.sleep(3600)
    finally:
        await client.disconnect()

# async def test_emit(**kwargs):
#     """Example of connecting and emitting an event."""
#     client = NjsPCClient(**kwargs)
#     try:
#         await client.connect()
#         # Wait a moment for connection to establish
#         await asyncio.sleep(1)
#         await client.emit(SocketIOEventsOutbound.CIRCUIT, {"id": 2, "state": False, "toggle": False})
#         print("Event emitted successfully")
#         # Keep connection alive briefly to see any responses
#         await asyncio.sleep(1)
#     finally:
#         await client.disconnect()

async def test_http_commands(**kwargs):
    """Example of connecting and sending HTTP commands."""
    client = NjsPCClient(**kwargs)
    try:
        await client.connect()
        # Wait a moment for connection to establish
        await asyncio.sleep(1)
        
        print("Testing HTTP commands...")
        
        # Test 1: Set circuit state using convenience method
        print("1. Setting circuit 2 state to ON using convenience method...")
        result = await client.set_circuit_state(circuit_id=2, state=True)
        print(f"   Result: {result}")

        await asyncio.sleep(5)  # Wait for a moment to see the effect
        
        # Test 2: Set circuit state using direct HTTP command
        print("2. Setting circuit 2 state to OFF using direct HTTP command...")
        data = {"id": 2, "state": False}
        result = await client.send_command(ApiEndpoints.CIRCUIT_SETSTATE, data)
        print(f"   Result: {result}")
        
        print("All HTTP commands completed successfully!")
        
    except Exception as e:
        print(f"Error during HTTP command test: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Get all configuration from environment variables with defaults
    host = os.getenv("NJSPC_HOST", "nixie-poolcontroller")
    port = int(os.getenv("NJSPC_PORT", "4200"))
    mode = os.getenv("EXAMPLE_MODE", "test_emit")
    
    # Parse configuration values from environment
    request_timeout = os.getenv("NJSPC_REQUEST_TIMEOUT")
    auto_reconnect = os.getenv("NJSPC_AUTO_RECONNECT")
    reconnect_delay = os.getenv("NJSPC_RECONNECT_DELAY")
    max_reconnect_attempts = os.getenv("NJSPC_MAX_RECONNECT_ATTEMPTS")
    watchdog_timeout = os.getenv("NJSPC_WATCHDOG_TIMEOUT")
    unknown_events_log = os.getenv("NJSPC_UNKNOWN_EVENTS_LOG")
    
    kwargs = {
        "host": host,
        "port": port,
        "request_timeout": request_timeout,
        "auto_reconnect": auto_reconnect,
        "reconnect_delay": reconnect_delay,
        "max_reconnect_attempts": max_reconnect_attempts,
        "watchdog_timeout": watchdog_timeout,
        "unknown_events_log": unknown_events_log
    }
    
    print(f"Configuration: {kwargs}")
    
    if mode == "monitor_all":
        print(f"Running monitor_all mode with {host}:{port}")
        asyncio.run(monitor_all(**kwargs))
    elif mode == "monitor_pump":
        print(f"Running monitor_pump mode with {host}:{port}")
        asyncio.run(monitor_pump(**kwargs))
    # elif mode == "test_emit":
    #     print(f"Running test_emit mode with {host}:{port}")
    #     asyncio.run(test_emit(**kwargs))
    elif mode == "test_http_commands":
        print(f"Running test_http_commands mode with {host}:{port}")
        asyncio.run(test_http_commands(**kwargs))

        