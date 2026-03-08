"""
PhantomAI Multi-AI Analyzer
Providers: Claude, GPT-4o, Gemini, Groq, Cohere, Mistral, Ollama
Deep analysis: ports, threat intel, attack surface, infrastructure fingerprinting
Merges all results into one unified report
"""
import json
import re
import asyncio
from loguru import logger
from app.core.config import settings

# ─── Prompts ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are PhantomAI, an elite cybersecurity analyst and threat intelligence expert.
Analyze OSINT data and return ONLY valid JSON. No markdown. No explanation outside JSON.
Be specific — use actual values from the data. Skip empty, null, or false values entirely."""

ANALYSIS_PROMPT = """Perform a comprehensive security analysis for target: {target}

RAW OSINT DATA:
{data}

DEEP ANALYSIS REQUIRED:

1. INFRASTRUCTURE FINGERPRINTING
2. ATTACK SURFACE MAPPING
3. PORT & SERVICE RISK SCORING
4. THREAT INTELLIGENCE
5. SEVERITY-TAGGED FINDINGS with REMEDIATION

Return ONLY this JSON:
{{
  "summary": "4-6 sentence summary covering infrastructure, ownership, threat posture, key risks",
  "risk_level": "low|medium|high|critical",
  "risk_score": <integer 0-100>,
  "infrastructure": {{
    "hosting_provider": "string",
    "server_type": "string",
    "cdn_detected": true,
    "cloud_provider": "string",
    "fingerprint_notes": ["note1"]
  }},
  "attack_surface": {{
    "total_entry_points": 0,
    "exposed_services": ["service:port"],
    "subdomains_count": 0,
    "critical_exposures": ["exposure1"],
    "ssl_issues": ["issue1"]
  }},
  "port_risks": [
    {{"port": 80, "service": "http", "risk": "low|medium|high|critical", "note": "reason"}}
  ],
  "threat_intel": {{
    "blacklist_status": "clean|listed",
    "blacklist_count": 0,
    "reputation_score": 100,
    "malware_detected": false,
    "threat_indicators": ["indicator1"],
    "abuse_history": "none detected"
  }},
  "severity_findings": [
    {{
      "severity": "critical|medium|ok",
      "category": "SSL|Headers|Ports|Blacklist|DNS|WHOIS|Malware|Config",
      "title": "Short title of the finding",
      "detail": "Specific detail using real values from the scan",
      "fix": "1. Step one\\n2. Step two\\n3. Step three — null if severity is ok"
    }}
  ],
  "key_findings": ["finding1"],
  "recommendations": ["action1"],
  "tags": ["tag1"]
}}

Risk scoring guide:
0-20: Clean infrastructure, trusted, well configured
21-40: Minor issues, some missing configs
41-60: Notable concerns, weak security posture
61-80: High risk, vulnerabilities or blacklisted
81-100: Critical — malware, heavily blacklisted, dangerous

