"""SSE (Server-Sent Events) server for git-sim MCP."""

import asyncio
import json
import logging
import os

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from git_sim_mcp.server import server

logger = logging.getLogger("git-sim-mcp.sse")


# Get CORS configuration from environment
def get_cors_config():
    """Get CORS configuration from environment variables."""
    # Check for simple accept-all CORS mode
    accept_all = os.getenv("GIT_SIM_CORS_ACCEPT_ALL", "false").lower() in ("true", "1", "yes")
    
    if accept_all:
        # Accept all CORS: allow all origins, methods, and headers
        return {
            "allow_origins": ["*"],
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "allow_credentials": False,
        }
    
    # Otherwise, use individual configuration settings
    allow_origins = os.getenv("GIT_SIM_CORS_ALLOW_ORIGINS", "*")
    allow_methods = os.getenv("GIT_SIM_CORS_ALLOW_METHODS", "GET,POST,OPTIONS")
    allow_headers = os.getenv("GIT_SIM_CORS_ALLOW_HEADERS", "*")
    
    # Parse comma-separated values
    origins = [o.strip() for o in allow_origins.split(",")] if allow_origins != "*" else ["*"]
    methods = [m.strip() for m in allow_methods.split(",")]
    headers = [h.strip() for h in allow_headers.split(",")] if allow_headers != "*" else ["*"]
    
    return {
        "allow_origins": origins,
        "allow_methods": methods,
        "allow_headers": headers,
        "allow_credentials": os.getenv("GIT_SIM_CORS_ALLOW_CREDENTIALS", "false").lower() in ("true", "1", "yes"),
    }


async def handle_sse(request):
    """Handle SSE connections."""
    async with SseServerTransport("/messages") as transport:
        await server.run(
            transport.read_stream,
            transport.write_stream,
            server.create_initialization_options(),
        )


async def handle_messages(request):
    """Handle message endpoint."""
    return Response("SSE endpoint", media_type="text/plain")


async def health_check(request):
    """Health check endpoint."""
    return Response(
        json.dumps({"status": "healthy", "service": "git-sim-mcp", "transport": "sse"}),
        media_type="application/json",
    )


# Get CORS configuration
cors_config = get_cors_config()
logger.info(f"CORS configuration: {cors_config}")

# Create middleware
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        allow_credentials=cors_config["allow_credentials"],
    )
]

# Create Starlette app
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=health_check),
    ],
    middleware=middleware,
)


async def main(host: str = "127.0.0.1", port: int = 8000):
    """Run the SSE server."""
    logger.info(f"Starting git-sim MCP SSE server on {host}:{port}")

    config = uvicorn.Config(app=app, host=host, port=port, log_level="info")

    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()


if __name__ == "__main__":
    asyncio.run(main())
