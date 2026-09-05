#!/bin/sh
set -eu

TEMPLATE=/opt/xiaozhi-esp32-server/data/.config.yaml.template
TARGET=/opt/xiaozhi-esp32-server/data/.config.yaml

if [ ! -f "$TARGET" ]; then
  : "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY ist nicht gesetzt. Trage ihn in server/.env ein (siehe .env.example).}"
  : "${LAN_IP:?LAN_IP ist nicht gesetzt. Trage die LAN-IP dieses Docker-Hosts in server/.env ein (das Board muss den Server im WLAN erreichen).}"

  export ANTHROPIC_API_KEY
  export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-claude-sonnet-5}"
  export LAN_IP
  export WS_PORT="${WS_PORT:-8000}"
  export HTTP_PORT="${HTTP_PORT:-8003}"
  export TTS_VOICE="${TTS_VOICE:-de-DE-KatjaNeural}"
  export ASR_LANGUAGE="${ASR_LANGUAGE:-auto}"

  envsubst < "$TEMPLATE" > "$TARGET"
  echo "[entrypoint] data/.config.yaml aus Umgebungsvariablen erzeugt."
else
  echo "[entrypoint] data/.config.yaml existiert bereits (persistentes Volume) - wird unverändert verwendet."
  echo "[entrypoint] Um Änderungen an server/.env zu übernehmen: Datei/Volume löschen und Container neu starten."
fi

exec "$@"
