"""
Orchestrator - Runs all OSINT tools + AI analyzers with real-time WebSocket progress
"""
import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from loguru import logger

from app.models.schemas import InvestigateResponse, ToolResult, TargetType, AIAnalysis
from app.utils.target import classify_target
from app.services.ai.analyzer import MultiAIAnalyzer
from app.services.ws_manager import progress_manager
from app.services.tools.geoip import GeoIPTool
from app.services.tools.dns_lookup import DNSLookupTool
from app.services.tools.whois_lookup import WhoisTool
from app.services.tools.ssl_cert import SSLCertTool
from app.services.tools.subdomains import SubdomainsTool
from app.services.tools.http_headers import HTTPHeadersTool
from app.services.tools.shodan_lookup import ShodanTool
from app.services.tools.virustotal import VirusTotalTool
from app.services.tools.blacklist import BlacklistTool

ALL_TOOLS = [
    GeoIPTool(), DNSLookupTool(), WhoisTool(), SSLCertTool(),
    SubdomainsTool(), HTTPHeadersTool(), ShodanTool(), VirusTotalTool(), BlacklistTool(),
]

class InvestigationOrchestrator:
    def __init__(self):
        self.ai = MultiAIAnalyzer()

    async def _run_tool_with_progress(self, tool, target: str, target_type, scan_id: str) -> ToolResult:
        """Run a single tool and emit WebSocket events on start/done."""
        await progress_manager.emit_tool_start(scan_id, tool.name)
        t0 = time.time()
        try:
            result = await tool.run(target, target_type)
            duration = (time.time() - t0) * 1000
            await progress_manager.emit_tool_done(scan_id, tool.name, result.status, duration)
            return result
        except Exception as e:
            duration = (time.time() - t0) * 1000
            await progress_manager.emit_tool_done(scan_id, tool.name, "error", duration)
            return ToolResult(tool_name=tool.name, status="error", error=str(e))

    async def investigate(
        self,
        target: str,
        tool_filter: Optional[List[str]] = None,
        scan_id: Optional[str] = None,
    ) -> tuple[InvestigateResponse, str]:
        if not scan_id:
            scan_id = str(uuid.uuid4())

        start_time = time.time()
        target_type = classify_target(target)

        tools = ALL_TOOLS
        if tool_filter:
            tools = [t for t in ALL_TOOLS if t.name in tool_filter]

        logger.info(f"🔍 [{scan_id[:8]}] Investigating {target} ({target_type}) with {len(tools)} tools")

        # Run all tools concurrently — each emits its own WS events
        tasks = [self._run_tool_with_progress(tool, target, target_type, scan_id) for tool in tools]
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        for tool, result in zip(tools, tool_results):
            if isinstance(result, Exception):
                results[tool.name] = ToolResult(
                    tool_name=tool.name, status="error", error=str(result)
                ).model_dump()
            else:
                results[tool.name] = result.model_dump()

        success_count = sum(1 for r in results.values() if r["status"] == "success")

        # AI analysis
        ai_analysis = None
        try:
            await progress_manager.emit_ai_start(scan_id)
            ai_analysis = await self.ai.analyze(target, results)
            if ai_analysis:
                await progress_manager.emit_ai_done(scan_id, ai_analysis.risk_level, ai_analysis.risk_score)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")

        total_duration = (time.time() - start_time) * 1000
        await progress_manager.emit_scan_complete(scan_id, total_duration)

        response = InvestigateResponse(
            target=target,
            target_type=target_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=round(total_duration, 2),
            tools_run=len(tools),
            tools_success=success_count,
            results=results,
            ai_analysis=ai_analysis,
        )

        return response, scan_id
