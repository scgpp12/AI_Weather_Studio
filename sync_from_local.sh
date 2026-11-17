#!/bin/bash
# 把本机两个工作目录同步进仓库（只拷文字、脚本、图片；不拷视频和模型）
# 用法：在仓库根目录 bash sync_from_local.sh
set -e
SRC=/c/Users/sons/Downloads/ClaudeUsers
for d in 天气预报_AIWeatherStudio 人物视频资源库; do
  mkdir -p "$d"
  (cd "$SRC/$d" && find . -type f \( -iname '*.md' -o -iname '*.py' -o -iname '*.sh' -o -iname '*.json' -o -iname '*.jsonl' -o -iname '*.txt' -o -iname '*.jpg' -o -iname '*.png' -o -iname '*.webp' \) -size -50M -print0) \
  | while IFS= read -r -d '' f; do mkdir -p "$d/$(dirname "$f")"; cp -p "$SRC/$d/$f" "$d/$f"; done
done
echo "synced"

PYTHONUTF8=1 python redact.py
