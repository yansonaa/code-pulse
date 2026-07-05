# CodePulse 产品需求文档 (PRD)

> 版本：v1.0  
> 日期：2026-07-05  
> 产品：CodePulse - 研发活跃度智能分析平台

---

## 1. 文档概述

### 1.1 产品定位
CodePulse 是一款面向研发团队的全栈研发活跃度智能分析平台，通过自动化采集 Git 提交数据，提供可视化仪表盘、代码趋势分析和异常检测能力，替代传统手工导出 GitLab/GitHub 数据并手动处理的工作流。

### 1.2 目标用户
| 用户角色 | 核心诉求 |
|---------|---------|
| 研发经理 / 技术 Lead | 监控团队代码产出趋势、识别效率瓶颈、关注成员工作健康度 |
| DevOps / 平台工程师 | 配置数据源、管理同步策略、保障数据管道稳定 |
| 个人开发者 | 查看个人贡献雷达图、了解自身提交模式 |
| QA / 审计合规人员 | 导出审计报表、识别自动化提交冒充人工产出、确认评审覆盖率 |

### 1.3 技术架构
- **后端**：Python 3.10+ + FastAPI + SQLAlchemy (SQLite) + Pydantic v1
- **前端**：React 18 + TypeScript + Vite + TailwindCSS + ECharts
- **Git 集成**：GitPython（本地）、PyGithub（GitHub）、requests（GitLab）

---

## 2. 功能需求

### 2.1 数据接入层

#### 2.1.1 Git Log 文件上传
- **需求编号**：F-001
- **功能描述**：支持上传 `.txt`、`.log`、`.csv` 格式的 Git 日志文件，系统自动解析并入库
- **输入格式**：
  - 标准 `git log --stat` 输出（`commit <hash>\nAuthor: ...\nDate: ...`）
  - 自定义 `|`-分隔格式（`<hash> | <author> | <date> | <message>`）
  - CSV 格式（`hash,author,email,date,message,additions,deletions,files_changed`）
- **边界处理**：
  - 重复 commit_hash 自动跳过
  - 短 hash（7 位）与完整 hash（40 位）互斥去重
  - 清除 BOM 字符（`﻿`）
- **异常提示**：解析失败返回 400，`{"detail":"未能解析到任何提交记录"}`

#### 2.1.2 JSON 数据导入
- **需求编号**：F-002
- **功能描述**：支持在前端弹窗中粘贴 JSON 数组直接导入
- **兼容性要求**：
  - 字段别名自动映射：`hash`/`sha` → `commit_hash`，`name` → `author`，`msg` → `message`
  - 支持嵌套结构（如 GitHub API 的 `commit.author.name`）
  - 支持外层包裹对象（`{ "commits": [...] }`）
  - `null` 数值字段自动转为 `0`
  - 日期字符串自动转为 ISO 8601 格式
- **异常提示**：未输入 JSON 点击导入时弹框提示"请先输入 Git Log JSON 数据再进行导入"

#### 2.1.3 模拟数据生成
- **需求编号**：F-003
- **功能描述**：一键生成约 2000 条模拟提交数据，覆盖 90 天，模拟 25 名开发者
- **模拟规则**：
  - 工作日提交概率高于周末
  - 夜间（0-6 点）有更高概率出现自动化提交
  - 偶现大文件删除（>1000 行）模拟虚假高产出
- **接口**：`POST /api/mock/generate?days=90&total_commits=2000`
- **前置条件**：生成前自动清空现有数据（`clear_existing=true`）

#### 2.1.4 本地 Git 仓库同步
- **需求编号**：F-004
- **功能描述**：通过本地文件系统路径直连 Git 仓库，自动读取 commit 历史
- **配置参数**：`repo_type: "local"`，`local_path: "/path/to/repo"`
- **提取字段**：author、email、date、message、additions、deletions、files_changed、branch
- **自动化检测**：通过关键字匹配识别自动化提交（CI/CD、Jenkins、Dependabot、Renovate 等）

