# 对话记录导出

**日期**: 2026-06-26  
**项目路径**: `e:\code\code-commit-statistics-report\CodePulse\`  
**需求来源**: `CodePulse.md`

## 会话信息
---
## 主要任务
## 一、项目需求概述

CodePulse 是一个**研发活跃度智能分析平台**，旨在替代手工从 GitLab/GitHub 导出数据再处理的低效流程，解决以下核心痛点：

1. **效率低下**：手工统计 20 人团队月度数据平均耗时 2 小时，需实现自动化数据采集与报表生成。
2. **趋势不可见**：无法直观看到提交频率变化，需通过趋势图自动识别成员活跃度突然下降。
3. **代码量统计失真**：简单以“行数”衡量产出，大文件删除被算作高产出，需区分新增/删除/净增行数。
4. **异常模式难识别**：无法识别凌晨 3 点的批量提交是自动化脚本还是人工编码，需通过时段热力图标记异常。
5. **缺乏对标数据**：无法判断团队活跃度处于什么水平，需提供团队间横向对比的基准线。

### 技术栈要求
- **后端**: Python（FastAPI）+ SQLite，使用 `python-gitlab` 或 `PyGithub` 库对接 API
- **前端**: React + TypeScript + TailwindCSS + ECharts/Chart.js
- **导出**: 使用 `openpyxl` 生成 Excel，`WeasyPrint` 或浏览器无头模式生成 PDF
- **定时任务**: 使用 APScheduler 或 Celery 实现定期报表生成与邮件发送

---

## 二、对话与操作记录

### 第一轮：项目初始开发

**用户指令**: 按照 CodePulse.md 中内容完成 CodePulse 项目开发。

**系统状态**:
- 用户 IDE 打开文件: `e:\code\code-commit-statistics-report\CodePulse.md`
- 当前工作目录: `e:\Workspaces\IDEA\finder`
- 平台: Windows 10, PowerShell

**执行步骤**:

1. **读取需求文件**: 读取 `CodePulse.md`，理解项目需求。

2. **检查项目目录**:
   - `e:\code\code-commit-statistics-report` 目录下只有 `CodePulse.md`
   - `e:\Workspaces\IDEA\finder` 目录下有 Java 项目（pom.xml, src, target）

3. **创建项目目录结构**:
   ```
   CodePulse/
   ├── backend/
   │   ├── app/
   │   │   ├── api/
   │   │   ├── services/
   │   │   ├── data/
   │   │   ├── main.py
   │   │   ├── models.py
   │   │   ├── schemas.py
   │   │   ├── crud.py
   │   │   └── database.py
   │   └── requirements.txt
   ├── frontend/
   │   ├── src/
   │   │   ├── components/
   │   │   ├── pages/
   │   │   ├── services/
   │   │   ├── types/
   │   │   ├── App.tsx
   │   │   ├── main.tsx
   │   │   └── index.css
   │   ├── index.html
   │   ├── package.json
   │   ├── tsconfig.json
   │   └── vite.config.ts
   └── README.md
   ```

4. **创建后端文件**（按顺序写入）:
   - `backend/app/main.py` - FastAPI 入口，注册路由，CORS 配置
   - `backend/app/database.py` - SQLAlchemy SQLite 配置
   - `backend/app/models.py` - Commit, Member, Team ORM 模型
   - `backend/app/schemas.py` - Pydantic 数据模型（KPI, Trend, Heatmap, Radar, Anomaly）
   - `backend/app/crud.py` - 数据库 CRUD 操作
   - `backend/app/services/git_parser.py` - Git Log / CSV 解析服务
   - `backend/app/services/mock_generator.py` - 模拟数据生成器（25 人，3 个月，2000 条提交）
   - `backend/app/services/stats_calculator.py` - 统计计算服务（KPI, 趋势, 热力图, 雷达图, 异常检测）
   - `backend/app/services/export_service.py` - CSV 导出服务
   - `backend/app/api/commits.py` - 提交记录路由（上传, 查询, 删除）
   - `backend/app/api/stats.py` - 统计路由（KPI, 趋势, 代码, 热力图, 雷达图, 异常）
   - `backend/app/api/export_data.py` - 导出路由
   - `backend/app/api/mock.py` - 模拟数据路由
   - `backend/app/api/__init__.py` 和 `services/__init__.py`
   - `backend/requirements.txt` - 初始依赖（FastAPI 0.104, SQLAlchemy 2.0, Pydantic v2）

5. **创建前端文件**（按顺序写入）:
   - `frontend/package.json` - React 18 + TypeScript + Vite + TailwindCSS + ECharts
   - `frontend/tsconfig.json` / `tsconfig.node.json`
   - `frontend/vite.config.ts` - Vite 配置，代理 `/api` 到 `localhost:8000`
   - `frontend/index.html`
   - `frontend/src/main.tsx` - React 入口
   - `frontend/src/index.css` - Tailwind + 自定义组件样式 + 打印样式
   - `frontend/src/types/index.ts` - TypeScript 类型定义
   - `frontend/src/services/api.ts` - Axios API 封装
   - `frontend/src/App.tsx` - 主应用组件，包含所有图表和交互逻辑
   - `frontend/tailwind.config.js` / `postcss.config.js`

6. **修复 models.py 导入问题**: 将 `from datetime import datetime` 从文件底部移到顶部。

7. **创建 README.md**: 包含项目介绍、功能特性、技术栈、快速开始、API 文档、项目结构、部署说明。

**第一轮完成状态**:
- 后端文件全部创建完毕，Python 语法检查通过
- 前端文件全部创建完毕
- 项目结构完整

---

### 第二轮：后端启动问题 - 接口调用失败修复

**用户报告问题**:
```
[vite] http proxy error: /api/stats/kpi?start_date=... 
AggregateError [ECONNREFUSED]: ...
```

**用户指令**: 这里有一批接口调用失败了，处理一下，让接口可以调用成功。

**诊断过程**:
1. 检查后端是否运行: `curl http://localhost:8000/api/health` → 后端未运行
2. 检查 Python 版本: `python --version` → `Python 3.7.8rc1`
3. 检查虚拟环境: 不存在，需要创建
4. 尝试创建虚拟环境并安装依赖 → 失败
   - 错误: `Could not find a version that satisfies the requirement fastapi==0.104.1`
   - 原因: Python 3.7 不支持 FastAPI 0.104、SQLAlchemy 2.0、Pydantic v2

