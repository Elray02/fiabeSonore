#!/usr/bin/env python3
"""
Read one RFID card and print its hardware id and stored payload.
Useful for inspecting what a card currently has written on it.
"""

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Avvicina una card al lettore...")
    tag_id, payload = reader.read()
    payload = payload.strip()
    print(f"ID:      {tag_id}")
    print(f"Payload: {payload!r}" if payload else "Payload: (vuoto — card non programmata)")
finally:
    GPIO.cleanup()
