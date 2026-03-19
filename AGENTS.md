# AGENTS.md - NovelAS-Universal

## 这个项目是什么

**NovelAS-Universal 是一个 AI 辅助小说创作系统**，不是常规的软件工程项目。

用户用它来写小说——具体来说是日式轻小说（ライトノベル）。系统提供：
- 章节撰写、润色、去 AI 味
- 人物/势力/世界观设定库管理（lore database）
- 情节记忆与逻辑验证（防止前后矛盾）
- 文风分析、大纲生成、批量处理

**当你在这个仓库里写代码时，你是在为一个小说创作者服务。** 所有功能改动都应该服务于"让 AI 更好地辅助写小说"这个目标。

## Project Overview

系统由多个组件构成：
- **Backend**: Python 3.11+ / FastAPI REST API
- **Frontend**: React 18 / TypeScript / Vite 管理界面
- **MCP Server**: Model Context Protocol 服务器，暴露小说创作工具给 Claude/Gemini
- **Skill System**: 声明式 YAML/MD skill 定义，指导 AI 如何执行写作任务
- **Vector Memory**: ChromaDB + sentence-transformers，用于情节语义检索

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, Pydantic v2, pydantic-settings, ChromaDB, sentence-transformers
- Frontend: React 18, TypeScript 5.6, Vite 6, Tailwind CSS v4, Zustand, React Query, Axios
- MCP: `mcp` Python SDK (FastMCP), stdio transport
- AI Providers: OpenAI, Anthropic, Gemini, local models (pluggable via `backend/services/`)

## Build / Dev / Test Commands

### Start the full application
```bash
start.bat              # Windows: starts backend + frontend
```

### Backend (Python)
```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install -e ".[dev]"     # dev extras (pytest, httpx)
pip install -e ".[mcp]"     # MCP server support

# Run dev server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run MCP server (for Claude/Gemini integration)
python -m backend.mcp.server

# Run tests (pytest is a dev dependency)
pytest                       # all tests
pytest tests/test_foo.py     # single file
pytest tests/test_foo.py::test_bar -v   # single test

# Type checking (no tool configured; use mypy manually if needed)
mypy backend/
```

### Frontend (TypeScript)
```bash
cd frontend

# Install dependencies
npm ci    # if package-lock.json exists
npm install

# Dev server (Vite, port 5173, proxies /api to backend)
npm run dev

# Production build (tsc + vite build)
npm run build

# Preview production build
npm run preview

# Type checking
npx tsc --noEmit
```

### MCP Server
The backend includes an MCP (Model Context Protocol) server at `backend/mcp/server.py`
for tool-based AI integration. It provides tools for chapter management, lore operations,
vector memory queries, and document conversion.

Configured in `.mcp.json` and `.gemini/settings.json` for Claude Code and Gemini CLI.

## Project Structure

```
NovelAS-Universal/
├── backend/
│   ├── api/           # FastAPI route handlers (REST endpoints)
│   ├── core/          # Business logic managers (project, chapter, lore, job, knowledge)
│   ├── models/        # Pydantic request/response models
│   ├── services/      # External integrations (AI providers, vector memory, skill executor)
│   ├── utils/         # Helpers (logging, git ops, docx converter, importer)
│   ├── mcp/           # MCP server for tool integration
│   ├── config.py      # Pydantic BaseSettings (env prefix: NOVELAS_)
│   └── main.py        # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── api/       # Axios client and API functions
│       ├── components/# React components (Chapter, Dashboard, Layout, Lore, Project)
│       ├── pages/     # Route page components
│       ├── store/     # Zustand state stores
│       ├── types/     # TypeScript interfaces
│       └── hooks/     # Custom React hooks (currently empty)
├── shared/
│   └── skill_definitions/  # YAML/MD skill definitions for AI
│       └── novel-assistant/ # Main novel-writing skill with references/
├── .claude/
│   └── commands/      # Claude Code slash commands (skill definitions)
├── .gemini/
│   └── skills/        # Gemini CLI skill definitions
├── knowledge/         # Project-agnostic knowledge files
├── projects/          # Per-project data (chapters, lore, drafts)
├── pyproject.toml
└── start.bat
```

## Skill System & MCP Tools

### Skill Definitions
Skills are defined in `shared/skill_definitions/` and mirrored to `.claude/commands/` and
`.gemini/skills/`. The main skill is **novel-assistant** which covers 14 writing capabilities:
writing, polishing, outlining, lore management, style analysis, plot verification, etc.

Key skill files:
- `shared/skill_definitions/novel-assistant/SKILL.md` — Main skill definition with routing table
- `shared/skill_definitions/novel-assistant/references/writing-workflow.md` — Writing pipeline
- `shared/skill_definitions/novel-assistant/references/lore-management.md` — Lore CRUD operations
- `shared/skill_definitions/novel-assistant/references/analysis-tools.md` — Style/plot analysis
- `shared/skill_definitions/novel-assistant/references/memory-tools.md` — Vector memory operations

