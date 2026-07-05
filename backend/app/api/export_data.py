from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.export_service import ExportService

router = APIRouter()

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")

@router.get("/csv")
def export_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """导出 CSV 格式的提交记录"""
    service = ExportService(db)
    csv_data = service.export_csv(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date)
    )
    return StreamingResponse(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=codepulse_commits.csv"}
    )

@router.get("/members/csv")
def export_member_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """导出成员统计 CSV"""
    service = ExportService(db)
    csv_data = service.export_member_csv(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date)
    )
    return StreamingResponse(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=codepulse_members.csv"}
    )
