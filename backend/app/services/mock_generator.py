"""模拟数据生成器"""
import random
import string
from datetime import datetime, timedelta
from typing import List
from app import schemas

class MockDataGenerator:
    DEVELOPERS = [
        "张伟", "李娜", "王强", "刘洋", "陈静",
        "杨明", "赵磊", "黄丽", "周杰", "吴敏",
        "徐涛", "孙艳", "朱辉", "马丽", "胡军",
        "郭芳", "林峰", "何平", "高婷", "罗刚",
        "郑浩", "梁雪", "宋鹏", "唐薇", "许文"
    ]

    MESSAGES = [
        "fix: 修复登录页面的验证码问题",
        "feat: 新增用户权限管理模块",
        "refactor: 优化数据库查询性能",
        "docs: 更新 API 接口文档",
        "test: 添加订单模块的单元测试",
        "chore: 升级依赖包版本",
        "style: 统一代码格式",
        "perf: 减少首页加载时间",
        "build: 配置 CI/CD 流水线",
        "ci: 修复自动化测试脚本",
        "merge: 合并 feature/order 分支",
        "hotfix: 紧急修复支付回调异常",
        "feat: 实现数据导出功能",
        "fix: 处理并发情况下的库存扣减",
        "refactor: 抽取公共组件",
        "docs: 补充部署说明",
        "test: 集成测试覆盖率提升至 85%",
        "feat: 新增消息推送服务",
        "fix: 修复缓存穿透问题",
        "perf: 引入 Redis 缓存策略",
    ]

    REPOSITORIES = [
        "codepulse-backend", "codepulse-frontend", "codepulse-mobile",
        "shared-components", "auth-service", "payment-gateway",
        "notification-service", "data-analytics"
    ]

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate(self, days: int = 90, total_commits: int = 2000) -> List[schemas.CommitCreate]:
        commits = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 生成提交频率分布（工作日更多，周末更少）
        commit_times = self._generate_commit_times(start_date, end_date, total_commits)

        for commit_time in commit_times:
            author = random.choice(self.DEVELOPERS)
            is_weekend = commit_time.weekday() >= 5
            hour = commit_time.hour

            # 深夜提交有概率是自动化脚本
            is_automated = (hour < 6 or hour > 23) and random.random() < 0.7

            # 代码量统计
            if is_automated:
                additions = random.randint(1, 50)
                deletions = random.randint(1, 30)
                files_changed = random.randint(1, 5)
            else:
                additions = random.randint(5, 500)
                deletions = random.randint(0, 300)
                files_changed = random.randint(1, 20)

            # 随机某些 commit 有大量删除（模拟大文件删除）
            if random.random() < 0.05:
                deletions = random.randint(1000, 5000)
                additions = random.randint(0, 50)

            message = random.choice(self.MESSAGES)
            if random.random() < 0.3:
                message += f" #{random.randint(100, 999)}"

            commit_hash = ''.join(random.choices(string.hexdigits.lower(), k=40))

            commit = schemas.CommitCreate(
                commit_hash=commit_hash,
                author=author,
                email=f"{author.lower()}@example.com",
                date=commit_time,
                message=message,
                additions=additions,
                deletions=deletions,
                files_changed=files_changed,
                review_comments_count=random.randint(0, 15) if not is_automated else 0,
                is_automated=is_automated,
                repository=random.choice(self.REPOSITORIES),
                branch=random.choice(["main", "develop", "feature/new-module"])
            )
            commits.append(commit)

        return sorted(commits, key=lambda x: x.date)

    def _generate_commit_times(self, start: datetime, end: datetime, total: int) -> List[datetime]:
        times = []
        current = start
        while len(times) < total:
            # 工作日权重更高
            if current.weekday() < 5:
                daily_commits = random.randint(15, 40)
            else:
                daily_commits = random.randint(0, 10)

            for _ in range(daily_commits):
                if len(times) >= total:
                    break
                # 工作时间分布：9-18 点为主，但也有夜间提交
                hour_weights = [
                    (0, 6, 0.05),    # 凌晨
                    (6, 9, 0.1),     # 早晨
                    (9, 12, 0.25),   # 上午
                    (12, 14, 0.1),   # 午休
                    (14, 18, 0.3),   # 下午
                    (18, 22, 0.15),  # 晚上
                    (22, 24, 0.05)   # 深夜
                ]
                hour = self._weighted_hour_choice(hour_weights)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                commit_time = current.replace(hour=hour, minute=minute, second=second)
                times.append(commit_time)

            current += timedelta(days=1)
            if current > end:
                current = start

        return times[:total]

    def _weighted_hour_choice(self, hour_weights):
        r = random.random()
        cumulative = 0
        for start, end, weight in hour_weights:
            cumulative += weight
            if r <= cumulative:
                return random.randint(start, end - 1)
        return random.randint(9, 18)
