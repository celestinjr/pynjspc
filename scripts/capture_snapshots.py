"""Capture real API responses from a live njsPC instance and save to snapshots."""

import json
import asyncio
import argparse
from pathlib import Path
from pynjspc import NjsPCClient


SNAPSHOT_DIR = Path("tests/snapshots")


async def capture_snapshot(server_url: str, endpoints: list[str]) -> None:
    """Connect to the given server and capture snapshots for the specified endpoints."""
    client = NjsPCClient(server_url)
    await client.connect()

    print(f"Connected to {server_url}, capturing endpoints: {endpoints}")

    try:
        for endpoint in endpoints:
            method = getattr(client, endpoint, None)
            if method is None:
                print(f"❌ No method for endpoint '{endpoint}'")
                continue

            data = await method()
            snapshot_path = SNAPSHOT_DIR / f"{endpoint}.json"
            with snapshot_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                print(f"✅ Saved snapshot: {snapshot_path}")
    finally:
        await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Capture snapshots from a njsPC server.")
    parser.add_argument("--host", required=True, help="Server host (e.g., http://localhost:4200)")
    parser.add_argument(
        "--endpoints",
        nargs="+",
        default=["status", "temps", "pumps"],
        help="Endpoints to capture",
    )

    args = parser.parse_args()
    asyncio.run(capture_snapshot(args.host, args.endpoints))


if __name__ == "__main__":
    main()