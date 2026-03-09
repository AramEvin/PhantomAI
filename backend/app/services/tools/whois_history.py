"""
WHOIS History Tool — Track domain ownership changes over time
Uses WhoisXML API (free tier: 500 req/month)
Falls back to SecurityTrails free API if configured
"""
import httpx
from loguru import logger
from app.models.schemas import ToolResult
from app.core.config import settings


class WHOISHistoryTool:
    name = "whois_history"

    async def run(self, target: str, target_type: str) -> ToolResult:
        # Only makes sense for domains
        if target_type == "ip":
            return ToolResult(
                status="success",
                data={"note": "WHOIS history is only available for domains, not IPs"}
            )

        # Try WhoisXML API first
        if hasattr(settings, "WHOISXML_API_KEY") and settings.WHOISXML_API_KEY:
            result = await self._whoisxml_history(target)
            if result:
                return ToolResult(status="success", data=result)

        # Fallback: SecurityTrails
        if hasattr(settings, "SECURITYTRAILS_API_KEY") and settings.SECURITYTRAILS_API_KEY:
            result = await self._securitytrails_history(target)
            if result:
                return ToolResult(status="success", data=result)

        # Free fallback: basic WHOIS age analysis from current record
        result = await self._basic_age_analysis(target)
        return ToolResult(status="success", data=result)

    async def _whoisxml_history(self, domain: str) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://whois-history.whoisxmlapi.com/api/v1",
                    params={
                        "apiKey": settings.WHOISXML_API_KEY,
                        "domainName": domain,
                        "outputFormat": "JSON",
                    }
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                records = data.get("records", [])
                if not records:
                    return None

                history = []
                for r in records[:10]:
                    history.append({
                        "date": r.get("date", ""),
                        "registrar": r.get("registrarName", ""),
                        "registrant": r.get("registrantName", ""),
                        "registrant_org": r.get("registrantOrganization", ""),
                        "registrant_country": r.get("registrantCountry", ""),
                        "expires": r.get("expiresDate", ""),
                    })

                return {
                    "source": "WhoisXML",
                    "domain": domain,
                    "history_count": len(records),
                    "history": history,
                    "ownership_changes": self._count_ownership_changes(history),
                    "risk_flags": self._analyze_history_risk(history),
                }
        except Exception as e:
            logger.warning(f"WhoisXML history error: {e}")
            return None

    async def _securitytrails_history(self, domain: str) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://api.securitytrails.com/v1/history/{domain}/whois",
                    headers={"APIKEY": settings.SECURITYTRAILS_API_KEY},
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                result = data.get("result", {})
                items = result.get("items", [])

                history = []
                for item in items[:10]:
                    history.append({
                        "date": item.get("added", ""),
                        "registrar": item.get("registrar", ""),
                        "registrant": item.get("contacts", [{}])[0].get("name", "") if item.get("contacts") else "",
                        "nameservers": item.get("nameservers", []),
                    })

                return {
                    "source": "SecurityTrails",
                    "domain": domain,
                    "history_count": len(items),
                    "history": history,
                    "ownership_changes": self._count_ownership_changes(history),
                    "risk_flags": self._analyze_history_risk(history),
                }
        except Exception as e:
            logger.warning(f"SecurityTrails history error: {e}")
            return None

    async def _basic_age_analysis(self, domain: str) -> dict:
        """Free fallback — basic risk analysis from current WHOIS"""
        try:
            import whois as python_whois
            import asyncio
            from datetime import datetime, timezone

            loop = asyncio.get_event_loop()
            w = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: python_whois.whois(domain)),
                timeout=10
            )

            created = w.creation_date
            if isinstance(created, list):
                created = created[0]
            expires = w.expiration_date
            if isinstance(expires, list):
                expires = expires[0]

            age_days = None
            if created:
                now = datetime.now(timezone.utc)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                age_days = (now - created).days

            risk_flags = []
            if age_days and age_days < 30:
                risk_flags.append("⚠ Domain registered less than 30 days ago — high phishing risk")
            if age_days and age_days < 180:
                risk_flags.append("New domain — less than 6 months old")
            if w.registrar and "privacy" in w.registrar.lower():
                risk_flags.append("Registrar offers privacy protection — owner identity hidden")

            return {
                "source": "basic_whois",
                "domain": domain,
                "created": str(created)[:10] if created else None,
                "expires": str(expires)[:10] if expires else None,
                "age_days": age_days,
                "registrar": str(w.registrar) if w.registrar else None,
                "history_count": 1,
                "history": [],
                "risk_flags": risk_flags,
                "note": "Add WHOISXML_API_KEY or SECURITYTRAILS_API_KEY for full ownership history",
            }
        except Exception as e:
            return {
                "source": "basic_whois",
                "error": str(e),
                "note": "Could not retrieve WHOIS history",
            }

    def _count_ownership_changes(self, history: list) -> int:
        registrants = set()
        for h in history:
            r = h.get("registrant") or h.get("registrant_org")
            if r:
                registrants.add(r.lower())
        return max(0, len(registrants) - 1)

    def _analyze_history_risk(self, history: list) -> list:
        flags = []
        if len(history) > 5:
            flags.append(f"Domain has changed hands {len(history)} times — unusual ownership history")
        registrants = [h.get("registrant", "") for h in history if h.get("registrant")]
        if len(set(registrants)) > 3:
            flags.append("Multiple different owners detected — potential domain parking or resale")
        return flags
