# ESP32 Voice Claude - Home-Assistant-Add-on

Läuft komplett unabhängig von deiner Home-Assistant-Konfiguration (keine
Entities, keine Automationen, keine Integration) - nutzt dein
Home-Assistant-Gerät nur als dauerhaft laufenden Hosting-Platz für den
Sprach-KI-Server.

## Einrichtung

1. **Anthropic-API-Key** besorgen: https://console.anthropic.com/settings/keys
2. Falls dein Key organisationsweit ist (nicht direkt einem Workspace
   zugeordnet): die Workspace-ID unter
   https://console.anthropic.com/settings/workspaces eintragen. Bei einem
   privaten Account meist leer lassen.
3. **Groq-API-Key** besorgen (kostenlos, für die Spracherkennung):
   https://console.groq.com
4. Im **Konfiguration**-Tab dieses Add-ons ausfüllen:
   - `anthropic_api_key` - dein Anthropic-Key
   - `anthropic_model` - Standard `claude-sonnet-5`, i.d.R. unverändert lassen
   - `anthropic_workspace_id` - nur falls Schritt 2 nötig war, sonst leer
   - `groq_api_key` - dein Groq-Key
   - `tts_voice` - Stimme für die Sprachausgabe, Standard
     `de-DE-KatjaNeural` (andere Stimmen: `edge-tts --list-voices`)
   - `lan_ip` - die LAN-IP **dieses Home-Assistant-Geräts** (nicht deines
     Computers!) - unter Home Assistant: Einstellungen → System → Netzwerk,
     oder in deiner Router-Oberfläche nachsehen
5. Add-on **starten**
6. In der Firmware (`idf.py menuconfig` bzw. `sdkconfig.defaults`) die
   OTA-URL auf `http://<lan_ip>:8003/xiaozhi/ota/` setzen, wobei `<lan_ip>`
   dieselbe Adresse wie oben ist - siehe Haupt-Repo,
   [`docs/firmware.md`](https://github.com/rolandtimpel/esp32-voice-claude/blob/main/docs/firmware.md)

## Ports

- `8000` - WebSocket, hier verbindet sich das ESP32-Board
- `8003` - HTTP (OTA-Check, Vision-Endpunkt)

## Logs

Übers **Protokoll**-Tab dieses Add-ons einsehbar - hilfreich, um zu prüfen,
ob sich das Board erfolgreich verbindet.
