# CodePulse 技术方案文档 (Technical Design Document)

> 版本：v1.0  
> 日期：2026-07-05  
> 项目：CodePulse - 研发活跃度智能分析平台

---

## 1. 系统架构设计

### 1.1 总体架构

CodePulse 采用经典的前后端分离（B/S）架构，由三层组成：

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端层 (Client)                        │
│  ┌─────────────┐                                            │
│  │   Browser   │  React 18 + Vite + TailwindCSS + ECharts   │
│  │  (Chrome/   │  ───────→ 单页应用 (SPA)                   │
│  │   Edge/Fire-│            无路由，所有组件内联于 App.tsx    │
│  │   fox/Safari)                                            │
│  └─────────────┘                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/1.1 (JSON)
                           │ RESTful API
                           │ CORS 跨域
┌──────────────────────────┴──────────────────────────────────┐
│                     应用服务层 (Server)                     │
│  ┌────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python 3.7+)                              │   │
│  │  ├─ API 路由层 (app/api/)                          │   │
│  │  ├─ 业务逻辑层 (app/services/)                       │   │
│  │  ├─ 数据访问层 (app/crud.py)                        │   │
│  │  ├─ ORM 模型层 (app/models.py)                      │   │
│  │  └─ Pydantic 校验层 (app/schemas.py)                 │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ SQLAlchemy ORM
                           │ SQLite 文件级数据库
┌──────────────────────────┴──────────────────────────────────┐
│                     数据存储层 (Storage)                      │
│  ┌────────────────────────────┐  ┌────────────────────────┐ │
│  │   SQLite (codepulse.db)    │  │   Git Repositories     │ │
│  │  ──────── 主数据存储         │  │  ─────── 只读数据源     │ │
│  │  commits / members /        │  │  本地 .git 目录          │ │
│  │  repository_configs / teams │  │  GitHub/GitLab API      │ │
│  └────────────────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 部署架构

**生产环境部署模式：**

```
[Internet]
    │
    ▼
[Nginx Reverse Proxy]
    │  ├── 静态文件请求 → /frontend/dist/* (index.html)
    │  └── API 请求     → /api/* → Gunicorn + Uvicorn Workers
    │
    ▼
[Gunicorn (4 Workers)]
    │  uvicorn.workers.UvicornWorker
    │  bind 0.0.0.0:8000
    ▼
[FastAPI Application]
    │  ├─ CORS Middleware
    │  ├─ Exception Handlers
    │  └─ API Routers
    ▼
[SQLite Database]
    backend/app/data/codepulse.db
```

**开发环境部署模式：**

```
Terminal 1:  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Terminal 2:  cd frontend && npm run dev  (Vite proxy /api → localhost:8000)
```

### 1.3 数据流架构

```
[数据源] ──→ [解析/采集] ──→ [数据校验] ──→ [去重入库] ──→ [SQLite]
   │            │              │              │
   │            │              │              │
   │            ▼              ▼              ▼
   │       GitLogParser    Pydantic      create_commits_
   │       LocalGitService schemas       bulk (前缀去重)
   │       RemoteGitService              │
   │                                     │
   │                                     ▼
   │                                [StatsCalculator]
   │                                     │
   │                    ┌────────────────┼────────────────┐
   │                    ▼                ▼                ▼
   │               [KPI计算]      [趋势分析]        [异常检测]
   │                    │                │                │
   │                    ▼                ▼                ▼
   │              /api/stats/kpi   /api/stats/trend  /api/stats/anomalies
   │                    │                │                │
   └────────────────────┴────────────────┴────────────────┘
                        │
                        ▼
                   [React Frontend]
                   并行 6 个 GET 请求
                   ECharts 渲染
```

---

## 2. 技术选型

