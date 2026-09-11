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

Zwei Wege, den Server zu betreiben - beide nutzen dasselbe Docker-Image,
such dir den passenden aus.

### Option A: Docker Compose (Mac/PC/NAS)

```bash
cd server
cp .env.example .env
# .env öffnen: ANTHROPIC_API_KEY und LAN_IP eintragen
docker compose up -d --build
docker compose logs -f   # prüfen, dass der Server sauber hochkommt
```

Details/Hintergrund: [`docs/secrets.md`](docs/secrets.md) (Umgang mit
API-Keys - niemals ins Repo committen).

**Nachteil:** Muss laufen, solange du den Assistenten nutzen willst - auf
einem Laptop, der schläft/ausgeht, ist das kein Dauerbetrieb.

### Option B: Als Home-Assistant-Add-on (empfohlen für Dauerbetrieb)

Läuft komplett getrennt von deiner Home-Assistant-Konfiguration (keine
Entities/Automationen) - nutzt dein ohnehin durchgehend laufendes
HA-Gerät nur als Hosting-Platz. Funktioniert mit **Home Assistant OS**
und **Home Assistant Supervised** (nicht mit reinem "Core"/"Container",
da dort kein Add-on-Store existiert - dort bleibt Option A der Weg).

1. In Home Assistant: **Einstellungen → Add-ons → Add-on Store → ⋮ (oben
   rechts) → Repositories**
2. URL eintragen: `https://github.com/rolandtimpel/esp32-voice-claude`
3. Das Add-on **"ESP32 Voice Claude"** erscheint in der Liste - installieren
4. Im **Konfiguration**-Tab die Keys/Einstellungen eintragen (Details:
   [`server/DOCS.md`](server/DOCS.md)), dann starten

Danach OTA-URL in der Firmware auf die LAN-IP deines Home-Assistant-Geräts
zeigen lassen (statt auf deinen Mac).

### Firmware (am Board, per USB - musst du selbst machen)

Schritt-für-Schritt-Anleitung: [`docs/firmware.md`](docs/firmware.md).
Kurzfassung: xiaozhi-esp32 klonen, Board-Profil + Server-Adresse
(`LAN_IP`+Port aus `server/.env`) per `idf.py menuconfig` setzen, flashen.

## Status / offene Punkte

- [x] Server lokal getestet (Docker-Build, Verbindung eines Test-Clients)
- [x] Firmware geflasht und mit Server verbunden
- [x] Ende-zu-Ende getestet: Wake-Word ("Hi ESP") → Claude antwortet hörbar
      auf Deutsch
- [x] STT auf Groq Whisper umgestellt (bessere Erkennungsqualität als
      lokales FunASR), TTS: EdgeTTS `de-DE-KatjaNeural`
- [ ] Emotions-Gesicht auf dem Display verifiziert
- [ ] Dauerbetrieb: Server auf stabilerem Host als dem Mac (Home-Assistant-
      Add-on, siehe oben)
- [ ] Wake-Word-Zuverlässigkeit/Mikrofonempfindlichkeit weiter verbessern
- [ ] Eigenes Gesicht/Persönlichkeit (Nomi-artig) - zurückgestellt, bis
      Grundfunktion stabil läuft
- [ ] Phase 2 (Home Assistant Smart-Home-Steuerung) - bewusst noch nicht
      begonnen
