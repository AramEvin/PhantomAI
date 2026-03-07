"""
Tool: Blacklist Check - Check if IP is on spam/abuse blacklists
"""
import asyncio
import dns.resolver
from .base import BaseTool
from app.utils.target import resolve_to_ip

# Common DNS-based blacklists
DNSBL_LISTS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "dnsbl.sorbs.net",
    "b.barracudacentral.org",
    "dnsbl-1.uceprotect.net",
    "psbl.surriel.com",
    "cbl.abuseat.org",
    "db.wpbl.info",
]

class BlacklistTool(BaseTool):
    name = "blacklist"
    description = "DNSBL spam/abuse blacklist checks"

    async def execute(self, target: str, target_type: str) -> dict:
        ip = target if target_type == "ip" else resolve_to_ip(target)
        if not ip:
            raise Exception(f"Could not resolve {target}")

        # Reverse the IP for DNSBL query
        reversed_ip = ".".join(reversed(ip.split(".")))
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3

        results = []
        listed_count = 0

        for dnsbl in DNSBL_LISTS:
            query = f"{reversed_ip}.{dnsbl}"
            try:
                resolver.resolve(query, "A")
                results.append({"list": dnsbl, "listed": True})
                listed_count += 1
            except dns.resolver.NXDOMAIN:
                results.append({"list": dnsbl, "listed": False})
            except Exception:
                results.append({"list": dnsbl, "listed": None, "error": "timeout"})

        return {
            "ip": ip,
            "listed_count": listed_count,
            "total_checked": len(DNSBL_LISTS),
            "is_blacklisted": listed_count > 0,
            "results": results,
        }