### 2.1 技术栈总览

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| **后端框架** | FastAPI | 0.95.2 | 异步高性能、自动 Swagger 文档、Python 3.7 兼容、依赖注入机制 |
| **ORM** | SQLAlchemy | 1.4.54 | 成熟稳定、Python 3.7 兼容、声明式模型、支持 SQLite |
| **数据校验** | Pydantic v1 | 1.10.13 | FastAPI 原生集成、Python 3.7 兼容、类型安全 |
| **数据库** | SQLite | 3.x | 零配置、单文件存储、足够支撑单机分析场景（万级数据） |
| **WSGI/ASGI** | Uvicorn + Gunicorn | 0.22.0 | 生产环境多 Worker 部署、热重载开发体验 |
| **Git 解析** | GitPython | 3.1.43 | 直接读取本地 .git 目录、完整 commit 信息提取 |
| **GitHub API** | PyGithub | 1.59.1 | 官方 SDK 封装、Token 认证、分页处理 |
| **GitLab API** | requests | 2.31.0 | 轻量 HTTP 客户端、直接调用 REST API |
| **前端框架** | React | 18.2.0 | 组件化、Hooks、TypeScript 支持好、生态丰富 |
| **构建工具** | Vite | 5.0.0 | 极速冷启动、HMR、代理配置简单、生产优化 |
| **样式框架** | TailwindCSS | 3.4.0 | 原子化 CSS、开发效率高、暗色主题支持 |
| **图表库** | ECharts | 5.4.3 | 功能全面（折线/柱状/热力/雷达）、支持响应式 |
| **HTTP 客户端** | Axios | 1.6.0 | 拦截器、自动 JSON 解析、错误处理友好 |
| **图标库** | Lucide React | 0.300.0 | 轻量、SVG、React 封装友好 |
| **语言** | TypeScript | 5.3.0 | 类型安全、IDE 提示友好、减少运行时错误 |

### 2.2 关键技术决策说明

#### 决策 1：为什么用 SQLite 而非 PostgreSQL/MySQL？

**理由：**
- 单机部署、零运维成本，无需额外安装数据库服务
- 万级 commit 数据量完全在 SQLite 性能范围内
- 单文件存储（`codepulse.db`），便于备份和迁移
- 分析型查询（聚合、分组）在 SQLite 中执行效率足够

**未来可扩展方向：** 当数据量增长至 10 万+ 时，可无缝迁移至 PostgreSQL，SQLAlchemy 抽象层屏蔽了底层差异。

#### 决策 2：为什么用单文件 SPA 而非 Next.js？

**理由：**
- 项目只有 1 个页面（仪表盘），无路由需求
- 所有组件内联于 `App.tsx`，减少文件切换成本
- Vite 构建产物为纯静态文件，Nginx 直接托管即可
- 无需 SSR，所有数据通过客户端 AJAX 获取

#### 决策 3：为什么用 Pydantic v1 而非 v2？

**理由：**
- 生产环境限制为 Python 3.7，Pydantic v2 不支持 Python 3.7
- FastAPI 0.95.2 与 Pydantic v1 完全兼容
- 使用 `orm_mode = True`（而非 v2 的 `from_attributes = True`）

#### 决策 4：为什么 stats 接口不缓存？

**理由：**
- 数据量小（万级），实时查询耗时 < 100ms
- 筛选条件组合多（日期 + 搜索词），缓存命中率低
- 简单查询比缓存管理（失效策略、预热）成本更低

**未来优化方向：** 当数据量达到 10 万+ 时，可引入 Redis 缓存热点查询结果（如默认 30 天范围）。

---

## 3. 数据库设计说明

### 3.1 实体关系图 (ER Diagram)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────────┐
│     commits     │       │    members      │       │  repository_configs │
├─────────────────┤       ├─────────────────┤       ├─────────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)             │
│ commit_hash (UQ)│       │ name            │       │ name                │
│ author          │◄──────┤ email (UQ)      │       │ repo_type           │
│ email           │       │ team            │       │ local_path          │
│ date            │       │ role            │       │ remote_url          │
│ message         │       │ avatar          │       │ access_token        │
│ additions       │       │ is_active       │       │ branch              │
│ deletions       │       └─────────────────┘       │ is_active           │
│ files_changed   │                                 │ auto_sync           │
│ review_comments │                                 │ last_sync_at        │
│ is_automated    │                                 │ created_at          │
│ repository      │                                 │ updated_at          │
│ branch          │                                 └─────────────────────┘
│ created_at      │
└─────────────────┘
         │
         │ (逻辑关联，无物理外键)
         ▼
