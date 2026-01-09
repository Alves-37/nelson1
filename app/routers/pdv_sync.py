from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.db.database import get_db_session
from app.db.models import PdvSyncStatus

router = APIRouter(prefix="/api/pdv-sync", tags=["PDV Sync"])


class PdvSyncStatusIn(BaseModel):
    pdv_id: str = Field(..., min_length=1, max_length=80)
    status: str = Field(..., min_length=1, max_length=30)
    total_enviadas: int = 0
    total_recebidas: int = 0
    pending_sales_local: int = 0
    errors: List[str] = Field(default_factory=list)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    app_version: Optional[str] = None
    device_name: Optional[str] = None


@router.post("/status")
async def upsert_pdv_sync_status(payload: PdvSyncStatusIn, db: AsyncSession = Depends(get_db_session)):
    try:
        stmt = select(PdvSyncStatus).where(PdvSyncStatus.pdv_id == payload.pdv_id)
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()

        now = datetime.utcnow()
        errors_json: Dict[str, Any] = {"errors": payload.errors}

        if existing:
            existing.status = payload.status
            existing.total_enviadas = int(payload.total_enviadas or 0)
            existing.total_recebidas = int(payload.total_recebidas or 0)
            existing.pending_sales_local = int(payload.pending_sales_local or 0)
            existing.errors_json = errors_json
            existing.started_at = payload.started_at
            existing.finished_at = payload.finished_at
            existing.app_version = payload.app_version
            existing.device_name = payload.device_name
            existing.last_seen_at = now
        else:
            row = PdvSyncStatus(
                pdv_id=payload.pdv_id,
                status=payload.status,
                total_enviadas=int(payload.total_enviadas or 0),
                total_recebidas=int(payload.total_recebidas or 0),
                pending_sales_local=int(payload.pending_sales_local or 0),
                errors_json=errors_json,
                started_at=payload.started_at,
                finished_at=payload.finished_at,
                app_version=payload.app_version,
                device_name=payload.device_name,
                last_seen_at=now,
            )
            db.add(row)

        await db.commit()
        return {"status": "ok"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar status do PDV: {e}")


@router.get("/status")
async def list_pdv_sync_status(db: AsyncSession = Depends(get_db_session)):
    try:
        stmt = select(PdvSyncStatus).order_by(PdvSyncStatus.last_seen_at.desc())
        res = await db.execute(stmt)
        rows = res.scalars().all()
        out = []
        for r in rows:
            out.append(
                {
                    "pdv_id": r.pdv_id,
                    "status": r.status,
                    "total_enviadas": int(r.total_enviadas or 0),
                    "total_recebidas": int(r.total_recebidas or 0),
                    "pending_sales_local": int(r.pending_sales_local or 0),
                    "errors": (getattr(r, "errors_json", None) or {}).get("errors", []),
                    "started_at": r.started_at,
                    "finished_at": r.finished_at,
                    "app_version": r.app_version,
                    "device_name": r.device_name,
                    "last_seen_at": r.last_seen_at.isoformat() if getattr(r, "last_seen_at", None) else None,
                }
            )
        return {"items": out, "count": len(out)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar status dos PDVs: {e}")