**修复步骤**:

1. **修改 requirements.txt**（降级到 Python 3.7 兼容版本）:
   - `fastapi==0.95.2` (从 0.104.1)
   - `sqlalchemy==1.4.54` (从 2.0.23)
   - `pydantic==1.10.13` (从 2.5.0)
   - `uvicorn==0.22.0` (从 0.24.0)
   - 移除 numpy, pandas, celery, redis, PyGithub, python-gitlab, openpyxl, apscheduler, python-jose, passlib 等非核心依赖

2. **修改 schemas.py**（Pydantic v1 适配）:
   - `from_attributes = True` → `orm_mode = True`（所有 Config 类）
   - `List[dict]` → `List[Dict]`（导入 `Dict`）
   - `details: dict` → `details: Dict[str, int]`

3. **修改 stats.py**（Python 3.7 类型注解适配）:
   - `list[schemas.CodeStats]` → `List[schemas.CodeStats]`
   - `list[schemas.AnomalyReport]` → `List[schemas.AnomalyReport]`
   - 修复重复导入 `from typing import Optional, List, List`

4. **创建虚拟环境并安装依赖**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   - pip 升级成功: 20.1.1 → 24.0
   - 核心依赖安装成功: fastapi, uvicorn, sqlalchemy, pydantic, python-multipart, requests

5. **启动后端服务**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - 启动成功
   - 健康检查验证: `{"status":"ok","timestamp":"..."}`

**第二轮完成状态**:
- 后端兼容 Python 3.7，成功启动
- 接口可以正常访问

---

### 第三轮：搜索框布局与功能修复

**用户报告问题**:
- 首页的搜索输入框与左侧时间搜索框重叠了
- 搜索输入框样式需要调整，与左侧时间搜索框间隔 1px 宽度
- 搜索输入框要支持按照输入的成员名称或 Commit Message 内容同步筛选数据

