"""SSE (Server-Sent Events) server for git-sim MCP."""

import asyncio
import json
import logging
from typing import Any

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
import uvicorn

from git_sim_mcp.server import server

logger = logging.getLogger("git-sim-mcp.sse")


async def handle_sse(request):
    """Handle SSE connections."""
    async with SseServerTransport("/messages") as transport:
        await server.run(
            transport.read_stream,
            transport.write_stream,
            server.create_initialization_options()
        )


async def handle_messages(request):
    """Handle message endpoint."""
    return Response("SSE endpoint", media_type="text/plain")


async def health_check(request):
    """Health check endpoint."""
    return Response(
        json.dumps({
            "status": "healthy",
            "service": "git-sim-mcp",
            "transport": "sse"
        }),
        media_type="application/json"
    )


# Create Starlette app
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=health_check),
    ]
)


async def main(host: str = "127.0.0.1", port: int = 8000):
    """Run the SSE server."""
    logger.info(f"Starting git-sim MCP SSE server on {host}:{port}")
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
