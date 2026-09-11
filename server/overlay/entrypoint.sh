#!/bin/sh
set -eu

TEMPLATE=/etc/xiaozhi-config.template.yaml
TARGET=/opt/xiaozhi-esp32-server/data/.config.yaml

mkdir -p "$(dirname "$TARGET")"

if [ ! -f "$TARGET" ]; then
  : "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY ist nicht gesetzt. Trage ihn in server/.env ein (siehe .env.example).}"
  : "${LAN_IP:?LAN_IP ist nicht gesetzt. Trage die LAN-IP dieses Docker-Hosts in server/.env ein (das Board muss den Server im WLAN erreichen).}"

  export ANTHROPIC_API_KEY
  export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-claude-sonnet-5}"
  export ANTHROPIC_WORKSPACE_ID="${ANTHROPIC_WORKSPACE_ID:-}"
  export LAN_IP
  export WS_PORT="${WS_PORT:-8000}"
  export HTTP_PORT="${HTTP_PORT:-8003}"
  export TTS_VOICE="${TTS_VOICE:-de-DE-KatjaNeural}"
  export GROQ_API_KEY="${GROQ_API_KEY:-}"

  envsubst < "$TEMPLATE" > "$TARGET"
  echo "[entrypoint] data/.config.yaml aus Umgebungsvariablen erzeugt."
else
  echo "[entrypoint] data/.config.yaml existiert bereits (persistentes Volume) - wird unverändert verwendet."
  echo "[entrypoint] Um Änderungen an server/.env zu übernehmen: Datei/Volume löschen und Container neu starten."
fi

exec "$@"
