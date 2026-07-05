"""远程Git仓库服务（GitHub/GitLab）"""
import os
from datetime import datetime
from typing import List, Optional, Dict
from app import schemas

class RemoteGitService:
    """通过API获取远程Git仓库的提交历史"""

    def __init__(self, repo_url: str, access_token: str, repo_type: str = "github"):
        self.repo_url = repo_url
        self.access_token = access_token
        self.repo_type = repo_type.lower()
        self.repo_owner = None
        self.repo_name = None
        self._parse_repo_url()

    def _parse_repo_url(self):
        """解析仓库URL获取owner和name"""
        # 支持格式: https://github.com/owner/repo.git 或 https://github.com/owner/repo
        url = self.repo_url.replace('.git', '').rstrip('/')
        parts = url.split('/')
        if len(parts) >= 2:
            self.repo_name = parts[-1]
            self.repo_owner = parts[-2]

    def get_github_commits(
        self,
        branch: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_count: Optional[int] = None
    ) -> List[schemas.CommitCreate]:
        """通过GitHub API获取提交"""
        try:
            from github import Github
        except ImportError:
            raise ImportError("PyGithub not installed. Run: pip install PyGithub")

        g = Github(self.access_token)
        repo = g.get_repo(f"{self.repo_owner}/{self.repo_name}")

        kwargs = {}
        if branch:
            kwargs['sha'] = branch
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until

        github_commits = repo.get_commits(**kwargs)

        commits = []
        count = 0
        for commit in github_commits:
            if max_count and count >= max_count:
                break
            try:
                # GitHub API获取文件统计需要额外请求
                stats = commit.raw_data.get('stats', {})
                additions = stats.get('additions', 0)
                deletions = stats.get('deletions', 0)
                files_changed = stats.get('total', 0)

                commit_data = commit.commit
                author = commit_data.author.name if commit_data.author else "Unknown"
                email = commit_data.author.email if commit_data.author else None
                date = commit_data.author.date if commit_data.author else datetime.utcnow()
                message = commit_data.message or ""

                is_automated = self._detect_automated(message, author)

                commits.append(schemas.CommitCreate(
                    commit_hash=commit.sha,
                    author=author,
                    email=email,
                    date=date,
                    message=message.strip(),
                    additions=additions,
                    deletions=deletions,
                    files_changed=files_changed,
                    review_comments_count=0,
                    is_automated=is_automated,
                    repository=f"{self.repo_owner}/{self.repo_name}",
                    branch=branch or "default"
                ))
                count += 1
            except Exception:
                continue

        return commits

    def get_gitlab_commits(
        self,
        branch: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_count: Optional[int] = None
    ) -> List[schemas.CommitCreate]:
        """通过GitLab API获取提交"""
        import requests

        # 解析GitLab URL获取项目ID或路径
        url = self.repo_url.replace('.git', '').rstrip('/')
        # GitLab API基础URL
        base_url = url.split('/' + self.repo_owner + '/')[0] if self.repo_owner else url
        project_path = f"{self.repo_owner}/{self.repo_name}"
        encoded_path = project_path.replace('/', '%2F')

        api_url = f"{base_url}/api/v4/projects/{encoded_path}/repository/commits"
        headers = {"Private-Token": self.access_token}
        params = {}
        if branch:
            params['ref_name'] = branch
        if since:
            params['since'] = since.isoformat()
        if until:
            params['until'] = until.isoformat()
        if max_count:
            params['per_page'] = min(max_count, 100)

        commits = []
        page = 1
        while True:
            params['page'] = page
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code != 200:
                break
            data = response.json()
            if not data:
                break

            for commit in data:
                try:
                    # 获取详细统计
                    stats_url = f"{api_url}/{commit['id']}"
                    stats_response = requests.get(stats_url, headers=headers)
                    stats = stats_response.json().get('stats', {}) if stats_response.status_code == 200 else {}

                    author = commit.get('author_name', 'Unknown')
                    message = commit.get('message', '')
                    is_automated = self._detect_automated(message, author)

                    commits.append(schemas.CommitCreate(
                        commit_hash=commit['id'],
                        author=author,
                        email=commit.get('author_email'),
                        date=datetime.fromisoformat(commit['committed_date'].replace('Z', '+00:00')),
                        message=message.strip(),
                        additions=stats.get('additions', 0),
                        deletions=stats.get('deletions', 0),
                        files_changed=stats.get('total', 0),
                        review_comments_count=0,
                        is_automated=is_automated,
                        repository=project_path,
                        branch=branch or commit.get('ref_name', 'default')
                    ))
                except Exception:
                    continue

            if max_count and len(commits) >= max_count:
                commits = commits[:max_count]
                break
            page += 1

        return commits

    def get_commits(
        self,
        branch: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        max_count: Optional[int] = None
    ) -> List[schemas.CommitCreate]:
        """根据仓库类型获取提交"""
        if self.repo_type == "github":
            return self.get_github_commits(branch, since, until, max_count)
        elif self.repo_type == "gitlab":
            return self.get_gitlab_commits(branch, since, until, max_count)
        else:
            raise ValueError(f"不支持的仓库类型: {self.repo_type}")

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
        """获取远程仓库基本信息"""
        if self.repo_type == "github":
            try:
                from github import Github
                g = Github(self.access_token)
                repo = g.get_repo(f"{self.repo_owner}/{self.repo_name}")
                return {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "default_branch": repo.default_branch,
                    "total_commits": repo.get_commits().totalCount,
                    "type": "github"
                }
            except Exception as e:
                return {"name": self.repo_name, "error": str(e), "type": "github"}
        return {"name": self.repo_name, "type": self.repo_type}
