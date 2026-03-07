"""
Tool: WHOIS - Domain registration info, owner, dates
"""
import asyncio
import socket
import whois
from .base import BaseTool

class WhoisTool(BaseTool):
    name = "whois"
    description = "Registrar, owner, creation/expiry dates, nameservers, status"

    async def execute(self, target: str, target_type: str) -> dict:
        loop = asyncio.get_event_loop()
        try:
            w = await asyncio.wait_for(
                loop.run_in_executor(None, self._do_whois, target),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            raise Exception("WHOIS lookup timed out after 10s")
        except socket.gaierror as e:
            raise Exception(f"DNS resolution failed for WHOIS: {e}")
        except Exception as e:
            raise Exception(f"WHOIS lookup failed: {e}")

        def serialize(val):
            if val is None:
                return None
            if isinstance(val, list):
                return [str(v) for v in val]
            return str(val)

        return {
            "domain_name": serialize(w.domain_name),
            "registrar": serialize(w.registrar),
            "whois_server": serialize(w.whois_server),
            "creation_date": serialize(w.creation_date),
            "expiration_date": serialize(w.expiration_date),
            "updated_date": serialize(w.updated_date),
            "name_servers": serialize(w.name_servers),
            "status": serialize(w.status),
            "emails": serialize(w.emails),
            "dnssec": serialize(w.dnssec),
            "name": serialize(w.name),
            "org": serialize(w.org),
            "country": serialize(w.country),
        }

    def _do_whois(self, target: str):
        return whois.whois(target)
