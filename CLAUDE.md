# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`fiabeSonore` ("sound fairy tales") is an offline RFID-triggered media player for a Raspberry Pi 3B. Tap a card on the MFRC522 reader → the mapped audio or video file plays from local storage. No streaming, no cloud. See `plan.md` for the locked-in design decisions.

## Running

Main entry point:
```
python3 rfidReader.py
```

Programming a card (writes a filename onto the card's NFC memory):
```
python3 program_card.py                  # list available files in base_path
python3 program_card.py cappuccetto.mp3  # write filename to a presented card
```

Hardware smoke tests:
- `python3 basicTest.py` — read one card, print its numeric id and stored payload, exit.
- `python3 playSound.py` — loop a hardcoded MP3 via pygame; verifies audio output.

Install deps on the Pi: `pip install -r requirements.txt`. Requires SPI enabled (`raspi-config`) and the run user in the `spi` and `gpio` groups. Video playback also needs `vlc` from apt.

## Architecture

**The card is the configuration.** Each card stores a 48-byte ASCII payload (3 blocks × 16) — the script writes the media filename there with `program_card.py`, and `rfidReader.py` reads that payload at tap time and resolves it inside `base_path`. There is no central `tag_id → file` registry; `config.json` only carries `base_path`.

`rfidReader.py` shape:

- `RFIDMediaPlayer` loads `config.json`, opens `SimpleMFRC522`, and owns one `AudioPlayer` and one `VideoPlayer`.
- The polling loop calls `reader.read_no_block()` every `POLL_INTERVAL` (0.1 s) and applies a 2-second debounce on the card's hardware UID (so a held card doesn't retrigger).
- `resolve_media_path()` strips the payload, rejects empty payloads and anything containing path separators or `..`, and verifies the resolved path stays inside `base_path` (defense against a maliciously-programmed card).
- `_trigger()` picks a player by extension (`AUDIO_EXTS` vs `VIDEO_EXTS`), stops any currently-active player, and starts the new one. The `active` reference is also cleared automatically when natural-end is detected.
- HDMI is blanked via `vcgencmd display_power 0` whenever no video is playing, and re-enabled before a video starts. The shim in `hdmi_power()` no-ops on dev machines (no `vcgencmd` binary) so the script doesn't crash off-Pi.

**Adding a new fairy tale** = drop the file into `base_path`, run `python3 program_card.py <filename>`, tap a blank card. No code changes, no service restart.

**Audio vs. video dispatch is by extension only** — `.mp3 .wav .ogg .flac` go to pygame; `.mp4 .mkv .avi .webm` go to VLC. The card payload doesn't carry a type tag.

## Deployment

`fiabesonore.service` is the systemd unit. It targets `graphical.target` and sets `DISPLAY=:0` / `XAUTHORITY=...` so VLC can open a window in the desktop session. Hardcoded for user `r` and the deployment path `/home/r/cantaStorie/Desktop/fiabeSonore` — adjust if either differs. Install steps are in the comments at the bottom of the unit file.

## Dev-machine caveats

`RPi.GPIO`, `mfrc522`, `vlc`, and `vcgencmd` are all Pi-specific or hardware-specific. Importing `rfidReader.py` on a non-Pi will fail at the `RPi.GPIO`/`mfrc522` import. There is no mock/stub today — testing happens on the actual Pi. The `base_path` in `config.json` likewise points at the Pi filesystem.