#### 2.1.5 远程 GitHub/GitLab 同步
- **需求编号**：F-005
- **功能描述**：通过 API Token 连接 GitHub 或 GitLab，拉取远程仓库提交记录
- **配置参数**：
  - `repo_type: "github"` 或 `"gitlab"`
  - `remote_url: "https://github.com/org/repo.git"`
  - `access_token: "ghp_xxxx"`
  - `branch: "main"`
- **同步范围**：默认最近 90 天，最大 5000 条提交
- **同步策略**：增量追加（`clear_existing=false`）或全量覆盖（`clear_existing=true`）
- **接口**：`POST /api/sync/sync/{config_id}`

#### 2.1.6 仓库配置管理
- **需求编号**：F-006
- **功能描述**：CRUD 管理所有仓库连接配置，支持启用/停用、分支切换、手动/批量触发同步
- **管理字段**：name、repo_type、local_path、remote_url、access_token、branch、is_active、auto_sync
- **接口**：
  - `GET/POST /api/sync/configs`
  - `GET/PUT/DELETE /api/sync/configs/{id}`
  - `POST /api/sync/sync-all`

---

### 2.2 数据管理层

#### 2.2.1 提交记录存储
- **表名**：`commits`
- **核心字段**：
  | 字段 | 类型 | 约束 | 说明 |
  |------|------|------|------|
  | `commit_hash` | VARCHAR(40) | UNIQUE, NOT NULL | 提交唯一标识 |
  | `author` | VARCHAR(100) | NOT NULL | 作者名 |
  | `email` | VARCHAR(200) | NULL | 邮箱 |
  | `date` | DATETIME | NOT NULL | 提交时间 |
  | `message` | TEXT | NULL | 提交消息 |
  | `additions` | INTEGER | DEFAULT 0 | 新增行数 |
  | `deletions` | INTEGER | DEFAULT 0 | 删除行数 |
  | `files_changed` | INTEGER | DEFAULT 0 | 变更文件数 |
  | `review_comments_count` | INTEGER | DEFAULT 0 | 评审评论数 |
  | `is_automated` | BOOLEAN | DEFAULT FALSE | 是否自动化提交 |
  | `repository` | VARCHAR(200) | NULL | 所属仓库 |
  | `branch` | VARCHAR(200) | NULL | 所属分支 |

#### 2.2.2 去重机制
- **规则 1**：精确匹配 `commit_hash` 已存在则跳过
- **规则 2**：短 hash（长度 < 40）导入时，检查数据库中是否有以该前缀开头的完整 hash → 跳过
- **规则 3**：完整 hash（长度 >= 40）导入时，检查数据库中是否有以该前缀开头的短 hash → 跳过，并删除短 hash
- **规则 4**：清理 hash 中的 BOM 字符（`﻿`）

#### 2.2.3 数据清空
- **接口**：`DELETE /api/commits/all`
- **功能**：一键清空所有提交数据，用于重新导入或重置环境

---

### 2.3 分析可视化层

#### 2.3.1 KPI 概览卡片
- **需求编号**：V-001
- **展示指标**：
  - 总提交次数（Total Commits）
  - 净代码行数（Net Lines = Additions - Deletions）
  - 活跃开发者数（Active Developers）
  - 平均评审响应时长（Avg Review Response Hours，基于 review_comments_count 估算）
- **数据刷新**：日期范围或搜索条件变化时自动重新计算
- **接口**：`GET /api/stats/kpi`

#### 2.3.2 提交频率趋势图
- **需求编号**：V-002
- **图表类型**：折线图（ECharts Line）
- **维度**：日期（X 轴）vs 提交次数 / 新增行数 / 删除行数（Y 轴）
- **智能检测**：自动识别下降趋势（最近 7 天均值 < 前 7 天均值 × 50%），标红预警
- **接口**：`GET /api/stats/trend`

