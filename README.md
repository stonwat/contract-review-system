# 合同审查系统（Contract Review System）

政企工程项目合同风控系统：通过 OCR + LLM 自动提取合同信息，自动完成前后项合同比对、毛利率计算、风险判定，生成统计报表。

## 技术栈

| 层 | 技术 |
|:---|:---|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Pydantic |
| 数据库 | PostgreSQL 16 |
| 文件存储 | MinIO（S3 兼容）|
| 任务队列 | Redis + arq |
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia + Vue Router + Vite |
| OCR | PaddleOCR（本地 Agent）|
| 容器化 | Docker Compose |

## 目录结构

```
contract-review-system/
├── backend/            # 后端 FastAPI
├── frontend/           # 前端 Vue 3
├── agent/              # 本地 Agent 脚本
├── specing-docs/       # 项目文档
├── docker-compose.yml  # 全服务编排
├── .env.example        # 环境变量模板
└── README.md
```

## 环境要求

| 软件 | 版本 |
|:---|:---|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 16 |
| Redis | 7+ |
| MinIO | latest |
| Docker | 24+（可选，用于一键编排）|

## 快速启动

### 1. 准备环境变量

```bash
cp .env.example .env
# 按需修改 .env 中的密码、密钥、LLM 配置
```

### 2. 启动依赖服务

```bash
docker compose up -d postgres minio redis
```

### 3. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
alembic upgrade head            # 执行数据库迁移
python -m app.main              # 启动服务，访问 http://localhost:8000/docs
```

### 4. 启动前端

```bash
cd frontend
pnpm install                    # 或 npm install
pnpm dev                        # 访问 http://localhost:5173
```

## 常用命令

| 命令 | 说明 |
|:---|:---|
| `docker compose up -d` | 启动全部服务（含 backend）|
| `docker compose up -d postgres minio redis` | 仅启动依赖 |
| `cd backend && alembic revision --autogenerate -m "msg"` | 生成迁移脚本 |
| `cd backend && alembic upgrade head` | 执行迁移 |
| `cd backend && ruff check .` | 后端代码检查 |
| `cd backend && mypy app` | 后端类型检查 |
| `cd frontend && pnpm dev` | 前端开发 |
| `cd frontend && pnpm build` | 前端构建 |

## 文档

所有文档位于 [`specing-docs/`](./specing-docs)，编号顺序为阅读顺序：

- `00.文档规范清单.md` — 文档总纲与规范
- `01.用户需求.md` — 原始业务需求
- `02.技术选型.md` — 技术选型与决策
- `03.需求规格说明书.md` — 功能详细规格
- `04.项目整体设计构思.md` — 架构与总纲设计
- `05.数据库设计文档.md` — 数据库设计
- `06.接口设计文档.md` — API 设计
- `07.前端设计文档.md` — 前端设计
- `08.工作流程描述.md` — 端到端流程

## 默认账号

首次初始化后通过脚本创建管理员：

```bash
cd backend
python -m app.scripts.create_admin --username admin --password <your_password>
```
