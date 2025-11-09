#!/usr/bin/env bash
# backend/run_dev.sh
export PYTHONPATH="${PYTHONPATH}:./"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
