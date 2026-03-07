"""PhantomAI Pydantic Models"""
from pydantic import BaseModel, field_validator
from typing import Optional, Any, Dict, List
from enum import Enum
import re

class TargetType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"

class InvestigateRequest(BaseModel):
    target: str
    tools: Optional[List[str]] = None

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        v = v.strip().lower()
        ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        domain_pattern = r"^([a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$"
        if not re.match(ip_pattern, v) and not re.match(domain_pattern, v):
            raise ValueError(f"Invalid IP address or domain: {v}")
        return v

class ToolResult(BaseModel):
    tool_name: str
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None

class AIAnalysis(BaseModel):
    summary: str
    risk_level: str
    risk_score: int
    key_findings: List[str] = []
    recommendations: List[str] = []
    tags: List[str] = []
    infrastructure: Dict[str, Any] = {}
    attack_surface: Dict[str, Any] = {}
    port_risks: List[Dict[str, Any]] = []
    threat_intel: Dict[str, Any] = {}

class InvestigateResponse(BaseModel):
    target: str
    target_type: TargetType
    timestamp: str
    duration_ms: float
    tools_run: int
    tools_success: int
    results: Dict[str, Any]
    ai_analysis: Optional[AIAnalysis] = None
