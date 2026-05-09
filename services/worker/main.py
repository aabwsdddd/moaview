"""MoaView worker placeholder.

This module intentionally performs no production crawling. Future jobs should use
approved adapters and fixture-safe inputs until the crawler policy is reviewed.
"""


def run() -> None:
    """Run a no-op worker heartbeat."""

    print("MoaView worker placeholder: no jobs scheduled")


if __name__ == "__main__":
    run()
