#!/usr/bin/env bash
set -e

# ──────────────────────────────────────────────
# NovelAS-Universal 一键启动脚本 (macOS / Linux)
# ──────────────────────────────────────────────

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 脚本所在目录
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT/.venv"
BACKEND_PID=""
FRONTEND_PID=""

# ── 工具函数 ──────────────────────────────────

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    echo ""
    log_info "正在停止服务..."
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    # 杀掉可能残留的子进程
    jobs -p | xargs -r kill 2>/dev/null || true
    log_info "已停止所有服务。"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ── 检查依赖 ──────────────────────────────────

echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}   NovelAS-Universal 一键启动${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

# 检查 Python
log_info "[1/5] 检查 Python..."
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    log_error "未找到 Python。请安装 Python 3.11+："
    log_error "  macOS: brew install python@3.11"
    log_error "  或从 https://www.python.org/downloads/ 下载"
    exit 1
fi

PY_VERSION=$("$PYTHON_CMD" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
    log_error "Python 版本过低: $PY_VERSION (需要 3.11+)"
    exit 1
fi
log_info "找到 Python $PY_VERSION ($PYTHON_CMD)"

# 检查 Node.js
log_info "[2/5] 检查 Node.js..."
if ! command -v node &>/dev/null; then
    log_error "未找到 Node.js。请安装 Node.js 18+："
    log_error "  macOS: brew install node"
    log_error "  或从 https://nodejs.org/ 下载"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//')
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 18 ]; then
    log_error "Node.js 版本过低: v$NODE_VERSION (需要 18+)"
    exit 1
fi
log_info "找到 Node.js v$NODE_VERSION"

# 检查 npm
if ! command -v npm &>/dev/null; then
    log_error "未找到 npm。请重新安装 Node.js。"
    exit 1
fi

# ── 安装依赖 ──────────────────────────────────

# Python 虚拟环境 + 依赖
log_info "[3/5] 检查 Python 依赖..."
if [ ! -d "$VENV_DIR" ]; then
    log_info "创建虚拟环境..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
fi

# 激活 venv
source "$VENV_DIR/bin/activate"

# 检查是否需要安装依赖
NEED_INSTALL=false
if ! python -c "import fastapi" &>/dev/null; then
    NEED_INSTALL=true
fi

if [ "$NEED_INSTALL" = true ]; then
    log_info "安装 Python 依赖（首次运行需要几分钟）..."
    pip install --upgrade pip -q
    pip install -r "$ROOT/backend/requirements.txt" -q
    log_info "Python 依赖安装完成。"
else
    log_info "Python 依赖已就绪。"
fi

# 前端依赖
log_info "[4/5] 检查前端依赖..."
cd "$ROOT/frontend"
FRONTEND_NEED_INSTALL=false
if [ ! -d "node_modules" ]; then
    FRONTEND_NEED_INSTALL=true
elif [ -f "node_modules/.bin/vite" ] && [ ! -x "node_modules/.bin/vite" ]; then
    log_warn "node_modules 权限异常（跨平台拷贝导致），正在重新安装..."
    rm -rf node_modules
    FRONTEND_NEED_INSTALL=true
fi

if [ "$FRONTEND_NEED_INSTALL" = true ]; then
    log_info "安装前端依赖（首次运行需要几分钟）..."
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    log_info "前端依赖安装完成。"
else
    log_info "前端依赖已就绪。"
fi
cd "$ROOT"

# ── 启动服务 ──────────────────────────────────

log_info "[5/5] 启动服务..."
echo ""

# 启动后端
log_info "启动后端 (http://127.0.0.1:8000)..."
"$VENV_DIR/bin/python" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等后端启动
sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    log_error "后端启动失败！请检查日志。"
    exit 1
fi

# 启动前端
log_info "启动前端 (http://localhost:5173)..."
cd "$ROOT/frontend"
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd "$ROOT"

# 等前端启动
sleep 3

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}   NovelAS-Universal 已启动！${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "  后端:  ${GREEN}http://127.0.0.1:8000/api/health${NC}"
echo -e "  前端:  ${GREEN}http://localhost:5173${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

# 打开浏览器
if command -v open &>/dev/null; then
    # macOS
    sleep 1
    open "http://localhost:5173"
elif command -v xdg-open &>/dev/null; then
    # Linux
    sleep 1
    xdg-open "http://localhost:5173" 2>/dev/null || true
fi

# 等待任意子进程退出
wait
