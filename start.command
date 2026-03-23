#!/usr/bin/env bash
# macOS 双击启动 - 会自动打开 Terminal 执行 start.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/start.sh"
