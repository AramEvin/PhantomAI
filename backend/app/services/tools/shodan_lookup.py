from app.models.schemas import ToolResult, TargetType

class ShodanTool:
    name = "shodan"

    async def run(self, target: str, target_type: TargetType) -> ToolResult:
        if not __import__('app.core.config', fromlist=['settings']).settings.SHODAN_API_KEY:
            return ToolResult(tool_name=self.name, status="skipped", data={"note": "No Shodan API key configured"})
        try:
            import shodan
            api = shodan.Shodan(__import__('app.core.config', fromlist=['settings']).settings.SHODAN_API_KEY)
            import asyncio
            loop = asyncio.get_event_loop()
            host = await loop.run_in_executor(None, lambda: api.host(target))
            return ToolResult(tool_name=self.name, status="success", data={
                "found": True,
                "ip": host.get("ip_str"),
                "org": host.get("org"),
                "isp": host.get("isp"),
                "country": host.get("country_name"),
                "city": host.get("city"),
                "os": host.get("os"),
                "ports": host.get("ports", []),
                "hostnames": host.get("hostnames", []),
                "domains": host.get("domains", []),
                "tags": host.get("tags", []),
                "vulns": host.get("vulns", {}),
                "last_update": host.get("last_update"),
                "services": [{"port": s["port"], "transport": s.get("transport"), "product": s.get("product"), "version": s.get("version"), "banner": s.get("data", "")[:200]} for s in host.get("data", [])]
            })
        except Exception as e:
            err = str(e)
            if "upgrade" in err.lower() or "403" in err or "401" in err:
                return ToolResult(tool_name=self.name, status="skipped", data={"note": "Shodan free plan — upgrade at shodan.io/store/member"})
            return ToolResult(tool_name=self.name, status="error", data={"note": err})