┌─────────────────┐
│      teams      │
├─────────────────┤
│ id (PK)         │
│ name (UQ)       │
│ description     │
│ created_at      │
└─────────────────┘
```

### 3.2 表结构设计

#### 表 1：commits（核心事实表）

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | 自增主键 |
| `commit_hash` | VARCHAR(40) | UNIQUE, NOT NULL | - | Git commit SHA，唯一标识 |
| `author` | VARCHAR(100) | NOT NULL, INDEX | - | 提交作者名，用于统计分组 |
| `email` | VARCHAR(200) | NULL | - | 作者邮箱 |
| `date` | DATETIME | NOT NULL, INDEX | - | 提交时间，时区信息由前端 ISO 字符串处理 |
| `message` | TEXT | NULL | - | 提交消息，支持长文本 |
| `additions` | INTEGER | NOT NULL | 0 | 新增代码行数 |
| `deletions` | INTEGER | NOT NULL | 0 | 删除代码行数 |
| `files_changed` | INTEGER | NOT NULL | 0 | 变更文件数 |
| `review_comments_count` | INTEGER | NOT NULL | 0 | 评审评论数（GitHub/GitLab API 提供） |
| `is_automated` | BOOLEAN | NOT NULL | FALSE | 是否自动化提交（关键字匹配） |
| `repository` | VARCHAR(200) | NULL | - | 所属仓库名称或 URL |
| `branch` | VARCHAR(200) | NULL | - | 所属分支名称 |
| `created_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 记录入库时间 |

**索引设计：**
- 唯一索引：`commit_hash` — 防止重复导入
- 普通索引：`author` — 加速按作者统计查询
- 普通索引：`date` — 加速按日期范围过滤
- 联合索引：`(date, author)` — 覆盖最常用的统计查询

**为什么 commit_hash 是 VARCHAR(40)：**
- Git SHA-1 完整长度为 40 位十六进制字符串
- 短 hash（7 位）通过解析器处理后入库，但主键始终要求完整 hash
- 当前实现允许短 hash 入库（`length < 40`），但去重逻辑在 `crud.py` 中处理前缀匹配

#### 表 2：members（成员目录表）

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| `id` | INTEGER | PRIMARY KEY | - | 自增主键 |
| `name` | VARCHAR(100) | NOT NULL | - | 成员姓名（与 `commits.author` 逻辑关联） |
| `email` | VARCHAR(200) | UNIQUE, NULL | - | 邮箱 |
| `team` | VARCHAR(100) | NULL | - | 所属团队（预留） |
| `role` | VARCHAR(50) | NULL | - | 角色（预留） |
| `avatar` | VARCHAR(500) | NULL | - | 头像 URL（预留） |
| `is_active` | BOOLEAN | NOT NULL | TRUE | 是否在职 |

**说明：** 当前版本 `members` 表与 `commits` 表无物理外键关联，通过 `author` 名字段进行逻辑关联。未来可扩展为 `member_id` 外键。

#### 表 3：repository_configs（仓库配置表）

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| `id` | INTEGER | PRIMARY KEY | - | 自增主键 |
| `name` | VARCHAR(200) | NOT NULL | - | 配置名称（如"后端主仓库"） |
| `repo_type` | VARCHAR(50) | NOT NULL | "local" | 仓库类型：local / github / gitlab |
| `local_path` | VARCHAR(500) | NULL | - | 本地仓库绝对路径（repo_type=local） |
| `remote_url` | VARCHAR(500) | NULL | - | 远程仓库 URL（repo_type=github/gitlab） |
| `access_token` | VARCHAR(500) | NULL | - | 访问令牌（当前明文存储） |
| `branch` | VARCHAR(200) | NOT NULL | "main" | 默认分支 |
| `is_active` | BOOLEAN | NOT NULL | TRUE | 是否启用 |
| `auto_sync` | BOOLEAN | NOT NULL | FALSE | 是否自动同步（预留） |
| `last_sync_at` | DATETIME | NULL | - | 最后同步时间 |
| `created_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| `updated_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间（onupdate） |

**说明：** `access_token` 当前明文存储在 SQLite 中，生产环境建议升级为 AES 加密存储。

#### 表 4：teams（团队表）

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| `id` | INTEGER | PRIMARY KEY | - | 自增主键 |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | - | 团队名称 |
| `description` | TEXT | NULL | - | 描述 |
| `created_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

**说明：** 当前版本为预留表，未在前端使用。

### 3.3 数据库初始化流程

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app/data/codepulse.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 多线程安全
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# main.py 启动时自动创建表
Base.metadata.create_all(bind=engine)
```

