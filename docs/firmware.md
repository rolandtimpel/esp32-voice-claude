# Firmware bauen & flashen (musst du selbst am Gerät machen)

Das Flashen per USB kann nicht remote erledigt werden - diese Anleitung ist
für dich zum Nachmachen am eigenen Rechner mit angeschlossenem Board.

## 1. Voraussetzungen

- ESP-IDF (Espressif IoT Development Framework) installiert, Version wie im
  xiaozhi-esp32-Repo empfohlen: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/
- USB-Kabel mit Datenleitung (nicht nur Ladekabel) zum Board

## 2. Firmware-Quellcode holen

```bash
git clone https://github.com/78/xiaozhi-esp32.git
cd xiaozhi-esp32
```

## 3. Zielchip setzen

```bash
idf.py set-target esp32s3
```

## 4. Board-Profil + Server-Adresse konfigurieren

```bash
idf.py menuconfig
```

- Unter **Xiaozhi Assistant** das passende Board-Profil für dein Board
  auswählen (SpotPear-Variante mit 1,28"-Rund-LCD - der genaue Eintragsname
  hat sich zwischen Firmware-Versionen schon geändert, einfach in der Liste
  nach "Spotpear"/"1.28" suchen).
- Die **OTA-URL** auf deinen selbstgehosteten Server umstellen, Format
  ungefähr:
  ```
  http://<LAN_IP_DEINES_SERVERS>:8003/xiaozhi/ota/
  ```
  (dieselbe `LAN_IP` und derselbe `HTTP_PORT`, die du in `server/.env`
  eingetragen hast). Den Menüpunkt findest du unter **Xiaozhi Assistant** in
  einer Version, die sich je nach Firmware-Stand leicht unterscheiden kann -
  im Zweifel im Repo nach `OTA_URL` bzw. `Kconfig.projbuild` suchen.
- Optional: Wake-Word ändern unter **ESP Speech Recognition → Wake Word**
  (Standard ist "你好小智" / "Hallo Xiaozhi"). Die Doku des Firmware-Repos
  (`docs/`) listet die verfügbaren Wake-Word-Modelle - dort auch nachsehen,
  falls ein geändertes Wake-Word nach dem Flashen nicht greift (bekanntes
  Problem bei fehlenden Cloud-Ressourcendateien für bestimmte Modelle).
- Mit `S` speichern, `Q`/Esc zum Verlassen.

## 5. Bauen und flashen

```bash
idf.py build
idf.py -p <DEIN_USB_PORT> flash monitor
```

`<DEIN_USB_PORT>` z.B. `/dev/ttyUSB0` (Linux) oder `/dev/cu.usbserial-XXXX`
(macOS) - je nachdem, wie sich das Board meldet.

## 6. Erststart / WLAN einrichten

Beim ersten Boot spannt das Gerät normalerweise einen eigenen WLAN-Access-
Point auf, über den du dein Heim-WLAN hinterlegst (Captive Portal im
Browser). Details dazu stehen in der `docs/`-Sektion des xiaozhi-esp32-Repos,
falls sich der Ablauf zwischenzeitlich geändert hat.

## 7. Verbindung prüfen

Nach dem WLAN-Setup sollte sich das Gerät automatisch mit unserem Server
(`ws://<LAN_IP>:8000/xiaozhi/v1/`, aus `server/.env`) verbinden. Server-Logs
prüfen mit:

```bash
docker compose -f server/docker-compose.yml logs -f
```

Ein neuer verbundener Client sollte dort auftauchen, sobald das Board
online ist.
