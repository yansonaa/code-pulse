from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import os

from app.database import get_db
from app import schemas, crud, models
from app.services.local_git_service import LocalGitService
from app.services.remote_git_service import RemoteGitService

router = APIRouter()

@router.get("/configs", response_model=schemas.RepositoryConfigListResponse)
def list_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有仓库配置"""
    configs = crud.get_repository_configs(db, skip=skip, limit=limit)
    return schemas.RepositoryConfigListResponse(
        data=configs,
        total=len(configs)
    )

@router.post("/configs", response_model=schemas.RepositoryConfigResponse)
def create_config(
    config: schemas.RepositoryConfigCreate,
    db: Session = Depends(get_db)
):
    """创建仓库配置"""
    # 验证配置
    if config.repo_type == "local":
        if not config.local_path:
            raise HTTPException(status_code=400, detail="本地仓库必须提供路径")
        # 尝试验证路径
        try:
            LocalGitService(config.local_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        if not config.remote_url:
            raise HTTPException(status_code=400, detail="远程仓库必须提供URL")
        if not config.access_token:
            raise HTTPException(status_code=400, detail="远程仓库必须提供Access Token")

    return crud.create_repository_config(db, config)

@router.get("/configs/{config_id}", response_model=schemas.RepositoryConfigResponse)
def get_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """获取单个仓库配置"""
    config = crud.get_repository_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config

@router.put("/configs/{config_id}", response_model=schemas.RepositoryConfigResponse)
def update_config(
    config_id: int,
    config: schemas.RepositoryConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新仓库配置"""
    db_config = crud.update_repository_config(db, config_id, config)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return db_config

@router.delete("/configs/{config_id}")
def delete_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """删除仓库配置"""
    success = crud.delete_repository_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"message": "配置已删除"}

@router.post("/sync/{config_id}", response_model=schemas.SyncResult)
def sync_repository(
    config_id: int,
    days: Optional[int] = 90,
    clear_existing: bool = False,
    db: Session = Depends(get_db)
):
    """手动同步指定仓库的提交数据"""
    config = crud.get_repository_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    if not config.is_active:
        raise HTTPException(status_code=400, detail="仓库配置未激活")

    try:
        since = datetime.utcnow() - timedelta(days=days) if days else None

        if config.repo_type == "local":
            service = LocalGitService(config.local_path)
            commits = service.get_commits(
                branch=config.branch,
                since=since,
                max_count=5000
            )
            repo_name = os.path.basename(config.local_path)
        elif config.repo_type in ["github", "gitlab"]:
            service = RemoteGitService(
                config.remote_url,
                config.access_token,
                config.repo_type
            )
            commits = service.get_commits(
                branch=config.branch,
                since=since,
                max_count=5000
            )
            repo_name = f"{service.repo_owner}/{service.repo_name}"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的仓库类型: {config.repo_type}")

        if clear_existing:
            crud.delete_all_commits(db)

        if commits:
            crud.create_commits_bulk(db, commits)

        crud.update_last_sync(db, config_id)

        return schemas.SyncResult(
            success=True,
            message=f"成功同步 {len(commits)} 条提交记录",
            imported_count=len(commits),
            repo_name=repo_name,
            branch=config.branch
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")

@router.post("/sync-all")
def sync_all_repositories(
    days: Optional[int] = 90,
    db: Session = Depends(get_db)
):
    """同步所有激活的仓库"""
    configs = crud.get_active_repository_configs(db)
    results = []

    for config in configs:
        try:
            since = datetime.utcnow() - timedelta(days=days) if days else None

            if config.repo_type == "local":
                service = LocalGitService(config.local_path)
                commits = service.get_commits(
                    branch=config.branch,
                    since=since,
                    max_count=5000
                )
                repo_name = os.path.basename(config.local_path)
            elif config.repo_type in ["github", "gitlab"]:
                service = RemoteGitService(
                    config.remote_url,
                    config.access_token,
                    config.repo_type
                )
                commits = service.get_commits(
                    branch=config.branch,
                    since=since,
                    max_count=5000
                )
                repo_name = f"{service.repo_owner}/{service.repo_name}"
            else:
                continue

            if commits:
                crud.create_commits_bulk(db, commits)

            crud.update_last_sync(db, config.id)

            results.append({
                "config_id": config.id,
                "repo_name": repo_name,
                "success": True,
                "imported_count": len(commits)
            })
        except Exception as e:
            results.append({
                "config_id": config.id,
                "repo_name": config.name,
                "success": False,
                "error": str(e)
            })

    return {"results": results}

@router.get("/branches")
def get_local_branches(
    path: str,
    db: Session = Depends(get_db)
):
    """获取本地仓库的所有分支"""
    try:
        service = LocalGitService(path)
        branches = service.get_branches()
        return {"branches": branches}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