**SQLite 配置说明：**
- `check_same_thread=False`：允许 FastAPI 的异步线程池访问同一连接（SQLite 单线程限制）
- 数据库文件位于 `backend/app/data/codepulse.db`，随项目迁移

---

## 4. 接口设计

### 4.1 接口规范总则

- **Base URL**: `http://localhost:8000/api`（开发环境）
- **协议**: HTTP/1.1 + JSON
- **Content-Type**: `application/json`（除文件上传接口使用 `multipart/form-data`）
- **认证方式**: 当前无认证（内网/本地使用），未来可扩展 JWT
- **错误响应格式**: `{"detail": "错误描述"}`（FastAPI 默认）

### 4.2 接口清单

#### 4.2.1 提交数据接口 (Commits)

**接口 1：单条提交上传**

```http
POST /api/commits/upload
Content-Type: application/json

Request Body:
{
  "commit_hash": "abc123...",
  "author": "张三",
  "email": "zhangsan@example.com",
  "date": "2024-01-01T00:00:00",
  "message": "fix bug",
  "additions": 10,
  "deletions": 2,
  "files_changed": 3,
  "review_comments_count": 0,
  "is_automated": false,
  "repository": "my-project",
  "branch": "main"
}

Response 200:
{
  "id": 1,
  "commit_hash": "abc123...",
  ...
  "created_at": "2024-01-01T00:00:00"
}
```

**接口 2：批量提交上传**

```http
POST /api/commits/upload/bulk
Content-Type: application/json

Request Body: [CommitCreate, CommitCreate, ...]

Response 200: 42  (成功插入数量)
```

**接口 3：Git Log 文件上传**

```http
POST /api/commits/upload/git-log
Content-Type: multipart/form-data

Request Body:
file: [Binary File]  (.txt / .log / .csv)

Response 200:
{
  "message": "成功导入 3 条提交记录",
  "count": 3
}

Response 400:
{
  "detail": "未能解析到任何提交记录"
}
```

**接口 4：JSON 数据导入**

```http
POST /api/commits/upload/json
Content-Type: application/json

Request Body: [CommitCreate, ...]  或  { "commits": [CommitCreate, ...] }

Response 200:
{
  "message": "成功导入 0 条提交记录",
  "count": 0
}
```

**接口 5：查询提交列表**

```http
GET /api/commits/?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59&search=张三&skip=0&limit=1000

Response 200:
[
  {
    "id": 1,
    "commit_hash": "abc123...",
    "author": "张三",
    "date": "2024-01-01T00:00:00",
    ...
  }
]
```

**接口 6：清空所有提交**

```http
DELETE /api/commits/all

Response 200:
{
  "message": "已删除 42 条提交记录"
}
```

---

#### 4.2.2 统计接口 (Stats)

**接口 7：KPI 概览**

```http
GET /api/stats/kpi?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59&search=张三

Response 200:
{
  "total_commits": 42,
  "net_lines": 1234,
  "active_developers": 5,
  "avg_review_response_hours": 4.5,
  "period_days": 30
}
```

**接口 8：提交趋势**

```http
GET /api/stats/trend?start_date=...&end_date=...&search=...&interval=day

Response 200:
{
  "data": [
    { "date": "2024-01-01", "count": 5, "additions": 100, "deletions": 20 },
    ...
  ],
  "has_decline": true,
  "decline_dates": ["2024-01-28", "2024-01-29"]
}
```

**接口 9：代码量统计**

```http
GET /api/stats/code?start_date=...&end_date=...&search=...

Response 200:
[
  {
    "author": "张三",
    "additions": 500,
    "deletions": 100,
    "net": 400,
    "commits": 15
  }
]
```

**接口 10：热力图**

```http
GET /api/stats/heatmap?start_date=...&end_date=...&search=...

Response 200:
{
  "data": [
    { "day": 0, "hour": 0, "count": 2 },   // 周一 00:00
    { "day": 0, "hour": 1, "count": 0 },
    ...
  ],
  "max_count": 10,
  "anomalies": [
    {
      "day": 2,
      "hour": 3,
      "count": 8,
      "type": "late_night_batch",
      "description": "周三 3:00-4:00 有 8 次提交，疑似自动化脚本"
    }
  ]
}
```