Severity rules — be thorough, list ALL findings:
CRITICAL: RDP/Telnet/FTP open, malware detected, blacklisted, no SSL, admin panel exposed
MEDIUM: Missing security headers, weak SSL config, WHOIS privacy off, info disclosure
OK: Valid SSL cert, clean blacklist, HSTS present, CSP configured, low VirusTotal score"""




# ─── Helpers ─────────────────────────────────────────────────────────────────

def parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group())

def strip_empty(obj):
    if isinstance(obj, dict):
        c = {k: strip_empty(v) for k, v in obj.items()}
        return {k: v for k, v in c.items() if v not in (None, "", [], {}, False)}
    if isinstance(obj, list):
        c = [strip_empty(i) for i in obj]
        return [i for i in c if i not in (None, "", [], {}, False)]
    return obj

def build_clean_data(results: dict) -> dict:
    clean = {}
    for name, result in results.items():
        if result.get("status") != "success":
            continue
        data = result.get("data")
        if not data:
            continue
        if isinstance(data, dict) and data.get("skipped"):
            continue
        cleaned = strip_empty(data)
        if cleaned:
            clean[name] = cleaned
    return clean

def merge_results(results: list) -> dict | None:
    valid = [r for r in results if r and isinstance(r, dict)]
    if not valid:
        return None

    risk_order = ["low", "medium", "high", "critical"]
    scores = [r.get("risk_score", 0) for r in valid]
    avg_score = round(sum(scores) / len(scores))
    max_risk = max(
        (r.get("risk_level", "low") for r in valid),
        key=lambda x: risk_order.index(x) if x in risk_order else 0
    )

    # Deduplicate and merge lists
    def merge_list(key):
        seen = set()
        out = []
        for r in valid:
            for item in r.get(key, []):
                k = str(item).lower()[:50]
                if k not in seen:
                    seen.add(k)
                    out.append(item)
        return out

    # Best summary = longest
    best_summary = max((r.get("summary", "") for r in valid), key=len)

    # Merge infrastructure
    infra = {}
    for r in valid:
        i = r.get("infrastructure", {})
        if i:
            for k, v in i.items():
                if v and v not in ("unknown", False) and k not in infra:
                    infra[k] = v
    if any(r.get("infrastructure", {}) for r in valid):
        notes = list(set(
            n for r in valid
            for n in r.get("infrastructure", {}).get("fingerprint_notes", [])
        ))
        infra["fingerprint_notes"] = notes

    # Merge attack surface
    attack = {}
    for r in valid:
        a = r.get("attack_surface", {})
        if a:
            for k, v in a.items():
                if v and k not in attack:
                    attack[k] = v
    if any(r.get("attack_surface", {}) for r in valid):
        exposures = list(set(
            e for r in valid
            for e in r.get("attack_surface", {}).get("critical_exposures", [])
        ))
        attack["critical_exposures"] = exposures
        services = list(set(
            s for r in valid
            for s in r.get("attack_surface", {}).get("exposed_services", [])
        ))
        attack["exposed_services"] = services

    # Merge port risks - dedupe by port
    port_map = {}
    for r in valid:
        for p in r.get("port_risks", []):
            port = p.get("port")
            if port and port not in port_map:
                port_map[port] = p
    port_risks = list(port_map.values())

    # Merge threat intel
    threat = {}
    for r in valid:
        t = r.get("threat_intel", {})
        if t:
            for k, v in t.items():
                if v and k not in threat:
                    threat[k] = v
    if any(r.get("threat_intel", {}) for r in valid):
        indicators = list(set(
            i for r in valid
            for i in r.get("threat_intel", {}).get("threat_indicators", [])
        ))
        threat["threat_indicators"] = indicators

    return {
        "summary": best_summary,
        "risk_level": max_risk,
        "risk_score": avg_score,
        "infrastructure": infra,
        "attack_surface": attack,
        "port_risks": port_risks,
        "threat_intel": threat,
        "key_findings": merge_list("key_findings")[:12],
        "recommendations": merge_list("recommendations")[:8],
        "tags": list(set(t for r in valid for t in r.get("tags", []))),
    }


# ─── AI Callers ──────────────────────────────────────────────────────────────

async def call_claude(data_str: str, target: str) -> dict | None:
    if not settings.ANTHROPIC_API_KEY or "your_" in settings.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        loop = asyncio.get_event_loop()
        msg = await loop.run_in_executor(None, lambda: client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}]
        ))
        result = parse_json(msg.content[0].text)
        logger.info("✓ Claude responded")
        return result
    except Exception as e:
        if "credit balance" in str(e):
            logger.warning("Claude: insufficient credits")
        else:
            logger.error(f"Claude error: {e}")
        return None

async def call_openai(data_str: str, target: str) -> dict | None:
    if not settings.OPENAI_API_KEY or "your_" in settings.OPENAI_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.chat.completions.create(
            model="gpt-4o", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ GPT-4o responded")
        return result
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None

async def call_gemini(data_str: str, target: str) -> dict | None:
    if not settings.GEMINI_API_KEY or "your_" in settings.GEMINI_API_KEY:
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: client.models.generate_content(
            model="gemini-2.0-flash",
            contents=ANALYSIS_PROMPT.format(target=target, data=data_str),
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        ))
        result = parse_json(resp.text)
        logger.info("✓ Gemini responded")
        return result
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            logger.warning("Gemini: rate limited — will retry next scan")
        else:
            logger.error(f"Gemini error: {e}")
        return None

async def call_groq(data_str: str, target: str) -> dict | None:
    if not settings.GROQ_API_KEY or "your_" in settings.GROQ_API_KEY:
        return None
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ Groq responded")
        return result
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return None

async def call_cohere(data_str: str, target: str) -> dict | None:
    if not settings.COHERE_API_KEY or "your_" in settings.COHERE_API_KEY:
        return None
    try:
        import cohere
        co = cohere.AsyncClientV2(api_key=settings.COHERE_API_KEY)
        resp = await co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.message.content[0].text)
        logger.info("✓ Cohere responded")
        return result
    except Exception as e:
        err = str(e)
        if "removed" in err or "404" in err:
            logger.warning("Cohere: model unavailable")
        else:
            logger.error(f"Cohere error: {e}")
        return None

async def call_mistral(data_str: str, target: str) -> dict | None:
    if not settings.MISTRAL_API_KEY or "your_" in settings.MISTRAL_API_KEY:
        return None
    try:
        from mistralai import Mistral
        client = Mistral(api_key=settings.MISTRAL_API_KEY)
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        ))
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ Mistral responded")
        return result
    except Exception as e:
        logger.error(f"Mistral error: {e}")
        return None

async def call_ollama(data_str: str, target: str) -> dict | None:
    # Silently skip if Ollama is not running
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as check:
            r = await check.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if r.status_code != 200:
                return None
    except Exception:
        return None
    try:
        import httpx
        prompt = f"{SYSTEM_PROMPT}\n\n{ANALYSIS_PROMPT.format(target=target, data=data_str)}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False}
            )
            if resp.status_code != 200:
                return None
            text = resp.json().get("response", "")
            result = parse_json(text)
            logger.info(f"✓ Ollama ({settings.OLLAMA_MODEL}) responded")
            return result
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return None


# ─── Schemas ─────────────────────────────────────────────────────────────────

from app.models.schemas import AIAnalysis

class MultiAIAnalyzer:
    async def analyze(self, target: str, results: dict) -> AIAnalysis | None:
        clean_data = build_clean_data(results)
        if not clean_data:
            return self._local_analysis(target, {})

        data_str = json.dumps(clean_data, indent=2, default=str)
        if len(data_str) > 18000:
            data_str = data_str[:18000] + "\n...[truncated]"

        # Run ALL AIs in parallel
        ai_results = await asyncio.gather(
            call_claude(data_str, target),
            call_openai(data_str, target),
            call_gemini(data_str, target),
            call_groq(data_str, target),
            call_cohere(data_str, target),
            call_mistral(data_str, target),
            call_ollama(data_str, target),
            return_exceptions=False
        )

        valid = [r for r in ai_results if r is not None]
        logger.info(f"AI analysis: {len(valid)}/7 providers responded")

        if valid:
            merged = merge_results(valid)
            if merged:
                return AIAnalysis(
                    summary=merged.get("summary", ""),
                    risk_level=merged.get("risk_level", "low"),
                    risk_score=merged.get("risk_score", 0),
                    key_findings=merged.get("key_findings", []),
                    recommendations=merged.get("recommendations", []),
                    tags=merged.get("tags", []),
                    infrastructure=merged.get("infrastructure", {}),
                    attack_surface=merged.get("attack_surface", {}),
                    port_risks=merged.get("port_risks", []),
                    threat_intel=merged.get("threat_intel", {}),
                )

        logger.info("All AI providers unavailable — using local analysis")
        return self._local_analysis(target, clean_data)

    def _local_analysis(self, target: str, data: dict) -> AIAnalysis:
        findings = []
        recommendations = []
        tags = []
        risk_score = 0
        port_risks = []
        attack_surface = {"exposed_services": [], "critical_exposures": [], "ssl_issues": []}
        infrastructure = {"fingerprint_notes": []}
        threat_intel = {"threat_indicators": [], "blacklist_count": 0}

        # GeoIP
        geo = data.get("geoip", {})
        if geo:
            country = geo.get("country", "")
            city = geo.get("city", "")
            isp = geo.get("isp", "")
            org = geo.get("org", "")
            asn = geo.get("asn", "")
            loc = f"{city}, {country}".strip(", ")
            if loc:
                findings.append(f"Hosted in {loc} by {isp or org}" + (f" ({asn})" if asn else ""))
            infrastructure["hosting_provider"] = isp or org or "Unknown"
            infrastructure["fingerprint_notes"].append(f"ASN: {asn}" if asn else "No ASN info")
            tags.append("has-geo")

        # Blacklist
        bl = data.get("blacklist", {})
        if bl:
            listed = bl.get("listed_count", 0)
            total = bl.get("total_checked", 0)
            threat_intel["blacklist_count"] = listed
            threat_intel["blacklist_status"] = "listed" if listed > 0 else "clean"
            if listed > 0:
                listed_on = [r["list"] for r in bl.get("results", []) if r.get("listed")]
                findings.append(f"⚠️ Blacklisted on {listed}/{total} DNS blacklists: {', '.join(listed_on[:3])}")
                threat_intel["threat_indicators"].append(f"Listed on {listed} DNSBL lists")
                threat_intel["abuse_history"] = f"Listed on {listed} blacklists"
                recommendations.append("Investigate blacklist listings — may indicate spam, botnet, or abuse")
                risk_score += min(listed * 12, 50)
                tags.append("blacklisted")
            else:
                findings.append(f"Clean — not listed on any of {total} DNS blacklists")
                tags.append("clean-blacklist")

        # DNS
        dns = data.get("dns", {})
        if dns:
            a = dns.get("A", [])
            mx = dns.get("MX", [])
            ns = dns.get("NS", [])
            txt = dns.get("TXT", [])
            if a:
                findings.append(f"Resolves to: {', '.join(a[:3])}")
                attack_surface["exposed_services"].extend([f"DNS:53"])
                tags.append("has-dns")
            if mx:
                findings.append(f"Mail servers: {', '.join(mx[:2])}")
                attack_surface["exposed_services"].append("SMTP:25")
                tags.append("has-mx")
            if ns:
                infrastructure["fingerprint_notes"].append(f"Nameservers: {', '.join(ns[:2])}")
            if txt:
                spf = [t for t in txt if 'spf' in t.lower()]
                dmarc = [t for t in txt if 'dmarc' in t.lower()]
                if spf:
                    findings.append("SPF record configured — email spoofing protection active")
                    tags.append("has-spf")
                else:
                    recommendations.append("Add SPF TXT record to prevent email spoofing")
                    attack_surface["critical_exposures"].append("No SPF record — email spoofing possible")
                if dmarc:
                    tags.append("has-dmarc")

        # SSL
        ssl = data.get("ssl", {})
        live = ssl.get("live_cert", {}) if ssl else {}
        if live.get("is_valid"):
            issuer = live.get("issuer", {}).get("organizationName", "")
            not_after = live.get("not_after", "")
            san_count = len(live.get("san", []))
            findings.append(f"Valid SSL/TLS certificate" + (f" by {issuer}" if issuer else "") + (f", expires {not_after}" if not_after else "") + (f", {san_count} SANs" if san_count else ""))
            attack_surface["exposed_services"].append("HTTPS:443")
            infrastructure["fingerprint_notes"].append(f"TLS cert issuer: {issuer}" if issuer else "TLS enabled")
            tags.append("has-ssl")
        elif ssl:
            findings.append("No valid SSL/TLS certificate on port 443")
            attack_surface["ssl_issues"].append("No valid SSL certificate")
            attack_surface["critical_exposures"].append("HTTP without TLS — traffic unencrypted")
            recommendations.append("Configure HTTPS with valid SSL certificate immediately")
            risk_score += 15
            tags.append("no-ssl")

        # HTTP Headers
        http = data.get("http_headers", {})
        http_data = http.get("https", http.get("http", {})) if http else {}
        if isinstance(http_data, dict) and http_data.get("status_code"):
            server = http_data.get("server", "")
            powered_by = http_data.get("powered_by", "")
            missing = http_data.get("missing_security_headers", [])
            if server and server != "Unknown":
                findings.append(f"Web server: {server}" + (f" ({powered_by})" if powered_by and powered_by != "Unknown" else ""))
                infrastructure["server_type"] = server
                infrastructure["fingerprint_notes"].append(f"Server header: {server}")
            if missing:
                findings.append(f"Missing {len(missing)} HTTP security headers: {', '.join(missing[:4])}")
                for h in missing:
                    attack_surface["ssl_issues"].append(f"Missing header: {h}")
                recommendations.append(f"Implement missing security headers: {', '.join(missing[:4])}")
                risk_score += len(missing) * 2
                tags.append("weak-headers")
            else:
                findings.append("All HTTP security headers properly configured")
                tags.append("strong-headers")

        # Subdomains
        subs = data.get("subdomains", {})
        if subs and subs.get("count", 0) > 0:
            count = subs["count"]
            sample = subs.get("subdomains", [])[:4]
            findings.append(f"Found {count} subdomains via cert transparency: {', '.join(sample)}" + (f" +{count-4} more" if count > 4 else ""))
            attack_surface["subdomains_count"] = count
            if count > 20:
                attack_surface["critical_exposures"].append(f"Large attack surface: {count} subdomains")
                recommendations.append(f"Audit all {count} subdomains — each is a potential entry point")
                risk_score += 5
            tags.append(f"{count}-subdomains")

        # WHOIS
        whois = data.get("whois", {})
        if whois:
            registrar = whois.get("registrar", "")
            expiry = whois.get("expiration_date", "")
            org = whois.get("org", "")
            country = whois.get("country", "")
            if registrar:
                findings.append(f"Domain registered via {registrar}" + (f", org: {org}" if org else "") + (f", country: {country}" if country else ""))
                if expiry:
                    findings.append(f"Domain expires: {str(expiry)[:10]}")
                infrastructure["fingerprint_notes"].append(f"Registrar: {registrar}")
                tags.append("whois-available")

        # Shodan
        shodan = data.get("shodan", {})
        if shodan and shodan.get("found"):
            ports = shodan.get("ports", [])
            vulns = shodan.get("vulns", {})
            os_info = shodan.get("os", "")
            if os_info:
                infrastructure["fingerprint_notes"].append(f"OS: {os_info}")
            if ports:
                findings.append(f"Open ports: {', '.join(map(str, ports[:10]))}")
                attack_surface["total_entry_points"] = len(ports)
                for port in ports:
                    attack_surface["exposed_services"].append(f"port:{port}")
                    risk = "low"
                    note = "Standard service"
                    if port in [23, 2323]: risk = "critical"; note = "Telnet — unencrypted, disable immediately"
                    elif port in [3389]: risk = "high"; note = "RDP exposed — brute force target"
                    elif port in [445, 139]: risk = "high"; note = "SMB — common ransomware vector"
                    elif port in [1433, 3306, 5432, 27017]: risk = "high"; note = "Database port exposed to internet"
                    elif port in [21]: risk = "medium"; note = "FTP — use SFTP instead"
                    elif port in [22]: risk = "medium"; note = "SSH — ensure key-only auth"
                    elif port in [80]: risk = "low"; note = "HTTP — ensure redirects to HTTPS"
                    elif port in [443]: risk = "low"; note = "HTTPS — standard web traffic"
                    if risk in ("high", "critical"):
                        attack_surface["critical_exposures"].append(f"Port {port}: {note}")
                    port_risks.append({"port": port, "service": note.split(" —")[0], "risk": risk, "note": note})
                    risk_score += {"low": 0, "medium": 3, "high": 8, "critical": 15}.get(risk, 0)
            if vulns:
                cves = list(vulns.keys())
                findings.append(f"⚠️ {len(cves)} CVEs detected: {', '.join(cves[:4])}")
                threat_intel["threat_indicators"].extend(cves[:5])
                risk_score += len(cves) * 8
                recommendations.append(f"URGENT: Patch CVEs — {', '.join(cves[:3])}")
                tags.append("has-cves")

        # VirusTotal
        vt = data.get("virustotal", {})
        if vt and vt.get("found"):
            malicious = vt.get("malicious", 0)
            suspicious = vt.get("suspicious", 0)
            reputation = vt.get("reputation", 0)
            threat_intel["reputation_score"] = max(0, 100 + reputation)
            threat_intel["malware_detected"] = malicious > 0
            if malicious > 0:
                findings.append(f"⚠️ VirusTotal: {malicious} AV engines flagged as MALICIOUS")
                threat_intel["threat_indicators"].append(f"Flagged malicious by {malicious} AV engines")
                risk_score += malicious * 8
                tags.append("malicious-vt")
                recommendations.append(f"CRITICAL: {malicious} AV engines flagged this — investigate immediately")
            elif suspicious > 0:
                findings.append(f"VirusTotal: {suspicious} engines flagged suspicious, reputation: {reputation}")
                risk_score += suspicious * 3
                tags.append("suspicious-vt")
            else:
                findings.append(f"VirusTotal: Clean — reputation score {reputation}")
                tags.append("clean-vt")

        # CDN detection
        cdn_headers = ["cloudflare", "fastly", "akamai", "cloudfront", "cdn"]
        if http_data:
            headers_str = json.dumps(http_data.get("headers", {})).lower()
            for cdn in cdn_headers:
                if cdn in headers_str:
                    infrastructure["cdn_detected"] = True
                    infrastructure["cloud_provider"] = cdn.title()
                    infrastructure["fingerprint_notes"].append(f"CDN detected: {cdn.title()}")
                    tags.append(f"cdn-{cdn}")
                    break

        risk_score = min(risk_score, 100)
        if risk_score <= 20: risk_level = "low"
        elif risk_score <= 40: risk_level = "medium"
        elif risk_score <= 65: risk_level = "high"
        else: risk_level = "critical"

        attack_surface["total_entry_points"] = attack_surface.get("total_entry_points", len(attack_surface["exposed_services"]))

        geo_str = f"in {geo.get('city', '')}, {geo.get('country', '')}".strip(", ") if geo else "at unknown location"
        isp_str = f"by {geo.get('isp', geo.get('org', 'unknown provider'))}" if geo else ""
        bl_str = f"blacklisted on {bl.get('listed_count', 0)} lists" if bl and bl.get("listed_count", 0) > 0 else "not blacklisted"
        ssl_str = "has valid SSL/TLS" if live.get("is_valid") else "no SSL detected"
        ports_str = f"{len(shodan.get('ports', []))} open ports detected" if shodan and shodan.get("found") else "no port data available"
        sub_str = f"{subs.get('count', 0)} subdomains discovered" if subs else ""

        summary_parts = [
            f"Target {target} is hosted {geo_str} {isp_str}.",
            f"It is {bl_str} and {ssl_str}.",
        ]
        if ports_str: summary_parts.append(f"Shodan reports {ports_str}.")
        if sub_str: summary_parts.append(f"Certificate transparency reveals {sub_str}.")
        summary_parts.append(f"Overall risk assessment: {risk_score}/100 ({risk_level.upper()}).")

        return AIAnalysis(
            summary=" ".join(summary_parts),
            risk_level=risk_level,
            risk_score=risk_score,
            key_findings=findings or ["Scan completed — add AI API keys for deeper analysis"],
            recommendations=recommendations or ["No immediate action required based on available data"],
            tags=list(set(tags)),
            infrastructure=infrastructure,
            attack_surface=attack_surface,
            port_risks=port_risks,
            threat_intel=threat_intel,
        )