#### 2.3.3 代码量构成分析
- **需求编号**：V-003
- **图表类型**：堆叠柱状图（ECharts Bar）
- **维度**：作者（X 轴）vs 新增行数 / 删除行数 / 净行数（Y 轴）
- **展示上限**：Top 15 贡献者
- **接口**：`GET /api/stats/code`

#### 2.3.4 提交时段热力图
- **需求编号**：V-004
- **图表类型**：热力图（ECharts Heatmap）
- **维度**：星期（Y 轴，0=周一 ~ 6=周日）× 小时（X 轴，0~23）
- **颜色映射**：深蓝 → 蓝 → 紫 → 红（密度由低到高）
- **Tooltip 格式**：`周二 14:00\n提交次数: 5`
- **接口**：`GET /api/stats/heatmap`

#### 2.3.5 评审参与度雷达图
- **需求编号**：V-005
- **图表类型**：雷达图（ECharts Radar）
- **评估维度**（每人 5 项）：
  - 评论数量（review_comments_count / commits × 20）
  - 参与率（有提交天数 / 30 × 100）
  - 响应速度（基于评论数反推）
  - 代码贡献（净增行数 / 100）
  - 提交频率（提交次数 / 30 × 100）
- **展示上限**：Top 5 成员
- **接口**：`GET /api/stats/radar`

#### 2.3.6 成员详情表格
- **需求编号**：V-006
- **展示字段**：成员名、提交次数、新增行数、删除行数、净行数、异常标签
- **交互**：支持排序、异常高亮
- **数据来源**：`GET /api/stats/code` + `GET /api/stats/anomalies`

#### 2.3.7 异常检测报告
- **需求编号**：V-007
- **检测类型**：
  | 异常类型 | 检测逻辑 | 严重程度 |
  |---------|---------|---------|
  | 深夜高频提交 | 0-6 点或 23-24 点提交 > 10 次，且占峰值 30% 以上 | medium / high |
  | 零评审提交 | 非自动化提交中 review_comments_count == 0 的 > 20 次 | low |
  | 大文件删除 | deletions > 1000 且 additions < 100 | medium |
  | 趋势下降 | 最近 7 天均值 < 前 7 天均值 × 50% | warning |
- **接口**：`GET /api/stats/anomalies`

---

### 2.4 数据导出层

#### 2.4.1 CSV 导出（提交明细）
- **接口**：`GET /api/export/csv`
- **参数**：start_date, end_date
- **输出**：包含所有 commit 字段的 CSV 文件

#### 2.4.2 CSV 导出（成员统计）
- **接口**：`GET /api/export/members/csv`
- **参数**：start_date, end_date
- **输出**：按作者聚合的提交次数、新增/删除/净行数、平均每提交行数

#### 2.4.3 打印报表
- **功能**：点击「打印报表」按钮，隐藏控制面板，调整图表尺寸，适配 A4 纸输出
- **实现**：CSS `@media print` 媒体查询 + `window.print()`

---

## 3. 业务流程

### 3.1 首次数据初始化流程
```
[用户打开页面] → [选择数据源]
    │
    ├─→ [点击"生成模拟数据"] → [后端生成 2000 条模拟数据] → [仪表盘展示]
    │
    ├─→ [点击"导入数据"] → [上传 Git Log 文件 或 粘贴 JSON]
    │      → [前端解析/标准化] → [POST /api/commits/upload/*] → [后端去重入库]
    │      → [提示"成功导入 X 条提交记录"] → [仪表盘展示]
    │
    └─→ [点击"仓库管理"] → [添加本地/GitHub/GitLab 配置]
           → [点击"同步"] → [后端拉取最近 90 天提交] → [去重入库]
           → [仪表盘展示真实数据]
```

### 3.2 日常监控分析流程
```
[用户选择日期范围] → [7天/30天/90天/自定义]
    │
    → [输入搜索关键词（可选）] → [500ms 防抖实时触发]
    │
    → [前端并行调用 6 个 /api/stats/* 接口]
    │
    → [KPI 卡片刷新]
    → [趋势图刷新 + 下降预警检测]
    → [代码量柱状图刷新]
    → [热力图刷新 + 深夜异常标记]
    → [雷达图刷新]
    → [异常报告表格刷新]
```

