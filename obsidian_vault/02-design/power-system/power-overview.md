# Power System Overview

## Per-Component Power Budget

| Component | Voltage | Typical Current | Peak Current |
|---|---|---|---|
| Orange Pi 5 (idle) | 5V | 0.8A (4W) | — |
| Orange Pi 5 (NPU load) | 5V | 2.5–3A (12–15W) | 4A |
| MG996R servo × 2 | 5–6V | 0.5A each (5W total) | 2.5A each (stall) |
| Water gun pump | 4.5–6V | 0.5–1A (3–5W) | 2A |
| USB camera | 5V (USB) | 0.5A | 0.5A |
| PCA9685 driver | 3.3–5V | 0.01A | — |

**Use two separate power rails.** Servos and pumps generate electrical noise and current spikes that can crash the Orange Pi if they share a supply.

---

## Converter Selection

Both rails use the same model — the **DROK 12V to 5V 5A USB Buck Converter**:

[DROK Buck Converter 12V to 5V, 5A USB Voltage Regulator](https://www.amazon.com/Converter-DROK-Regulator-Inverter-Transformer/dp/B01NALDSJ0)
- Input: 9–36V DC | Output: fixed 5V (5.0–5.3V) @ up to 5–6A
- USB output connector — plugs directly into the Orange Pi 5 USB-C port (with appropriate cable)
- Purchase two: one per rail

---

## Rail 1 — Orange Pi 5

- Output: **5V @ 5A** from the DROK converter above
- Wattage draw from 12V source: ~25W → ~2.1A @ 12V
- Connect via USB output on the converter → USB-C cable into the Orange Pi 5

## Rail 2 — Servos + Water Gun

- Output: **5V @ 5A** from a second DROK converter
- Wattage draw from 12V source: ~30W → ~2.5A @ 12V
- Water pistol confirmed 5V (USB rechargeable battery internally)
- Servos: MG996R runs fine at 5V
- Add a 5A fuse on this rail as protection

---

## Total 12V Source Sizing

| Rail | Draw from 12V |
|---|---|
| Orange Pi 5 rail | ~2.1A |
| Servos + water gun rail | ~2.5A |
| Margin (20%) | ~1A |
| **Total** | **~5.5–6A @ 12V (~65–70W)** |

A **12V/6A (72W) power supply or battery** is sufficient. If running from a car battery or solar setup, this is a very light load.

---

## Wiring Diagram (simplified)

```
12V Source
   ├── DROK Converter #1 → 5V/5A (USB out) → USB-C → Orange Pi 5
   └── DROK Converter #2 → 5V/5A → Servos + Water Gun + PCA9685
```
