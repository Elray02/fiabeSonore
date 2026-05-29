# Speaker decision for fiabeSonore

## Chosen build (purchased 2026-05-29)

| Component | Choice |
|---|---|
| Amplifier | **MAX98357A** I2S Class-D module |
| Speaker | **8 Ω 3 W** passive driver (from spare parts) |
| Volume control | Software (with a B20K pot + MCP3008 ADC as a planned upgrade) |

**Why this combo over a powered USB-speaker setup:**

- All-digital chain from Pi to amp (I2S) — bypasses the noisy onboard
  PWM jack and avoids USB DAC enumeration issues like the `cm109`
  driver gotcha (see README troubleshooting).
- Single 5 V supply for both Pi and amp — one power brick, fewer cables.
- Embeddable inside a small enclosure (Toniebox-style form factor) —
  no separate desktop speakers needed.
- 3 W speaker gives the MAX98357A (~2 W into 8 Ω at 5 V) safe
  headroom: no risk of overdriving the driver even at max output.

See `audio.md` for the wiring + config.txt setup.

---

## Why the 3 W speaker over the 1 W

The MAX98357A delivers ~2 W into 8 Ω at 5 V. With:

- A **1 W speaker** → amp can exceed the speaker's rating → must cap
  GAIN and software volume to avoid damage
- A **3 W speaker** → amp is well below the speaker's rating →
  full headroom, +9 dB GAIN, no software ceiling needed

The 3 W also tends to use a larger driver (1.5"–2" cone) with
noticeably fuller sound for spoken word + music — important for the
fiaba use case.

---

## Alternative paths (not chosen, kept for reference)

### Powered USB speakers (Tier 1 / 2)

| Model | Notes |
|---|---|
| Creative Pebble V2 | USB-C powered, 3.5 mm in, ~€20. Best for a desktop setup. |
| Logitech Z120 / Z130 | Cheaper, USB powered. Fine for fiabe. |
| Anker Soundcore Mini (AUX) | Portable + battery, ~€25 |
| JBL Go 3 (AUX) | Rubberized, water-resistant, ~€35 |

These need a **clean line-level signal** — pair with a USB DAC (the
`0d8c:000e` C-Media class) since the Pi's analog jack hisses. See the
README troubleshooting for the `cm109` blacklist + `alsamixer` unmute
recipe.

### Integrated USB DAC + small speaker combo

Cheap AliExpress kits (~€10–18) bundle a CM108-class DAC with a small
passive driver via PH2.0 connector. Plug-and-play but speaker is mono,
tinny, no bass. Acceptable only for short close-listening sessions —
not chosen for this build.

---

## Search tips on AliExpress (for replacement / future builds)

- `MAX98357A I2S amplifier module` — the amp board, ~€2–4
- `8 ohm 3W speaker 2 inch` — small full-range driver, ~€1–3
- `MCP3008 ADC module` — for the future pot+ADC volume knob, ~€2

## Hardware audio chain (final)

```
Pi 3B GPIO  ──I2S──▶  MAX98357A  ──amplified analog──▶  8Ω 3W speaker
                       GAIN floating (+9 dB)
                       SD high (L+R mixed → mono)
```
