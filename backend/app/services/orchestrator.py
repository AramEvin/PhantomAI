"""
Orchestrator - Runs all 15 OSINT tools in parallel
Original 9: GeoIP, DNS, WHOIS, SSL, Subdomains, HTTP Headers, Shodan, VirusTotal, Blacklist
New 6: Nmap, CVE Lookup, Reverse IP, WHOIS History, LeakDB, BGP/ASN
"""
import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from loguru import logger

from app.models.schemas import InvestigationResult, ToolResult
from app.utils.target import classify_target
from app.services.ai.analyzer import MultiAIAnalyzer
from app.services.tools.geoip import GeoIPTool
from app.services.tools.dns_lookup import DNSLookupTool
from app.services.tools.whois_lookup import WhoisTool
from app.services.tools.ssl_cert import SSLCertTool
from app.services.tools.subdomains import SubdomainsTool
from app.services.tools.http_headers import HTTPHeadersTool
from app.services.tools.shodan_lookup import ShodanTool
from app.services.tools.virustotal import VirusTotalTool
from app.services.tools.blacklist import BlacklistTool
from app.services.tools.nmap_scan import NmapTool
from app.services.tools.cve_lookup import CVELookupTool
from app.services.tools.reverse_ip import ReverseIPTool
from app.services.tools.whois_history import WHOISHistoryTool
from app.services.tools.leakdb import LeakDBTool
from app.services.tools.bgp_asn import BGPASNTool

ALL_TOOLS = [
    # Original 9
    GeoIPTool(),
    DNSLookupTool(),
    WhoisTool(),
    SSLCertTool(),
    SubdomainsTool(),
    HTTPHeadersTool(),
    ShodanTool(),
    VirusTotalTool(),
    BlacklistTool(),
    # New 6
    NmapTool(),
    ReverseIPTool(),
    WHOISHistoryTool(),
    LeakDBTool(),
    BGPASNTool(),
    CVELookupTool(),  # runs last — uses nmap results
]


class InvestigationOrchestrator:
    def __init__(self):
        self.ai = MultiAIAnalyzer()

    async def investigate(
        self,
        target: str,
        tool_filter: Optional[List[str]] = None,
        scan_id: Optional[str] = None,
    ) -> tuple:
        if not scan_id:
            scan_id = str(uuid.uuid4())

        start_time = time.time()
        target_type = classify_target(target)

        tools = ALL_TOOLS
        if tool_filter:
            tools = [t for t in ALL_TOOLS if t.name in tool_filter]

        logger.info(f"🔍 [{scan_id[:8]}] Scanning {target} ({target_type}) with {len(tools)} tools")

        # Run all tools in parallel — CVE lookup runs after nmap but asyncio handles this
        tasks = [tool.run(target, target_type) for tool in tools]
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        for tool, result in zip(tools, tool_results):
            if isinstance(result, Exception):
                results[tool.name] = ToolResult(
                    status="error", error=str(result)
                ).model_dump()
            else:
                results[tool.name] = result.model_dump()

        success_count = sum(1 for r in results.values() if r["status"] == "success")

        # AI analysis — feed ALL tool results including new ones
        ai_analysis = None
        try:
            ai_analysis = await self.ai.analyze(target, results)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")

        total_duration = (time.time() - start_time) * 1000
        logger.info(f"✓ [{scan_id[:8]}] Done in {total_duration:.0f}ms — {success_count}/{len(tools)} tools succeeded")

        response = InvestigationResult(
            target=target,
            target_type=target_type,
            timestamp=datetime.now(timezone.utc),
            duration_ms=round(total_duration, 2),
            tools_run=len(tools),
            tools_success=success_count,
            results=results,
            ai_analysis=ai_analysis,
        )

        return response, scan_id
