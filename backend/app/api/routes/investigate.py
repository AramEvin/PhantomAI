"""
Investigation routes with WebSocket progress + DB persistence
"""
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.schemas import InvestigateRequest
from app.services.orchestrator import InvestigationOrchestrator
from app.services.ws_manager import progress_manager
from app.database import get_db, ScanRecord

router = APIRouter()
orchestrator = InvestigationOrchestrator()

@router.post("/investigate")
async def investigate(request: InvestigateRequest, db: AsyncSession = Depends(get_db)):
    """Run investigation, save to DB, return full result."""
    scan_id = str(uuid.uuid4())

    response, scan_id = await orchestrator.investigate(
        target=request.target,
        tool_filter=request.tools,
        scan_id=scan_id,
    )

    # Save to PostgreSQL
    try:
        ai_dict = response.ai_analysis.model_dump() if response.ai_analysis else None
        record = ScanRecord(
            target=response.target,
            target_type=response.target_type.value,
            duration_ms=response.duration_ms,
            tools_run=response.tools_run,
            tools_success=response.tools_success,
            risk_level=response.ai_analysis.risk_level if response.ai_analysis else None,
            risk_score=response.ai_analysis.risk_score if response.ai_analysis else None,
            results=response.results,
            ai_analysis=ai_dict,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        logger.info(f"✓ Saved scan #{record.id} for {response.target}")
    except Exception as e:
        logger.error(f"DB save failed: {e}")

    return response

@router.websocket("/ws/scan/{scan_id}")
async def scan_websocket(scan_id: str, ws: WebSocket):
    """WebSocket endpoint — client connects before POSTing to /investigate."""
    await progress_manager.connect(scan_id, ws)
    try:
        # Keep connection open until client disconnects
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        progress_manager.disconnect(scan_id, ws)
