#!/usr/bin/env python3
"""
fiabeSonore — RFID-triggered local audio/video player.

Each card stores its own filename in its NFC memory. On tap, the script
reads that filename, resolves it inside base_path, and dispatches by
extension: audio → pygame, video → python-vlc.

Use program_card.py to write a filename onto a new card.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Protocol

import pygame
import vlc
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".webm"}

DEBOUNCE_SECONDS = 2.0
POLL_INTERVAL = 0.1


class MediaPlayer(Protocol):
    def play(self, filepath: Path) -> None: ...
    def stop(self) -> None: ...
    def is_playing(self) -> bool: ...
    def shutdown(self) -> None: ...


def hdmi_power(on: bool) -> None:
    """Toggle HDMI output to save power when no video is playing."""
    try:
        subprocess.run(
            ["vcgencmd", "display_power", "1" if on else "0"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass  # vcgencmd unavailable (e.g. dev machine) — silently ignore


class AudioPlayer:
    def __init__(self) -> None:
        pygame.mixer.init()

    def play(self, filepath: Path) -> None:
        pygame.mixer.music.load(str(filepath))
        pygame.mixer.music.play()

    def stop(self) -> None:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def shutdown(self) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.quit()


class VideoPlayer:
    BUSY_STATES = (vlc.State.Opening, vlc.State.Buffering, vlc.State.Playing)

    def __init__(self) -> None:
        self._instance = vlc.Instance("--quiet", "--no-video-title-show")
        self._player = self._instance.media_player_new()
        self._player.set_fullscreen(True)

    def play(self, filepath: Path) -> None:
        hdmi_power(True)
        media = self._instance.media_new(str(filepath))
        self._player.set_media(media)
        self._player.play()

    def stop(self) -> None:
        self._player.stop()
        hdmi_power(False)

    def is_playing(self) -> bool:
        return self._player.get_state() in self.BUSY_STATES

    def shutdown(self) -> None:
        self._player.stop()
        self._player.release()
        self._instance.release()


def resolve_media_path(base_path: Path, payload: str) -> Optional[Path]:
    """
    Turn a card payload into a real file under base_path.
    Rejects empty payloads and anything that tries to escape base_path
    (path separators, '..', absolute paths).
    """
    name = payload.strip()
    if not name:
        return None
    if "/" in name or "\\" in name or name.startswith(".."):
        return None
    candidate = (base_path / name).resolve()
    try:
        candidate.relative_to(base_path.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


class RFIDMediaPlayer:
    def __init__(self, config_path: Path) -> None:
        config = json.loads(config_path.read_text())
        self.base_path = Path(config["base_path"])
        if not self.base_path.is_dir():
            print(f"⚠️  base_path non esiste: {self.base_path}")

        self.reader = SimpleMFRC522()
        self.audio = AudioPlayer()
        self.video = VideoPlayer()
        self.active: Optional[MediaPlayer] = None

        hdmi_power(False)  # start with HDMI off; video player turns it on
        self._announce()

    def _announce(self) -> None:
        files = sorted(p.name for p in self.base_path.glob("*") if p.is_file())
        print(f"✓ fiabeSonore avviato — {len(files)} file in {self.base_path}")
        for name in files:
            print(f"  - {name}")

    def _player_for(self, filepath: Path) -> Optional[MediaPlayer]:
        ext = filepath.suffix.lower()
        if ext in AUDIO_EXTS:
            return self.audio
        if ext in VIDEO_EXTS:
            return self.video
        return None

    def _stop_active(self) -> None:
        if self.active is not None:
            self.active.stop()
            self.active = None

    def _trigger(self, filepath: Path) -> None:
        player = self._player_for(filepath)
        if player is None:
            print(f"❌ Estensione non supportata: {filepath.suffix}")
            return

        self._stop_active()
        try:
            player.play(filepath)
            self.active = player
            print(f"🎵 Riproduzione: {filepath.name}")
        except Exception as e:
            print(f"❌ Errore riproduzione: {e}")

    def run(self) -> None:
        print("\nAvvicina un tag RFID al lettore...\n")
        last_id: Optional[int] = None
        last_time = 0.0

        try:
            while True:
                tag_id, payload = self.reader.read_no_block()

                if tag_id is not None:
                    now = time.time()
                    if tag_id == last_id and (now - last_time) < DEBOUNCE_SECONDS:
                        time.sleep(POLL_INTERVAL)
                        continue

                    print(f"\n📡 Tag {tag_id} → '{payload.strip()}'")
                    filepath = resolve_media_path(self.base_path, payload)
                    if filepath is not None:
                        self._trigger(filepath)
                        last_id = tag_id
                        last_time = now
                    elif not payload.strip():
                        print("⚠️  Card vuota. Programmala con:")
                        print("   python3 program_card.py <nome_file>")
                    else:
                        print(f"⚠️  File non trovato in {self.base_path}")

                # Auto-clear active reference when playback ends naturally,
                # so HDMI gets blanked after a video finishes.
                if self.active is not None and not self.active.is_playing():
                    if self.active is self.video:
                        hdmi_power(False)
                    self.active = None

                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Player fermato")
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        self.audio.shutdown()
        self.video.shutdown()
        hdmi_power(True)  # leave HDMI on so the next user sees the console
        GPIO.cleanup()
        print("✓ Risorse rilasciate")


if __name__ == "__main__":
    config_file = Path(__file__).parent / "config.json"
    if not config_file.exists():
        print(f"❌ Config mancante: {config_file}")
        sys.exit(1)
    RFIDMediaPlayer(config_file).run()
