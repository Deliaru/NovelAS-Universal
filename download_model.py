"""
手动下载 MiniLM 模型到本地 data 目录的脚本
如果 HuggingFace 连接有问题，可以使用镜像源
"""

import os
from pathlib import Path

# 设置镜像源（可选）
# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from huggingface_hub import snapshot_download

# 模型配置
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_DIR = Path(__file__).parent / "data" / "models" / "all-MiniLM-L6-v2"

print(f"开始下载模型: {MODEL_NAME}")
print(f"目标目录: {LOCAL_DIR}")

LOCAL_DIR.mkdir(parents=True, exist_ok=True)

try:
    snapshot_download(
        repo_id=MODEL_NAME,
        local_dir=str(LOCAL_DIR),
        local_dir_use_symlinks=False,
        resume_download=True,
    )
    print(f"\n✓ 模型下载成功！")
    print(f"  位置: {LOCAL_DIR}")
except Exception as e:
    print(f"\n✗ 下载失败: {e}")
    print("\n如果遇到网络问题，可以尝试：")
    print("1. 使用镜像源：取消注释脚本中的 HF_ENDPOINT 设置")
    print("2. 手动下载：访问 https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2")
    print(f"   然后将文件放到: {LOCAL_DIR}")
