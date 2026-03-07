import json
from typing import Dict, Set
from fastapi import WebSocket
from loguru import logger

class ScanProgressManager:
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, scan_id: str, ws: WebSocket):
        await ws.accept()
        if scan_id not in self._connections:
            self._connections[scan_id] = set()
        self._connections[scan_id].add(ws)

    def disconnect(self, scan_id: str, ws: WebSocket):
        if scan_id in self._connections:
            self._connections[scan_id].discard(ws)
            if not self._connections[scan_id]:
                del self._connections[scan_id]

    async def emit(self, scan_id: str, event: str, data: dict):
        if scan_id not in self._connections:
            return
        message = json.dumps({"event": event, "data": data})
        dead = set()
        for ws in self._connections[scan_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(scan_id, ws)

    async def emit_tool_start(self, scan_id: str, tool_name: str):
        await self.emit(scan_id, "tool_start", {"tool": tool_name, "status": "running"})

    async def emit_tool_done(self, scan_id: str, tool_name: str, status: str, duration_ms: float):
        await self.emit(scan_id, "tool_done", {"tool": tool_name, "status": status, "duration_ms": round(duration_ms, 1)})

    async def emit_ai_start(self, scan_id: str):
        await self.emit(scan_id, "ai_start", {"message": "Running AI analysis..."})

    async def emit_ai_done(self, scan_id: str, risk_level: str, risk_score: int):
        await self.emit(scan_id, "ai_done", {"risk_level": risk_level, "risk_score": risk_score})

    async def emit_scan_complete(self, scan_id: str, duration_ms: float):
        await self.emit(scan_id, "scan_complete", {"duration_ms": round(duration_ms, 1)})

progress_manager = ScanProgressManager()
