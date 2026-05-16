# Display options for fiabeSonore

Shortlist of screens compatible with Raspberry Pi 3B, ≤ 8".

Since fiabeSonore uses **RFID cards as input**, touch is **not needed** —
a non-touch panel is cheaper and works equally well. The best value is a
7" HDMI panel with **built-in speakers**: it lets you drop the separate
3.5 mm speaker setup and route audio over HDMI (configure with
`raspi-config` → System Options → Audio → HDMI).

---

## Amazon — 7" HDMI with speakers (recommended path)

| Model | Why it fits | Notes |
|---|---|---|
| SunFounder 7" HDMI 1024×600 with built-in speaker | HDMI + speaker + AV/VGA fallback; explicitly listed for Pi 3B | Cheapest "speaker included" option |
| ELECROW 7" 1024×600 IPS Touchscreen + dual speakers | Stand included, plug-and-play HDMI, dual speakers | Touch is wasted here but build quality is solid |
| Hosyond 7" 1024×600 IPS with dual speakers | Ships with Pi 3B HDMI adapters in the box | Minimal accessory shopping |
| Waveshare 7" HDMI LCD (H) with case | Reputable brand, IPS, optional case | No speakers — pair with the 3.5 mm jack route |

## Amazon — official DSI (no HDMI cable needed)

- **Raspberry Pi Official 7" Touchscreen (800×480, DSI)** — connects via
  the DSI ribbon + GPIO power, frees the HDMI port. No speakers; still
  needs audio via the 3.5 mm jack. Best build quality but lowest
  resolution of the bunch.

## Smaller (≤ 5") if you want a compact build

- **5" HDMI 800×480 (Waveshare / generic)** on AliExpress — fine for
  thumbnail-style video, very compact. Search:
  `5 inch HDMI LCD raspberry pi 800x480`.
- **3.5" SPI displays — avoid.** SPI/framebuffer rendering means VLC
  cannot hardware-accelerate video on the Pi 3B; playback will stutter.

## AliExpress — same panels, lower prices, longer shipping

Search terms that surface the right products:

- `raspberry pi 7 inch HDMI 1024x600 speaker` — typically €25–40, often
  the same OEM panels as ELECROW/Hosyond rebranded
- `raspberry pi 5 inch HDMI 800x480` — compact, €15–25

Stores worth checking: **Waveshare official store**, **VS DISPLAY**, **52Pi**.

---

## Recommendation for fiabeSonore

If you want **one purchase that just works**: a non-touch **7" 1024×600
HDMI panel with built-in speakers**. It consolidates display + audio
over a single HDMI cable, fits in a small enclosure, and matches the
kid-friendly form factor.

- Cheapest path → SunFounder or AliExpress equivalents
- Safer brand for returns → ELECROW

---

## Compatibility notes

- Pi 3B has **full-size HDMI** (Pi 4 has micro-HDMI — different cable).
- All Pi models including 3B have the DSI connector for the official
  display.
- Power: small displays usually pull < 500 mA at 5 V. The Pi 3B's
  official 2.5 A PSU can power both via USB-from-Pi on smaller panels;
  7" panels generally need their own 5 V input.
- HDMI audio: set in `raspi-config` → System Options → Audio → HDMI.
  Switch back to 3.5 mm if using a no-speaker panel.

---

## Source links (captured 2026-05-16)

- SunFounder 7" HDMI with built-in speaker — https://www.sunfounder.com/products/7inch-tft-monitor
- SunFounder 7" IPS LCD touchscreen with speakers — https://www.sunfounder.com/products/raspberry-pi-7-inch-ips-lcd-touch-screen-monitor-display-1024-600-capacitive-screen-hdmi-plug-play-for-raspberry-pi-5-4b-3b-built-in-speaker-3-5mm-audio-jack
- ELECROW 7" Touchscreen Monitor — https://www.amazon.com/ELECROW-Raspberry-Touchscreen-Capacitive-1024x600/dp/B08FMNDDSL
- Hosyond 7" IPS LCD with adapters — https://www.amazon.com/Hosyond-Raspberry-1024%C3%97600-Capacitive-Compatible/dp/B0BKGCB18T
- JUNEBOX 7" Touchscreen dual-speaker — https://www.amazon.com/Touchscreen-Raspberry-1024-touchscreen-Dual-Speaker/dp/B0F2SV82R1
- Waveshare 7" HDMI LCD (H) with case — https://www.amazon.com/7inch-HDMI-LCD-Resolution-Capacitive/dp/B077PLVZCX
- Raspberry Pi Official 7" Touchscreen (DSI) — https://www.amazon.com/Raspberry-Pi-7-Touchscreen-Display/dp/B0153R2A9I
- AliExpress — 7" IPS 1024×600 touch for Pi — https://www.aliexpress.com/item/1005001485174459.html
- AliExpress — 5" HDMI LCD module — https://www.aliexpress.com/item/1005003541450032.html
- AliExpress — search: Raspberry Pi screen — https://www.aliexpress.com/w/wholesale-raspberry-pi-screen.html
