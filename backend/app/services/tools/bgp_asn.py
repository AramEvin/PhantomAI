"""
BGP / ASN Intelligence Tool
Gets routing info, netblock owner, upstream providers, country routing
Uses BGPView API (free, no key needed)
"""
import httpx
import re
from loguru import logger
from app.models.schemas import ToolResult


BGPVIEW_API = "https://api.bgpview.io"


class BGPASNTool:
    name = "bgp_asn"

    async def run(self, target: str, target_type: str) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Step 1: Get ASN info for IP/domain
                ip_data = await self._get_ip_info(client, target)
                if not ip_data:
                    return ToolResult(status="error", error="Could not resolve BGP info")

                asn = ip_data.get("asn")
                result = {"ip_info": ip_data}

                # Step 2: Get full ASN details if we have one
                if asn:
                    asn_data = await self._get_asn_details(client, asn)
                    if asn_data:
                        result["asn_details"] = asn_data

                    # Step 3: Get ASN prefixes (IP ranges owned by this ASN)
                    prefixes = await self._get_asn_prefixes(client, asn)
                    if prefixes:
                        result["prefixes"] = prefixes

                    # Step 4: Get ASN peers (upstream/downstream providers)
                    peers = await self._get_asn_peers(client, asn)
                    if peers:
                        result["peers"] = peers

                return ToolResult(status="success", data=result)

        except Exception as e:
            logger.error(f"BGP/ASN error: {e}")
            return ToolResult(status="error", error=str(e))

    async def _get_ip_info(self, client: httpx.AsyncClient, target: str) -> dict | None:
        try:
            resp = await client.get(f"{BGPVIEW_API}/ip/{target}")
            if resp.status_code != 200:
                return None
            data = resp.json().get("data", {})

            prefixes = data.get("prefixes", [])
            prefix = prefixes[0] if prefixes else {}
            asn_info = prefix.get("asn", {})

            return {
                "ip": target,
                "asn": asn_info.get("asn"),
                "asn_name": asn_info.get("name"),
                "asn_description": asn_info.get("description"),
                "prefix": prefix.get("prefix"),
                "prefix_name": prefix.get("name"),
                "country_code": prefix.get("country_code"),
                "rir_allocation": prefix.get("rir_allocation", {}).get("rir_name"),
            }
        except Exception as e:
            logger.warning(f"BGPView IP lookup error: {e}")
            return None

    async def _get_asn_details(self, client: httpx.AsyncClient, asn: int) -> dict | None:
        try:
            resp = await client.get(f"{BGPVIEW_API}/asn/{asn}")
            if resp.status_code != 200:
                return None
            data = resp.json().get("data", {})
            return {
                "asn": data.get("asn"),
                "name": data.get("name"),
                "description_short": data.get("description_short"),
                "description_full": data.get("description_full", [])[:3],
                "country_code": data.get("country_code"),
                "website": data.get("website"),
                "email_contacts": data.get("email_contacts", [])[:3],
                "abuse_contacts": data.get("abuse_contacts", [])[:3],
                "looking_glass": data.get("looking_glass"),
                "traffic_estimation": data.get("traffic_estimation"),
                "traffic_ratio": data.get("traffic_ratio"),
                "rir_allocation": data.get("rir_allocation", {}).get("rir_name"),
                "founded_year": data.get("info", {}).get("org_id"),
            }
        except Exception as e:
            logger.warning(f"BGPView ASN details error: {e}")
            return None

    async def _get_asn_prefixes(self, client: httpx.AsyncClient, asn: int) -> dict | None:
        try:
            resp = await client.get(f"{BGPVIEW_API}/asn/{asn}/prefixes")
            if resp.status_code != 200:
                return None
            data = resp.json().get("data", {})
            v4 = data.get("ipv4_prefixes", [])
            v6 = data.get("ipv6_prefixes", [])
            return {
                "ipv4_prefix_count": len(v4),
                "ipv6_prefix_count": len(v6),
                "ipv4_prefixes": [
                    {"prefix": p.get("prefix"), "name": p.get("name"), "country": p.get("country_code")}
                    for p in v4[:10]
                ],
                "ipv6_prefixes": [
                    {"prefix": p.get("prefix"), "name": p.get("name")}
                    for p in v6[:5]
                ],
            }
        except Exception as e:
            logger.warning(f"BGPView prefixes error: {e}")
            return None

    async def _get_asn_peers(self, client: httpx.AsyncClient, asn: int) -> dict | None:
        try:
            resp = await client.get(f"{BGPVIEW_API}/asn/{asn}/peers")
            if resp.status_code != 200:
                return None
            data = resp.json().get("data", {})
            v4_peers = data.get("ipv4_peers", [])

            return {
                "upstream_count": len(v4_peers),
                "upstreams": [
                    {
                        "asn": p.get("asn"),
                        "name": p.get("name"),
                        "description": p.get("description"),
                        "country": p.get("country_code"),
                    }
                    for p in v4_peers[:10]
                ],
            }
        except Exception as e:
            logger.warning(f"BGPView peers error: {e}")
            return None
