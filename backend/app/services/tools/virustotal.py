"""
Tool: VirusTotal - Reputation, malware detections
"""
import httpx
from .base import BaseTool
from app.core.config import settings

class VirusTotalTool(BaseTool):
    name = "virustotal"
    description = "Malware detections, reputation score, analysis stats"

    async def execute(self, target: str, target_type: str) -> dict:
        if not settings.VIRUSTOTAL_API_KEY:
            return {"skipped": True, "reason": "VIRUSTOTAL_API_KEY not configured"}

        endpoint = "ip_addresses" if target_type == "ip" else "domains"

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://www.virustotal.com/api/v3/{endpoint}/{target}",
                headers={"x-apikey": settings.VIRUSTOTAL_API_KEY}
            )

        if resp.status_code == 404:
            return {"found": False, "target": target}

        if resp.status_code != 200:
            raise Exception(f"VirusTotal API error: {resp.status_code}")

        data = resp.json().get("data", {})
        attrs = data.get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})

        return {
            "found": True,
            "reputation": attrs.get("reputation", 0),
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "clean": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "total_votes": attrs.get("total_votes", {}),
            "tags": attrs.get("tags", []),
            "last_analysis_date": attrs.get("last_analysis_date"),
            "categories": attrs.get("categories", {}),
            "whois": attrs.get("whois", ""),
        }
