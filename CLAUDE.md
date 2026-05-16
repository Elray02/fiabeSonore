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

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (60-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk go test             # Go test failures only (90%)
rtk jest                # Jest failures only (99.5%)
rtk vitest              # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk pytest              # Python test failures only (90%)
rtk rake test           # Ruby test failures only (90%)
rtk rspec               # RSpec test failures only (60%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%). Format flags (-c, -l, -L, -o, -Z) run raw.
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->