### MCP Tools (provided by `backend/mcp/server.py`)
| Tool | Purpose |
|---|---|
| `read_chapter_content` | Read chapter text |
| `save_chapter_draft` | Save chapter draft |
| `list_chapters` | List all chapters in a volume |
| `get_lore_snapshot` | Get lightweight lore overview |
| `get_entry_details` | Get full lore entry details |
| `search_lore` | Full-text search lore database |
| `propose_patch` | Stage lore changes (Propose-Commit pattern) |
| `commit_patch` | Apply staged lore changes |
| `query_plot_memory` | Semantic search in vector memory |
| `store_plot_memory` | Store plot memory entry |
| `update_knowledge_file` | Save/update knowledge files |
| `convert_markdown_to_docx` | Convert MD to DOCX |
| `batch_convert_markdown_to_docx` | Batch convert MD to DOCX |
| `calculate_chapter_batches` | Split chapters into processing batches |
| `claim_next_batch` | Get next batch for job processing |

### Key Patterns
- **Propose-Commit**: All lore modifications must go through propose → review → commit flow
- **Interactive Review**: All generated content must be shown to user before saving
- **Job Routing**: Long-running batch tasks use `calculate_chapter_batches` + `claim_next_batch`
- **Lore Compliance**: Before writing, extract entity names and verify against lore database
- **Anti-AI Detection**: Polish output must remove AI writing patterns (parallel structures, clichés)

## Code Style Guidelines

### Python (Backend)

**Naming:**
- snake_case for variables, functions, methods, modules
- PascalCase for classes
- UPPER_SNAKE for constants
- Prefix private attributes with `_`

**Types:**
- Use Python 3.11+ type hints everywhere: `list[str]`, `dict[str, Any]`, `str | None`
- Use `Path` from `pathlib` for all file paths
- Pydantic v2 models for all request/response schemas
- Use `BaseSettings` from `pydantic-settings` for configuration

**Imports:**
- Group: stdlib → third-party → local, separated by blank lines
- Use absolute imports: `from backend.models.chapter import ChapterContent`
- Lazy imports inside functions when importing heavy dependencies (e.g., sentence-transformers)

**Error Handling:**
- Raise specific exceptions (`FileNotFoundError`, `FileExistsError`)
- Catch and convert to HTTPException in API handlers with appropriate status codes
- Use structured logging via `backend.utils.logging_config.logger`

**Patterns:**
- All API routes use `APIRouter` with prefix and tags
- Response models declared via `response_model=` parameter
- Manager classes in `core/` handle business logic; services handle external APIs
- Use `async` for I/O-bound endpoints; sync functions are acceptable for pure file I/O

### TypeScript (Frontend)

**Naming:**
- camelCase for variables, functions, methods
- PascalCase for components, interfaces, types
- UPPER_SNAKE for constants

**Types:**
- Define interfaces in `src/types/index.ts` — mirror backend Pydantic models
- Avoid `any`; use `unknown` or proper types. The `api/client.ts` has some `any` — prefer typed alternatives
- Use `Record<string, unknown>` instead of `Record<string, any>`

**Components:**
- Functional components with default export
- One component per file; filename matches component name (PascalCase)
- Pages in `src/pages/`, reusable components in `src/components/`

**State Management:**
- Zustand for global state (`src/store/`)
- React Query (`@tanstack/react-query`) for server state (API data fetching)
- Persist user preferences with Zustand `persist` middleware

**Styling:**
- Tailwind CSS v4 with CSS custom properties defined in `src/styles.css`
- Dark theme is the default; use CSS variables (`--color-bg-primary`, `--color-text-primary`, etc.)
- Animation classes: `animate-fade-in-up`, `animate-fade-in`, `animate-glow`

**API Layer:**
- All API calls go through `src/api/client.ts` using Axios
- Base URL is `/api`; Vite proxies to backend at port 8000
- Use `.then(r => r.data)` pattern for response unwrapping

### General Rules

- No comments unless asked — code should be self-documenting
- Docstrings in Python: one-line for simple functions, multi-line for complex ones
- Keep files focused: one responsibility per module
- Run `npx tsc --noEmit` after frontend changes
- Run `pytest` after backend changes
- Environment variables use `NOVELAS_` prefix (e.g., `NOVELAS_DEBUG=true`)

### Chapter Naming Convention
Files follow strict naming: `Chapter.001.md`, `Interlude.000.md`, `Extra.000.md`, `Prologue.md`, `Finale.md`
- Stored in `chapters/vol{N}/` for volume-specific, `chapters/extras/` for extras
- Defined in `backend/core/naming.py` with `ChapterId` dataclass and `ChapterType` enum
