"""
CodePulse - 研发活跃度智能分析平台
FastAPI 后端主入口
"""
import os
from fastapi import FastAPI, UploadFile, File, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io
import csv
from datetime import datetime, timedelta

from app.database import engine, Base, get_db
from app import models, schemas, crud
from app.services.git_parser import GitLogParser
from app.services.mock_generator import MockDataGenerator
from app.services.stats_calculator import StatsCalculator
from app.services.export_service import ExportService
from app.api import commits, stats, export_data, mock, sync, sync

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodePulse API",
    description="研发活跃度智能分析平台 - 后端 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(commits.router, prefix="/api/commits", tags=["commits"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(export_data.router, prefix="/api/export", tags=["export"])
app.include_router(mock.router, prefix="/api/mock", tags=["mock"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])

@app.get("/")
def read_root():
    return {"message": "CodePulse API 运行中", "version": "1.0.0"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
