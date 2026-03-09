"""
CVE Deep Scan — Uses NVD (National Vulnerability Database) API
Detects software versions from other tools and looks up real CVEs
NVD API is free, no key required (rate limited to 5 req/30s without key)
"""
import asyncio
import httpx
import re
from loguru import logger
from app.models.schemas import ToolResult
from app.core.config import settings


NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Common software keywords to extract from scan data
SOFTWARE_PATTERNS = [
    r"(Apache(?:\s+httpd)?)[/ ]([\d.]+)",
    r"(nginx)[/ ]([\d.]+)",
    r"(OpenSSH)[/ ]([\d.]+)",
    r"(PHP)[/ ]([\d.]+)",
    r"(MySQL)[/ ]([\d.]+)",
    r"(PostgreSQL)[/ ]([\d.]+)",
    r"(MongoDB)[/ ]([\d.]+)",
    r"(Redis)[/ ]([\d.]+)",
    r"(IIS)[/ ]([\d.]+)",
    r"(WordPress)[/ ]([\d.]+)",
    r"(Drupal)[/ ]([\d.]+)",
    r"(OpenSSL)[/ ]([\d.]+)",
    r"(Tomcat)[/ ]([\d.]+)",
    r"(Jenkins)[/ ]([\d.]+)",
    r"(Elasticsearch)[/ ]([\d.]+)",
    r"(Kubernetes)[/ ]([\d.]+)",
    r"(Docker)[/ ]([\d.]+)",
    r"(vsftpd)[/ ]([\d.]+)",
    r"(ProFTPD)[/ ]([\d.]+)",
    r"(Exim)[/ ]([\d.]+)",
    r"(Postfix)[/ ]([\d.]+)",
]


class CVELookupTool:
    name = "cve_lookup"

    async def run(self, target: str, target_type: str) -> ToolResult:
        try:
            # CVE lookup needs context from other scan results
            # We'll accept a "scan_context" dict via the target field
            # But for standalone: extract from target string
            software_list = self._extract_software_from_target(target)

            if not software_list:
                return ToolResult(
                    status="success",
                    data={
                        "cves_found": [],
                        "software_detected": [],
                        "message": "No software version banners detected — run Nmap or Shodan first"
                    }
                )

            all_cves = []
            headers = {}
            if hasattr(settings, "NVD_API_KEY") and settings.NVD_API_KEY:
                headers["apiKey"] = settings.NVD_API_KEY

            async with httpx.AsyncClient(timeout=15) as client:
                for software, version in software_list[:6]:  # limit to 6 to avoid rate limits
                    cves = await self._lookup_cves(client, software, version, headers)
                    all_cves.extend(cves)
                    await asyncio.sleep(0.7)  # NVD rate limit: 5 req/30s

            # Sort by CVSS score
            all_cves.sort(key=lambda x: x.get("cvss_score", 0), reverse=True)

            return ToolResult(
                status="success",
                data={
                    "cves_found": all_cves[:20],
                    "cve_count": len(all_cves),
                    "critical_count": sum(1 for c in all_cves if c.get("severity") == "critical"),
                    "high_count": sum(1 for c in all_cves if c.get("severity") == "high"),
                    "software_detected": [f"{s} {v}" for s, v in software_list],
                }
            )

        except Exception as e:
            logger.error(f"CVE lookup error: {e}")
            return ToolResult(status="error", error=str(e))

    async def _lookup_cves(
        self, client: httpx.AsyncClient, software: str, version: str, headers: dict
    ) -> list:
        try:
            # Search NVD by keyword (software name + version)
            params = {
                "keywordSearch": f"{software} {version}",
                "keywordExactMatch": False,
                "resultsPerPage": 10,
            }
            resp = await client.get(NVD_API, params=params, headers=headers)
            if resp.status_code != 200:
                return []

            data = resp.json()
            cves = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_id = cve.get("id", "")

                # Get description
                descs = cve.get("descriptions", [])
                desc = next((d["value"] for d in descs if d["lang"] == "en"), "")

                # Get CVSS score
                metrics = cve.get("metrics", {})
                cvss_score = 0.0
                severity = "low"

                # Try CVSS v3.1 first, then v3.0, then v2
                for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    metric_list = metrics.get(key, [])
                    if metric_list:
                        cvss_data = metric_list[0].get("cvssData", {})
                        cvss_score = cvss_data.get("baseScore", 0.0)
                        sev = cvss_data.get("baseSeverity", "").lower()
                        if sev:
                            severity = sev
                        break

                if cvss_score < 4.0:
                    continue  # Skip low-impact CVEs

                # Get fix/references
                refs = cve.get("references", [])
                fix_url = next((r["url"] for r in refs if "patch" in r.get("tags", [])), "")
                if not fix_url:
                    fix_url = next((r["url"] for r in refs[:1]), "")

                cves.append({
                    "software": f"{software} {version}",
                    "cve_id": cve_id,
                    "severity": severity,
                    "cvss_score": cvss_score,
                    "description": desc[:300] if desc else "No description available",
                    "fix": fix_url or f"Update {software} to latest version",
                    "published": cve.get("published", "")[:10],
                })

            logger.info(f"CVE lookup: {software} {version} → {len(cves)} CVEs")
            return cves

        except Exception as e:
            logger.warning(f"CVE lookup failed for {software} {version}: {e}")
            return []

    def _extract_software_from_target(self, target: str) -> list[tuple]:
        """Extract software name + version from string (used for standalone run)"""
        found = []
        for pattern in SOFTWARE_PATTERNS:
            matches = re.findall(pattern, target, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    found.append((m[0], m[1]))
                else:
                    found.append((m, ""))
        return found
