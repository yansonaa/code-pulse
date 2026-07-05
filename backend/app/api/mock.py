from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, crud
from app.services.mock_generator import MockDataGenerator

router = APIRouter()

@router.post("/generate")
def generate_mock_data(
    days: int = 90,
    total_commits: int = 2000,
    db: Session = Depends(get_db)
):
    """生成模拟数据并写入数据库"""
    generator = MockDataGenerator()
    commits = generator.generate(days=days, total_commits=total_commits)

    # 先清空旧数据
    crud.delete_all_commits(db)

    count = crud.create_commits_bulk(db, commits)
    return {
        "message": f"成功生成 {count} 条模拟提交记录",
        "count": count,
        "developers": generator.DEVELOPERS[:5]
    }

@router.get("/developers")
def get_mock_developers():
    """获取模拟开发者列表"""
    return MockDataGenerator.DEVELOPERS
