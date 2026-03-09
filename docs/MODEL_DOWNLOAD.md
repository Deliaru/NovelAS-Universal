# MiniLM 模型下载指南

由于网络或 SSL 问题，自动下载可能失败。请按以下步骤手动下载模型：

## 方法 1: 使用 Git LFS (推荐)

```bash
# 1. 安装 Git LFS
# 访问 https://git-lfs.github.com/ 下载安装

# 2. 克隆模型仓库
cd D:\Work\NovelAS-Universal\data\models
git lfs install
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
```

## 方法 2: 使用浏览器下载

1. 访问 https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/main
2. 下载以下文件到 `D:\Work\NovelAS-Universal\data\models\all-MiniLM-L6-v2\`:
   - config.json
   - pytorch_model.bin
   - tokenizer_config.json
   - vocab.txt
   - special_tokens_map.json
   - tokenizer.json
   - modules.json
   - sentence_bert_config.json
   - config_sentence_transformers.json

## 方法 3: 使用 ModelScope (国内镜像)

```bash
pip install modelscope

python -c "from modelscope import snapshot_download; snapshot_download('AI-ModelScope/all-MiniLM-L6-v2', cache_dir='D:/Work/NovelAS-Universal/data/models')"
```

## 方法 4: 使用 HF-Mirror

```bash
# 设置环境变量
set HF_ENDPOINT=https://hf-mirror.com

# 运行下载脚本
python download_model.py
```

## 验证安装

下载完成后，确保目录结构如下：

```
D:\Work\NovelAS-Universal\data\models\all-MiniLM-L6-v2\
├── config.json
├── pytorch_model.bin
├── tokenizer_config.json
├── vocab.txt
├── special_tokens_map.json
├── tokenizer.json
├── modules.json
├── sentence_bert_config.json
└── config_sentence_transformers.json
```

然后重启后端服务即可。
