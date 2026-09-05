# Secrets / API-Keys

**Grundsatz: Nichts davon gehört in dieses Git-Repo.**

## Anthropic API-Key

1. Key erzeugen: https://console.anthropic.com/settings/keys
2. In `server/.env` eintragen (Datei aus `server/.env.example` kopieren,
   `server/.env` ist in `.gitignore` und wird nie committed):
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. `entrypoint.sh` im Container liest den Key aus der Umgebungsvariable und
   schreibt ihn in `data/.config.yaml` (liegt in einem Docker-Volume, nicht
   im Image und nicht im Git-Repo).

Gib deinen Anthropic-Key niemals in einem Chat (auch nicht mit mir) oder in
einer Konfigurationsdatei ein, die committed wird - trage ihn ausschließlich
lokal in `server/.env` ein.

## Sonstige Keys (optional, falls du Cloud-STT/TTS statt der kostenlosen
lokalen Defaults nutzen willst)

Genauso behandeln: neue Variable in `server/.env.example` dokumentieren,
echten Wert nur in der lokalen, nicht committeten `server/.env` eintragen,
und in `server/overlay/config.template.yaml` per `${VARIABLE}` referenzieren.

## WLAN-Zugangsdaten der Firmware

Die xiaozhi-esp32-Firmware fragt WLAN-Zugangsdaten beim ersten Start über ein
Onboarding (Access-Point/Captive-Portal am Gerät) ab - sie werden nicht in
Code oder Repo hinterlegt. Solltest du sie doch fest im Quellcode setzen
wollen (z.B. für automatisiertes Flashen mehrerer Geräte), lege sie lokal in
einer nicht committeten `sdkconfig.local`/`.env`-Datei ab, nie in
`sdkconfig.defaults` oder `Kconfig.projbuild`.
