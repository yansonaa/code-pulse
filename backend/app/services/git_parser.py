"""Git 日志解析服务"""
import re
from datetime import datetime
from typing import List, Optional
from app import schemas

class GitLogParser:
    # Git log 格式示例：
    # hash|author|email|date|message|additions|deletions|files_changed
    # 或标准 git log --pretty=format 输出

    COMMIT_PATTERN = re.compile(
        r'commit\s+([a-f0-9]{40})\n'
        r'Author:\s+(.+?)\s*<(.+?)>\n'
        r'Date:\s+(.+?)\n'
        r'\n'
        r'\s*(.+?)(?=\ncommit|\Z)',
        re.DOTALL
    )

    STAT_PATTERN = re.compile(r'(\d+)\s+insertions\(\+\)')
    STAT_DEL_PATTERN = re.compile(r'(\d+)\s+deletions\(-\)')
    FILE_PATTERN = re.compile(r'\d+\s+files?\s+changed')

    def parse_git_log(self, log_text: str) -> List[schemas.CommitCreate]:
        commits = []
        # 尝试解析标准 git log 格式
        raw_commits = re.split(r'\ncommit\s+', log_text.strip())

        for raw in raw_commits:
            if not raw.strip():
                continue
            commit = self._parse_single_commit(raw)
            if commit:
                commits.append(commit)

        # 如果标准格式解析为空，尝试自定义格式（hash | author | date | message）
        if not commits:
            commits = self._parse_custom_git_log(log_text)

        return commits

    def _parse_single_commit(self, raw_text: str) -> Optional[schemas.CommitCreate]:
        # 提取 hash
        hash_match = re.match(r'([a-f0-9]{40})', raw_text)
        if not hash_match:
            return None
        commit_hash = hash_match.group(1)

        # 提取 Author
        author_match = re.search(r'Author:\s+(.+?)\s*<(.+?)>', raw_text)
        author = author_match.group(1).strip() if author_match else "Unknown"
        email = author_match.group(2).strip() if author_match else None

        # 提取 Date
        date_match = re.search(r'Date:\s+(.+)', raw_text)
        date_str = date_match.group(1).strip() if date_match else None
        date = self._parse_date(date_str) if date_str else datetime.now()

        # 提取 Message
        message_match = re.search(r'\n\n\s*(.+?)(?=\n\d+\s+files?|\Z)', raw_text, re.DOTALL)
        message = message_match.group(1).strip() if message_match else ""

        # 提取统计信息
        additions = self._extract_additions(raw_text)
        deletions = self._extract_deletions(raw_text)
        files_changed = self._extract_files_changed(raw_text)

        # 判断是否为自动化提交
        is_automated = self._detect_automated(message, author)

        return schemas.CommitCreate(
            commit_hash=commit_hash,
            author=author,
            email=email,
            date=date,
            message=message,
            additions=additions,
            deletions=deletions,
            files_changed=files_changed,
            review_comments_count=0,
            is_automated=is_automated
        )

    def _parse_date(self, date_str: str) -> datetime:
        formats = [
            "%a %b %d %H:%M:%S %Y %z",
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%a %b %d %H:%M:%S %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    def _extract_additions(self, text: str) -> int:
        match = self.STAT_PATTERN.search(text)
        return int(match.group(1)) if match else 0

    def _extract_deletions(self, text: str) -> int:
        match = self.STAT_DEL_PATTERN.search(text)
        return int(match.group(1)) if match else 0

    def _extract_files_changed(self, text: str) -> int:
        match = self.FILE_PATTERN.search(text)
        if match:
            num_match = re.search(r'(\d+)', match.group(0))
            return int(num_match.group(1)) if num_match else 0
        return 0

    def _detect_automated(self, message: str, author: str) -> bool:
        automated_keywords = [
            'automated', 'auto', 'bot', 'ci/cd', 'jenkins', 'github action',
            'dependabot', 'renovate', 'semantic-release', 'release-please'
        ]
        lower_msg = message.lower()
        lower_author = author.lower()
        return any(kw in lower_msg or kw in lower_author for kw in automated_keywords)

    def _parse_custom_git_log(self, log_text: str) -> List[schemas.CommitCreate]:
        """解析自定义格式：hash | author | date | message"""
        commits = []
        # 按空行分割成块（支持多个空行）
        blocks = [b.strip() for b in re.split(r'\n\s*\n', log_text.strip()) if b.strip()]

        for block in blocks:
            lines = block.splitlines()
            if not lines:
                continue

            # 第一行是头部：hash | author | date | message
            header_parts = [p.strip() for p in lines[0].split('|')]
            if len(header_parts) < 4:
                continue

            commit_hash = header_parts[0]
            author = header_parts[1]
            date_str = header_parts[2]
            message = '|'.join(header_parts[3:])
            date = self._parse_date(date_str) if date_str else datetime.now()

            # 查找统计行（最后几行）
            additions = 0
            deletions = 0
            files_changed = 0
            for line in lines[1:]:
                if 'file changed' in line or 'files changed' in line:
                    f_match = re.search(r'(\d+)\s+file', line)
                    a_match = re.search(r'(\d+)\s+insertions', line)
                    d_match = re.search(r'(\d+)\s+deletions', line)
                    if f_match:
                        files_changed = int(f_match.group(1))
                    if a_match:
                        additions = int(a_match.group(1))
                    if d_match:
                        deletions = int(d_match.group(1))
                    break

            is_automated = self._detect_automated(message, author)
            commits.append(schemas.CommitCreate(
                commit_hash=commit_hash,
                author=author,
                email=None,
                date=date,
                message=message,
                additions=additions,
                deletions=deletions,
                files_changed=files_changed,
                review_comments_count=0,
                is_automated=is_automated
            ))

        return commits

    def parse_csv_data(self, csv_text: str) -> List[schemas.CommitCreate]:
        commits = []
        import csv
        import io
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            try:
                commit = schemas.CommitCreate(
                    commit_hash=row.get('commit_hash', row.get('hash', '')),
                    author=row.get('author', 'Unknown'),
                    email=row.get('email'),
                    date=datetime.fromisoformat(row.get('date', datetime.now().isoformat())),
                    message=row.get('message', ''),
                    additions=int(row.get('additions', 0) or 0),
                    deletions=int(row.get('deletions', 0) or 0),
                    files_changed=int(row.get('files_changed', 0) or 0),
                    review_comments_count=int(row.get('review_comments_count', 0) or 0),
                    is_automated=row.get('is_automated', 'false').lower() == 'true'
                )
                commits.append(commit)
            except Exception:
                continue
        return commits
