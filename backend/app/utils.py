# backend/app/utils.py
import json
from datetime import datetime

def now_iso():
    return datetime.utcnow().isoformat()

def json_dumps(obj):
    return json.dumps(obj, default=str)

