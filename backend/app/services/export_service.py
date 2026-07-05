"""导出服务"""
import csv
import io
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app import crud, schemas
from app.services.stats_calculator import StatsCalculator

class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.calculator = StatsCalculator(db)

    def export_csv(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> io.StringIO:
        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "commit_hash", "author", "email", "date", "message",
            "additions", "deletions", "files_changed", "review_comments_count",
            "is_automated", "repository", "branch"
        ])

        for c in commits:
            writer.writerow([
                c.commit_hash, c.author, c.email or "",
                c.date.strftime("%Y-%m-%d %H:%M:%S"), c.message or "",
                c.additions, c.deletions, c.files_changed,
                c.review_comments_count, c.is_automated,
                c.repository or "", c.branch or ""
            ])

        output.seek(0)
        return output

    def export_member_csv(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> io.StringIO:
        code_stats = self.calculator.get_code_stats(start_date, end_date)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["author", "commits", "additions", "deletions", "net_lines", "avg_per_commit"])

        for stat in code_stats:
            avg = round((stat.additions + stat.deletions) / max(stat.commits, 1), 2)
            writer.writerow([
                stat.author, stat.commits, stat.additions,
                stat.deletions, stat.net, avg
            ])

        output.seek(0)
        return output
