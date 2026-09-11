#!/usr/bin/env python3
"""Entrypoint wrapper: reads Home Assistant add-on options (/data/options.json)
and exports them as the same environment variables entrypoint.sh expects, so
the exact same image works both as a plain docker-compose service (.env) and
as a Home Assistant add-on (Konfiguration-Tab) without any duplicated logic.
Outside the add-on (no options.json present) this is a no-op passthrough.
"""
import json
import os

OPTIONS_FILE = "/data/options.json"

OPTION_TO_ENV = {
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "anthropic_model": "ANTHROPIC_MODEL",
    "anthropic_workspace_id": "ANTHROPIC_WORKSPACE_ID",
    "groq_api_key": "GROQ_API_KEY",
    "tts_voice": "TTS_VOICE",
    "lan_ip": "LAN_IP",
}

if os.path.exists(OPTIONS_FILE):
    with open(OPTIONS_FILE, encoding="utf-8") as f:
        options = json.load(f)
    for option_key, env_key in OPTION_TO_ENV.items():
        value = options.get(option_key)
        if value:
            os.environ[env_key] = str(value)
    os.environ.setdefault("WS_PORT", "8000")
    os.environ.setdefault("HTTP_PORT", "8003")

os.execv("/entrypoint.sh", ["/entrypoint.sh", "python", "app.py"])
