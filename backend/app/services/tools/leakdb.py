"""
LeakDB / Breach Check Tool
Checks HaveIBeenPwned API for breaches associated with the target domain
Free API key from https://haveibeenpwned.com/API/Key
"""
import httpx
from loguru import logger
from app.models.schemas import ToolResult
from app.core.config import settings


HIBP_API = "https://haveibeenpwned.com/api/v3"


class LeakDBTool:
    name = "leakdb"

    async def run(self, target: str, target_type: str) -> ToolResult:
        results = {}

        # Domain breach check — check all breaches that affected this domain
        if target_type == "domain":
            breaches = await self._check_domain_breaches(target)
            results["domain_breaches"] = breaches

        # Check pastes (IPs and domains)
        pastes = await self._check_pastes(target)
        results["pastes"] = pastes

        # Compute risk summary
        breach_count = len(results.get("domain_breaches", {}).get("breaches", []))
        paste_count = results.get("pastes", {}).get("paste_count", 0)

        risk = "clean"
        if breach_count > 0 or paste_count > 0:
            risk = "exposed"
        if breach_count > 3 or paste_count > 5:
            risk = "high_exposure"

        results["summary"] = {
            "breach_count": breach_count,
            "paste_count": paste_count,
            "exposure_risk": risk,
        }

        has_data = breach_count > 0 or paste_count > 0 or "error" not in str(results)
        return ToolResult(
            status="success" if has_data else "error",
            data=results,
            error=None if has_data else "No data returned"
        )

    async def _check_domain_breaches(self, domain: str) -> dict:
        """Check all breaches that involved this domain (HIBP API)"""
        if not hasattr(settings, "HIBP_API_KEY") or not settings.HIBP_API_KEY:
            return {
                "error": "HIBP_API_KEY not configured",
                "note": "Get a free key at haveibeenpwned.com/API/Key",
                "breaches": []
            }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{HIBP_API}/breacheddomain/{domain}",
                    headers={
                        "hibp-api-key": settings.HIBP_API_KEY,
                        "user-agent": "PhantomAI-OSINT"
                    }
                )

                if resp.status_code == 404:
                    return {"breaches": [], "message": "No breaches found for this domain"}
                if resp.status_code == 401:
                    return {"error": "Invalid HIBP API key", "breaches": []}
                if resp.status_code != 200:
                    return {"error": f"HIBP API error {resp.status_code}", "breaches": []}

                data = resp.json()
                breaches = []
                for email, breach_list in data.items():
                    breaches.append({
                        "email": email,
                        "breaches": breach_list,
                        "breach_count": len(breach_list)
                    })

                return {
                    "breaches": breaches,
                    "affected_accounts": len(breaches),
                    "breach_names": list(set(
                        b for item in breaches for b in item["breaches"]
                    ))[:20]
                }

        except Exception as e:
            logger.error(f"HIBP domain check error: {e}")
            return {"error": str(e), "breaches": []}

    async def _check_pastes(self, target: str) -> dict:
        """Check if target appears in public paste sites"""
        if not hasattr(settings, "HIBP_API_KEY") or not settings.HIBP_API_KEY:
            return {"paste_count": 0, "note": "HIBP_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{HIBP_API}/pasteaccount/{target}",
                    headers={
                        "hibp-api-key": settings.HIBP_API_KEY,
                        "user-agent": "PhantomAI-OSINT"
                    }
                )

                if resp.status_code == 404:
                    return {"paste_count": 0, "pastes": []}
                if resp.status_code != 200:
                    return {"paste_count": 0, "error": f"Status {resp.status_code}"}

                pastes = resp.json()
                return {
                    "paste_count": len(pastes),
                    "pastes": [
                        {
                            "source": p.get("Source"),
                            "title": p.get("Title"),
                            "date": p.get("Date", "")[:10] if p.get("Date") else None,
                            "email_count": p.get("EmailCount"),
                        }
                        for p in pastes[:10]
                    ]
                }

        except Exception as e:
            logger.warning(f"HIBP paste check error: {e}")
            return {"paste_count": 0, "error": str(e)}