### 3.3 异常排查流程
```
[热力图/成员表/异常报告发现异常标记]
    │
    → [点击查看异常详情]
    │
    → [调整日期范围缩小排查范围]
    │
    → [通过搜索框过滤作者或 Commit Message]
    │
    → [导出 CSV 审计明细]
    │
    → [联系相关开发者确认/整改]
```

### 3.4 增量同步流程
```
[用户进入仓库管理] → [查看现有配置列表]
    │
    → [选择单条配置点击"同步"] 或 [点击"全部同步"]
    │
    → [后端调用 GitPython/PyGithub/requests 拉取数据]
    │
    → [解析提交记录 → 字段映射 → 自动化检测]
    │
    → [create_commits_bulk 去重入库]
    │
    → [更新 last_sync_at 时间戳]
    │
    → [前端仪表盘自动刷新]
```

---

## 4. 用户场景

### 场景 1：新团队接入代码活跃度监控
> **角色**：研发经理  
> **背景**：新成立的 10 人前端团队，需要建立代码产出基线  
> **操作步骤**：
> 1. 打开 CodePulse，点击「仓库管理」
> 2. 添加 GitHub 仓库配置，粘贴 Personal Access Token
> 3. 选择主分支 `main`，点击「同步」
> 4. 查看 KPI 卡片确认已导入数据
> 5. 设置日期范围为「最近 30 天」，观察团队提交趋势
> 6. 检查热力图，发现周末有 2 名成员深夜提交，进一步确认是否为自动化脚本
> 7. 导出成员统计 CSV，作为周报附件发送给上级

### 场景 2：识别虚假高产出
> **角色**：QA 审计人员  
> **背景**：季度考核前，需要验证某成员的代码产出真实性  
> **操作步骤**：
> 1. 在成员详情表格中定位该成员，发现「大文件删除」异常标签
> 2. 点击异常报告，查看详情："删除了 3 个大文件，共计 5000+ 行"
> 3. 通过搜索框过滤该作者，查看具体 commit message
> 4. 发现删除的是 `node_modules` 和 `package-lock.json`
> 5. 在绩效考核中排除该行数统计，要求补充实际功能代码产出

### 场景 3：趋势下降预警响应
> **角色**：技术 Lead  
> **背景**：Sprint 中期，发现团队提交频率明显下滑  
> **操作步骤**：
> 1. 打开趋势图，发现红色「下降预警」标记
> 2. 查看 decline_dates，确认最近 7 天提交量下降 60%
> 3. 通过代码量柱状图对比，发现主力开发者 A 的新增行数从 500/天降至 50/天
> 4. 通过搜索框过滤开发者 A，查看其最近 commit message，发现大量 "WIP"、"fix typo"
> 5. 私下沟通得知该成员被阻塞在等待后端接口，协调资源解除阻塞

### 场景 4：审计合规检查
> **角色**：合规审计员  
> **背景**：需要证明关键代码变更都经过评审  
> **操作步骤**：
> 1. 设置日期范围为审计周期（如 Q2）
> 2. 查看异常报告，筛选「零评审提交」类型
> 3. 导出提交明细 CSV，按 `review_comments_count == 0` 过滤
> 4. 发现 30% 的提交没有评审评论，且未标记为自动化
> 5. 向团队发出整改通知，要求配置强制 Code Review 流程

### 场景 5：个人开发者自评
> **角色**：后端开发工程师  
> **操作步骤**：
> 1. 在雷达图中找到自己的名字
> 2. 发现「评论数量」维度得分较低（仅 15/100）
> 3. 查看代码量柱状图，自己的新增行数排名靠后
> 4. 调整工作习惯，在提交 PR 时增加详细注释，主动参与他人代码评审
> 5. 一个月后重新查看雷达图，评论数量维度提升至 60/100

