"""
Tool: DNS Lookup - Fetch all DNS record types
"""
import asyncio
import dns.resolver
import dns.reversename
from .base import BaseTool

class DNSLookupTool(BaseTool):
    name = "dns"
    description = "A, AAAA, MX, NS, TXT, CNAME, SOA, PTR records"

    async def execute(self, target: str, target_type: str) -> dict:
        results = {}
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        for rtype in record_types:
            try:
                answers = resolver.resolve(target, rtype)
                records = []
                for rdata in answers:
                    records.append(str(rdata))
                results[rtype] = records
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                results[rtype] = []
            except Exception as e:
                results[rtype] = {"error": str(e)}

        # Reverse DNS if IP
        if target_type == "ip":
            try:
                rev = dns.reversename.from_address(target)
                ptr = resolver.resolve(rev, "PTR")
                results["PTR"] = [str(r) for r in ptr]
            except Exception:
                results["PTR"] = []

        return results
