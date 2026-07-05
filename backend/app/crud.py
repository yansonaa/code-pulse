"""CRUD 操作"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
from app import models, schemas

def create_commit(db: Session, commit: schemas.CommitCreate) -> models.Commit:
    db_commit = models.Commit(**commit.dict())
    db.add(db_commit)
    db.commit()
    db.refresh(db_commit)
    return db_commit

def create_commits_bulk(db: Session, commits: List[schemas.CommitCreate]) -> int:
    # 清理传入 hash 中的 BOM 并去重
    all_existing = {r[0] for r in db.query(models.Commit.commit_hash).all()}
    new_commits = []
    for c in commits:
        h = c.commit_hash.lstrip('﻿')
        if h in all_existing:
            continue
        # 短 hash（如 7 位）检查是否已有以该前缀开头的完整 hash
        if len(h) < 40 and any(e.startswith(h) for e in all_existing):
            continue
        # 完整 hash 检查是否已有其短 hash 前缀存在于数据库
        if len(h) >= 40 and any(h.startswith(e) for e in all_existing if len(e) < 40):
            continue
        # 更新清理后的 hash
        c.commit_hash = h
        new_commits.append(c)
    if not new_commits:
        return 0
    db_commits = [models.Commit(**c.dict()) for c in new_commits]
    db.bulk_save_objects(db_commits)
    db.commit()
    return len(db_commits)

def get_commits(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    authors: Optional[List[str]] = None,
    repositories: Optional[List[str]] = None,
    search: Optional[str] = None
) -> List[models.Commit]:
    query = db.query(models.Commit)

    if start_date:
        query = query.filter(models.Commit.date >= start_date)
    if end_date:
        query = query.filter(models.Commit.date <= end_date)
    if authors:
        query = query.filter(models.Commit.author.in_(authors))
    if repositories:
        query = query.filter(models.Commit.repository.in_(repositories))
    if search:
        query = query.filter(
            or_(
                models.Commit.author.contains(search),
                models.Commit.message.contains(search)
            )
        )

    return query.order_by(models.Commit.date.desc()).offset(skip).limit(limit).all()

def get_commit_count(db: Session, **filters) -> int:
    return db.query(func.count(models.Commit.id)).filter_by(**filters).scalar() or 0

def delete_all_commits(db: Session) -> int:
    count = db.query(func.count(models.Commit.id)).scalar() or 0
    db.query(models.Commit).delete()
    db.commit()
    return count

def get_authors(db: Session) -> List[str]:
    return [r[0] for r in db.query(models.Commit.author).distinct().all()]

def get_repositories(db: Session) -> List[str]:
    return [r[0] for r in db.query(models.Commit.repository).distinct().all() if r[0]]

def create_member(db: Session, member: schemas.MemberCreate) -> models.Member:
    db_member = models.Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_members(db: Session) -> List[models.Member]:
    return db.query(models.Member).all()

def create_team(db: Session, team: schemas.TeamCreate) -> models.Team:
    db_team = models.Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def create_repository_config(db: Session, config: schemas.RepositoryConfigCreate) -> models.RepositoryConfig:
    db_config = models.RepositoryConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def get_repository_config(db: Session, config_id: int) -> Optional[models.RepositoryConfig]:
    return db.query(models.RepositoryConfig).filter(models.RepositoryConfig.id == config_id).first()

def get_repository_configs(db: Session, skip: int = 0, limit: int = 100) -> List[models.RepositoryConfig]:
    return db.query(models.RepositoryConfig).offset(skip).limit(limit).all()

def get_active_repository_configs(db: Session) -> List[models.RepositoryConfig]:
    return db.query(models.RepositoryConfig).filter(models.RepositoryConfig.is_active == True).all()

def update_repository_config(db: Session, config_id: int, config: schemas.RepositoryConfigUpdate) -> Optional[models.RepositoryConfig]:
    db_config = db.query(models.RepositoryConfig).filter(models.RepositoryConfig.id == config_id).first()
    if not db_config:
        return None
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_repository_config(db: Session, config_id: int) -> bool:
    db_config = db.query(models.RepositoryConfig).filter(models.RepositoryConfig.id == config_id).first()
    if not db_config:
        return False
    db.delete(db_config)
    db.commit()
    return True

def update_last_sync(db: Session, config_id: int) -> Optional[models.RepositoryConfig]:
    db_config = db.query(models.RepositoryConfig).filter(models.RepositoryConfig.id == config_id).first()
    if db_config:
        db_config.last_sync_at = datetime.utcnow()
        db.commit()
        db.refresh(db_config)
    return db_config

    return db.query(models.Team).all()