**接口 11：雷达图**

```http
GET /api/stats/radar?author=张三

Response 200:
[
  {
    "author": "张三",
    "dimensions": [
      { "dimension": "评论数量", "value": 60, "full_mark": 100 },
      { "dimension": "参与率", "value": 80, "full_mark": 100 },
      { "dimension": "响应速度", "value": 70, "full_mark": 100 },
      { "dimension": "代码贡献", "value": 90, "full_mark": 100 },
      { "dimension": "提交频率", "value": 50, "full_mark": 100 }
    ]
  }
]
```

**接口 12：异常检测报告**

```http
GET /api/stats/anomalies?start_date=...&end_date=...&search=...

Response 200:
[
  {
    "author": "张三",
    "anomaly_type": "深夜高频提交",
    "description": "张三 在非工作时间（0-6点）提交了 15 次，其中 10 次被标记为自动化脚本",
    "severity": "medium",
    "details": { "late_night_count": 15, "automated_count": 10 }
  }
]
```

---

#### 4.2.3 导出接口 (Export)

**接口 13：导出提交 CSV**

```http
GET /api/export/csv?start_date=...&end_date=...

Response: text/csv (Blob download)
```

**接口 14：导出成员统计 CSV**

```http
GET /api/export/members/csv?start_date=...&end_date=...

Response: text/csv (Blob download)
```

---

#### 4.2.4 同步接口 (Sync)

**接口 15：仓库配置 CRUD**

```http
GET    /api/sync/configs          → 列出所有配置
POST   /api/sync/configs         → 创建配置
GET    /api/sync/configs/{id}    → 获取单条配置
PUT    /api/sync/configs/{id}    → 更新配置
DELETE /api/sync/configs/{id}    → 删除配置
```

**接口 16：触发同步**

```http
POST /api/sync/sync/{id}?days=90&clear_existing=false

Response 200:
{
  "success": true,
  "message": "成功导入 150 条提交记录",
  "imported_count": 150,
  "repo_name": "my-project",
  "branch": "main"
}
```

**接口 17：全部同步**

```http
POST /api/sync/sync-all?days=90

Response 200:
[
  { "success": true, "message": "...", "imported_count": 150, ... },
  ...
]
```

**接口 18：获取本地分支列表**

```http
GET /api/sync/branches?path=/path/to/repo

Response 200:
["main", "develop", "feature/login"]
```

---

### 4.3 接口设计原则

#### 4.3.1 统一的过滤参数设计

所有统计接口共享同一套过滤参数解析逻辑：

```python
def _parse_date(date_str: Optional[str]):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")
```

**参数传递链：**
`Endpoint Query Params` → `_parse_date` → `StatsCalculator` → `crud.get_commits(..., start_date, end_date, search)`

**优点：** 新增统计维度时，只需在 endpoint 和 calculator 方法签名中添加参数，CRUD 层自动支持。

#### 4.3.2 错误处理策略

| 场景 | HTTP 状态码 | 响应体 | 示例 |
|------|------------|--------|------|
| 参数校验失败 | 422 | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` | Pydantic 自动生成 |
| 业务逻辑错误 | 400 | `{"detail": "未能解析到任何提交记录"}` | 解析失败 |
| 资源未找到 | 404 | `{"detail": "配置不存在"}` | 删除不存在的 config |
| 数据库冲突 | 500 | `{"detail": "Internal Server Error"}` | 唯一约束冲突（已在前端去重处理） |
| 服务器内部错误 | 500 | `{"detail": "Internal Server Error"}` | 未捕获异常 |

#### 4.3.3 并发查询设计

前端仪表盘一次加载触发 6 个并行 GET 请求：

```typescript
const [kpiRes, trendRes, codeRes, heatRes, radarRes, anomalyRes] = await Promise.all([
  statsApi.getKPI(params),
  statsApi.getTrend(params),
  statsApi.getCodeStats(params),
  statsApi.getHeatmap(params),
  statsApi.getRadar(params),
  statsApi.getAnomalies(params),
]);
```

**后端处理：** 6 个请求共享同一个 SQLite 数据库连接池（通过 FastAPI `Depends(get_db)`），SQLAlchemy 的 Session 是线程安全的，不会出现竞争问题。

---

## 5. 核心算法设计

### 5.1 去重算法（create_commits_bulk）

```python
def create_commits_bulk(db: Session, commits: List[schemas.CommitCreate]) -> int:
    all_existing = {r[0] for r in db.query(models.Commit.commit_hash).all()}
    new_commits = []
    for c in commits:
        h = c.commit_hash.lstrip('')  # 去除 BOM
        
        # 规则 1：精确匹配已存在
        if h in all_existing:
            continue
            
        # 规则 2：短 hash 检查完整 hash 前缀
        if len(h) < 40 and any(e.startswith(h) for e in all_existing):
            continue
            
        # 规则 3：完整 hash 检查短 hash 前缀
        if len(h) >= 40 and any(h.startswith(e) for e in all_existing if len(e) < 40):
            continue
            
        c.commit_hash = h
        new_commits.append(c)
    
    if not new_commits:
        return 0
    db.bulk_save_objects([models.Commit(**c.dict()) for c in new_commits])
    db.commit()
    return len(new_commits)