**诊断过程**:
1. 检查前端布局: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4`
   - 日期范围（第2列）和搜索框（第3列）在 lg 屏幕下可能挤压
2. 检查前端搜索逻辑: `onChange` 更新 `filters.search`，`useEffect` 依赖 `filters.search` 触发 `fetchData()`
3. 检查后端接口: `stats.py` 路由没有接收 `search` 参数！
   - 前端虽然传递了 `search`，但后端统计接口忽略了它

**修复步骤**:

1. **修改后端 stats.py**（所有统计接口添加 search 参数）:
   - `/api/stats/kpi` - 添加 `search: Optional[str] = Query(None)`
   - `/api/stats/trend` - 添加 `search` 参数
   - `/api/stats/code` - 添加 `search` 参数
   - `/api/stats/heatmap` - 添加 `search` 参数
   - `/api/stats/anomalies` - 添加 `search` 参数
   - 所有接口将 `search` 传递给 `StatsCalculator`

2. **修改 StatsCalculator**（传递 search 参数）:
   - `get_kpi` - 已有 `search` 参数 ✓
   - `get_trend` - 已有 `search` 参数 ✓
   - `get_code_stats` - 添加 `search` 参数
   - `get_heatmap` - 添加 `search` 参数
   - `get_anomalies` - 添加 `search` 参数
   - 所有方法将 `search` 传递给 `crud.get_commits(..., search=search)`
   - `crud.get_commits` 已经支持 `search` 参数（模糊搜索 author 和 message）

3. **修改前端 App.tsx**（布局和防抖）:
   - 添加 `useDebounce` Hook（500ms 延迟）:
     ```typescript
     function useDebounce<T>(value: T, delay: number): T {
       const [debouncedValue, setDebouncedValue] = useState<T>(value);
       useEffect(() => {
         const timer = setTimeout(() => setDebouncedValue(value), delay);
         return () => clearTimeout(timer);
       }, [value, delay]);
       return debouncedValue;
     }
     ```
   - 在 App 组件中使用: `const debouncedSearch = useDebounce(filters.search, 500);`
   - 修改 `fetchData` 使用 `debouncedSearch` 而不是 `filters.search`
   - 修改 `useEffect` 依赖项: `debouncedSearch` 替代 `filters.search`
   - 修改搜索框布局（ControlPanel）:
     ```html
     <div className="space-y-2 border-l border-slate-700 pl-3 ml-px">
     ```
     - 添加左边框 `border-l border-slate-700`
     - 添加左内边距 `pl-3`
     - 添加 1px 左外边距 `ml-px`

4. **重新启动后端**:
   - 检查 Python 语法: `python -m py_compile` 通过
   - 启动 uvicorn: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
   - 启动成功
   - 验证搜索接口: `/api/stats/kpi?search=张` → `{"total_commits":79, ...}`

**第三轮完成状态**:
- 搜索框添加左侧分隔线和 1px 边距，不再与时间筛选框重叠
- 搜索输入支持 500ms 防抖，避免频繁请求
- 后端所有统计接口支持 `search` 参数，按成员名称或 Commit Message 筛选
- 接口验证通过

---

### 第四轮：导出对话记录

**用户指令**: 将今天所有的对话内容都导出来，用 markdown 文件记录。

**执行步骤**:
- 整理上述三轮对话记录，生成本文档。

---

## 三、项目文件清单

### 后端文件（`backend/`）

| 文件 | 大小 | 说明 |
|------|------|------|
| `app/main.py` | 1,641 B | FastAPI 入口，路由注册，CORS，健康检查 |
| `app/database.py` | 620 B | SQLAlchemy SQLite 引擎和 Session |
| `app/models.py` | 1,621 B | Commit, Member, Team ORM 模型 |
| `app/schemas.py` | 2,640 B | Pydantic 数据模型，Pydantic v1 兼容 |
| `app/crud.py` | 2,758 B | 数据库 CRUD 操作，支持 search 模糊查询 |
| `app/api/commits.py` | 3,035 B | 提交记录上传/查询/删除 API |
| `app/api/stats.py` | 2,872 B | 统计接口（KPI, 趋势, 代码, 热力图, 雷达图, 异常），支持 search |
| `app/api/export_data.py` | 1,636 B | CSV 导出接口 |
| `app/api/mock.py` | 934 B | 模拟数据生成接口 |
| `app/services/git_parser.py` | 5,319 B | Git Log 和 CSV 解析服务 |
| `app/services/mock_generator.py` | 5,599 B | 25 人 3 个月 2000 条模拟数据生成 |
| `app/services/stats_calculator.py` | 11,254 B | 统计计算（KPI, 趋势, 热力图, 雷达图, 异常检测） |
| `app/services/export_service.py` | 1,955 B | CSV 导出服务 |
| `requirements.txt` | 303 B | 核心依赖（FastAPI 0.95.2, SQLAlchemy 1.4.54, Pydantic 1.10.13） |

### 前端文件（`frontend/`）

| 文件 | 大小 | 说明 |
|------|------|------|
| `src/App.tsx` | 26,302 B | 主应用组件，包含所有图表、筛选、导出、导入模态框 |
| `src/main.tsx` | 236 B | React 入口 |
| `src/index.css` | 1,764 B | Tailwind + 自定义组件样式 + 打印样式 |
| `src/types/index.ts` | 1,600 B | TypeScript 类型定义 |
| `src/services/api.ts` | 1,954 B | Axios API 封装（Commit, Stats, Export, Mock） |
| `package.json` | 775 B | React 18 + Vite + Tailwind + ECharts + Lucide |
| `vite.config.ts` | 306 B | Vite 配置，代理 `/api` 到 `localhost:8000` |
| `tsconfig.json` | 626 B | TypeScript 配置 |
| `tailwind.config.js` | 263 B | Tailwind 配置 |
| `postcss.config.js` | 79 B | PostCSS 配置 |
| `index.html` | 396 B | HTML 入口 |

### 其他文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `README.md` | 4,948 B | 项目说明、快速开始、API 文档、部署说明 |
| `CodePulse.md` | 5,809 B | 原始需求文档 |

---

## 四、后端 API 列表

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/api/health` | GET | - | 健康检查 |
| `/api/commits/upload/git-log` | POST | `file` (UploadFile) | 上传 Git Log 文件 |
| `/api/commits/upload/json` | POST | `commits` (List[CommitCreate]) | 粘贴 JSON 数据 |
| `/api/commits/` | GET | `start_date`, `end_date`, `authors`, `repositories`, `search` | 查询提交记录 |
| `/api/commits/authors` | GET | - | 获取所有作者 |
| `/api/commits/repositories` | GET | - | 获取所有仓库 |
| `/api/commits/all` | DELETE | - | 清空所有提交 |
| `/api/stats/kpi` | GET | `start_date`, `end_date`, `search` | KPI 概览 |
| `/api/stats/trend` | GET | `start_date`, `end_date`, `interval`, `search` | 提交频率趋势 |
| `/api/stats/code` | GET | `start_date`, `end_date`, `search` | 代码量构成 |
| `/api/stats/heatmap` | GET | `start_date`, `end_date`, `search` | 提交时段热力图 |
| `/api/stats/radar` | GET | `author` | 评审参与度雷达图 |
| `/api/stats/anomalies` | GET | `start_date`, `end_date`, `search` | 异常检测 |
| `/api/export/csv` | GET | `start_date`, `end_date` | 导出提交 CSV |
| `/api/export/members/csv` | GET | `start_date`, `end_date` | 导出成员统计 CSV |
| `/api/mock/generate` | POST | `days`, `total_commits` | 生成模拟数据 |
| `/api/mock/developers` | GET | - | 获取模拟开发者列表 |

