from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from app.database import get_db
from app import schemas, crud
from app.services.git_parser import GitLogParser
from app.services.export_service import ExportService

router = APIRouter()

@router.post("/upload", response_model=schemas.CommitResponse)
def upload_commit(
    commit: schemas.CommitCreate,
    db: Session = Depends(get_db)
):
    """上传单条提交记录"""
    return crud.create_commit(db, commit)

@router.post("/upload/bulk", response_model=int)
def upload_commits_bulk(
    commits: List[schemas.CommitCreate],
    db: Session = Depends(get_db)
):
    """批量上传提交记录"""
    return crud.create_commits_bulk(db, commits)

@router.post("/upload/git-log")
def upload_git_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传 Git Log 文件并解析"""
    content = file.file.read().decode('utf-8')
    parser = GitLogParser()

    if file.filename.endswith('.csv'):
        commits = parser.parse_csv_data(content)
    else:
        commits = parser.parse_git_log(content)

    if not commits:
        raise HTTPException(status_code=400, detail="未能解析到任何提交记录")

    count = crud.create_commits_bulk(db, commits)
    return {"message": f"成功导入 {count} 条提交记录", "count": count}

@router.post("/upload/json")
def upload_json_data(
    commits: List[schemas.CommitCreate],
    db: Session = Depends(get_db)
):
    """粘贴 JSON 数据导入"""
    count = crud.create_commits_bulk(db, commits)
    return {"message": f"成功导入 {count} 条提交记录", "count": count}

@router.get("/", response_model=List[schemas.CommitResponse])
def list_commits(
    skip: int = 0,
    limit: int = 1000,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    authors: Optional[List[str]] = Query(None),
    repositories: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """查询提交记录"""
    s_date = datetime.fromisoformat(start_date) if start_date else None
    e_date = datetime.fromisoformat(end_date) if end_date else None
    return crud.get_commits(db, skip=skip, limit=limit, start_date=s_date, end_date=e_date, authors=authors, repositories=repositories, search=search)

@router.delete("/all")
def delete_all_commits(db: Session = Depends(get_db)):
    """清空所有提交数据"""
    count = crud.delete_all_commits(db)
    return {"message": f"已删除 {count} 条提交记录"}

@router.get("/authors")
def get_authors(db: Session = Depends(get_db)):
    """获取所有作者列表"""
    return crud.get_authors(db)

@router.get("/repositories")
def get_repositories(db: Session = Depends(get_db)):
    """获取所有仓库列表"""
    return crud.get_repositories(db)
