# Audio build — MAX98357A I2S amplifier

Wiring, config, and software setup notes for the chosen audio chain.
See `speakers.md` for why this combo was picked.

## Bill of materials

| Part | Notes |
|---|---|
| MAX98357A I2S Class-D amp module | Generic AliExpress board, ~€2–4 |
| 8 Ω 3 W passive speaker | Full-range driver, ~1.5"–2" cone |
| Pi 3B (existing) | 5 V supply shared with amp |
| Hookup wire | Pi → amp + amp → speaker |
| (Future) B20K linear pot + MCP3008 ADC | Physical volume knob |

## Pin map (Pi 3B → MAX98357A)

The amp uses **I2S0** on the Pi. None of these pins conflict with the
MFRC522 (which lives on SPI0 pins 19/21/23/24 + GPIO 25 / pin 22).

| MAX98357A pin | Pi BCM | Pi physical pin | Notes |
|---|---|---|---|
| VIN  | 5V       | 2 or 4   | 5 V from the Pi's power rail |
| GND  | GND      | 6        | Common ground |
| LRC  | GPIO 19  | 35       | I2S word select (LRCLK) |
| BCLK | GPIO 18  | 12       | I2S bit clock |
| DIN  | GPIO 21  | 40       | I2S data |
| GAIN | —        | —        | **Leave floating** for +9 dB (default) |
| SD   | —        | —        | Leave floating / pulled high → L+R mixed mono output |

Speaker connects to the amp's `+` and `−` output terminals (the
Class-D output is bridge-tied — do **not** ground either side).

## Enable I2S on Raspberry Pi OS

Edit `/boot/firmware/config.txt`:

```
# replace the default audio config
# dtparam=audio=on              ← comment this out
dtoverlay=hifiberry-dac         ← add this (MAX98357A is compatible)
```

The MAX98357A doesn't need a dedicated overlay — `hifiberry-dac` works
because the amp is a generic I2S receiver. Reboot after editing.

## Verify after reboot

```bash
aplay -l
```

Should show a new card, something like:

```
card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi pcm5102a-hifi-0
```

Make it the default sink in PipeWire:

```bash
wpctl status                          # find the HifiBerry sink id
wpctl set-default <id>
wpctl set-volume <id> 0.70            # start at ~70%
```

Test:

```bash
aplay /home/r/Desktop/fiabeSonore/match0.wav
```

You should hear a clean tone through the 3" speaker. No hiss between
samples (one of the big wins over the analog jack).

## Software volume in `rfidReader.py`

The polling loop can set per-player volume on startup, capped at a
safe level for the speaker:

```python
# audio
pygame.mixer.music.set_volume(0.70)        # 0.0–1.0

# video (VLC)
self._player.audio_set_volume(70)          # 0–100
```

## Future: physical volume knob via pot + ADC

When the MCP3008 arrives, the wiring plan is:

- MCP3008 on **SPI0 CE1** (MFRC522 uses CE0 — they share MOSI/MISO/SCLK)
- Pot 3 V3 → MCP3008 CH0 (wiper) → GND
- Read ADC in `rfidReader.py`'s poll loop
- Map 0–1023 ADC value → 0.0–1.0 with a perceptual curve:
  `volume = (raw / 1023) ** 2`
- Apply to whichever player is `active`

A linear-taper pot (B20K) is fine because the curve is applied in
software.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `aplay -l` doesn't show HifiBerry card after reboot | `dtoverlay=hifiberry-dac` not added, or `dtparam=audio=on` still active. Re-check `/boot/firmware/config.txt`. |
| Card shows but silent | Pot/GAIN wiring issue, SD pulled low (= shutdown), or PipeWire default still on the onboard. Run `wpctl status` and verify the `*` is on HifiBerry. |
| Distortion at high volume | GAIN too high for the speaker, or output clipping in software. Cap volume at 70 % first. |
| Hum / buzz when idle | Bad ground or unshielded I2S wires too long. Keep amp-to-Pi wires under 10 cm and twist BCLK/LRC/DIN with GND. |
| Sound but cuts in/out | Power. The Pi 3B's 5 V rail can sag under audio peaks. Use a ≥ 2.5 A power supply, or power the amp from its own regulated 5 V. |
