#!/usr/bin/env python3
"""
Write a media filename onto an RFID card.

Usage:
    python3 program_card.py                  # list available files
    python3 program_card.py <filename>       # write <filename> to a card

The card stores a 48-byte ASCII payload (3 blocks × 16 bytes), so the
filename must be ≤ 48 characters.
"""

import json
import sys
from pathlib import Path

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

MAX_PAYLOAD = 48


def load_base_path() -> Path:
    config_file = Path(__file__).parent / "config.json"
    config = json.loads(config_file.read_text())
    return Path(config["base_path"])


def list_files(base_path: Path) -> None:
    files = sorted(p.name for p in base_path.glob("*") if p.is_file())
    if not files:
        print(f"Nessun file in {base_path}")
        return
    print(f"File disponibili in {base_path}:")
    for name in files:
        marker = "  " if len(name) <= MAX_PAYLOAD else " ⚠"  # too long
        print(f"{marker} {name}")
    print(f"\nUso: python3 program_card.py <nome_file>")


def write_card(base_path: Path, filename: str) -> int:
    target = base_path / filename
    if not target.is_file():
        print(f"❌ File non trovato: {target}")
        return 1
    if len(filename) > MAX_PAYLOAD:
        print(f"❌ Nome troppo lungo ({len(filename)} > {MAX_PAYLOAD} caratteri)")
        return 1

    reader = SimpleMFRC522()
    try:
        print(f"Pronto a scrivere '{filename}'.")
        print("Avvicina la card al lettore e tienila ferma...")
        reader.write(filename)
        print("✓ Scrittura completata. Conferma in corso — tieni la card vicina.")

        tag_id, payload = reader.read()
        written = payload.strip()
        if written == filename:
            print(f"✓ Card {tag_id} programmata con '{written}'")
            return 0
        print(f"❌ Verifica fallita. Letto: '{written}' (atteso '{filename}')")
        return 1
    finally:
        GPIO.cleanup()


def main() -> int:
    base_path = load_base_path()
    if not base_path.is_dir():
        print(f"❌ base_path non esiste: {base_path}")
        return 1

    if len(sys.argv) == 1:
        list_files(base_path)
        return 0
    if len(sys.argv) != 2:
        print("Uso: python3 program_card.py [<nome_file>]")
        return 1

    return write_card(base_path, sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
