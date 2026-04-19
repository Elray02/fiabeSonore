# fiabeSonore

An offline RFID-triggered audio and video player for Raspberry Pi 3B. Tap an NFC card on the reader → the mapped media file plays from local storage. No streaming, no cloud, no internet required.

*fiabeSonore* = "sound fairy tales" in Italian.

## How it works

**The card is the configuration.** Each RFID card stores the media filename directly in its own NFC memory (48 bytes). When a card is tapped, the player reads that filename, resolves it inside a configured local directory, and plays it. There is no central tag→file registry — adding a new story is just dropping a file and programming a card.

```
Tap card  →  read payload ("cappuccetto-rosso.mp3")
          →  resolve inside base_path
          →  play via pygame (audio) or VLC (video)
```

## Hardware

| Component | Details |
|---|---|
| Board | Raspberry Pi 3B |
| RFID reader | MFRC522 on SPI |
| Audio output | 3.5 mm jack |
| Video output | HDMI display |

## Requirements

**System packages** (install with `apt`):

```
vlc
```

**Python packages** (install with `pip`):

```
pip install -r requirements.txt
```

- `pygame` — audio playback
- `mfrc522` — RFID reader driver
- `RPi.GPIO` — GPIO access
- `python-vlc` — video playback

**Pi configuration:**

- SPI must be enabled: `sudo raspi-config` → Interface Options → SPI
- The run user must be in the `spi` and `gpio` groups:
  ```
  sudo usermod -aG spi,gpio <your-user>
  ```

## Setup

1. Clone the repo and `cd` into it.
2. Edit `config.json` to point `base_path` at the directory where your media files live:
   ```json
   { "base_path": "/home/r/media/fiabe" }
   ```
3. Drop your `.mp3`, `.mp4`, etc. files into that directory.
4. Program a card for each file (see below).

## Running

**Start the player:**

```bash
python3 rfidReader.py
```

**Program a card** (write a filename onto a card's NFC memory):

```bash
python3 program_card.py                   # list available files
python3 program_card.py cappuccetto.mp3   # write filename to a presented card
```

After running the write command, hold the card near the reader and keep it still until the confirmation message appears.

## Adding a new fairy tale

1. Drop the media file into `base_path`.
2. Run `python3 program_card.py <filename>` and tap a blank card.
3. Done — no code changes, no service restart.

## Supported formats

| Type | Extensions |
|---|---|
| Audio | `.mp3` `.wav` `.ogg` `.flac` |
| Video | `.mp4` `.mkv` `.avi` `.webm` |

Dispatch is by file extension only.

## Playback behavior

- **Same card held** → ignored for 2 seconds (debounce on hardware UID).
- **New card tapped mid-playback** → current track stops, new one starts immediately.
- **Blank card** → warning message with programming instructions.
- **Unknown filename** → warning naming the missing file.
- **HDMI** → blanked automatically when no video is playing to save power; re-enabled before a video starts.

## Hardware smoke tests

```bash
python3 basicTest.py   # read one card, print its ID and stored payload, exit
python3 playSound.py   # loop a test MP3 via pygame — verifies audio output
```

## Autostart with systemd

Install `fiabesonore.service` to run the player automatically on boot:

```bash
sudo cp fiabesonore.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fiabesonore
```

View logs:

```bash
journalctl -u fiabesonore -f
```

> **Note:** The service file is hardcoded for user `r` and path `/home/r/cantaStorie/Desktop/fiabeSonore`. Edit it to match your setup before installing.

## File layout

```
fiabeSonore/
├── rfidReader.py       # main player
├── program_card.py     # write a filename onto a card
├── basicTest.py        # one-shot card inspector
├── playSound.py        # audio output sanity check
├── config.json         # base_path setting
├── requirements.txt
├── fiabesonore.service # systemd unit
└── match0.wav          # test sound
```

## Security

`rfidReader.py` validates every card payload before touching the filesystem: empty payloads, path separators (`/`, `\`), and `..` sequences are rejected, and the resolved path is checked to stay inside `base_path`. A maliciously-programmed card cannot escape the media directory.

## Dev-machine note

`RPi.GPIO`, `mfrc522`, `python-vlc`, and `vcgencmd` are Pi-specific. Importing `rfidReader.py` on a non-Pi machine will fail at the hardware imports. Testing is done on the actual device. The `vcgencmd` HDMI shim silently no-ops if the binary is absent, so other parts of the code are safe to read on any machine.
