# Deer Defense System — Automated Water Gun Turret for Tomato Plants

An AI-powered, automated water gun turret that detects deer using computer vision and fires a water burst to deter them from your tomato plants.

---

## Project Overview

- **Goal**: Protect tomato plants from deer using a humane, automated water deterrent.
- **Detection**: YOLO-World v2 (open-vocabulary) — detects "deer" (or any text prompt: rabbit, groundhog, etc.)
- **Hardware**: Orange Pi 5 (RK3588 NPU) + USB camera + 2 servos + disassembled electric water gun
- **Inference**: Runs fully local/on-device, 24/7, no cloud needed
- **Inspired by**: u/muxamilian's automated pigeon defense system (r/SideProject, April 2026)

---

## Concept Image

![Deer Defense Turret Concept](docs/concept-image.png)

*AI-generated concept image of the assembled deer defense turret*

---

## Bill of Materials (BOM)

**Estimated total cost**: $150–350 USD

### 1. Computing & Vision
- **Orange Pi 5 4GB** (RK3588S NPU, 6 TOPS) — [Amazon listing](https://www.amazon.com/Orange-Pi-Frequency-Development-Android12/dp/B0BN16ZLXB)
- 5V/4A+ USB-C power supply (dedicated — do not share with servos)
- **USB Camera** — Logitech C920/C270 or generic wide-angle 1080p (UVC-compatible)
- SD card (32GB+ Class 10/A2) or eMMC module

### 2. Actuation (Aiming)
- **2× Servo motors**: MG90S or MG996R (metal gear recommended for outdoor use)
- Pan-tilt bracket / servo mount kit (or 3D-print from Thingiverse/Printables)
- Optional: **PCA9685** 16-channel PWM servo driver (I²C) — reduces jitter, frees GPIO pins

### 3. Water Gun & Triggering
- **Battery-powered electric water gun** (cheap toy) — disassemble to access pump circuit; look for one with a simple DC motor pump triggered by holding the button (not a manual pump)
- **IRLZ44N** N-channel logic-level MOSFET + resistors (10kΩ pull-down, ~220Ω gate resistor)
- Alternative: 5V relay module (simpler/safer isolation)
- Jumper wires, breadboard/perfboard, Dupont connectors, heat shrink

> ⚠️ **Untested — requires further research and testing before purchase:**
> [StimuVariety Electric Water Gun](https://www.amazon.com/gp/product/B0GGB86N1X) — selected as the target model for this project; verify battery type, pump circuit accessibility, and trigger mechanism before purchasing

### 4. Mechanical & Mounting
- 3D-printed or custom turret mount (holds camera + servos + water gun)
- Base/platform (wood, acrylic, or repurposed mount)
- Weatherproof enclosure for Orange Pi + electronics (IP-rated if possible)
- Cable management, zip ties, hot glue/epoxy, screws, silicone sealant

### 5. Power & Misc
- Separate 5V/6V battery pack or regulated supply for servos + water gun pump
- Do **not** power servos from the Orange Pi 5V rail under load
- Multimeter, soldering iron, wire strippers
- Optional: Small fan + heatsink for Orange Pi under sustained NPU load

**Rough cost breakdown**:
- Orange Pi 5 + PSU + camera: ~$80–120
- Servos + mounts + water gun: ~$30–60
- Electronics/misc: ~$20–40
- Enclosure/3D printing: variable

---

## System Flowcharts

Diagrams are split into focused pages for easy reading on GitHub:

- [Overview](docs/flowcharts/overview.md) — start here
- [Initialization](docs/flowcharts/01-initialization.md)
- [Detection and Targeting Loop](docs/flowcharts/02-detection-loop.md)
- [Error Handling and Monitoring](docs/flowcharts/03-error-handling.md)

---

## Power Requirements & Buck Converter Guide

### Per-Component Power Budget

| Component | Voltage | Typical Current | Peak Current |
|---|---|---|---|
| Orange Pi 5 (idle) | 5V | 0.8A (4W) | — |
| Orange Pi 5 (NPU load) | 5V | 2.5–3A (12–15W) | 4A |
| MG996R servo × 2 | 5–6V | 0.5A each (5W total) | 2.5A each (stall) |
| MG90S servo × 2 | 4.8–6V | 0.1A each (1W total) | 0.5A each (stall) |
| Water gun pump | 4.5–6V | 0.5–1A (3–5W) | 2A |
| USB camera | 5V (USB) | 0.5A | 0.5A |
| PCA9685 driver | 3.3–5V | 0.01A | — |

**Use two separate power rails.** Servos and pumps generate electrical noise and current spikes that can crash the Orange Pi if they share a supply.

### Converter Selection

Both rails use the same model — the **DROK 12V to 5V 5A USB Buck Converter**:

[DROK Buck Converter 12V to 5V, 5A USB Voltage Regulator](https://www.amazon.com/Converter-DROK-Regulator-Inverter-Transformer/dp/B01NALDSJ0)
- Input: 9–36V DC | Output: fixed 5V (5.0–5.3V) @ up to 5–6A
- USB output connector — plugs directly into the Orange Pi 5 USB-C port (with appropriate cable)
- Purchase two: one per rail

### Rail 1 — Orange Pi 5

- Output: **5V @ 5A** from the DROK converter above
- Wattage draw from 12V source: ~25W → ~2.1A @ 12V
- Connect via USB output on the converter → USB-C cable into the Orange Pi 5

### Rail 2 — Servos + Water Gun

- Output: **5V @ 5A** from a second DROK converter
- Wattage draw from 12V source: ~30W → ~2.5A @ 12V
- Water pistol confirmed 5V (USB rechargeable battery internally)
- Servos: use MG90S (4.8–6V) or MG996R (5–6V) — both run fine at 5V
- Add a 5A fuse on this rail as protection

### Total 12V Source Sizing

| Rail | Draw from 12V |
|---|---|
| Orange Pi 5 rail | ~2.1A |
| Servos + water gun rail | ~2.5A |
| Margin (20%) | ~1A |
| **Total** | **~5.5–6A @ 12V (~65–70W)** |

A **12V/6A (72W) power supply or battery** is sufficient. If running from a car battery or solar setup, this is a very light load.

### Wiring Diagram (simplified)

```
12V Source
   ├── DROK Converter #1 → 5V/5A (USB out) → USB-C → Orange Pi 5
   └── DROK Converter #2 → 5V/5A → Servos + Water Gun + PCA9685
```

---

## How It Works

1. A USB camera streams video continuously
2. YOLO-World identifies deer in the frame
3. Two servo motors aim the water gun at the target
4. A short water burst is triggered via a MOSFET/relay circuit
5. The system resets and keeps watching

Runs 24/7, fully local, no cloud required.

---

## Hardware Summary

| Component | Details |
|---|---|
| Compute board | Orange Pi 5 (RK3588 NPU, 6 TOPS) |
| Camera | USB 1080p webcam (UVC-compatible) |
| Servos | 2× MG90S or MG996R (pan + tilt) |
| Servo driver | PCA9685 I²C PWM driver (optional) |
| Trigger | IRLZ44N MOSFET or 5V relay module |
| Water gun | Disassembled battery-powered toy water gun |
| OS | Armbian on Orange Pi 5 |

---

## Repository Structure

```
deer-defense-project/
├── src/                  # Python source code
│   ├── main.py           # Entry point — detection + control loop
│   ├── detector.py       # YOLO-World inference wrapper
│   ├── servo_control.py  # Pan/tilt servo control
│   ├── trigger.py        # Water gun trigger (MOSFET/relay)
│   └── config.py         # Configuration (target class, thresholds, etc.)
├── docs/
│   └── flowcharts/       # System diagrams (overview + detail views)
├── hardware/             # Wiring diagrams, BOM, mechanical notes
├── tests/                # Unit and integration tests
├── CLAUDE.md             # Full project reference (this file)
├── README.md
└── .gitignore
```

---

## Getting Started

### Prerequisites

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
```

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy ultralytics
```

### Run (CPU/prototype mode)

```bash
python3 src/main.py
```

### Configuration

Edit `src/config.py` to set:
- `TARGET_CLASS` — text prompt for YOLO-World (default: `"deer"`)
- `CONFIDENCE_THRESHOLD` — detection confidence cutoff (default: `0.5`)
- `COOLDOWN_SECONDS` — delay between triggers (default: `3`)
- `BURST_DURATION` — water burst length in seconds (default: `0.5`)

---

## Contributing

Pull requests welcome. Open an issue first to discuss significant changes.

## License

MIT

---

## Step-by-Step Development Plan

### Phase 1: Planning & Mechanical Design (1–2 days)
1. Decide mounting location (garden stake, fence post, raised bed corner, etc.)
2. Design or buy a **pan-tilt mechanism** that holds the water gun + camera rigidly
3. Disassemble the water gun — identify how to trigger the pump (MOSFET vs relay)
4. Sketch wiring diagram and plan power rails
5. Plan coverage zone: map out where deer approach the tomato plants

**Tip**: 3D print a pan-tilt turret — many STL files on Thingiverse/Printables.

### Phase 2: Electronics Assembly & Basic Control (2–4 days)
1. Wire the two servos (signal, power, ground). Test with simple Python PWM first.
2. Build the trigger circuit:
   - MOSFET version: GPIO → Gate drives Drain/Source to switch water gun pump
   - Relay version: simpler, safer isolation
3. Connect USB camera and verify it works (`lsusb`, `fswebcam`, or OpenCV test)
4. Test basic movement + trigger without AI

**Recommended libraries**: `OPi.GPIO` or `gpiod` for GPIO; `adafruit-circuitpython-pca9685` if using the PWM driver.

### Phase 3: Software Environment Setup on Orange Pi 5 (1–2 days)
1. Flash **Armbian** (recommended for RK3588) or official Orange Pi OS
2. Update system, install: `python3`, `pip`, `git`, `opencv-python`, `numpy`
3. Install GPIO libraries and test
4. Set up a Python virtual environment

### Phase 4: AI Model — YOLO-World Inference (3–7 days)

Uses **yolo_world_v2l** (open-vocabulary — change target text without retraining).

**Options**:
- **Easiest starting point**: Ultralytics YOLO-World → export to ONNX, run on CPU first
- **Full NPU acceleration**: Convert to **RKNN** format using `rknn-toolkit2`
  - Export model to ONNX → convert with Rockchip tools → run on RK3588 NPU

**Basic detection loop** (Python pseudocode):
```python
import cv2

model = load_yolo_world("yolo_world_v2l.rknn")  # or ONNX for initial dev

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model.infer(frame, text_prompt="deer")

    for det in results:
        if det.conf > 0.5:
            x_center, y_center = get_bbox_center(det)
            aim_servos(x_center, y_center)
            trigger_water_gun(duration=0.5)  # short burst
            time.sleep(2)  # cooldown
```

**Pixel-to-servo mapping**:
```python
def pixel_to_servo(x, y, frame_w, frame_h):
    pan  = 90 + (x - frame_w/2) * (90 / (frame_w/2))   # center = 90°
    tilt = 90 + (y - frame_h/2) * (60 / (frame_h/2))   # adjust multipliers
    return clamp(pan, 0, 180), clamp(tilt, 30, 150)     # safety limits
```

**Calibration**: Map camera FOV + resolution to servo angle ranges. Start with printed targets before deploying outdoors.

Start with **CPU/OpenCV + Ultralytics** for rapid prototyping, then move to NPU.

### Phase 5: Full Integration & Logic (3–5 days)
1. Combine detection + servo control + trigger
2. Add logic:
   - Only trigger if target is inside the "garden zone" (bounding box region of frame)
   - Short bursts + cooldown to avoid wasting water
   - Optional: logging, Telegram/email alert on detection, web dashboard
3. Handle edge cases: multiple deer, false positives, low light, night detection
4. Add config file for target class (`"deer"`, `"rabbit"`, `"groundhog"`, etc.)

### Phase 6: Enclosure, Weatherproofing & Installation (2–4 days)
1. Mount everything securely near the tomato bed
2. Waterproof electronics (conformal coating, sealed enclosure, desiccant)
3. Route cables safely, protect from rain
4. Long-term outdoor testing
5. Add systemd service + watchdog for auto-restart

### Phase 7: Testing, Tuning & Improvements
- Daytime vs low-light performance (add IR camera for night coverage)
- Servo speed and aiming accuracy
- Water pressure and range of the toy gun
- False positive rate — tune confidence threshold or add size filtering (deer are large)
- Power consumption for 24/7 operation
- **Advanced ideas**: solar panel + battery, IR night vision, web UI for live target-class config, multiple zones covering the whole garden

---

## Key Implementation Notes

- **Performance**: Orange Pi 5 + RK3588 NPU can achieve real-time tracking (10–30 FPS)
- **Target prompt**: Use `"deer"` as the YOLO-World text prompt; also try `"white-tailed deer"` for better accuracy
- **Fire zone restriction**: Only spray when the bounding box center falls within a defined pixel region (the garden rows), reducing false triggers on passing animals outside the protected area
- **Cooldown**: 2–5 seconds recommended for deer (longer than pigeons — deer take more convincing)
- **Multi-target**: Track the largest detection (deer are big) or highest-confidence one

---

## Resources
- YOLO-World official: https://github.com/AILab-CVC/YOLO-World
- Ultralytics YOLO-World docs (easier starting point for prototyping)
- Rockchip RKNN examples + Ultralytics RKNN export guide
- Thingiverse/Printables: search "pan tilt servo turret"
- Inspiration: [u/muxamilian's pigeon defense system](https://www.reddit.com/r/SideProject/comments/1s9ywir/automated_pigeon_defense_system/)
