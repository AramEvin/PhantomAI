"""
Tool: SSL Certificate - Check TLS cert details, expiry, SANs
Uses crt.sh for certificate transparency logs
"""
import httpx
import ssl
import socket
from datetime import datetime
from .base import BaseTool

class SSLCertTool(BaseTool):
    name = "ssl"
    description = "SSL/TLS certificate details, validity, SANs, issuer"

    async def execute(self, target: str, target_type: str) -> dict:
        results = {}

        # Live cert check via socket
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((target, 443), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                    cert = ssock.getpeercert()

            not_before = cert.get("notBefore", "")
            not_after = cert.get("notAfter", "")

            # Parse SANs
            sans = []
            for san_type, san_val in cert.get("subjectAltName", []):
                sans.append({"type": san_type, "value": san_val})

            results["live_cert"] = {
                "subject": dict(x[0] for x in cert.get("subject", [])),
                "issuer": dict(x[0] for x in cert.get("issuer", [])),
                "version": cert.get("version"),
                "serial_number": cert.get("serialNumber"),
                "not_before": not_before,
                "not_after": not_after,
                "san": sans,
                "ocsp": cert.get("OCSP"),
                "is_valid": True,
            }
        except ssl.SSLError as e:
            results["live_cert"] = {"error": f"SSL Error: {e}", "is_valid": False}
        except Exception as e:
            results["live_cert"] = {"error": str(e), "is_valid": False}

        # crt.sh - certificate transparency
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://crt.sh/",
                    params={"q": target, "output": "json"}
                )
                certs = resp.json()
                # Get last 10 certs
                results["cert_transparency"] = certs[:10] if certs else []
        except Exception as e:
            results["cert_transparency"] = {"error": str(e)}

        return results
