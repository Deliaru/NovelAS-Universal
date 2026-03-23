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

**macOS（推荐）**:
```bash
# 终端执行
bash start.sh

# 或双击 start.command（会自动打开 Terminal）
```
首次运行会自动创建 Python 虚拟环境并安装所有依赖，耐心等待即可。

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

## 使用指南

### 方式一：自然语言对话（推荐）

在项目根目录启动 OpenCode 后，直接用自然语言描述你的需求，AI 会自动调用对应的创作工具。

**示例对话**：

```
用户：帮我写第二卷第五章
AI：自动加载章纲、文风范本，逐场景撰写并展示

用户：润色这一段，去一下AI味
AI：自动进行文风分析和润色修改

用户：帮我完善主角的人物设定
AI：自动读取相关章节，提取新细节并更新设定库

用户：检查一下最新剧情有没有逻辑矛盾
AI：自动查询情节记忆，验证逻辑一致性
```

**首次使用**：直接对 AI 说"请介绍一下你的功能和使用方法"，AI 会引导你完成初始设置。

### 方式二：通过关键词触发

系统会根据关键词自动识别并加载对应的创作能力：

| 关键词 | 触发的能力 |
|--------|------------|
| 写章节 / draft / 草稿 | 撰写章节 |
| 润色 / polish / 去AI味 / 校对 | 润色章节 |
| 大纲 / outline / 故事弧 | 创建大纲 |
| 章纲 / 细纲 / scene outline | 创建章纲 |
| 人物设定 / character lore | 完善人物设定 |
| 势力设定 / faction lore | 完善势力设定 |
| 世界观 / worldview | 完善世界观设定 |
| 审计 / 一致性检查 | 设定一致性审计 |
| 文风分析 / analyze style | 分析写作风格 |
| 逻辑验证 / 剧情检查 | 验证剧情逻辑 |
| 版本对比 / diff review | 章节版本对比 |
| 记忆构建 / build memory | 构建情节记忆 |
| 故事回顾 / recap | 生成叙事回顾 |

### 核心工作流程

1. **撰写新章节**：AI 会自动加载章纲 → 文风范本 → 设定预检 → 逐场景撰写 → 质检润色
2. **润色修改**：AI 会分析文风问题 → 消除 AI 味 → 保持设定一致 → 输出润色结果
3. **设定管理**：AI 会读取章节内容 → 提取新细节 → Propose-Commit 安全更新
4. **逻辑验证**：AI 会语义搜索情节记忆 → 检查矛盾 → 输出验证报告

### 安全机制

- **Propose-Commit**：所有设定修改必须经过人工确认才能提交
- **Interactive Review**：所有生成内容必须展示给用户确认后才保存
- **草稿自动保存**：撰写过程中自动保存草稿，防止上下文溢出

## MCP 集成

项目包含 MCP 服务器，可与 OpenCode、Claude Code 或其他支持 MCP 的 AI 工具集成。

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