### 场景 6：多仓库统一管理
> **角色**：DevOps 工程师  
> **背景**：公司有 5 个微服务仓库，需要统一监控  
> **操作步骤**：
> 1. 在仓库管理中添加 5 个 GitLab 仓库配置，使用同一个 Group Token
> 2. 为每个仓库配置不同的分支（如 `develop`、`main`）
> 3. 点击「全部同步」，一次性拉取所有仓库最近 90 天数据
> 4. 在仪表盘查看聚合后的团队 KPI，发现 3 号仓库提交量异常低
> 5. 进一步查看该仓库的异常报告，发现长期零评审提交，推动配置 MR 强制评审

---

## 5. 非功能需求

### 5.1 性能需求
- 前端页面首屏加载时间 < 2 秒（Vite 构建优化）
- 数据筛选后 6 个统计接口并行响应时间 < 1 秒（单表查询，SQLite 足够）
- 导出 CSV 支持 10,000 条记录流式生成，不占用大量内存

### 5.2 兼容性需求
- 支持 Chrome、Edge、Firefox、Safari 最新 2 个版本
- 后端兼容 Python 3.7+（生产环境使用 Python 3.7）
- 前端不支持 IE

### 5.3 安全需求
- GitHub/GitLab Access Token 存储在本地 SQLite 中，明文存储（当前实现），建议后续升级为加密存储
- 后端配置 CORS，仅允许前端域名访问
- 文件上传限制为 `.txt`、`.log`、`.csv`，防止恶意文件执行

### 5.4 可扩展性需求
- 统计计算逻辑通过 `StatsCalculator` 统一注入，新增统计维度只需扩展该类和新端点
- 新增数据源（如 Gitee、Bitbucket）可通过新增 `RemoteGitService` 子类实现
- 前端图表组件通过 ECharts option 对象配置，新增图表类型成本低

---

## 6. 附录

### 6.1 API 端点清单
| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 提交 | `/api/commits/upload` | POST | 单条提交上传 |
| 提交 | `/api/commits/upload/bulk` | POST | 批量提交上传 |
| 提交 | `/api/commits/upload/git-log` | POST | Git Log 文件解析上传 |
| 提交 | `/api/commits/upload/json` | POST | JSON 粘贴导入 |
| 提交 | `/api/commits/` | GET | 查询提交列表（分页/过滤） |
| 提交 | `/api/commits/all` | DELETE | 清空所有提交 |
| 统计 | `/api/stats/kpi` | GET | KPI 概览 |
| 统计 | `/api/stats/trend` | GET | 趋势图数据 |
| 统计 | `/api/stats/code` | GET | 代码量统计 |
| 统计 | `/api/stats/heatmap` | GET | 热力图数据 |
| 统计 | `/api/stats/radar` | GET | 雷达图数据 |
| 统计 | `/api/stats/anomalies` | GET | 异常检测报告 |
| 导出 | `/api/export/csv` | GET | 导出提交 CSV |
| 导出 | `/api/export/members/csv` | GET | 导出成员统计 CSV |
| 同步 | `/api/sync/configs` | GET/POST | 仓库配置 CRUD |
| 同步 | `/api/sync/sync/{id}` | POST | 单仓库同步 |
| 同步 | `/api/sync/sync-all` | POST | 全仓库同步 |
| 模拟 | `/api/mock/generate` | POST | 生成模拟数据 |

### 6.2 数据库 ER 图
```
[commits] 1 ──── N [members]  (逻辑关联，无物理外键)
[commits] 1 ──── N [repository_configs]  (逻辑关联，repository 字段)
[teams] 1 ──── N [members]  (预留，当前未使用)
```

### 6.3 部署架构
```
[ Nginx ]  ←── 静态文件 (frontend/dist)
    │
    └── /api → [Gunicorn + Uvicorn Workers] → [FastAPI App] → [SQLite]
```

---

*本文档由 Claude Code 基于 CodePulse 项目代码分析生成，涵盖完整的产品功能需求、业务流程和用户场景。*