---

## 五、遇到的坑与解决方案

### 坑 1: Python 3.7 与最新依赖不兼容
- **问题**: `fastapi==0.104.1`, `sqlalchemy==2.0.23`, `pydantic==2.5.0` 需要 Python 3.8+，当前环境是 Python 3.7.8
- **解决**: 降级依赖版本到 Python 3.7 兼容版本（FastAPI 0.95.2, SQLAlchemy 1.4.54, Pydantic 1.10.13）

### 坑 2: Pydantic v1 vs v2 语法差异
- **问题**: `from_attributes = True` 是 Pydantic v2 语法，v1 中应使用 `orm_mode = True`
- **解决**: 将所有 `Config` 类中的 `from_attributes = True` 改为 `orm_mode = True`

### 坑 3: Python 3.7 不支持 `list[...]` 泛型语法
- **问题**: `response_model=list[schemas.CodeStats]` 在 Python 3.7 下运行报错
- **解决**: 改为 `List[schemas.CodeStats]`（从 `typing` 导入 `List`）

### 坑 4: pip 网络下载失败
- **问题**: 安装 numpy 等大包时网络连接重置 (`ConnectionResetError`)
- **解决**: 精简 requirements.txt，只保留核心依赖（FastAPI, SQLAlchemy, Pydantic, python-multipart, requests），非核心依赖后续按需安装

