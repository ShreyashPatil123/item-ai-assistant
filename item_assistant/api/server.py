"""
FastAPI Server
Main API server with HTTP and WebSocket support.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from item_assistant.config import get_config
from item_assistant.logging import get_logger
from item_assistant.api.endpoints import router

logger = get_logger()


# Create FastAPI app
app = FastAPI(
    title="Item AI Assistant API",
    description="API for controlling Item AI Assistant remotely",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 80)
    logger.info("Item AI Assistant API Server Starting")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("API Server Shutting Down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Item AI Assistant",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


def start_server(host: str = "0.0.0.0", port: int = 8765):
    """
    Start the API server
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    config = get_config()
    
    # Get port from config if not specified
    if port == 8765:
        port = config.get("network.api_port", 8765)
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
