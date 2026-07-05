"""SQLAlchemy ORM 模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from app.database import Base
class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    commit_hash = Column(String(40), unique=True, index=True, nullable=False)
    author = Column(String(100), index=True, nullable=False)
    email = Column(String(200), nullable=True)
    date = Column(DateTime, index=True, nullable=False)
    message = Column(Text, nullable=True)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    review_comments_count = Column(Integer, default=0)
    is_automated = Column(Boolean, default=False)
    repository = Column(String(200), nullable=True)
    branch = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=True)
    team = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

class RepositoryConfig(Base):
    __tablename__ = "repository_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    repo_type = Column(String(50), nullable=False, default="local")  # local, github, gitlab
    local_path = Column(String(500), nullable=True)
    remote_url = Column(String(500), nullable=True)
    access_token = Column(String(500), nullable=True)
    branch = Column(String(200), nullable=True, default="main")
    is_active = Column(Boolean, default=True)
    auto_sync = Column(Boolean, default=False)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
