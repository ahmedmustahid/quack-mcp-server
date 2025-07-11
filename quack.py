#!/usr/bin/env python3
"""
Quack - Python code analysis MCP server

This MCP server provides asynchronous linting and static analysis tools
for Python code.
"""

import argparse
import logging
import os
import signal
import sys


# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    print("Shutting down server gracefully...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("quack")

# Create a file handler for persistent logs if running in a writable directory
try:
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/quack.log")
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )
    )
    logger.addHandler(file_handler)
except (PermissionError, OSError):
    # Skip file logging if we can't write to the directory
    logger.warning("Could not create log directory. File logging disabled.")

# Import server creation function
from quack.server import create_server

# Create the server at module level with a standard name that MCP CLI can find
server = create_server()


def main():
    """Main entry point for the Quack server"""
    parser = argparse.ArgumentParser(
        description="Quack - Python code analysis MCP server"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "--streamable-http",
        action="store_true",
        help="Run with streamable-http transport",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind (default: 8000)"
    )
    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    try:
        if args.streamable_http:
            server.settings.host = args.host
            server.settings.port = args.port
            server.run(transport="streamable-http")
        else:
            logger.info(
                "[Server] Starting Quack MCP server with stdio transport"
            )
            server.run()
    except Exception as e:
        logger.critical(f"[Server] Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
