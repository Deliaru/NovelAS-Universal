# NovelAS-Universal

AI 辅助轻小说创作系统，基于 MCP 的设定库管理系统。

## 功能特性

- 章节撰写、润色、去 AI 味
- 人物/势力/世界观设定库管理（lore database）
- 情节记忆与逻辑验证（防止前后矛盾）
- 文风分析、大纲生成、批量处理
- 支持日式轻小说文风（日轻风）

## 技术栈

- **Backend**: Python 3.11+ / FastAPI / Pydantic v2 / ChromaDB
- **Frontend**: React 18 / TypeScript / Vite 6 / Tailwind CSS v4
- **MCP Server**: Model Context Protocol 服务器，暴露小说创作工具给 AI
- **Vector Memory**: ChromaDB + sentence-transformers，用于情节语义检索

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm

### 安装

```bash
# 克隆仓库
git clone https://github.com/Deliaru/NovelAS-Universal.git
cd NovelAS-Universal

# 安装后端依赖
pip install -e ".[dev]"
pip install -e ".[mcp]"

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 启动

**Windows**:
```bash
start.bat
```

**手动启动**:
```bash
# 后端
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 前端（新终端）
cd frontend
npm run dev
```

访问 http://localhost:5173

## MCP 集成

项目包含 MCP 服务器，可与 Claude Code 或其他支持 MCP 的 AI 工具集成。

配置文件 `opencode.json` 已预配置，启动后可直接使用 MCP 工具。

## 项目结构

```
NovelAS-Universal/
├── backend/          # Python/FastAPI 后端
│   ├── api/          # REST API 路由
│   ├── core/         # 业务逻辑
│   ├── models/       # Pydantic 数据模型
│   ├── services/     # 外部服务集成
│   ├── utils/        # 工具函数
│   └── mcp/          # MCP 服务器
├── frontend/         # React/TypeScript 前端
│   └── src/
├── knowledge/        # 创作技巧文档
├── projects/         # 用户项目数据（git 忽略）
├── data/             # 数据库和模型（git 忽略）
└── start.bat         # 一键启动脚本
```

## 许可证

MIT
