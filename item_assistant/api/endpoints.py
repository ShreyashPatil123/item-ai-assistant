"""
API Endpoints
HTTP and WebSocket endpoints for remote control.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime

from item_assistant.api.auth import verify_auth
from item_assistant.logging import get_log_manager
from item_assistant.core.orchestrator import get_orchestrator

logger = get_log_manager().get_logger()
log_manager = get_log_manager()

# Create API router
router = APIRouter()


# Request/Response models
class CommandRequest(BaseModel):
    command: str
    source: str = "api"
    language: Optional[str] = None


class CommandResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None
    timestamp: str


class StatusResponse(BaseModel):
    status: str
    uptime: float
    voice_enabled: bool
    llm_available: dict
    timestamp: str


# HTTP Endpoints

@router.post("/api/command", response_model=CommandResponse, dependencies=[Depends(verify_auth)])
async def execute_command(request: CommandRequest):
    """
    Execute a command
    
    Args:
        request: Command request
    
    Returns:
        Command result
    """
    logger.info(f"API command received: {request.command}")
    log_manager.log_command(request.command, request.source, request.language)
    
    # Get orchestrator and execute
    orchestrator = get_orchestrator()
    result = await orchestrator.process_command(request.command, source=request.source)
    
    return CommandResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        result=result.get("data"),
        timestamp=datetime.now().isoformat()
    )


@router.get("/api/status", response_model=StatusResponse, dependencies=[Depends(verify_auth)])
async def get_status():
    """Get system status"""
    orchestrator = get_orchestrator()
    status_data = orchestrator.get_status()
    
    return StatusResponse(
        status="online",
        uptime=status_data.get("uptime", 0),
        voice_enabled=status_data.get("voice_enabled", False),
        llm_available=status_data.get("llm_available", {}),
        timestamp=datetime.now().isoformat()
    )


@router.get("/api/logs", dependencies=[Depends(verify_auth)])
async def get_logs(lines: int = 100):
    """
    Get recent log entries
    
    Args:
        lines: Number of lines to retrieve
    
    Returns:
        Log content
    """
    logs = log_manager.get_recent_logs(lines)
    return {"logs": logs}


@router.post("/api/wol", dependencies=[Depends(verify_auth)])
async def trigger_wol():
    """
    Trigger Wake-on-LAN (for remote laptop power-on)
    Note: This endpoint would be on a separate always-on device or router
    """
    # This is a placeholder - actual WoL logic would be implemented
    # in a separate service or on the router
    return {"message": "WoL not implemented in this endpoint (use phone app directly)"}


# WebSocket endpoint for real-time communication
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional communication
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Item AI Assistant",
            "timestamp": datetime.now().isoformat()
        })
        
        orchestrator = get_orchestrator()
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            command = message.get("command", "")
            source = message.get("source", "websocket")
            
            log_manager.log_command(command, source)
            
            # Process command
            result = await orchestrator.process_command(command, source=source)
            
            # Send response
            await websocket.send_json({
                "type": "response",
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "result": result.get("data"),
                "timestamp": datetime.now().isoformat()
            })
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
