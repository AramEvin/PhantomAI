"""
Nmap Tool — Real port scanner with OS detection, service versions, script scanning
Requires nmap installed in the system (added to Dockerfile)
"""
import asyncio
import re
from loguru import logger
from app.models.schemas import ToolResult


class NmapTool:
    name = "nmap"

    async def run(self, target: str, target_type: str) -> ToolResult:
        try:
            # Run nmap: -sV=service versions, -O=OS detection, -T4=fast timing
            # --script=vuln runs basic vuln scripts (finds CVEs from banners)
            # Top 1000 ports, skip host discovery (-Pn for reliability)
            cmd = [
                "nmap", "-sV", "-T4", "-Pn",
                "--open",           # only show open ports
                "--script=banner,http-title,ssl-cert,ssh-hostkey",
                "-p", "21,22,23,25,53,80,110,143,443,445,993,995,1433,1521,3306,3389,5432,5900,6379,8080,8443,8888,9200,27017",
                target
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(status="error", error="Nmap timed out after 60s")

            output = stdout.decode("utf-8", errors="ignore")
            if not output or "0 hosts up" in output:
                return ToolResult(status="error", error="Host appears down or filtered")

            parsed = self._parse_nmap(output)
            return ToolResult(status="success", data=parsed)

        except FileNotFoundError:
            return ToolResult(status="error", error="nmap not installed")
        except Exception as e:
            logger.error(f"Nmap error: {e}")
            return ToolResult(status="error", error=str(e))

    def _parse_nmap(self, output: str) -> dict:
        ports = []
        os_info = None
        hostnames = []
        scripts = {}

        # Parse port lines: 80/tcp  open  http  Apache httpd 2.4.51
        port_re = re.compile(
            r"(\d+)/(tcp|udp)\s+(open|filtered|closed)\s+(\S+)(?:\s+(.+))?"
        )
        for line in output.splitlines():
            m = port_re.match(line.strip())
            if m:
                port_num, proto, state, service, version = m.groups()
                ports.append({
                    "port": int(port_num),
                    "protocol": proto,
                    "state": state,
                    "service": service,
                    "version": (version or "").strip(),
                })

        # OS detection
        os_m = re.search(r"OS details: (.+)", output)
        if os_m:
            os_info = os_m.group(1).strip()

        # Aggressive OS guess
        if not os_info:
            os_m2 = re.search(r"Running(?: \(JUST GUESSING\))?: (.+)", output)
            if os_m2:
                os_info = os_m2.group(1).strip()

        # Hostname
        hn = re.search(r"Nmap scan report for (.+)", output)
        if hn:
            hostnames = [hn.group(1).strip()]

        # Script output (banner, http-title etc)
        script_re = re.compile(r"\|[_\-] (.+?): (.+)")
        for line in output.splitlines():
            m = script_re.match(line.strip())
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                scripts[key] = m.group(2).strip()

        # Extract software versions for CVE matching
        software_versions = []
        for p in ports:
            v = p.get("version", "")
            if v:
                software_versions.append(f"{p['service']} {v}".strip())

        return {
            "open_ports": ports,
            "open_port_count": len(ports),
            "os_detection": os_info,
            "hostnames": hostnames,
            "scripts": scripts,
            "software_versions": software_versions,
            "raw_summary": self._extract_summary(output),
        }

    def _extract_summary(self, output: str) -> str:
        lines = []
        for line in output.splitlines():
            if any(x in line for x in ["open", "OS details", "MAC Address", "Nmap done"]):
                lines.append(line.strip())
        return "\n".join(lines[:30])
