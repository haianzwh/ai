#!/bin/bash
cd /tmp/opencode/ai-chat/server
source .venv/bin/activate
exec uvicorn python_app.main:app --host 0.0.0.0 --port 3001
