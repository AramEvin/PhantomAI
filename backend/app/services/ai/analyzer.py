"""
PhantomAI Multi-AI Analyzer
Providers: Claude, GPT-4o, Gemini, Groq, Cohere, Mistral, DeepSeek, Grok, Perplexity, Together, Ollama
Deep analysis: ports, threat intel, attack surface, infrastructure fingerprinting, CVE lookup
Merges all results into one unified report
"""
import json
import re
import asyncio
from loguru import logger
from app.core.config import settings

# ─── Prompts ─────────────────────────────────────────────────────────────────

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
6. CVE LOOKUP — identify software versions from scan data and list known CVEs

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
  "cve_findings": [
    {{
      "software": "Apache 2.4.49",
      "cve_id": "CVE-2021-41773",
      "severity": "critical|high|medium|low",
      "cvss_score": 9.8,
      "description": "Path traversal and RCE vulnerability",
      "fix": "Upgrade to Apache 2.4.51 or later"
    }}
  ],
  "severity_findings": [
    {{
      "severity": "critical|medium|ok",
      "category": "SSL|Headers|Ports|Blacklist|DNS|WHOIS|Malware|Config|CVE",
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

CVE rules:
- Extract ALL software names and versions from the scan data (server headers, SSL cert, Shodan banners)
- Look up real CVEs for those exact versions
- If no version detected, skip that software
- Only include CVEs you are confident about for the detected version
- CVSS score must be a real number (0.0-10.0)

Severity rules — be thorough, list ALL findings:
CRITICAL: RDP/Telnet/FTP open, malware detected, blacklisted, no SSL, admin panel exposed, critical CVE
MEDIUM: Missing security headers, weak SSL config, WHOIS privacy off, info disclosure, medium CVE
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

    # Merge port risks — dedupe by port number
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

    # Merge CVE findings — dedupe by cve_id
    cve_map = {}
    for r in valid:
        for c in r.get("cve_findings", []):
            cve_id = c.get("cve_id", "")
            if cve_id and cve_id not in cve_map:
                cve_map[cve_id] = c
    # Sort CVEs by CVSS score descending
    cve_findings = sorted(cve_map.values(), key=lambda x: x.get("cvss_score", 0), reverse=True)

    # Merge severity findings — dedupe by title
    sev_map = {}
    for r in valid:
        for f in r.get("severity_findings", []):
            title = f.get("title", "").lower()[:60]
            if title and title not in sev_map:
                sev_map[title] = f
    severity_findings = list(sev_map.values())

    return {
        "summary": best_summary,
        "risk_level": max_risk,
        "risk_score": avg_score,
        "infrastructure": infra,
        "attack_surface": attack,
        "port_risks": port_risks,
        "threat_intel": threat,
        "cve_findings": cve_findings,
        "severity_findings": severity_findings,
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
            logger.warning("Gemini: rate limited")
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

async def call_deepseek(data_str: str, target: str) -> dict | None:
    if not settings.DEEPSEEK_API_KEY or "your_" in settings.DEEPSEEK_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        # DeepSeek uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        resp = await client.chat.completions.create(
            model="deepseek-chat", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ DeepSeek responded")
        return result
    except Exception as e:
        logger.error(f"DeepSeek error: {e}")
        return None

async def call_grok(data_str: str, target: str) -> dict | None:
    if not settings.GROK_API_KEY or "your_" in settings.GROK_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        # xAI Grok uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=settings.GROK_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        resp = await client.chat.completions.create(
            model="grok-3", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ Grok responded")
        return result
    except Exception as e:
        logger.error(f"Grok error: {e}")
        return None

async def call_perplexity(data_str: str, target: str) -> dict | None:
    if not settings.PERPLEXITY_API_KEY or "your_" in settings.PERPLEXITY_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        # Perplexity uses OpenAI-compatible API
        # Uses sonar model which has live web search built in
        client = AsyncOpenAI(
            api_key=settings.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        resp = await client.chat.completions.create(
            model="sonar", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ Perplexity responded")
        return result
    except Exception as e:
        logger.error(f"Perplexity error: {e}")
        return None

async def call_together(data_str: str, target: str) -> dict | None:
    if not settings.TOGETHER_API_KEY or "your_" in settings.TOGETHER_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        # Together AI uses OpenAI-compatible API
        client = AsyncOpenAI(
            api_key=settings.TOGETHER_API_KEY,
            base_url="https://api.together.xyz/v1"
        )
        resp = await client.chat.completions.create(
            # Meta Llama 3.3 70B — best open source model on Together
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo", max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.format(target=target, data=data_str)}
            ]
        )
        result = parse_json(resp.choices[0].message.content)
        logger.info("✓ Together AI responded")
        return result
    except Exception as e:
        logger.error(f"Together AI error: {e}")
        return None

async def call_ollama(data_str: str, target: str) -> dict | None:
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


# ─── Main Analyzer ───────────────────────────────────────────────────────────

from app.models.schemas import AIAnalysis

class MultiAIAnalyzer:
    async def analyze(self, target: str, results: dict) -> AIAnalysis | None:
        clean_data = build_clean_data(results)
        if not clean_data:
            return self._local_analysis(target, {})

        data_str = json.dumps(clean_data, indent=2, default=str)
        if len(data_str) > 18000:
            data_str = data_str[:18000] + "\n...[truncated]"

        # Run ALL 11 AIs in parallel
        ai_results = await asyncio.gather(
            call_claude(data_str, target),
            call_openai(data_str, target),
            call_gemini(data_str, target),
            call_groq(data_str, target),
            call_cohere(data_str, target),
            call_mistral(data_str, target),
            call_deepseek(data_str, target),
            call_grok(data_str, target),
            call_perplexity(data_str, target),
            call_together(data_str, target),
            call_ollama(data_str, target),
            return_exceptions=False
        )

        valid = [r for r in ai_results if r is not None]
        logger.info(f"AI analysis: {len(valid)}/11 providers responded")

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
                    cve_findings=merged.get("cve_findings", []),
                    severity_findings=merged.get("severity_findings", []),
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
                recommendations.append("Investigate blacklist listings")
                risk_score += min(listed * 12, 50)
                tags.append("blacklisted")
            else:
                findings.append(f"Clean — not listed on any of {total} DNS blacklists")
                tags.append("clean-blacklist")

        ssl = data.get("ssl", {})
        if ssl:
            if ssl.get("expired"):
                findings.append("⚠️ SSL certificate is EXPIRED")
                attack_surface["ssl_issues"].append("Expired certificate")
                risk_score += 20
                tags.append("expired-ssl")
            elif ssl.get("valid"):
                days = ssl.get("days_remaining", 0)
                findings.append(f"SSL valid — {days} days remaining")
                tags.append("valid-ssl")

        return AIAnalysis(
            summary=f"Local analysis of {target}. " + " ".join(findings[:3]),
            risk_level="high" if risk_score > 60 else "medium" if risk_score > 30 else "low",
            risk_score=min(risk_score, 100),
            key_findings=findings[:8],
            recommendations=recommendations[:5],
            tags=tags,
            infrastructure=infrastructure,
            attack_surface=attack_surface,
            port_risks=port_risks,
            threat_intel=threat_intel,
            cve_findings=[],
            severity_findings=[],
        )
