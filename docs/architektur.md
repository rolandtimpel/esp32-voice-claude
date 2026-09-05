# Architektur (Phase 1)

```
┌─────────────────────────────┐        WLAN, WebSocket (Opus-Audio)
│  SpotPear ESP32-S3-1.28"-AI │  <────────────────────────────────────┐
│  (xiaozhi-esp32 Firmware)   │                                       │
│  - Wake-Word-Erkennung      │                                       │
│  - Mikrofon (INMP441)       │                                       ▼
│  - Lautsprecher (MAX98357A) │                         ┌───────────────────────────┐
│  - 240x240 rundes LCD:      │                         │ xiaozhi-esp32-server        │
│    animiertes Emotions-     │                         │ (Docker, selbstgehostet)   │
│    Gesicht (Augen/Mund)     │                         │  - VAD, ASR (FunASR lokal) │
└─────────────────────────────┘                         │  - LLM-Provider-Plugin:    │
                                                          │    AnthropicLLM.py ───────┼──▶ api.anthropic.com
                                                          │  - TTS (EdgeTTS)           │    (Claude API,
                                                          └───────────────────────────┘     dein API-Key)
```

## Warum diese Aufteilung

- **Firmware (xiaozhi-esp32):** wird für dieses Board bereits offiziell mitgeliefert
  (Board-Profil in `idf.py menuconfig`). Wake-Word, Audio-Streaming und das
  animierte Emotions-Gesicht sind vorhanden - nichts davon muss neu gebaut werden.
- **Server (xiaozhi-esp32-server):** übernimmt die schwere Pipeline-Arbeit
  (Sprache-zu-Text, Gesprächsverlauf, Text-zu-Sprache) und ist so gebaut, dass
  sich einzelne Bausteine (insbesondere das LLM) austauschen lassen.
- **`server/overlay/AnthropicLLM/`:** unser einziger eigener Code auf der
  Server-Seite - ein LLM-Provider-Plugin, das die Anthropic Messages API
  anstelle der eingebauten OpenAI/Qwen/DeepSeek-Anbieter anspricht. Alles
  andere kommt unverändert aus dem Upstream-Projekt.

## Kein Home Assistant in Phase 1

Der Server läuft komplett eigenständig (Docker, kein HA-Zugriff). Phase 2
(Smart-Home-Steuerung) wird später ein separates Thema - vermutlich über
Function-Calling/Tools im LLM-Provider oder eine ESPHome-Voice-Satellite-
Anbindung, aber das ist bewusst noch nicht Teil dieses Repos.

## Was Claude nicht kann

Claude ist ein reines Text-Modell - kein Spracherkennung (STT) und keine
Sprachsynthese (TTS). Deshalb bleiben ASR (FunASR, lokal, kostenlos) und TTS
(EdgeTTS, kostenlos) im Server unabhängig vom LLM konfiguriert und lassen
sich bei Bedarf gegen Cloud-Dienste (z.B. Deepgram, ElevenLabs) tauschen -
dazu einfach `selected_module.ASR`/`TTS` und den jeweiligen Provider-Block
in `server/overlay/config.template.yaml` anpassen.
