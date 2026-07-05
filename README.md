# CodePulse - 研发活跃度智能分析平台

CodePulse 是一个全栈研发效能分析工具，替代手工从 GitLab/GitHub 导出数据再处理的低效流程，通过可视化仪表盘直观展示团队提交频率、代码量构成、时段热力图及评审参与度等多维指标。

## 功能特性

- **数据导入**：支持上传 Git Log 文件、粘贴 JSON 数据，或一键生成 20+ 成员、近 3 个月的模拟数据
- **全局筛选**：时间范围（最近7天/30天/本季度/自定义）、成员、仓库、关键词搜索
- **核心仪表盘**：
  - KPI 概览卡片：总提交次数、净增代码行数、活跃开发者人数、平均评审响应时长
  - 提交频率趋势图：颜色标记活跃度下降时段，提示潜在阻塞
  - 代码量构成分析：区分新增/删除/净增行数，识别大文件删除带来的虚假高产出
  - 提交时段热力图：X轴小时、Y轴星期，标记深夜异常批量提交
  - 评审参与度雷达图：评论数量、参与率、响应速度、代码贡献、提交频率
- **详细报表**：成员列表展示提交数、代码行数、异常检测标记
- **数据导出**：支持 CSV 导出和浏览器打印优化

## 技术栈

### 后端
- Python 3.10+
- FastAPI + SQLAlchemy + SQLite
- Pandas / Openpyxl / APScheduler

### 前端
- React 18 + TypeScript
- Vite + TailwindCSS
- ECharts (echarts-for-react)
- Axios + Lucide React

## 快速开始

### 1. 克隆项目并启动后端

```bash
cd CodePulse/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 启动前端

```bash
cd CodePulse/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址：http://localhost:3000

### 3. 生成模拟数据

打开前端页面，点击「生成模拟数据」按钮，即可自动生成 2000 条近 3 个月的模拟提交记录，内置 25 位开发者数据。

## 项目结构

```
CodePulse/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI 路由
│   │   ├── services/         # 业务逻辑层
│   │   ├── main.py           # 入口文件
│   │   ├── models.py         # SQLAlchemy 模型
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── crud.py           # 数据库操作
│   │   └── database.py       # 数据库配置
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── services/api.ts   # API 封装
│   │   ├── types/index.ts    # TypeScript 类型
│   │   ├── App.tsx           # 主应用组件
│   │   └── index.css         # 全局样式
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 核心 API 说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/commits/upload/git-log` | POST | 上传 Git Log 文件 |
| `/api/commits/upload/json` | POST | 粘贴 JSON 数据 |
| `/api/commits/` | GET | 查询提交记录 |
| `/api/stats/kpi` | GET | KPI 概览 |
| `/api/stats/trend` | GET | 趋势图数据 |
| `/api/stats/code` | GET | 代码统计 |
| `/api/stats/heatmap` | GET | 热力图数据 |
| `/api/stats/radar` | GET | 雷达图数据 |
| `/api/stats/anomalies` | GET | 异常检测 |
| `/api/mock/generate` | POST | 生成模拟数据 |
| `/api/export/csv` | GET | 导出 CSV |

## 模拟数据字段

```json
{
  "commit_hash": "a1b2c3d4...",
  "author": "张伟",
  "email": "zhangwei@example.com",
  "date": "2024-01-15T09:30:00",
  "message": "feat: 新增用户权限管理模块",
  "additions": 120,
  "deletions": 20,
  "files_changed": 5,
  "review_comments_count": 3,
  "is_automated": false,
  "repository": "codepulse-backend",
  "branch": "main"
}
```

## 部署说明

### 生产环境部署

1. 使用 Gunicorn + Uvicorn 部署后端：
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. 构建前端静态文件：
```bash
npm run build
```

3. 使用 Nginx 托管前端 dist 目录，并代理 `/api` 请求到后端服务。

## 开发计划

- [x] 数据导入与模拟层
- [x] 全局控制面板（筛选器）
- [x] KPI 概览卡片
- [x] 提交频率趋势图
- [x] 代码量构成分析
- [x] 提交时段热力图
- [x] 评审参与度雷达图
- [x] 成员详细报表
- [x] 异常检测与标记
- [x] CSV 导出与打印优化
- [ ] GitLab/GitHub API 直接对接（需配置 Access Token）
- [ ] Excel / PDF 导出（openpyxl / WeasyPrint）
- [ ] 定时任务与邮件发送（APScheduler / Celery）

## 许可证

MIT