```

**时间复杂度：** O(N × M)，N=传入数量，M=已有数量。当前数据量小（万级），可接受。未来数据量增大时可优化为前缀树（Trie）或哈希表索引。

### 5.2 异常检测算法

**深夜高频提交检测：**
```python
late_night = [c for c in commits if c.date.hour < 6 or c.date.hour > 23]
if len(late_night) > 10:
    automated_count = sum(1 for c in late_night if c.is_automated)
    # severity: medium if automated_count > 50% else high
```

**趋势下降检测：**
```python
recent_7 = sum(d.count for d in data[-7:]) / 7
prev_7 = sum(d.count for d in data[-14:-7]) / 7
has_decline = recent_7 < prev_7 * 0.5
```

---

## 6. 安全与部署

### 6.1 安全措施

| 措施 | 实现 | 说明 |
|------|------|------|
| CORS | `CORSMiddleware` | 允许前端域名访问，阻止跨域恶意请求 |
| 文件类型限制 | `accept=".txt,.log,.csv"` | 前端限制文件上传类型 |
| 参数校验 | Pydantic | 自动校验类型和必填字段，防止注入 |
| Token 存储 | 明文 SQLite | **当前风险点**，建议后续升级为 AES 加密 |

### 6.2 部署命令

**开发环境：**
```bash
# 后端
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run dev
```

**生产环境：**
```bash
# 后端
cd backend
source venv/bin/activate
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 前端
cd frontend
npm run build
# 将 dist/ 目录部署到 Nginx
```

**Nginx 配置示例：**
```nginx
server {
    listen 80;
    server_name codepulse.example.com;

    location / {
        root /var/www/codepulse/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 7. 附录

### 7.1 目录结构

```
CodePulse/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── commits.py
│   │   │   ├── stats.py
│   │   │   ├── export_data.py
│   │   │   ├── mock.py
│   │   │   └── sync.py
│   │   ├── services/
│   │   │   ├── git_parser.py
│   │   │   ├── stats_calculator.py
│   │   │   ├── export_service.py
│   │   │   ├── local_git_service.py
│   │   │   └── remote_git_service.py
│   │   ├── data/
│   │   │   └── codepulse.db
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── database.py
│   ├── venv/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── services/
│   │       └── api.ts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── PRD.md
├── CONVERSATION_SUMMARY.md
└── CLAUDE.md
```

### 7.2 依赖版本

**后端 (requirements.txt)：**
```
fastapi==0.95.2
uvicorn==0.22.0
sqlalchemy==1.4.54
pydantic==1.10.13
python-multipart==0.0.6
requests==2.31.0
GitPython==3.1.43
PyGithub==1.59.1
```

**前端 (package.json)：**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.3.0",
  "vite": "^5.0.0",
  "tailwindcss": "^3.4.0",
  "echarts": "^5.4.3",
  "echarts-for-react": "^3.0.2",
  "axios": "^1.6.0",
  "lucide-react": "^0.300.0"
}
```

---

*本文档由 Claude Code 基于 CodePulse 项目代码分析生成，涵盖系统架构、技术选型、数据库设计和接口规范。*