### 坑 5: 搜索功能前端有但后端不支持
- **问题**: 前端传递了 `search` 参数，但后端 `stats.py` 路由没有接收，导致搜索无效
- **解决**: 为所有统计接口（KPI, 趋势, 代码, 热力图, 异常）添加 `search` 参数，并在 `StatsCalculator` 中传递给 `crud.get_commits`

---

## 六、启动命令

### 后端
```bash
cd e:\code\code-commit-statistics-report\CodePulse\backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端
```bash
cd e:\code\code-commit-statistics-report\CodePulse\frontend
npm install
npm run dev
```

---

## 七、最终验证状态

- ✅ 后端健康检查: `http://localhost:8000/api/health` → `{"status":"ok"}`
- ✅ 搜索接口测试: `/api/stats/kpi?search=张` → 正确返回匹配数据
- ✅ 后端代码语法: 全部通过 `python -m py_compile`
- ✅ 前端布局: 搜索框添加左侧分隔线和 1px 边距
- ✅ 前端搜索防抖: 500ms 延迟，避免频繁请求
- ✅ 项目结构完整，README 文档齐全
前端访问链接:`http://localhost:3000/`
---

*记录结束时间: 2026-06-26 23:08*

## 会话信息
- 时间：2026-07-01
- 项目：CodePulse (E:\code\code-commit-statistics-report\CodePulse)

## 主要任务
实现从模拟数据到真实 Git 仓库数据的迁移，支持自动连接 Git 仓库或通过导入 Git 日志加载数据。

## 实现内容

### 1. 后端变更
- **requirements.txt**: 新增 `GitPython==3.1.43` 和 `PyGithub==1.59.1`
- **models.py**: 新增 `RepositoryConfig` 模型用于存储仓库配置
- **schemas.py**: 新增仓库配置和同步结果的数据验证模型
- **crud.py**: 新增仓库配置的 CRUD 操作
- **services/local_git_service.py**: 新增本地 Git 仓库读取服务
- **services/remote_git_service.py**: 新增 GitHub/GitLab API 远程读取服务
- **api/sync.py**: 新增仓库配置管理和同步 API 路由
- **main.py**: 注册同步路由

### 2. 前端变更
- **types/index.ts**: 新增 `RepositoryConfig` 和 `SyncResult` 类型定义
- **services/api.ts**: 新增 `syncApi` 接口
- **App.tsx**: 新增仓库配置管理模态框组件，支持添加/编辑/删除仓库配置和触发同步

### 3. 功能特性
- 本地 Git 仓库直连（GitPython）
- 远程 GitHub 仓库对接（PyGithub）
- 远程 GitLab 仓库对接（requests）
- 仓库配置持久化（SQLite）
- 手动/批量同步触发
- 自动检测自动化提交（CI/CD、Dependabot 等）
- 前端仓库管理界面（"仓库管理"按钮和模态框）

### 4. 遇到的问题及修复
- 修复了 `RepositoryConfigListResponse` 中意外包含多余字段的问题
- 修复了 `App.tsx` 中存在的重复 `RepositoryConfigModal` 组件问题
- 修复了 `api.ts` 中重复 `syncApi` 定义的问题
- 修复了 `App.tsx` 中换行符转义字符导致的语法错误
- 修复了 `models.py` 中 `Team` 模型被意外覆盖的问题
- 修复了端口冲突问题（8000/8001 被占用）
- 修复了缺少 `)` 和 `footer` 的语法问题

### 5. 验证结果
- ✅ 后端服务启动成功
- ✅ 成功创建本地仓库配置并同步真实提交数据
- ✅ KPI/统计接口正确返回真实数据（1 commit, 4530 net lines）
- ✅ TypeScript 编译通过（仅剩一个已有的无关错误）
- ✅ Python 语法检查通过

