from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app import schemas
from app.services.stats_calculator import StatsCalculator

router = APIRouter()

def _get_calculator(db: Session = Depends(get_db)):
    return StatsCalculator(db)

def _parse_date(date_str: Optional[str]):
    from datetime import datetime
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")

@router.get("/kpi", response_model=schemas.KPIResponse)
def get_kpi(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取 KPI 概览数据"""
    return calculator.get_kpi(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        search=search
    )

@router.get("/trend", response_model=schemas.TrendResponse)
def get_trend(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    interval: str = Query("day"),
    search: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取提交频率趋势图数据"""
    return calculator.get_trend(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        interval=interval,
        search=search
    )

@router.get("/code", response_model=List[schemas.CodeStats])
def get_code_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取代码量构成分析数据"""
    return calculator.get_code_stats(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        search=search
    )

@router.get("/heatmap", response_model=schemas.HeatmapResponse)
def get_heatmap(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取提交时段热力图数据"""
    return calculator.get_heatmap(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        search=search
    )

@router.get("/radar")
def get_radar(
    author: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取评审参与度雷达图数据"""
    return calculator.get_radar(author=author)

@router.get("/anomalies", response_model=List[schemas.AnomalyReport])
def get_anomalies(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    calculator: StatsCalculator = Depends(_get_calculator)
):
    """获取异常检测报告"""
    return calculator.get_anomalies(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        search=search
    )
