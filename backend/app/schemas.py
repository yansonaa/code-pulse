"""Pydantic 数据模型 (Schema)"""
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Dict

class CommitBase(BaseModel):
    commit_hash: str
    author: str
    email: Optional[str] = None
    date: datetime
    message: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0
    review_comments_count: int = 0
    is_automated: bool = False
    repository: Optional[str] = None
    branch: Optional[str] = None

    @validator('additions', 'deletions', 'files_changed', 'review_comments_count', pre=True, always=True)
    def default_zero_for_none(cls, v):
        return 0 if v is None else v

class CommitCreate(CommitBase):
    pass

class CommitResponse(CommitBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MemberBase(BaseModel):
    name: str
    email: Optional[str] = None
    team: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int

    class Config:
        orm_mode = True

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class KPIResponse(BaseModel):
    total_commits: int
    net_lines: int
    active_developers: int
    avg_review_response_hours: float
    period_days: int

class TrendPoint(BaseModel):
    date: str
    count: int
    additions: int
    deletions: int

class TrendResponse(BaseModel):
    data: List[TrendPoint]
    has_decline: bool
    decline_dates: List[str]

class CodeStats(BaseModel):
    author: str
    additions: int
    deletions: int
    net: int
    commits: int

class HeatmapPoint(BaseModel):
    day: int  # 0=Mon, 6=Sun
    hour: int
    count: int

class HeatmapResponse(BaseModel):
    data: List[HeatmapPoint]
    max_count: int
    anomalies: List[Dict]

class RadarDimension(BaseModel):
    dimension: str
    value: float
    full_mark: float = 100

class MemberRadar(BaseModel):
    author: str
    dimensions: List[RadarDimension]

class ExportRequest(BaseModel):
    format: str  # csv, excel, pdf
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    authors: Optional[List[str]] = None

class RepositoryConfigBase(BaseModel):
    name: str
    repo_type: str = "local"  # local, github, gitlab
    local_path: Optional[str] = None
    remote_url: Optional[str] = None
    access_token: Optional[str] = None
    branch: Optional[str] = "main"
    is_active: bool = True
    auto_sync: bool = False

class RepositoryConfigCreate(RepositoryConfigBase):
    pass

class RepositoryConfigUpdate(BaseModel):
    name: Optional[str] = None
    repo_type: Optional[str] = None
    local_path: Optional[str] = None
    remote_url: Optional[str] = None
    access_token: Optional[str] = None
    branch: Optional[str] = None
    is_active: Optional[bool] = None
    auto_sync: Optional[bool] = None

class RepositoryConfigResponse(RepositoryConfigBase):
    id: int
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SyncResult(BaseModel):
    success: bool
    message: str
    imported_count: int = 0
    repo_name: Optional[str] = None
    branch: Optional[str] = None

class RepositoryConfigListResponse(BaseModel):
    data: List[RepositoryConfigResponse]
    total: int

class AnomalyReport(BaseModel):
    author: str
    anomaly_type: str
    description: str
    severity: str  # low, medium, high
    details: Dict[str, int]