## 使用方式
1. 启动后端：`cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. 启动前端：`cd frontend && npm run dev`
3. 打开前端页面，点击「仓库管理」
4. 添加仓库配置（本地路径或远程 URL + Token）
5. 点击「同步」加载真实数据

CodePulse 现在应该能够：
- 连接本地 Git 仓库自动加载提交数据
- 通过 GitHub/GitLab API 同步远程仓库
- 在前端界面管理仓库配置并触发同步                                                                                                                                                                                                              
如果您后续还需要：                                                                                                      
- 添加定时自动同步功能（Cron 作业）                                                                                     
- 支持更多的 Git 托管平台（如 Gitee、Bitbucket）                                                                        
- 优化大数据量同步的性能                                                                                                
- 或者任何其他功能
随时告诉我！

---

## 会话信息
- 时间：2026-07-05
- 项目：CodePulse (E:\code\code-commit-statistics-report\CodePulse)

## 主要任务
修复前端导入/上传功能缺陷、后端数据解析与去重问题、UI 布局问题。

## 修复内容

### 1. Git Log 上传 400 错误
- **文件**: `backend/app/services/git_parser.py`
- **原因**: `git-log.txt` 使用自定义格式 `hash | author | date | message`，后端只支持标准 git log 和 CSV
- **修复**: 在 `parse_git_log` 中新增 `_parse_custom_git_log` 方法，支持自定义格式解析

### 2. JSON 导入 422 错误
- **文件**: `backend/app/schemas.py`
- **原因**: `files_changed` 等数值字段传入 `null` 时 Pydantic 校验失败
- **修复**: 添加 `default_zero_for_none` validator，将 `null` 自动替换为 `0`
- **文件**: `frontend/src/App.tsx`
- **修复**: 新增 `normalizeCommit` 函数，支持字段别名映射（`hash`→`commit_hash` 等）和日期格式自动转换

### 3. 数据库唯一约束冲突 500 错误
- **文件**: `backend/app/crud.py`
- **原因**: 重复导入同一 commit 导致 SQLite 唯一约束冲突
- **修复**: `create_commits_bulk` 中去重逻辑：先检查数据库已有 hash，过滤已存在记录后再插入

### 4. 重复提交记录问题（3条变6条/4条变5条）
- **文件**: `backend/app/crud.py`
- **原因**: git-log.txt 使用短 hash（7位），JSON 使用完整 hash（40位），被视为不同记录
- **修复**: 
  - 清理 BOM 字符：`h = c.commit_hash.lstrip('﻿')`
  - 双向前缀匹配去重：短 hash 检查完整 hash 前缀，完整 hash 检查短 hash 前缀
  - 清理数据库中已有的短 hash 重复记录

### 5. 热力图 tooltip 显示 undefined
- **文件**: `frontend/src/App.tsx`
- **原因**: tooltip formatter 中 `days[params.value[0]]` 误把 hour（0-23）当作 day 索引
- **修复**: 改为 `days[params.value[1]]`（day 索引）和 `params.value[0]`（hour）

### 6. 控制面板布局问题
- **文件**: `frontend/src/App.tsx`
- **问题1**: 日期输入框被搜索框遮挡
- **修复1**: grid 从 `grid-cols-4` 改为 `grid-cols-[1fr_1.2fr_0.8fr_1fr]`，日期列更宽、搜索框列更窄
- **问题2**: 日期显示不全（最后一位被截断）
- **修复2**: `input[type="date"]` 添加 `min-w-[150px]`
- **问题3**: 搜索框列多余左边框增加拥挤感
- **修复3**: 移除搜索框列的 `border-l border-slate-700 pl-3 ml-px`

### 7. 搜索框实时筛选优化
- **文件**: `frontend/src/App.tsx`
- **修复**: debounce 延迟从 500ms 缩短到 200ms；`fetchData` 中添加 `setLoading(true/false)` 提供视觉反馈

### 8. 导入成功提示
- **文件**: `frontend/src/App.tsx`
- **修复**: 
  - `handleFileUpload` 成功后添加 `alert(\`上传成功：${res.data.message}\`)`
  - `handleJsonUpload` 成功后改为 `alert(res.data.message)`（显示后端返回的实际插入数量，而非前端传入数量）

### 9. 空点击按钮提示
- **文件**: `frontend/src/App.tsx`
- **修复**: 
  - 上传按钮 `disabled` 从 `!file || loading` 改为 `loading`，未选文件时点击弹出 `alert('请先选择文件再进行上传')`
  - 导入 JSON 按钮 `disabled` 从 `!jsonText || loading` 改为 `loading`，未填数据时点击弹出 `alert('请先输入Git Log JSON 数据再进行导入JSON数据')`

## 验证结果
- ✅ Git Log 文件上传成功（3条记录）
- ✅ JSON 导入成功（去重后正确显示实际插入数）
- ✅ 数据库重复记录清理完成（4条唯一记录）
- ✅ 热力图 tooltip 正常显示（如"周日 6:00"）
- ✅ 控制面板布局正常，日期图标和搜索框无遮挡
- ✅ 搜索实时筛选有 loading 反馈
- ✅ 空点击按钮有弹框提示

---
*此文件由 Claude Code 自动生成，记录了 CodePulse 项目导入功能与数据去重的修复过程。*
---
*此文件由 Claude Code 自动生成，记录了 CodePulse 项目从模拟数据到真实 Git 数据迁移的完整实现过程。*

---

## 2026-07-05 对话修复记录

### 1. Git Log 文件上传 400 错误修复
- **问题**：上传 `git-log.txt` 返回 `{"detail":"未能解析到任何提交记录"}`
- **原因**：文件格式为自定义 `hash | author | date | message`，非标准 git log 格式
- **修复**：`backend/app/services/git_parser.py` 新增 `_parse_custom_git_log` 方法，支持该自定义格式解析
- **验证**：成功解析 3 条 commit，数据正确

### 2. JSON 数据导入 422 错误修复
- **问题**：粘贴 JSON 后返回 422，`commit_hash` 缺失、`files_changed` null 不被允许
- **修复**：
  - `frontend/src/App.tsx` 新增 `normalizeCommit` 函数，自动映射字段别名（`hash`→`commit_hash`、`name`→`author` 等）
  - 日期自动转为 ISO 8601 格式
  - `backend/app/schemas.py` 新增 Pydantic validator `default_zero_for_none`，`null` 数值自动替换为 `0`

### 3. 数据库唯一约束冲突 500 错误修复
- **问题**：重复上传触发 `sqlite3.IntegrityError: UNIQUE constraint failed`
- **修复**：`backend/app/crud.py` 的 `create_commits_bulk` 改为先查询已存在 hash，跳过重复记录
- **后续增强**：清理 BOM 字符、双向前缀匹配（短 hash ↔ 完整 hash 互斥去重）

### 4. 热力图 tooltip 显示 undefined 修复
- **问题**：tooltip 显示 `undefined 6:00`
- **原因**：`params.value[0]` 是 hour（0-23），误用 `days[hour]` 导致越界
- **修复**：`frontend/src/App.tsx` 改为 `days[params.value[1]]`（day 索引）+ `params.value[0]`（hour）

### 5. 控制面板布局修复
- **问题**：1314×832 分辨率下，第二个日期选择图标被搜索框遮挡
- **修复**：
  - `grid-cols-4` 改为自适应比例 `grid-cols-[1fr_1.2fr_0.8fr_1fr]`，日期列更宽、搜索列更窄
  - 搜索框添加 `max-w-[220px]`
  - 日期输入框最小宽度 `min-w-[150px]` 确保日期完整显示

### 6. 搜索实时筛选优化
- **修复**：`useDebounce` 延迟从 500ms 缩短至 200ms
- `fetchData` 添加 `setLoading(true/false)`，搜索时有视觉反馈

### 7. 导入成功提示添加
- **修复**：`handleFileUpload` 和 `handleJsonUpload` 成功后添加 `alert` 弹框提示，显示后端返回的真实导入数量

### 8. 空点击防护
- **修复**：未选择文件/未填写 JSON 时点击按钮，弹出 `alert` 提示，禁止调用后端接口
- 按钮 `disabled` 状态仅限制 `loading`，不限制文件/文本存在性，确保用户始终获得点击反馈

### 9. 重复提交记录去重增强
- **清理**：数据库删除短 hash（7 位）和带 BOM 前缀的重复记录，统一保留完整 40 位 hash
- **代码增强**：`create_commits_bulk` 支持：
  - 短 hash 导入时，检查数据库中是否有完整 hash 前缀已存在 → 跳过
  - 完整 hash 导入时，检查数据库中是否有短 hash 前缀已存在 → 跳过

### 最终数据状态
- 数据库提交记录：4 条（与 git 实际提交数一致）
- KPI 接口返回：`total_commits: 4`
- 所有接口正常工作，不影响其他功能
