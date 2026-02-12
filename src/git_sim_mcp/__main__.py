"""Main entry point for git-sim MCP server."""

import sys
import argparse
import logging
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="git-sim MCP Server - Model Context Protocol server for git-sim"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for SSE transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if args.version:
        from git_sim_mcp import __version__
        print(f"git-sim-mcp version {__version__}")
        sys.exit(0)
    
    # Import and run appropriate server
    if args.transport == "stdio":
        from git_sim_mcp.server import main as server_main
        import asyncio
        asyncio.run(server_main())
    elif args.transport == "sse":
        from git_sim_mcp.sse_server import main as sse_main
        import asyncio
        asyncio.run(sse_main(host=args.host, port=args.port))
    else:
        print(f"Unknown transport: {args.transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
