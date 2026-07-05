"""本地Git仓库服务"""
import os
from datetime import datetime
from typing import List, Optional, Dict
from git import Repo, Commit as GitCommit
from app import schemas

class LocalGitService:
    """使用GitPython读取本地Git仓库的提交历史"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = None
        self._validate_repo()

    def _validate_repo(self):
        """验证路径是否为有效的Git仓库"""
        if not os.path.exists(self.repo_path):
            raise ValueError(f"路径不存在: {self.repo_path}")
        git_dir = os.path.join(self.repo_path, '.git')
        if not os.path.exists(git_dir):
            raise ValueError(f"路径不是Git仓库: {self.repo_path}")
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            raise ValueError(f"无法打开Git仓库: {str(e)}")

    def get_branches(self) -> List[str]:
        """获取所有分支名称"""
        return [ref.name for ref in self.repo.branches]

    def get_commits(
        self,
        branch: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_count: Optional[int] = None
    ) -> List[schemas.CommitCreate]:
        """获取提交记录"""
        target = self.repo.branches[branch] if branch and branch in [b.name for b in self.repo.branches] else self.repo.head

        kwargs = {}
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until
        if max_count:
            kwargs['max_count'] = max_count

        commits = []
        iter_commits = self.repo.iter_commits(target, **kwargs)

        for commit in iter_commits:
            try:
                # 获取统计信息
                stats = commit.stats
                additions = stats.total.get('insertions', 0)
                deletions = stats.total.get('deletions', 0)
                files_changed = stats.total.get('files', 0)

                # 判断是否为自动化提交
                is_automated = self._detect_automated(commit.message, commit.author.name)

                commits.append(schemas.CommitCreate(
                    commit_hash=commit.hexsha,
                    author=commit.author.name or "Unknown",
                    email=commit.author.email,
                    date=commit.committed_datetime,
                    message=commit.message.strip(),
                    additions=additions,
                    deletions=deletions,
                    files_changed=files_changed,
                    review_comments_count=0,
                    is_automated=is_automated,
                    repository=os.path.basename(self.repo.working_dir),
                    branch=branch or self.repo.active_branch.name
                ))
            except Exception:
                continue

        return commits

    def _detect_automated(self, message: str, author: str) -> bool:
        """检测是否为自动化提交"""
        automated_keywords = [
            'automated', 'auto', 'bot', 'ci/cd', 'jenkins', 'github action',
            'dependabot', 'renovate', 'semantic-release', 'release-please',
            'merge branch', 'merge pull request'
        ]
        lower_msg = message.lower()
        lower_author = author.lower()
        return any(kw in lower_msg or kw in lower_author for kw in automated_keywords)

    def get_repo_info(self) -> Dict:
        """获取仓库基本信息"""
        return {
            "path": self.repo_path,
            "name": os.path.basename(self.repo.working_dir),
            "active_branch": self.repo.active_branch.name,
            "branches": self.get_branches(),
            "total_commits": self.repo.git.rev_list('--count', 'HEAD')
        }
