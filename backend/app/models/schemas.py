from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TargetType(str, Enum):
    ip = "ip"
    domain = "domain"


class InvestigateRequest(BaseModel):
    target: str
    tools: Optional[List[str]] = None  # if None, run all tools

class ToolResult(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: Optional[float] = None

class SeverityFinding(BaseModel):
    severity: str        # critical | medium | ok
    category: str
    title: str
    detail: str
    fix: Optional[str] = None

class CVEFinding(BaseModel):
    software: str
    cve_id: str
    severity: str        # critical | high | medium | low
    cvss_score: float
    description: str
    fix: str

class AIAnalysis(BaseModel):
    summary: str = ""
    risk_level: str = "low"
    risk_score: int = 0
    key_findings: List[str] = []
    recommendations: List[str] = []
    tags: List[str] = []
    infrastructure: Dict[str, Any] = {}
    attack_surface: Dict[str, Any] = {}
    port_risks: List[Dict[str, Any]] = []
    threat_intel: Dict[str, Any] = {}
    severity_findings: List[SeverityFinding] = []
    cve_findings: List[CVEFinding] = []

class InvestigationResult(BaseModel):
    target: str
    target_type: str
    timestamp: datetime
    duration_ms: float = 0.0
    tools_run: int = 0
    tools_success: int = 0
    results: Dict[str, Any] = {}
    ai_analysis: Optional[AIAnalysis] = None

class ScanRecord(BaseModel):
    id: int
    target: str
    target_type: str
    timestamp: datetime
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    tools_run: int = 0
    tools_success: int = 0

    class Config:
        from_attributes = True
