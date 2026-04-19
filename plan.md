# fiabeSonore — plan

A small offline RFID-triggered audio + video player for Raspberry Pi 3B. Tap a card → the matching `.mp3` / `.mp4` / etc. plays from local storage. No streaming, no cloud.

## Hardware

- **Raspberry Pi 3B** (already on hand).
- MFRC522 RFID reader on SPI.
- Speakers on the 3.5 mm jack; HDMI display for video.
- **Wi-Fi: ON** (kept enabled for SSH access during dev/maintenance).

## Locked-in decisions

| Concern | Choice |
|---|---|
| Config | `config.json` next to the script — only `base_path`. No tag→file map. |
| Tag↔file binding | **The card carries the filename.** Each card stores the media filename (e.g. `cappuccetto-rosso.mp3`) on its NFC memory; the script reads it on tap and resolves it inside `base_path`. No central registry. |
| Programming a card | `program_card.py <filename>` — validates the file exists in `base_path`, fits in the 48-byte payload, then writes it to a presented card and reads it back to confirm. |
| Audio backend | `pygame.mixer.music` (already in use). |
| Video backend | `python-vlc`. Reliable on Pi 3B, handles fullscreen, hardware decode where available. |
| Audio vs video dispatch | By file extension. `.mp3 .wav .ogg .flac` → audio. `.mp4 .mkv .avi .webm` → video. |
| Adding new media | Drop the file in `base_path`, run `program_card.py <filename>`, tap a blank card. No restart needed. |
| Process management | `systemd` unit (`fiabesonore.service`), auto-start on boot, restart on failure, logs to `journalctl`. |
| Dependencies | `requirements.txt`: `pygame`, `mfrc522`, `RPi.GPIO`, `python-vlc`. |

## Playback semantics (current behavior, kept)

- Same card tapped within 2 s → ignored (debounce on the card's hardware UID, not the payload).
- Different card mid-playback → current track stops, new one starts.
- No "stop" card. Each track plays to its end unless interrupted by another card.
- Card with empty payload → "card vuota, programmala" message.
- Card whose payload doesn't match any file → warning naming the missing file.

## Card payload constraints

- 48 bytes ASCII (3 blocks × 16, padded with spaces by `mfrc522`).
- Filenames must be ≤ 48 characters, no path separators (`/`, `\`), no leading `..`. The reader rejects anything that would escape `base_path`.

## Energy tweaks for the Pi 3B

Modest but worth doing once. In `/boot/firmware/config.txt`:

```
dtoverlay=disable-bt
dtparam=act_led_trigger=none
dtparam=pwr_led_trigger=none
```

(Note: **no** `disable-wifi` — Wi-Fi stays on for SSH.)

In code:
- Blank HDMI when nothing is playing video: `vcgencmd display_power 0`; re-enable before starting a video. Saves a few hundred mW and stops a dark room from glowing.
- Keep the 0.1 s poll loop. Lower polling = sluggish tag response, no real energy gain.
- Leave the CPU governor at default `ondemand`.

Skip: undervolting, custom kernels, idle-shutdown. A Pi 3B at idle (~1.4 W) is already cheap to run 24/7.

## Project cleanup

Delete from the repo (unused by the live code):
- `MFRC522.py`, `SimpleMFRC522.py`, `MFRC522.pyc`, `SimpleMFRC522.pyc`
- `MFRC522-python/` (empty submodule directory)
- `*.py.save*` (nano backups from 2019)
- `.mypy_cache/`

Keep: `rfidReader.py`, `basicTest.py` (handy for discovering new tag ids), `playSound.py` (handy for verifying audio output), `match0.wav`, `CLAUDE.md`, `plan.md`.

## Resulting file layout

```
fiabeSonore/
├── rfidReader.py          # main player (reads card payload, dispatches by extension)
├── program_card.py        # write a filename onto a card
├── basicTest.py           # one-shot tag id + payload reader
├── playSound.py           # audio output sanity check
├── config.json            # base_path only
├── requirements.txt
├── fiabesonore.service    # systemd unit (copy to /etc/systemd/system/)
├── match0.wav             # test sound
├── CLAUDE.md
└── plan.md
```
