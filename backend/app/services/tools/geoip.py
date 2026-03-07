"""
Tool: GeoIP - Get geolocation, ASN, ISP info for IP/domain
Uses ip-api.com (free, no key needed)
"""
import httpx
from .base import BaseTool
from app.utils.target import resolve_to_ip, TargetType

class GeoIPTool(BaseTool):
    name = "geoip"
    description = "Geolocation, ASN, ISP, country, city, coordinates"

    async def execute(self, target: str, target_type: str) -> dict:
        ip = target if target_type == TargetType.IP else resolve_to_ip(target)
        if not ip:
            raise Exception(f"Could not resolve {target} to IP")

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,query"}
            )
            data = resp.json()

        if data.get("status") == "fail":
            raise Exception(data.get("message", "GeoIP lookup failed"))

        return {
            "ip": data.get("query"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "zip": data.get("zip"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "asn": data.get("as"),
            "asn_name": data.get("asname"),
        }
