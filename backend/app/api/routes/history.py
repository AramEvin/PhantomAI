from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, Any
from app.database import get_db, ScanRecord
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ScanSummary(BaseModel):
    id: int
    target: str
    target_type: str
    timestamp: datetime
    duration_ms: float
    tools_run: int
    tools_success: int
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None

class ScanDetail(ScanSummary):
    results: Optional[Any] = None
    ai_analysis: Optional[Any] = None

@router.get("/history", response_model=list[ScanSummary])
async def get_history(limit: int = Query(20, le=100), offset: int = Query(0), target: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    q = select(ScanRecord).order_by(desc(ScanRecord.timestamp)).limit(limit).offset(offset)
    if target:
        q = q.where(ScanRecord.target.ilike(f"%{target}%"))
    result = await db.execute(q)
    records = result.scalars().all()
    return [ScanSummary(id=r.id, target=r.target, target_type=r.target_type, timestamp=r.timestamp, duration_ms=r.duration_ms, tools_run=r.tools_run, tools_success=r.tools_success, risk_level=r.risk_level, risk_score=r.risk_score) for r in records]

@router.get("/history/{scan_id}", response_model=ScanDetail)
async def get_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanDetail(id=record.id, target=record.target, target_type=record.target_type, timestamp=record.timestamp, duration_ms=record.duration_ms, tools_run=record.tools_run, tools_success=record.tools_success, risk_level=record.risk_level, risk_score=record.risk_score, results=record.results, ai_analysis=record.ai_analysis)

@router.delete("/history/{scan_id}")
async def delete_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScanRecord).where(ScanRecord.id == scan_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")
    await db.delete(record)
    await db.commit()
    return {"deleted": scan_id}

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count(ScanRecord.id)))
    by_risk = await db.execute(select(ScanRecord.risk_level, func.count(ScanRecord.id)).group_by(ScanRecord.risk_level))
    top_targets = await db.execute(select(ScanRecord.target, func.count(ScanRecord.id).label("count")).group_by(ScanRecord.target).order_by(desc("count")).limit(5))
    return {"total_scans": total.scalar(), "by_risk_level": {r: c for r, c in by_risk.all()}, "top_targets": [{"target": t, "count": c} for t, c in top_targets.all()]}
