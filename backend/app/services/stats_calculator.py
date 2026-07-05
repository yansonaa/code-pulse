"""统计计算服务"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app import models, schemas, crud

class StatsCalculator:
    def __init__(self, db: Session):
        self.db = db

    def get_kpi(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, search: Optional[str] = None) -> schemas.KPIResponse:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date, search=search)

        total_commits = len(commits)
        active_developers = len(set(c.author for c in commits))
        net_lines = sum(c.additions - c.deletions for c in commits)

        # 模拟平均评审响应时长（基于 review_comments_count 和提交时间估算）
        avg_review = 4.5  # 小时，简化处理
        if commits:
            total_reviews = sum(c.review_comments_count for c in commits)
            if total_reviews > 0:
                avg_review = max(1.0, 8.0 - (total_reviews / len(commits)) * 2)

        period_days = (end_date - start_date).days or 1

        return schemas.KPIResponse(
            total_commits=total_commits,
            net_lines=net_lines,
            active_developers=active_developers,
            avg_review_response_hours=round(avg_review, 2),
            period_days=period_days
        )

    def get_trend(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, interval: str = "day", search: Optional[str] = None) -> schemas.TrendResponse:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date, search=search)

        # 按日期分组
        daily_stats = defaultdict(lambda: {"count": 0, "additions": 0, "deletions": 0})
        for c in commits:
            date_key = c.date.strftime("%Y-%m-%d")
            daily_stats[date_key]["count"] += 1
            daily_stats[date_key]["additions"] += c.additions
            daily_stats[date_key]["deletions"] += c.deletions

        # 填充缺失日期
        all_dates = []
        current = start_date
        while current <= end_date:
            all_dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        data = []
        for date_str in all_dates:
            stats = daily_stats.get(date_str, {"count": 0, "additions": 0, "deletions": 0})
            data.append(schemas.TrendPoint(
                date=date_str,
                count=stats["count"],
                additions=stats["additions"],
                deletions=stats["deletions"]
            ))

        # 检测下降趋势（最近7天 vs 前7天）
        has_decline, decline_dates = self._detect_decline(data)

        return schemas.TrendResponse(
            data=data,
            has_decline=has_decline,
            decline_dates=decline_dates
        )

    def _detect_decline(self, data: List[schemas.TrendPoint]) -> (bool, List[str]):
        if len(data) < 14:
            return False, []

        recent_7 = sum(d.count for d in data[-7:]) / 7
        prev_7 = sum(d.count for d in data[-14:-7]) / 7

        has_decline = recent_7 < prev_7 * 0.5
        decline_dates = [d.date for d in data[-7:] if d.count < recent_7 * 0.5] if has_decline else []
        return has_decline, decline_dates

    def get_code_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, search: Optional[str] = None) -> List[schemas.CodeStats]:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date, search=search)

        author_stats = defaultdict(lambda: {"additions": 0, "deletions": 0, "commits": 0})
        for c in commits:
            author_stats[c.author]["additions"] += c.additions
            author_stats[c.author]["deletions"] += c.deletions
            author_stats[c.author]["commits"] += 1

        return [
            schemas.CodeStats(
                author=author,
                additions=stats["additions"],
                deletions=stats["deletions"],
                net=stats["additions"] - stats["deletions"],
                commits=stats["commits"]
            )
            for author, stats in author_stats.items()
        ]

    def get_heatmap(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, search: Optional[str] = None) -> schemas.HeatmapResponse:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date, search=search)

        # 按星期和小时统计 (Python weekday: 0=Mon, 6=Sun; 我们转换为 0=Mon)
        heatmap_data = [[0 for _ in range(24)] for _ in range(7)]

        for c in commits:
            day = c.date.weekday()  # 0-6
            hour = c.date.hour
            heatmap_data[day][hour] += 1

        max_count = max(max(row) for row in heatmap_data) if heatmap_data else 1

        # 转换为扁平化数据
        flat_data = []
        for day in range(7):
            for hour in range(24):
                flat_data.append(schemas.HeatmapPoint(
                    day=day,
                    hour=hour,
                    count=heatmap_data[day][hour]
                ))

        # 检测异常：深夜高频提交
        anomalies = []
        for day in range(7):
            for hour in range(0, 6):
                count = heatmap_data[day][hour]
                if count > max_count * 0.3 and count > 5:
                    anomalies.append({
                        "day": day,
                        "hour": hour,
                        "count": count,
                        "type": "late_night_batch",
                        "description": f"{'周一 周二 周三 周四 周五 周六 周日'.split()[day]}{hour}:00-{hour+1}:00 有 {count} 次提交，疑似自动化脚本"
                    })

        return schemas.HeatmapResponse(
            data=flat_data,
            max_count=max_count,
            anomalies=anomalies
        )

    def get_radar(self, author: Optional[str] = None) -> List[schemas.MemberRadar]:
        commits = crud.get_commits(self.db)

        if author:
            authors = [author]
        else:
            authors = list(set(c.author for c in commits))

        result = []
        for a in authors:
            author_commits = [c for c in commits if c.author == a]
            if not author_commits:
                continue

            total_commits = len(author_commits)
            total_reviews = sum(c.review_comments_count for c in author_commits)
            total_additions = sum(c.additions for c in author_commits)
            total_deletions = sum(c.deletions for c in author_commits)

            # 计算各维度得分 (0-100)
            # 评论数量：评论越多分数越高
            comment_score = min(100, total_reviews / max(total_commits, 1) * 20)

            # 参与率：有提交的天数 / 总天数（简化）
            unique_days = len(set(c.date.strftime("%Y-%m-%d") for c in author_commits))
            participation_score = min(100, unique_days / 30 * 100)

            # 响应速度：基于 review_comments_count 反推（简化）
            response_score = min(100, max(0, 100 - (total_reviews / max(total_commits, 1) * 10)))

            # 代码贡献度：净增行数
            net_lines = total_additions - total_deletions
            contribution_score = min(100, max(0, net_lines / 100))

            # 提交频率
            freq_score = min(100, total_commits / 30 * 100)

            result.append(schemas.MemberRadar(
                author=a,
                dimensions=[
                    schemas.RadarDimension(dimension="评论数量", value=round(comment_score, 2)),
                    schemas.RadarDimension(dimension="参与率", value=round(participation_score, 2)),
                    schemas.RadarDimension(dimension="响应速度", value=round(response_score, 2)),
                    schemas.RadarDimension(dimension="代码贡献", value=round(contribution_score, 2)),
                    schemas.RadarDimension(dimension="提交频率", value=round(freq_score, 2))
                ]
            ))

        return result

    def get_anomalies(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, search: Optional[str] = None) -> List[schemas.AnomalyReport]:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        commits = crud.get_commits(self.db, start_date=start_date, end_date=end_date, search=search)

        anomalies = []
        author_commits = defaultdict(list)
        for c in commits:
            author_commits[c.author].append(c)

        for author, a_commits in author_commits.items():
            # 检测深夜高频提交
            late_night = [c for c in a_commits if c.date.hour < 6 or c.date.hour > 23]
            if len(late_night) > 10:
                automated_count = sum(1 for c in late_night if c.is_automated)
                anomalies.append(schemas.AnomalyReport(
                    author=author,
                    anomaly_type="深夜高频提交",
                    description=f"{author} 在非工作时间（0-6点、23-24点）提交了 {len(late_night)} 次，其中 {automated_count} 次被标记为自动化脚本",
                    severity="medium" if automated_count > len(late_night) * 0.5 else "high",
                    details={"late_night_count": len(late_night), "automated_count": automated_count}
                ))

            # 检测零评审提交
            zero_review = [c for c in a_commits if c.review_comments_count == 0 and not c.is_automated]
            if len(zero_review) > 20:
                anomalies.append(schemas.AnomalyReport(
                    author=author,
                    anomaly_type="零评审提交",
                    description=f"{author} 有 {len(zero_review)} 次提交没有评审评论，可能缺乏代码审查",
                    severity="low",
                    details={"zero_review_count": len(zero_review)}
                ))

            # 检测大文件删除（虚假高产出）
            big_deletions = [c for c in a_commits if c.deletions > 1000 and c.additions < 100]
            if big_deletions:
                total_deleted = sum(c.deletions for c in big_deletions)
                anomalies.append(schemas.AnomalyReport(
                    author=author,
                    anomaly_type="大文件删除",
                    description=f"{author} 删除了 {len(big_deletions)} 个大文件，共计 {total_deleted} 行，可能产生虚假高产出统计",
                    severity="medium",
                    details={"big_deletion_count": len(big_deletions), "total_deleted": total_deleted}
                ))

        return anomalies
