#!/bin/bash
set -e

echo "=== 安装前端依赖 ==="
npm install

echo "=== 安装后端 Node.js 依赖 ==="
cd server && npm install && cd ..

echo "=== 安装后端 Python 依赖 ==="
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo "=== 全部依赖安装完成 ==="
