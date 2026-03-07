"""
Tool: Subdomain Enumeration - Find subdomains via crt.sh
"""
import httpx
from .base import BaseTool

class SubdomainsTool(BaseTool):
    name = "subdomains"
    description = "Find subdomains using certificate transparency logs (crt.sh)"

    async def execute(self, target: str, target_type: str) -> dict:
        if target_type == "ip":
            return {"note": "Subdomain enumeration not applicable for IP addresses"}

        subdomains = set()
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://crt.sh/",
                    params={"q": f"%.{target}", "output": "json"}
                )
                entries = resp.json()
                for entry in entries:
                    name = entry.get("name_value", "")
                    for sub in name.split("\n"):
                        sub = sub.strip().lstrip("*.")
                        if sub.endswith(target) and sub != target:
                            subdomains.add(sub)
        except Exception as e:
            return {"error": str(e), "subdomains": []}

        sorted_subs = sorted(list(subdomains))
        return {
            "count": len(sorted_subs),
            "subdomains": sorted_subs
        }
