"""
Reverse IP Tool — Find all domains hosted on the same IP
Uses HackerTarget API (free, 100 req/day without key)
"""
import httpx
from loguru import logger
from app.models.schemas import ToolResult


class ReverseIPTool:
    name = "reverse_ip"

    async def run(self, target: str, target_type: str) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # HackerTarget reverse IP — free, no key needed
                resp = await client.get(
                    "https://api.hackertarget.com/reverseiplookup/",
                    params={"q": target}
                )

                if resp.status_code != 200:
                    return ToolResult(status="error", error=f"API error: {resp.status_code}")

                text = resp.text.strip()

                # Check for rate limit or error
                if "error" in text.lower() or "api count" in text.lower():
                    return ToolResult(status="error", error=text)

                if not text or text == target:
                    return ToolResult(
                        status="success",
                        data={"domains": [], "domain_count": 0, "note": "No other domains found on this IP"}
                    )

                domains = [d.strip() for d in text.splitlines() if d.strip()]

                # Remove the target itself from results
                domains = [d for d in domains if d != target]

                # Categorize
                subdomains = [d for d in domains if len(d.split(".")) > 2]
                root_domains = [d for d in domains if len(d.split(".")) <= 2]

                return ToolResult(
                    status="success",
                    data={
                        "domains": domains[:100],  # cap at 100
                        "domain_count": len(domains),
                        "root_domains": root_domains[:20],
                        "subdomains": subdomains[:50],
                        "shared_hosting": len(domains) > 10,
                        "risk_note": (
                            "High domain count indicates shared hosting — one compromised domain can affect others"
                            if len(domains) > 20 else
                            "Low domain count — likely dedicated or VPS hosting"
                        )
                    }
                )

        except Exception as e:
            logger.error(f"Reverse IP error: {e}")
            return ToolResult(status="error", error=str(e))
