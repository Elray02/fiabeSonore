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

### Wiring (MFRC522 → Pi 3B GPIO)

Standard SPI0 pinout used by the `mfrc522` Python library:

| MFRC522 pin | Pi pin (BCM) | Pi physical pin |
|---|---|---|
| SDA  | GPIO 8 (CE0)  | 24 |
| SCK  | GPIO 11 (SCLK)| 23 |
| MOSI | GPIO 10       | 19 |
| MISO | GPIO 9        | 21 |
| IRQ  | — (not used)  | — |
| GND  | GND           | 6  |
| RST  | GPIO 25       | 22 |
| 3.3V | 3.3V          | 1  |

> **Do not connect the MFRC522 to 5V** — it is a 3.3 V device and will be damaged.

---

## Setup on Raspberry Pi 3B (Raspbian)

The steps below take a fresh Raspbian install to a working autostart deployment.

### 1. Install Raspbian

Flash **Raspberry Pi OS** (Raspbian) to an SD card with the official Raspberry Pi Imager. Use the **"with desktop"** image — video playback needs a graphical session.

On first boot, complete the setup wizard, connect to Wi-Fi (only needed for installing packages — runtime is fully offline), and then update the system:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

### 2. Enable SPI and add the user to the right groups

The MFRC522 reader talks to the Pi over SPI, which is disabled by default.

```bash
sudo raspi-config
```

- → **Interface Options** → **SPI** → **Yes**
- Exit and reboot.

Add your user (the one that will run the player) to the `spi` and `gpio` groups:

```bash
sudo usermod -aG spi,gpio $USER
```

Log out and back in (or reboot) for the group change to take effect. Verify with `groups` — both `spi` and `gpio` should appear.

### 3. Install system packages

```bash
sudo apt install -y python3-pip git vlc
```

- `vlc` — required for video playback (the `python-vlc` library is a thin binding around it).
- `git` — to clone the repo.
- `python3-pip` — to install the Python dependencies.

### 4. Configure audio output

Force audio out the 3.5 mm jack (not HDMI):

```bash
sudo raspi-config
```

- → **System Options** → **Audio** → **Headphones / 3.5mm jack**

Test it:

```bash
speaker-test -t sine -f 440 -c 2 -s 1
```

You should hear a beep. Adjust volume with `alsamixer` if needed.

### 5. Clone the repo and install Python dependencies

```bash
cd ~
git clone <your-repo-url> fiabeSonore
cd fiabeSonore
pip install -r requirements.txt
```

This installs:

- `pygame` — audio playback
- `mfrc522` — RFID reader driver
- `RPi.GPIO` — GPIO access
- `python-vlc` — video playback

### 6. Configure `base_path`

Edit `config.json` to point at the directory where your media files will live:

```json
{ "base_path": "/home/pi/media" }
```

Then create that directory and drop your `.mp3`, `.mp4`, etc. files into it:

```bash
mkdir -p /home/pi/media
cp /path/to/your/fairy-tales/*.mp3 /home/pi/media/
```

### 7. Smoke-test the hardware

Before wiring up autostart, confirm everything works manually.

```bash
python3 basicTest.py    # tap a card — should print its ID and any stored payload
python3 playSound.py    # verify audio output (Ctrl+C to stop)
python3 rfidReader.py   # the real player — Ctrl+C to stop
```

### 8. Program your cards

For each fairy tale, write its filename onto a blank card:

```bash
python3 program_card.py                   # list available files
python3 program_card.py cappuccetto.mp3   # tap a card to write
```

---

## Running automatically on boot

The included `fiabesonore.service` is a systemd unit that starts the player after the graphical desktop is up (needed so VLC can open a fullscreen window).

### 1. Enable desktop auto-login

The service depends on a running desktop session for `DISPLAY=:0`. Configure the Pi to boot straight into the desktop without a login prompt:

```bash
sudo raspi-config
```

- → **System Options** → **Boot / Auto Login** → **Desktop Autologin**

### 2. Edit the service file for your user and path

`fiabesonore.service` is hardcoded for user `r` and path `/home/r/cantaStorie/Desktop/fiabeSonore`. Adjust both before installing:

```ini
User=pi
WorkingDirectory=/home/pi/fiabeSonore
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/usr/bin/python3 /home/pi/fiabeSonore/rfidReader.py
```

Replace `pi` and the path with whatever your user and clone location actually are.

### 3. Install and enable

```bash
sudo cp fiabesonore.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fiabesonore
```

Reboot to confirm it starts on its own:

```bash
sudo reboot
```

After the desktop loads, tap a programmed card — the audio or video should play.

### 4. Useful service commands

```bash
sudo systemctl status fiabesonore     # is it running?
sudo systemctl restart fiabesonore    # restart after changing code
sudo systemctl stop fiabesonore       # stop temporarily
sudo systemctl disable fiabesonore    # turn off autostart
journalctl -u fiabesonore -f          # tail live logs
journalctl -u fiabesonore -b          # logs since last boot
```

---

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

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ImportError: No module named RPi.GPIO` | Not running on a Pi, or dependencies not installed. Run `pip install -r requirements.txt`. |
| `No such file or directory: '/dev/spidev0.0'` | SPI not enabled. Run `sudo raspi-config` → Interface Options → SPI. |
| `PermissionError` on the reader | User not in `spi` / `gpio` groups. Add them with `usermod -aG spi,gpio $USER` and log out/in. |
| Service runs but no video window | Desktop autologin not enabled, or `DISPLAY` / `XAUTHORITY` in the unit file don't match your user. |
| No audio | Wrong output device. Run `sudo raspi-config` → System Options → Audio → 3.5 mm jack. Check volume with `alsamixer`. |
| Card reads always empty | Card has not been programmed yet. Use `python3 program_card.py <filename>`. |

## Dev-machine note

`RPi.GPIO`, `mfrc522`, `python-vlc`, and `vcgencmd` are Pi-specific. Importing `rfidReader.py` on a non-Pi machine will fail at the hardware imports. Testing is done on the actual device. The `vcgencmd` HDMI shim silently no-ops if the binary is absent, so other parts of the code are safe to read on any machine.
