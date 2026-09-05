# ESP32 Voice Claude

Eigenständiger Sprach-KI-Begleiter für den SpotPear ESP32-S3-1.28"-AI
("DeepSeek/XiaoZhi Voice Chat Robot Ball"): Wake-Word-Aktivierung, ein
animiertes Gesicht auf dem runden Display, das je nach Antwort reagiert, und
ein Gesprächspartner, der über die Anthropic Claude API antwortet.

**Phase 1** (dieses Repo): reine Sprach-KI, ohne Smart-Home-Anbindung.
Phase 2 (später, separat): Anbindung an Home Assistant.

Details zur Architektur: [`docs/architektur.md`](docs/architektur.md).

## Bausteine

1. **Firmware:** [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32)
   (offiziell unverändert, nur konfiguriert) - läuft auf dem Board, macht
   Wake-Word, Audio-Streaming und das Emotions-Gesicht.
2. **Server:** [`server/`](server) - Docker-Setup, das
   [xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server)
   selbst hostet, plus einen eigenen LLM-Provider
   ([`server/overlay/AnthropicLLM/`](server/overlay/AnthropicLLM/AnthropicLLM.py)),
   der Anthropic Claude statt der eingebauten Anbieter anspricht.

## Quickstart

### Server (auf einem Rechner/NAS in deinem Heimnetz, mit Docker)

```bash
cd server
cp .env.example .env
# .env öffnen: ANTHROPIC_API_KEY und LAN_IP eintragen
docker compose up -d --build
docker compose logs -f   # prüfen, dass der Server sauber hochkommt
```

Details/Hintergrund: [`docs/secrets.md`](docs/secrets.md) (Umgang mit
API-Keys - niemals ins Repo committen).

### Firmware (am Board, per USB - musst du selbst machen)

Schritt-für-Schritt-Anleitung: [`docs/firmware.md`](docs/firmware.md).
Kurzfassung: xiaozhi-esp32 klonen, Board-Profil + Server-Adresse
(`LAN_IP`+Port aus `server/.env`) per `idf.py menuconfig` setzen, flashen.

## Status / offene Punkte

- [ ] Server lokal getestet (Docker-Build, Verbindung eines Test-Clients)
- [ ] Firmware geflasht und mit Server verbunden
- [ ] Emotions-Gesicht auf dem Display verifiziert
- [ ] STT/TTS-Qualität für Deutsch geprüft (Defaults: FunASR lokal,
      EdgeTTS `de-DE-KatjaNeural` - siehe
      [`server/overlay/config.template.yaml`](server/overlay/config.template.yaml))
- [ ] Phase 2 (Home Assistant) - bewusst noch nicht begonnen
