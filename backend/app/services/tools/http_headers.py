"""
Tool: HTTP Headers - Fetch HTTP headers and detect technologies
"""
import httpx
from .base import BaseTool

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "x-xss-protection",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-embedder-policy",
]

class HTTPHeadersTool(BaseTool):
    name = "http_headers"
    description = "HTTP response headers, server tech, security headers analysis"

    async def execute(self, target: str, target_type: str) -> dict:
        results = {}

        for scheme in ["https", "http"]:
            url = f"{scheme}://{target}"
            try:
                async with httpx.AsyncClient(
                    timeout=10,
                    follow_redirects=True,
                    verify=False
                ) as client:
                    resp = await client.get(url, headers={"User-Agent": "PhantomAI/1.0"})

                headers = dict(resp.headers)
                # Security headers analysis
                security_analysis = {}
                for h in SECURITY_HEADERS:
                    security_analysis[h] = headers.get(h, "MISSING")

                results[scheme] = {
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    "headers": headers,
                    "server": headers.get("server", "Unknown"),
                    "powered_by": headers.get("x-powered-by", "Unknown"),
                    "content_type": headers.get("content-type", ""),
                    "security_headers": security_analysis,
                    "missing_security_headers": [
                        h for h in SECURITY_HEADERS
                        if h not in headers
                    ],
                    "redirect_count": len(resp.history),
                }
                break  # Got a response, don't try http if https worked
            except Exception as e:
                results[scheme] = {"error": str(e)}

        return results
